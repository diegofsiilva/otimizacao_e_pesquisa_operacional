"""
scripts/reduce_csv.py
Reduz um arquivo .csv para uma porcentagem das primeiras linhas.

Uso:
    python reduce_csv.py <arquivo_entrada.csv> [porcentagem]

Argumentos:
    arquivo_entrada.csv : arquivo CSV em data/csv/
    porcentagem         : porcentagem das linhas a manter, de 1 a 100 (padrão: 10)

O arquivo reduzido é salvo com o sufixo _reduzido no mesmo diretório.

Exemplo:
    python reduce_csv.py clientes.csv        # salva clientes_reduzido.csv com 10%
    python reduce_csv.py clientes.csv 25     # salva clientes_reduzido.csv com 25%
"""

import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent

if len(sys.argv) < 2 or len(sys.argv) > 3:
    print("Uso:")
    print("    python reduce_csv.py <arquivo_entrada.csv> [porcentagem]")
    sys.exit(1)

arquivo_entrada = ROOT / "data" / "csv" / sys.argv[1]

if not arquivo_entrada.exists():
    print(f"Erro: arquivo {sys.argv[1]} não encontrado em data/csv/")
    sys.exit(1)

if len(sys.argv) == 3:
    try:
        porcentagem = int(sys.argv[2])
        if not 1 <= porcentagem <= 100:
            raise ValueError
    except ValueError:
        print("Erro: porcentagem deve ser um número inteiro entre 1 e 100")
        sys.exit(1)
else:
    porcentagem = 10

total_linhas = sum(1 for _ in open(arquivo_entrada)) - 1
n_linhas = max(1, int(total_linhas * porcentagem / 100))

arquivo_saida = arquivo_entrada.parent / (arquivo_entrada.stem + "_reduzido.csv")

df = pd.read_csv(arquivo_entrada, nrows=n_linhas)
df.to_csv(arquivo_saida, index=False)

print(f"Total de linhas: {total_linhas}")
print(f"Porcentagem: {porcentagem}%")
print(f"Linhas salvas: {n_linhas}")
print(f"Arquivo salvo em: {arquivo_saida}")
