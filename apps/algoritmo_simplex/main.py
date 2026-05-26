"""
algoritmo_simplex/main.py
Entrada de dados e execução do modelo de otimização de limites de crédito.

Uso:
    python main.py <arquivo_clientes.csv> <parametros.json>

    Exemplo:
        python main.py clientes_calibrado.csv parametros_producao.json
        python main.py clientes_calibrado.csv parametros_teste.json

Arquivos CSV devem estar em data/csv/
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
        params : dicionário com os parâmetros do modelo (t, LGD, u_bar, L_max)
    """
    df = pd.read_csv(arquivo_csv)
    print(f"Dados carregados: {len(df)} linhas, {len(df.columns)} colunas")

    with open(arquivo_json) as f:
        params = json.load(f)

    t = params["t"]
    LGD = params["LGD"]
    u_bar = params["u_bar"]
    L_max = params["L_max"]

    print(f"t={t}, LGD={LGD}, u_bar={u_bar}, L_max={L_max}")

    return df, params


def calcular_pd_fin_atual(df: pd.DataFrame) -> float:
    """
    Calcula a inadimplência financeira atual da carteira
    como média de pd_calibrada dos clientes elegíveis (flag_filtros == 0).
    """
    pd_fin_atual = df[df["flag_filtros"] == 0]["pd_calibrada"].mean()
    print(f"PD_fin_atual: {pd_fin_atual:.4f}")
    return pd_fin_atual


def garantir_clusters(arquivo_csv_nome: str) -> pd.DataFrame:
    """
    Verifica se o arquivo clusterizado já existe. Se não existir, roda o clustering.

    Retorna:
        clusters : DataFrame com os parâmetros agregados por cluster
    """
    stem = Path(arquivo_csv_nome).stem
    arquivo_clusters = (
        Path(__file__).resolve().parent.parent.parent
        / "data"
        / "csv"
        / f"{stem}_clusters.csv"
    )

    if not arquivo_clusters.exists():
        print(f"Gerando clusters para {arquivo_clusters.name}...")
        from clustering import main as clustering_main

        clustering_main(arquivo_csv_nome)
        print("Clustering concluído.")
    else:
        print(f"Arquivo {arquivo_clusters.name} encontrado. Pulando clustering.")

    clusters = pd.read_csv(arquivo_clusters)
    print(f"Clusters carregados: {len(clusters)} clusters")
    return clusters


def montar_problema(
    clusters: pd.DataFrame, params: dict, pd_fin_atual: float
) -> Problema:
    """
    Monta o problema de programação linear a partir dos parâmetros dos clusters.

    Restrições:
        R1: teto de inadimplência financeira (uma restrição para a carteira inteira)
        R2: capacidade de pagamento com alavancagem (uma restrição por cluster)
        R3: teto máximo de limite (uma restrição por cluster)
    """
    t = params["t"]
    LGD = params["LGD"]
    u_bar = params["u_bar"]
    L_max = params["L_max"]

    # monta o vetor de coeficientes da função objetivo (um por cluster)
    c = []
    for _, row in clusters.iterrows():
        ck = row["n_k"] * row["pi_k"] * (u_bar * t * 22 - row["PD_k"] * LGD)
        c.append(ck)

    # monta a matriz de restrições A e o vetor b
    A = []
    b = []

    # R1: teto de inadimplência financeira (uma restrição para a carteira inteira)
    r1 = []
    for _, row in clusters.iterrows():
        r1.append(row["n_k"] * (row["PD_k"] - pd_fin_atual))
    A.append(r1)
    b.append(0.0)

    # R2: capacidade de pagamento com alavancagem (uma restrição por cluster)
    for _, row in clusters.iterrows():
        linha = [0.0] * len(clusters)
        linha[int(row["cluster_id"])] = 1.0
        A.append(linha)
        b.append(row["m_k"] * row["CP_k"])

    # R3: teto máximo de limite (uma restrição por cluster)
    for _, row in clusters.iterrows():
        linha = [0.0] * len(clusters)
        linha[int(row["cluster_id"])] = 1.0
        A.append(linha)
        b.append(L_max)

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


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso:")
        print("    python main.py <arquivo_clientes.csv> <parametros.json>")
        print("Exemplo:")
        print("    python main.py clientes_calibrado.csv parametros.json")
        sys.exit(1)

    arquivo_csv = (
        Path(__file__).resolve().parent.parent.parent / "data" / "csv" / sys.argv[1]
    )
    arquivo_json = Path(__file__).resolve().parent / "input" / sys.argv[2]

    if not arquivo_csv.exists():
        print(f"Erro: arquivo CSV {sys.argv[1]} não encontrado em data/csv/")
        sys.exit(1)

    if not arquivo_json.exists():
        print(
            f"Erro: arquivo JSON {sys.argv[2]} não encontrado em algoritmo_simplex/input/"
        )
        sys.exit(1)

    # executa o pipeline completo
    df, params = carregar_dados(arquivo_csv, arquivo_json)
    pd_fin_atual = calcular_pd_fin_atual(df)
    clusters = garantir_clusters(sys.argv[1])
    problema = montar_problema(clusters, params, pd_fin_atual)
    x, z, status = simplex(problema)
    exibir_resultado(x, z, status, clusters)