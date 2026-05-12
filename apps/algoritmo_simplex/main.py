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
    print(f"Erro: arquivo JSON {sys.argv[2]} não encontrado em algoritmo_simplex/input/")
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
