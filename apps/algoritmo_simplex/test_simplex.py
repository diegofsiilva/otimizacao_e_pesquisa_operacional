"""
apps/algoritmo_simplex/test_simplex.py
Script para validar as novas implementações dinâmicas e de logs do otimizador.
"""

import logging
from main import executar_otimizacao_via_api

# Garante que os logs apareçam no terminal durante este teste
logging.basicConfig(level=logging.INFO)

def simular_teste_otimizador():
    print("=" * 70)
    print("🔬 INICIANDO TESTE DAS ATUALIZAÇÕES DO OTIMIZADOR (MAIN.PY)")
    print("=" * 70)

    # 1. Simulando os dados de 3 clusters que o Back-end enviaria na memória
    # (Pode ser 3, 7 ou mais de 100 clusters, o motor agora é dinâmico)
    dados_mock_clusters = [
        {
            "cluster_id": 0,
            "n_k": 500,        # Número de clientes
            "pi_k": 0.15,      # Propensão a uso
            "PD_k": 0.012,     # Probabilidade de Default (1.2%)
            "m_k": 1.1,        # Multiplicador do score
            "CP_k": 1500.0     # Capacidade de pagamento proxy
        },
        {
            "cluster_id": 1,
            "n_k": 800,
            "pi_k": 0.22,
            "PD_k": 0.035,     # Probabilidade de Default mais alta (3.5%)
            "m_k": 0.9,
            "CP_k": 2200.0
        },
        {
            "cluster_id": 2,
            "n_k": 300,
            "pi_k": 0.40,
            "PD_k": 0.008,     # Baixo risco (0.8%)
            "m_k": 1.5,
            "CP_k": 5000.0
        }
    ]

    # 2. Parâmetros macro simulando a nova parametrização dinâmica de L_max por cluster
    parametros_mock = {
        "t": 0.0175,
        "LGD": 0.60,
        "u_bar": 0.75,
        # Definindo tetos de limite diferentes para cada perfil de risco/renda
        "L_max": {
            "0": 2000.0,    # Perfil moderado
            "1": 1000.0,    # Risco mais alto, teto menor
            "2": 8000.0,    # Risco baixo, teto maior
            "default": 3000.0
        }
    }

    print("\n[Teste 1] Chamando 'executar_otimizacao_via_api' com dados em memória...\n")
    
    # 3. Executa a função que o Back-end em Python vai usar
    resposta = executar_otimizacao_via_api(
        dados_clusters_lista=dados_mock_clusters,
        parametros_json=parametros_mock,
        pd_fin_atual=0.0175 # Inadimplência alvo global
    )

    print("\n" + "=" * 70)
    print("📊 RESULTADOS RETORNADOS PARA A API:")
    print("=" * 70)
    print(f"Status da Resolução : {resposta['status'].upper()}")
    print(f"Valor Ótimo Total (Z): R$ {resposta['valor_otimo']:.2f}")
    print("\nLimites Calculados e Pós-processados (Múltiplos de R$ 50):")
    
    for cluster in resposta["resultados_por_cluster"]:
        print(f"  -> Cluster {cluster['cluster_id']}: R$ {cluster['limite_otimizado']} (Clientes: {cluster['n_k']})")
    
    print("=" * 70)
    print("✅ TESTE CONCLUÍDO COM SUCESSO!")
    print("=" * 70)

if __name__ == "__main__":
    simular_teste_otimizador()