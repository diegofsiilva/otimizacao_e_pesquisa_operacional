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
        print("Clustering concluído.")
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

    # R1: teto de inadimplência financeira ponderada (linearizada) usando pd_fin_max
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


def exibir_resultado(
    x: list[float], z: float, status: str, clusters: pd.DataFrame
) -> None:
    """
    Exibe os limites ótimos por cluster após pós-otimização:
    arredonda para múltiplo de 50, ou 0 se menor que 200.
    """
    print(f"\nStatus: {status}")
    print(f"Valor ótimo (z): {z:.2f}")
    print(f"\nLimites ótimos por cluster:")

    for i, row in clusters.iterrows():
        limite = x[i]
        if limite >= 200:
            limite_final = 50 * round(limite / 50)
        else:
            limite_final = 0
        print(
            f"  Cluster {int(row['cluster_id'])}: R$ {limite_final:.0f} (n={int(row['n_k'])})"
        )


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
exibir_resultado(x, z, status, clusters)
