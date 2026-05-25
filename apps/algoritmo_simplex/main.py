"""
apps/algoritmo_simplex/main.py

Entrada de dados e execução do modelo de otimização de limites de crédito.
Suporta execução via terminal (CLI) e chamadas dinâmicas pelo Back-end (APIs).
Inclui logs de iteração, parametrização de L_max e interface para FastAPI/Flask.
"""

import sys
import json
from pathlib import Path
import pandas as pd
from models import Problema
from simplex import simplex


def executar_otimizacao_via_api(dados_clusters_lista: list[dict], parametros_json: dict, pd_fin_atual: float = 0.0175) -> dict:
    """
    FUNÇÃO DE CONVENIÊNCIA PARA O BACK-END.
    Recebe os dados agregados dos clusters e as configurações diretamente em memória 
    (sem ler arquivos do disco) e retorna o resultado estruturado pronto para virar JSON.
    
    :param dados_clusters_lista: Lista de dicionários contendo os dados de cada cluster.
                                 Ex: [{'cluster_id': 0, 'n_k': 100, 'pi_k': 0.15, 'PD_k': 0.02, 'm_k': 1.2, 'CP_k': 2500.0}]
    :param parametros_json: Dicionário com os parâmetros macro (t, LGD, u_bar, L_max).
    :param pd_fin_atual: Taxa de inadimplência alvo global (default: 1.75%).
    :return: Dicionário estruturado com o status da otimização, Z ótimo e limites finais.
    """
    # Converte a lista de dicionários recebida da API em um DataFrame temporário em memória
    df_clusters = pd.DataFrame(dados_clusters_lista)
    
    # Executa a pipeline de otimização existente
    return executar_pipeline_otimizacao(df_clusters, parametros_json, pd_fin_atual)


def executar_pipeline_otimizacao(df_clusters: pd.DataFrame, params: dict, pd_fin_atual: float) -> dict:
    """
    Executa a montagem do problema linear e chama o Simplex dinamicamente.
    Retorna um dicionário com os resultados limpos e pós-processados para o Back-end.
    """
    t = params["t"]
    LGD = params["LGD"]
    u_bar = params["u_bar"]
    
    # Parametrização dinâmica do L_max (Aceita valor global ou dicionário por cluster)
    l_max_config = params.get("L_max", 5000.0) 

    c = []
    A = []
    b = []

    # 1. Montagem da Função Objetivo (c) baseada na quantidade dinâmica de clusters
    for _, row in df_clusters.iterrows():
        ck = row["n_k"] * row["pi_k"] * (u_bar * t - row["PD_k"] * LGD)
        c.append(float(ck))

    # 2. Restrição R1: Teto de inadimplência média global
    r1 = []
    for _, row in df_clusters.iterrows():
        r1.append(float(row["n_k"] * (row["PD_k"] - pd_fin_atual)))
    A.append(r1)
    b.append(0.0)

    total_clusters = len(df_clusters)

    # 3. Restrições R2 (Capacidade de Pagamento por cluster)
    for i, row in df_clusters.iterrows():
        linha_r2 = [0.0] * total_clusters
        linha_r2[i] = 1.0
        A.append(linha_r2)
        b.append(float(row["m_k"] * row["CP_k"]))

    # 4. Restrições R3: Teto máximo por cluster (Mapeamento Dinâmico)
    for i, row in df_clusters.iterrows():
        cluster_id = str(int(row["cluster_id"]))
        linha_r3 = [0.0] * total_clusters
        linha_r3[i] = 1.0
        A.append(linha_r3)
        
        if isinstance(l_max_config, dict):
            teto_cluster = l_max_config.get(cluster_id, l_max_config.get("default", 5000.0))
        else:
            teto_cluster = l_max_config
            
        b.append(float(teto_cluster))

    # 5. Instancia o Problema e Resolve via Simplex Autoral com Logs por Iteração
    problema = Problema(c=c, A=A, b=b)
    x_otimo, z_otimo, status = simplex(problema)

    # 6. Pós-Processamento dos limites (Regras de negócio de R$50 e corte de R$200)
    lista_limites_finais = []
    for i, row in df_clusters.iterrows():
        limite_cru = x_otimo[i]
        if limite_cru >= 200:
            limite_final = 50 * round(limite_cru / 50)
        else:
            limite_final = 0
        
        lista_limites_finais.append({
            "cluster_id": int(row["cluster_id"]),
            "n_k": int(row["n_k"]),
            "limite_otimizado": limite_final
        })

    return {
        "status": status,
        "valor_otimo": float(z_otimo),
        "resultados_por_cluster": lista_limites_finais
    }


def carregar_dados(arquivo_csv: Path, arquivo_json: Path) -> tuple[pd.DataFrame, dict]:
    """
    Carrega o CSV de clientes (já clusterizados) e o JSON de parâmetros do modelo.
    Usado apenas na execução local via terminal (CLI).
    """
    df = pd.read_csv(arquivo_csv)
    print(f"Dados carregados via CLI: {len(df)} linhas")

    with open(arquivo_json) as f:
        params = json.load(f)

    return df, params


def exibir_resultado(x: list[float], z: float, status: str, clusters: pd.DataFrame):
    """
    Exibe os resultados formatados no terminal (usado na execução manual via CLI).
    """
    print(f"\nStatus Final do Modelo: {status.upper()}")
    print(f"Valor ótimo da Carteira (Z): R$ {z:.2f}")
    print(f"\nLimites recomendados por cluster:")

    for i, row in clusters.iterrows():
        limite_final = x[i]
        print(
            f"  Cluster {int(row['cluster_id'])}: R$ {limite_final:.0f} (n={int(row['n_k'])})"
        )


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso:")
        print("    python main.py <arquivo_clientes.csv> <parametros.json>")
        sys.exit(1)

    raiz_projeto = Path(__file__).resolve().parent.parent
    arquivo_csv_origem = raiz_projeto / "data" / "csv" / sys.argv[1]
    arquivo_json = raiz_projeto / "algoritmo_simplex" / "input" / sys.argv[2]

    stem = arquivo_csv_origem.stem
    arquivo_clusters = arquivo_csv_origem.parent / f"{stem}_clusters.csv"

    if not arquivo_clusters.exists() or not arquivo_json.exists():
        print("Erro: Arquivos de entrada não encontrados nos caminhos padrões.")
        sys.exit(1)

    df_c, parametros = carregar_dados(arquivo_clusters, arquivo_json)
    
    # Testando o pipeline localmente
    resposta = executar_pipeline_otimizacao(df_c, parametros, pd_fin_atual=0.0175)
    
    vetor_x_puro = [
        next(c["limite_otimizado"] for c in resposta["resultados_por_cluster"] if c["cluster_id"] == idx)
        for idx in df_c["cluster_id"]
    ]
    exibir_resultado(vetor_x_puro, resposta["valor_otimo"], resposta["status"], df_c)