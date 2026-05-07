"""
apps/reduce_csv.py
Reduz um arquivo .csv para apenas as 10% primeiras linhas.

Uso:
    python reduce_csv.py <arquivo_entrada.csv>

Arquivos .csv devem estar em apps/data/csv
Arquivos reduzidos sairão em apps/data/csv/reduced
"""

import sys
from pathlib import Path
import pandas as pd

if len(sys.argv) != 2:
    print("Uso:")
    print("    python reduce_csv.py <arquivo_entrada.csv>")
    sys.exit(1)

arquivo_entrada = Path("data/csv") / sys.argv[1]
arquivo_saida = Path("data/csv/reduced") / sys.argv[1]

if not arquivo_entrada.exists():
    print("Erro: arquivo de entrada não encontrado em data/csv/")
    sys.exit(1)

arquivo_saida.parent.mkdir(parents=True, exist_ok=True)

total_linhas = sum(1 for _ in open(arquivo_entrada)) - 1  # -1 para ignorar o cabeçalho
n_linhas = int(total_linhas * 0.1)

df = pd.read_csv(arquivo_entrada, nrows=n_linhas)
df.to_csv(arquivo_saida, index=False)

print(f"Total de linhas: {total_linhas}")
print(f"Linhas salvas: {n_linhas}")
print(f"Arquivo salvo em: {arquivo_saida}")
