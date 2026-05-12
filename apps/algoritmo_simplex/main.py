"""
algoritmo_simplex/main.py
Entrada de dados e execução do modelo de otimização de limites de crédito.

Uso:
    python main.py <arquivo_clientes.csv> <parametros.json>

    Exemplo:
        python main.py clientes.csv parametros_producao.json
        python main.py clientes.csv parametros_teste.json

Arquivos CSV devem estar em apps/data/csv/
Arquivos JSON devem estar em apps/algoritmo_simplex/input/
"""

import sys
import json
from pathlib import Path
import pandas as pd
from simplex import simplex

if len(sys.argv) < 3:
    print("Uso:")
    print("    python main.py <arquivo_clientes.csv> <parametros.json>")
    print("Exemplo:")
    print("    python main.py clientes.csv parametros.json")
    sys.exit(1)

arquivo_csv = Path("../data/csv/" + sys.argv[1])
arquivo_json = Path("input/" + sys.argv[2])

if not arquivo_csv.exists():
    print(f"Erro: arquivo CSV {sys.argv[1]} não encontrado em data/csv/")
    sys.exit(1)

if not arquivo_json.exists():
    print(
        f"Erro: arquivo JSON {sys.argv[2]} não encontrado em algoritmo_simplex/input/"
    )
    sys.exit(1)

df = pd.read_csv(arquivo_csv)
print(f"Dados carregados: {len(df)} linhas, {len(df.columns)} colunas")

with open(arquivo_json) as f:
    params = json.load(f)

t = params["t"]
LGD = params["LGD"]
u_bar = params["u_bar"]
L_max = params["L_max"]

print(f"t={t}, LGD={LGD}, u_bar={u_bar}, L_max={L_max}")

# calcula a inadimplência financeira atual da carteira como média de pd_produto dos elegíveis
pd_fin_atual = df[df["flag_filtros"] == 0]["pd_produto"].mean()
print(f"PD_fin_atual: {pd_fin_atual:.4f}")

# determina o caminho do arquivo clusterizado correspondente ao CSV de entrada
stem = Path(sys.argv[1]).stem
arquivo_clusters = Path("../data/csv/") / f"{stem}_clusters.csv"

# se o arquivo clusterizado não existir, roda o clustering antes de continuar
if not arquivo_clusters.exists():
    print(f"Arquivo {arquivo_clusters.name} não encontrado. Rodando clustering...")
    from clustering import main as clustering_main

    clustering_main(sys.argv[1])
    print("Clustering concluído.")
else:
    print(f"Arquivo {arquivo_clusters.name} encontrado. Pulando clustering.")

# lê os parâmetros agregados por cluster gerados pelo clustering
clusters = pd.read_csv(arquivo_clusters)
print(f"Clusters carregados: {len(clusters)} clusters")

# monta o vetor de coeficientes da função objetivo (um por cluster)
c = []
for _, row in clusters.iterrows():
    ck = row["n_k"] * row["pi_k"] * (u_bar * t - row["PD_k"] * LGD)
    c.append(ck)

# monta a matriz de restrições A e o vetor b
# R1: teto de inadimplência financeira (uma restrição para a carteira inteira)
# R2: capacidade de pagamento com alavancagem (uma restrição por cluster)
# R3: teto máximo de limite (uma restrição por cluster)
A = []
b = []

# R1
r1 = []
for _, row in clusters.iterrows():
    r1.append(row["n_k"] * (row["PD_k"] - pd_fin_atual))
A.append(r1)
b.append(0.0)

# R2
for _, row in clusters.iterrows():
    linha = [0.0] * len(clusters)
    linha[int(row["cluster_id"])] = 1.0
    A.append(linha)
    b.append(row["m_k"] * row["CP_k"])

# R3
for _, row in clusters.iterrows():
    linha = [0.0] * len(clusters)
    linha[int(row["cluster_id"])] = 1.0
    A.append(linha)
    b.append(L_max)
