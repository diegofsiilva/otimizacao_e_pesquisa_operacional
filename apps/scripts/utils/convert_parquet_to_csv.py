"""
apps/scripts/utils/convert_parquet_to_csv.py
Converte um arquivo .parquet em data/parquet e salva como .csv em data/csv/

Uso:
    python convert_parquet_to_csv.py <arquivo_entrada.parquet> [nome_saida.csv] [--reduced [porcentagem]]

Argumentos:
    arquivo_entrada.parquet : arquivo em data/parquet/
    nome_saida.csv          : nome do arquivo de saída (padrão: mesmo nome do parquet)
    --reduced               : após converter, gera também uma versão reduzida
    porcentagem             : porcentagem a usar com --reduced (padrão: 10)

Exemplo:
    python convert_parquet_to_csv.py clientes.parquet
    python convert_parquet_to_csv.py clientes.parquet clientes_v2.csv
    python convert_parquet_to_csv.py clientes.parquet --reduced
    python convert_parquet_to_csv.py clientes.parquet --reduced 25
"""

import sys
import subprocess
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent.parent

args = sys.argv[1:]

if not args:
    print("Uso:")
    print(
        "    python convert_parquet_to_csv.py <arquivo_entrada.parquet> [nome_saida.csv] [--reduced [porcentagem]]"
    )
    sys.exit(1)

nome_parquet = args[0]
args = args[1:]

arquivo_entrada = ROOT / "data" / "parquet" / nome_parquet

if not arquivo_entrada.exists():
    print(f"Erro: arquivo {nome_parquet} não encontrado em data/parquet/")
    sys.exit(1)

if args and not args[0].startswith("--"):
    arquivo_saida = ROOT / "data" / "csv" / args[0]
    args = args[1:]
else:
    arquivo_saida = ROOT / "data" / "csv" / (arquivo_entrada.stem + ".csv")

reduced = False
porcentagem = 10

if args and args[0] == "--reduced":
    reduced = True
    args = args[1:]
    if args:
        try:
            porcentagem = int(args[0])
            if not 1 <= porcentagem <= 100:
                raise ValueError
        except ValueError:
            print("Erro: porcentagem deve ser um número inteiro entre 1 e 100")
            sys.exit(1)

print(f"Lendo {arquivo_entrada}...")
df = pd.read_parquet(arquivo_entrada)
df.to_csv(arquivo_saida, index=False)
print(f"Arquivo salvo em: {arquivo_saida}")

if reduced:
    print(f"Gerando versão reduzida ({porcentagem}%)...")
    subprocess.run(
        [
            sys.executable,
            str(Path(__file__).resolve().parent / "reduce_csv.py"),
            arquivo_saida.name,
            str(porcentagem),
        ]
    )
