"""
apps/algoritmo_simplex/otimizador.py

Ponte de comunicação para o Back-end da API (FastAPI / Flask).
Invoca as regras matemáticas do main.py dinamicamente sem gerar erros de importação.
"""

import pandas as pd
from models import Problema
from simplex import simplex

def executar_otimizacao_via_api(dados_clusters_lista: list[dict], parametros_json: dict, pd_fin_atual: float) -> dict:
    """
    Recebe os dados do front-end/banco em memória e executa o Simplex do projeto.
    Retorna a resposta limpa e estruturada mapeada para o front.
    """
    # Importação tardia (Lazy Import) para evitar problemas de escopo/leitura com o main.py
    import main 
    
    # Converte os dados recebidos via API para DataFrame
    df_clusters = pd.DataFrame(dados_clusters_lista)
    
    # Executa a montagem exata definida no seu main.py original
    problema = main.montar_problema(df_clusters, parametros_json, pd_fin_atual)
    
    # Resolve usando o algoritmo Simplex autoral
    x_otimo, z_otimo, status = simplex(problema)
    
    # Pós-processamento dos limites idêntico ao exibir_resultado do main.py
    resultados_clusters = []
    for i, row in df_clusters.iterrows():
        limite_cru = x_otimo[i]
        if limite_cru >= 200:
            limite_final = 50 * round(limite_cru / 50)
        else:
            limite_final = 0
            
        resultados_clusters.append({
            "cluster_id": int(row["cluster_id"]),
            "n_k": int(row["n_k"]),
            "limite_otimizado": limite_final,
            "status_front": "viavel" if limite_final > 0 else "sem"
        })
        
    return {
        "status": status,
        "valor_otimo": float(z_otimo),
        "resultados_por_cluster": resultados_clusters
    }