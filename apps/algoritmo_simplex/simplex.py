"""
apps/algoritmo_simplex/simplex.py
Resolve o problema de otimização de limites de crédito via algoritmo Simplex.

Por enquanto, resolvemos apenas uma versão simplificada do problema.
Entrada:
    - CSV com dados dos clientes (versão reduzida do parquet)
    - Parâmetros ajustáveis opcionais via terminal (t, LGD, u_bar, L_max)

Uso:
    python simplex.py <arquivo_clientes.csv> [t] [LGD] [u_bar] [L_max]

Arquivos CSV devem estar em apps/data/csv/
"""

import sys
from pathlib import Path
import pandas as pd

if len(sys.argv) < 2:
    print("Uso:")
    print("    python simplex.py <arquivo_clientes.csv> [t] [LGD] [u_bar] [L_max]")
    sys.exit(1)

arquivo_csv = Path("../data/csv/" + sys.argv[1])

if not arquivo_csv.exists():
    print(f"Erro: arquivo CSV não encontrado em data/csv/")
    sys.exit(1)

# lê o csv
df = pd.read_csv(arquivo_csv)
print(f"Dados carregados: {len(df)} linhas, {len(df.columns)} colunas")

# parâmetros ajustáveis (defaults da tabela, coluna "Fonte")
DEFAULTS = [0.0175, 0.60, 0.75, 25000.0]

t, LGD, u_bar, L_max = [
    float(sys.argv[i + 2]) if i + 2 < len(sys.argv) else DEFAULTS[i]
    for i in range(4)
]

print(f"t={t}, LGD={LGD}, u_bar={u_bar}, L_max={L_max}")