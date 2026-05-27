"""
algoritmo_simplex/main.py
Entrada de dados e execução do modelo de otimização de limites de crédito.

Uso:
    python main.py <arquivo.parquet> <parametros.json>

    Exemplo:
        python main.py base_ref_M1_v2.parquet parametros_producao.json
        python main.py base_ref_M1_v2.parquet parametros_teste.json

Arquivos parquet devem estar em data/parquet/
Arquivos JSON devem estar em apps/algoritmo_simplex/input/
"""

import sys
import json
from pathlib import Path
import pandas as pd
from models import Problema
from simplex import simplex

# calibrar_pd está em scripts/ - adicionado ao path uma única vez no nível do módulo
_SCRIPTS_DIR = str(Path(__file__).resolve().parent.parent.parent / "scripts")
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)
from calibrar_pd import calibrar as _calibrar_pd


def carregar_dados(
    arquivo_parquet: Path, arquivo_json: Path
) -> tuple[pd.DataFrame, dict]:
    """
    Carrega o parquet calibrado de clientes e o JSON de parâmetros do modelo.

    Retorna:
        df     : DataFrame com os dados dos clientes
        params : dicionário com os parâmetros do modelo (t, LGD, u_bar, L_max, T)
    """
    df = pd.read_parquet(arquivo_parquet)
    print(f"Dados carregados: {len(df)} linhas, {len(df.columns)} colunas")

    with open(arquivo_json) as f:
        params = json.load(f)

    t = params["t"]
    LGD = params["LGD"]
    u_bar = params["u_bar"]
    L_max = params["L_max"]
    T = params["T"]

    print(f"t={t}, LGD={LGD}, u_bar={u_bar}, L_max={L_max}, T={T}")

    return df, params


def calcular_pd_fin_atual(df: pd.DataFrame) -> float:
    """
    Calcula a inadimplência financeira atual da carteira
    como média de pd_calibrada dos clientes elegíveis (flag_filtros == 0).
    """
    pd_fin_atual = df[df["flag_filtros"] == 0]["pd_calibrada"].mean()
    print(f"PD_fin_atual: {pd_fin_atual:.4f}")
    return pd_fin_atual


def garantir_calibrado(parquet_nome: str) -> Path:
    """
    Verifica se o parquet calibrado existe em data/cache/.
    Se não existir, roda a calibração.
    Retorna o path do parquet calibrado.
    """
    cache_dir = Path(__file__).resolve().parent.parent.parent / "data" / "cache"
    stem = Path(parquet_nome).stem
    arquivo_calibrado = cache_dir / f"{stem}_calibrado.parquet"

    if not arquivo_calibrado.exists():
        print(f"Calibrando {parquet_nome}...")
        _calibrar_pd(parquet_nome)
        print("Calibração concluída.")
    else:
        print(f"{arquivo_calibrado.name} encontrado. Pulando calibração.")

    return arquivo_calibrado


def garantir_clusters(
    parquet_calibrado_nome: str, params_json_nome: str
) -> pd.DataFrame:
    """
    Verifica se o arquivo clusterizado já existe em data/cache/. Se não existir, roda o clustering.
    Passa o parametros.json para o clustering para garantir que T seja consistente.

    Retorna:
        clusters : DataFrame com os parâmetros agregados por cluster
    """
    stem = Path(parquet_calibrado_nome).stem
    arquivo_clusters = (
        Path(__file__).resolve().parent.parent.parent
        / "data"
        / "cache"
        / f"{stem}_clusters.parquet"
    )

    if not arquivo_clusters.exists():
        print(f"Gerando clusters para {arquivo_clusters.name}...")
        from clustering import main as clustering_main

        clustering_main(parquet_calibrado_nome, params_json_nome)
        print("Clustering concluído.")
    else:
        print(f"Arquivo {arquivo_clusters.name} encontrado. Pulando clustering.")

    clusters = pd.read_parquet(arquivo_clusters)
    print(f"Clusters carregados: {len(clusters)} clusters")
    return clusters


def montar_problema(clusters: pd.DataFrame, params: dict, df: pd.DataFrame) -> Problema:
    """
    Monta o problema de programação linear a partir dos parâmetros dos clusters.

    Restrições:
        R1: teto de inadimplência financeira (uma restrição para a carteira inteira)
        R2: capacidade de pagamento com alavancagem (uma restrição por cluster)
        R3: teto máximo de limite (uma restrição por cluster)
    """
    pd_fin_atual = calcular_pd_fin_atual(df)
    t = params["t"]
    LGD = params["LGD"]
    u_bar = params["u_bar"]
    L_max = params["L_max"]
    T = params["T"]

    # monta o vetor de coeficientes da função objetivo (um por cluster)
    c = []
    for _, row in clusters.iterrows():
        ck = row["n_k"] * row["pi_k"] * (u_bar * t * T - row["PD_k"] * LGD)
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

    # # R5: concentração máxima por cluster
    # alpha = params["alpha"]

    # for _, row_k in clusters.iterrows():
    #     linha = []
    #     for _, row_j in clusters.iterrows():
    #         if row_j["cluster_id"] == row_k["cluster_id"]:
    #             linha.append(row_j["n_k"] * (1 - alpha))
    #         else:
    #             linha.append(-row_j["n_k"] * alpha)
    #     A.append(linha)
    #     b.append(0.0)

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


def executar_pipeline(parquet_path: Path, params: dict) -> dict:
    """
    Executa o pipeline completo de otimização a partir de um parquet e um
    dicionário de parâmetros. Retorna um dicionário estruturado com o resultado.

    Usado pelo backend para chamar o otimizador sem depender de sys.argv
    nem de arquivo JSON em disco.

    Retorna:
        status              : status do Simplex ("otimo" ou "multiplas_solucoes")
        z                   : valor ótimo da função objetivo
        clusters            : lista de dicts com os parâmetros de cada cluster
                              e o limite otimizado
        parquet_com_cluster : path do parquet _com_cluster gerado pelo clustering,
                              usado pelo backend para persistir a atribuição de
                              cada cliente ao seu cluster
    """
    json_dir = Path(__file__).resolve().parent / "input"
    json_temp = json_dir / "_params_temp.json"

    try:
        # escreve os parâmetros num JSON temporário para o clustering
        json_temp.write_text(json.dumps(params), encoding="utf-8")

        parquet_calibrado = garantir_calibrado(parquet_path.name)
        df = pd.read_parquet(parquet_calibrado)
        clusters = garantir_clusters(parquet_calibrado.name, json_temp.name)
    finally:
        if json_temp.exists():
            json_temp.unlink()

    problema = montar_problema(clusters, params, df)
    x, z, status = simplex(problema)

    resultado_clusters = []
    for i, row in clusters.iterrows():
        limite = x[i]
        limite_final = 50 * round(limite / 50) if limite >= 200 else 0
        resultado_clusters.append(
            {
                "cluster_id": int(row["cluster_id"]),
                "n_clientes": int(row["n_k"]),
                "pd_media": float(row["PD_k"]),
                "pi_media": float(row["pi_k"]),
                "cp_percentil5": float(row["CP_k"]),
                "score_credito_cross_medio": float(row["score_cross_mean"]),
                "ck_medio": float(row["ck_medio"]),
                "fator_alavancagem": float(row["m_k"]),
                "limite_otimizado": limite_final,
            }
        )

    cache_dir = Path(__file__).resolve().parent.parent.parent / "data" / "cache"
    stem = parquet_calibrado.stem
    parquet_com_cluster = cache_dir / f"{stem}_com_cluster.parquet"

    return {
        "status": status,
        "z": z,
        "clusters": resultado_clusters,
        "parquet_com_cluster": parquet_com_cluster,
    }


def main() -> None:
    if len(sys.argv) < 3:
        print("Uso:")
        print("    python main.py <arquivo.parquet> <parametros.json>")
        print("Exemplo:")
        print("    python main.py base_ref_M1_v2.parquet parametros.json")
        sys.exit(1)

    arquivo_parquet = (
        Path(__file__).resolve().parent.parent.parent / "data" / "parquet" / sys.argv[1]
    )
    arquivo_json = Path(__file__).resolve().parent / "input" / sys.argv[2]

    if not arquivo_parquet.exists():
        print(f"Erro: arquivo {sys.argv[1]} não encontrado em data/parquet/")
        sys.exit(1)

    if not arquivo_json.exists():
        print(
            f"Erro: arquivo JSON {sys.argv[2]} não encontrado em algoritmo_simplex/input/"
        )
        sys.exit(1)

    # executa o pipeline completo
    try:
        _, params = carregar_dados(arquivo_parquet, arquivo_json)
        resultado = executar_pipeline(arquivo_parquet, params)

        # lê os clusters do cache para exibição no terminal
        cache_dir = Path(__file__).resolve().parent.parent.parent / "data" / "cache"
        stem = Path(sys.argv[1]).stem
        clusters = pd.read_parquet(cache_dir / f"{stem}_calibrado_clusters.parquet")
        x = [c["limite_otimizado"] for c in resultado["clusters"]]
        exibir_resultado(x, resultado["z"], resultado["status"], clusters)
    except FileNotFoundError as e:
        print(f"Erro: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Erro inesperado no pipeline: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
