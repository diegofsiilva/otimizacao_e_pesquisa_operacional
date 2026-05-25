"""
apps/algoritmo_simplex/main.py

Entrada de dados e execução do modelo de otimização de limites de crédito.
Suporta execução via terminal (CLI) e chamadas dinâmicas pelo Back-end.
Inclui logs de iteração e parametrização dinâmica de limites superiores (L_max).
"""

import sys
import json
from pathlib import Path
import pandas as pd
from models import Problema
from simplex import simplex


def carregar_dados(arquivo_csv: Path, arquivo_json: Path) -> tuple[pd.DataFrame, dict]:
    """
    Carrega o CSV de clientes (já clusterizados) e o JSON de parâmetros do modelo.
    """
    df = pd.read_csv(arquivo_csv)
    print(f"Dados carregados: {len(df)} linhas, {len(df.columns)} colunas")

    with open(arquivo_json) as f:
        params = json.load(f)

    return df, params


def executar_pipeline_otimizacao(df_clusters: pd.DataFrame, params: dict, pd_fin_atual: float) -> dict:
    """
    Executa a montagem do problema linear e chama o Simplex dinamicamente.
    Retorna um dicionário com os resultados limpos e pós-processados para o Back-end.
    """
    t = params["t"]
    LGD = params["LGD"]
    u_bar = params["u_bar"]
    
    # PARAMETRIZAÇÃO DINÂMICA DO L_MAX:
    # Obtém o parâmetro L_max. Pode ser um número único (global) ou um dicionário mapeando por cluster_id.
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

    # 4. Restrições R3: PARAMETRIZAÇÃO DINÂMICA DO TETO MÁXIMO POR CLUSTER
    for i, row in df_clusters.iterrows():
        cluster_id = str(int(row["cluster_id"]))
        linha_r3 = [0.0] * total_clusters
        linha_r3[i] = 1.0
        A.append(linha_r3)
        
        # Se L_max no JSON for um dicionário, busca pelo ID do cluster em formato string.
        # Caso contrário, assume que é um valor numérico global único para todos os clusters.
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


def exibir_resultado(x: list[float], z: float, status: str, clusters: pd.DataFrame):
    """
    Exibe os resultados formatados no terminal (usado na execução manual).
    """
    print(f"\nStatus Final do Modelo: {status.upper()}")
    print(f"Valor ótimo da Carteira (Z): R$ {z:.2f}")
    print(f"\nLimites recomendados por cluster:")

    for i, row in clusters.iterrows():
        limite_final = x[i]
        print(
            f"  Cluster {int(row['cluster_id'])}: R$ {limite_final:.0f} (n={int(row['n_k'])})"
        )


# Bloco executável caso você rode "python main.py ..." pelo terminal
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso:")
        print("    python main.py <arquivo_clientes.csv> <parametros.json>")
        print("Exemplo:")
        print("    python main.py clientes.csv parametros.json")
        sys.exit(1)

    # Define os caminhos baseados na estrutura de pastas recomendada
    raiz_projeto = Path(__file__).resolve().parent.parent
    arquivo_csv_origem = raiz_projeto / "data" / "csv" / sys.argv[1]
    arquivo_json = raiz_projeto / "algoritmo_simplex" / "input" / sys.argv[2]

    # Deriva o nome do arquivo de clusters gerado pelo clustering.py
    stem = arquivo_csv_origem.stem
    arquivo_clusters = arquivo_csv_origem.parent / f"{stem}_clusters.csv"

    if not arquivo_clusters.exists():
        print(f"Erro: Arquivo de clusters agrupados {arquivo_clusters.name} não encontrado.")
        print("Certifique-se de rodar o clustering.py primeiro.")
        sys.exit(1)

    if not arquivo_json.exists():
        print(f"Erro: Arquivo JSON de parâmetros {arquivo_json.name} não encontrado.")
        sys.exit(1)

    # 1. Carrega os dados dos clusters agregados
    df_c, parametros = carregar_dados(arquivo_clusters, arquivo_json)
    
    # 2. Chama a pipeline dinâmica
    resposta = executar_pipeline_otimizacao(df_c, parametros, pd_fin_atual=0.0175)
    
    # 3. Extrai e exibe o resultado formatado no terminal para conferência
    vetor_x_puro = [
        next(c["limite_otimizado"] for c in resposta["resultados_por_cluster"] if c["cluster_id"] == idx)
        for idx in df_c["cluster_id"]
    ]
    exibir_resultado(vetor_x_puro, resposta["valor_otimo"], resposta["status"], df_c)