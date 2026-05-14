"""
algoritmo_simplex/main.py
Entrada de dados e execução do modelo de otimização de limites de crédito.

Uso:
    python main.py <arquivo_clientes.csv> <parametros.json>

    Exemplo:
        python main.py clientes.csv parametros_base.json
        python main.py clientes.csv parametros_conservador.json

Arquivos CSV devem estar em apps/data/csv/
Arquivos JSON devem estar em apps/algoritmo_simplex/input/
"""

import sys
import json
from pathlib import Path
import pandas as pd
from models import Problema
from simplex import simplex


def carregar_dados(arquivo_csv: Path, arquivo_json: Path) -> tuple[pd.DataFrame, dict]:
    """
    Carrega o CSV de clientes e o JSON de parâmetros do modelo.

    Retorna:
        df     : DataFrame com os dados dos clientes
        params : dicionário com os parâmetros do modelo (t, LGD, u_bar, L_max, T,
                 pd_fin_max, alpha_conc, gamma_decil, edges_pd)
    """
    df = pd.read_csv(arquivo_csv)
    print(f"Dados carregados: {len(df)} linhas, {len(df.columns)} colunas")

    with open(arquivo_json) as f:
        params = json.load(f)

    t = params["t"]
    LGD = params["LGD"]
    u_bar = params["u_bar"]
    L_max = params["L_max"]
    T = params.get("T", 22)
    pd_fin_max = params["pd_fin_max"]
    alpha_conc = params["alpha_conc"]

    print(
        f"t={t}, LGD={LGD}, u_bar={u_bar}, L_max={L_max}, T={T}, "
        f"pd_fin_max={pd_fin_max}, alpha_conc={alpha_conc}"
    )

    return df, params


def calcular_pd_fin_atual(df: pd.DataFrame) -> float:
    """
    Calcula a inadimplência financeira atual da carteira como média de
    pd_produto dos clientes elegíveis (flag_filtros == 0). Mantido apenas
    como referência diagnóstica; o LP usa pd_fin_max do JSON (PD da carteira
    aprovada vigente, ~0,32) e não a PD média da base elegível.
    """
    pd_fin_atual = df[df["flag_filtros"] == 0]["pd_produto"].mean()
    print(f"PD_fin_atual (elegiveis, diagnostico): {pd_fin_atual:.4f}")
    return pd_fin_atual


def garantir_clusters(arquivo_csv_nome: str, params_json_nome: str) -> pd.DataFrame:
    """
    Verifica se o arquivo clusterizado já existe. Se não existir, roda o clustering.

    Retorna:
        clusters : DataFrame com os parâmetros agregados por cluster
    """
    stem = Path(arquivo_csv_nome).stem
    arquivo_clusters = Path("../data/csv/") / f"{stem}_clusters.csv"

    if not arquivo_clusters.exists():
        print(f"Gerando clusters para {arquivo_clusters.name}...")
        from clustering import main as clustering_main

        clustering_main(arquivo_csv_nome, params_json_nome)
        print("Clustering concluido.")
    else:
        print(f"Arquivo {arquivo_clusters.name} encontrado. Pulando clustering.")

    clusters = pd.read_csv(arquivo_clusters)
    print(f"Clusters carregados: {len(clusters)} clusters")
    return clusters


def aplicar_gamma_do_json(clusters: pd.DataFrame, params: dict) -> pd.DataFrame:
    """Atualiza a coluna gamma_decil do cluster CSV com os valores correntes do
    JSON. Útil para cenários de drift que reutilizam o mesmo cluster CSV com
    gammas diferentes."""
    gamma = params.get("gamma_decil")
    if gamma is None:
        return clusters
    clusters = clusters.copy()
    clusters["gamma_decil"] = clusters["cluster_id"].apply(lambda d: gamma[int(d)])
    return clusters


def montar_problema(clusters: pd.DataFrame, params: dict) -> Problema:
    """
    Monta o problema de programação linear a partir dos parâmetros dos clusters.

    Restrições incluídas no LP:
        R1: teto de inadimplência financeira ponderada (linearizada)
            sum_k n_k * (PD_k - pd_fin_max) * L_k <= 0
        R2: capacidade de pagamento com alavancagem  L_k <= m_k * CP_k
        R3: teto máximo de limite                    L_k <= L_max
        R5: concentração máxima por cluster
            n_k * L_k - alpha * sum_j n_j * L_j <= 0   para cada k

    R4 (inadimplência física) é tratada em pós-otimização e R6 (volume mínimo)
    é opcional, conforme Seção 1.7 da modelagem.
    """
    t = params["t"]
    LGD = params["LGD"]
    u_bar = params["u_bar"]
    L_max = params["L_max"]
    T = params.get("T", 22)
    pd_fin_max = params["pd_fin_max"]
    alpha_conc = params["alpha_conc"]

    K = len(clusters)

    # FO: c_k = n_k * pi_k * (T * u_bar * t - PD_k * gamma_d * LGD)
    # (Seção 1.6 da modelagem_matematica.md)
    c = []
    for _, row in clusters.iterrows():
        gamma_d = row["gamma_decil"]
        ck = row["n_k"] * row["pi_k"] * (T * u_bar * t - row["PD_k"] * gamma_d * LGD)
        c.append(ck)

    A = []
    b = []

    # R1: teto de inadimplencia financeira ponderada (linearizada) usando pd_fin_max
    r1 = []
    for _, row in clusters.iterrows():
        r1.append(row["n_k"] * (row["PD_k"] - pd_fin_max))
    A.append(r1)
    b.append(0.0)

    # R2: capacidade de pagamento alavancada (uma linha por cluster)
    for _, row in clusters.iterrows():
        linha = [0.0] * K
        linha[int(row["cluster_id"])] = 1.0
        A.append(linha)
        b.append(row["m_k"] * row["CP_k"])

    # R3: teto máximo de limite (uma linha por cluster)
    for _, row in clusters.iterrows():
        linha = [0.0] * K
        linha[int(row["cluster_id"])] = 1.0
        A.append(linha)
        b.append(L_max)

    # R5: concentração máxima por cluster (uma linha por cluster)
    # n_k * L_k - alpha * sum_j n_j * L_j <= 0
    # equivalente a: sum_j n_j * (1[j==k] - alpha) * L_j <= 0
    ns = [row["n_k"] for _, row in clusters.iterrows()]
    for k_idx in range(K):
        linha = [0.0] * K
        for j in range(K):
            linha[j] = ns[j] * ((1.0 if j == k_idx else 0.0) - alpha_conc)
        A.append(linha)
        b.append(0.0)

    return Problema(c=c, A=A, b=b)


def pos_otimizar_limite(limite: float) -> float:
    """Pós-otimizacao (Seção 1.7 da modelagem): arredonda para múltiplo de 50
    se >= 200, senao zera."""
    if limite >= 200:
        return 50 * round(limite / 50)
    return 0.0


def exibir_resultado(
    x, z: float, status: str, clusters: pd.DataFrame, params: dict
) -> None:
    """
    Exibe um resumo completo da solucao:
      - Status, Z* e tabela por cluster (L_k*, L_final, n_k*L_k, PD_k, gamma_d, m_k*CP_k).
      - Volume total ofertado e PD financeira ponderada (validacao de R1).
      - Folgas e flags de binding para R1, R2 e R5.
      - Comparacao L_k* vs m_k*CP_k (binding de R2).
    """
    pd_fin_max = params.get("pd_fin_max", float("nan"))
    alpha_conc = params.get("alpha_conc", float("nan"))

    print(f"\nStatus: {status}")
    print(f"Z* (retorno liquido em T meses): R$ {z:,.2f}")

    header = (
        f"\n{'k':>3} {'decil':>5} {'n_k':>10} {'PD_k':>7} "
        f"{'gamma':>6} {'m_k':>5} {'m_k*CP':>10} {'L_k*':>10} "
        f"{'L_final':>10} {'n_k*L_k*':>17}"
    )
    print(header)
    print("-" * len(header))

    volume_total = 0.0
    pd_ponderada_num = 0.0
    pd_ponderada_den = 0.0
    sum_nL = sum(clusters.iloc[i]["n_k"] * x[i] for i in range(len(clusters)))

    folga_r2 = []
    folga_r5 = []

    for i, row in clusters.iterrows():
        Lk = x[i]
        Lk_final = pos_otimizar_limite(Lk)
        nk = row["n_k"]
        cap_r2 = row["m_k"] * row["CP_k"]
        slack_r2 = cap_r2 - Lk
        slack_r5 = alpha_conc * sum_nL - nk * Lk
        folga_r2.append((row["cluster_id"], row["decil"], slack_r2, cap_r2, Lk))
        folga_r5.append((row["cluster_id"], row["decil"], slack_r5))

        volume_total += nk * Lk
        pd_ponderada_num += nk * row["PD_k"] * Lk
        pd_ponderada_den += nk * Lk

        print(
            f"{int(row['cluster_id']):>3} {row['decil']:>5} {int(nk):>10} "
            f"{row['PD_k']:>7.3f} {row['gamma_decil']:>6.2f} {row['m_k']:>5.2f} "
            f"{cap_r2:>10.2f} {Lk:>10.2f} {Lk_final:>10.0f} {nk*Lk:>17,.2f}"
        )

    print("-" * len(header))

    pd_ponderada = pd_ponderada_num / pd_ponderada_den if pd_ponderada_den > 0 else 0.0
    clusters_ativos = sum(1 for i in range(len(clusters)) if x[i] > 0.5)

    print("\nResumo da carteira otimizada:")
    print(f"  Z*                          : R$ {z:,.2f}")
    print(f"  Volume total (sum n_k * L_k): R$ {volume_total:,.2f}")
    print(
        f"  PD ponderada resultante     : {pd_ponderada*100:.2f}%  "
        f"(teto pd_fin_max = {pd_fin_max*100:.2f}%)"
    )
    print(f"  Clusters ativos (L_k > 0)   : {clusters_ativos} de {len(clusters)}")

    # R1: folga sobre a forma linearizada sum n_k (PD_k - pd_fin_max) L_k <= 0
    lhs_r1 = sum(
        clusters.iloc[i]["n_k"] * (clusters.iloc[i]["PD_k"] - pd_fin_max) * x[i]
        for i in range(len(clusters))
    )
    folga_r1 = -lhs_r1
    binding_r1 = abs(folga_r1) < 1e-3 * max(1.0, pd_ponderada_den)
    print(f"\nRestricao R1 (PD financeira <= {pd_fin_max*100:.2f}%):")
    print(
        f"  LHS = {lhs_r1:,.2f}  RHS = 0  folga = {folga_r1:,.2f}  binding = {binding_r1}"
    )

    print(f"\nRestricao R2 (L_k <= m_k * CP_k) por cluster:")
    print(
        f"  {'k':>3} {'decil':>5} {'L_k*':>10} {'m_k*CP':>10} {'folga':>10}  binding"
    )
    for cid, dec, slack, cap, Lk in folga_r2:
        binding = abs(slack) < 0.5
        print(
            f"  {int(cid):>3} {dec:>5} {Lk:>10.2f} {cap:>10.2f} {slack:>10.2f}  {binding}"
        )

    print(
        f"\nRestricao R5 (n_k*L_k <= alpha * sum n_j*L_j, alpha = {alpha_conc:.2f}) por cluster:"
    )
    print(f"  {'k':>3} {'decil':>5} {'folga':>17}  binding")
    tol_r5 = max(1.0, 1e-6 * max(1.0, sum_nL))
    for cid, dec, slack in folga_r5:
        binding = abs(slack) < tol_r5
        print(f"  {int(cid):>3} {dec:>5} {slack:>17,.2f}  {binding}")


if len(sys.argv) < 3:
    print("Uso:")
    print("    python main.py <arquivo_clientes.csv> <parametros.json>")
    print("Exemplo:")
    print("    python main.py clientes.csv parametros_base.json")
    sys.exit(1)

arquivo_csv = Path("../data/csv/" + sys.argv[1])
arquivo_json = Path("input/" + sys.argv[2])

if not arquivo_csv.exists():
    print(f"Erro: arquivo CSV {sys.argv[1]} nao encontrado em data/csv/")
    sys.exit(1)

if not arquivo_json.exists():
    print(f"Erro: arquivo JSON {sys.argv[2]} nao encontrado em algoritmo_simplex/input/")
    sys.exit(1)

# executa o pipeline completo
df, params = carregar_dados(arquivo_csv, arquivo_json)
pd_fin_atual = calcular_pd_fin_atual(df)
clusters = garantir_clusters(sys.argv[1], sys.argv[2])
clusters = aplicar_gamma_do_json(clusters, params)
problema = montar_problema(clusters, params)
x, z, status = simplex(problema)
exibir_resultado(x, z, status, clusters, params)
