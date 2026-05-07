"""
apps/algorito_simplex/simplex.py
Resolve o problema de otimização de limites de crédito via algoritmo Simplex.

Por enquanto, resolvemos apenas uma versão simplificada do problema.
Entrada:
    - CSV com dados dos clientes (versão reduzida do parquet)
    - JSON com parâmetros constantes do modelo (t, LGD, u, L_max, PD_fin_atual)

Uso:
    python simplex.py <arquivo_clientes.csv> <parametros.json>

Arquivos CSV devem estar em apps/data/csv/
Arquivos JSON devem estar em apps/algoritmo_simplex/
"""

import sys
import json
from pathlib import Path
import pandas as pd

if len(sys.argv) != 3:
    print("Uso:")
    print("    python simplex.py <arquivo_clientes.csv> <parametros.json>")
    sys.exit(1)

arquivo_csv = Path("../data/csv/" + sys.argv[1])
arquivo_json = Path(sys.argv[2])

if not arquivo_csv.exists():
    print(f"Erro: arquivo CSV não encontrado em data/csv/reduced/")
    sys.exit(1)

if not arquivo_json.exists():
    print(f"Erro: arquivo JSON não encontrado: {arquivo_json}")
    sys.exit(1)

# lê o csv
df = pd.read_csv(arquivo_csv)
print(f"Dados carregados: {len(df)} linhas, {len(df.columns)} colunas")

# falta apenas a parte de ler o json