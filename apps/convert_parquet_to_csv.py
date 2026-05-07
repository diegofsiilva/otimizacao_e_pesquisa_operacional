"""
apps/convert_parquet_to_csv.py
Converte um arquivo .parquet em data/parquet e salva como .csv em data/csv

Uso:
    python convert_parquet_to_csv.py <arquivo_entrada.parquet> [nome_arquivo_saida.csv]

Se o nome do arquivo de saída não for especificado, ele usa automaticamente o mesmo nome do arquivo de entrada, mas com extensão .csv

Arquivos .parquet devem estar em apps/data/parquet
Arquivos .csv sairão em apps/data/csv
"""

import sys
from pathlib import Path
import pandas as pd


if len(sys.argv) < 2 or len(sys.argv) > 3:
    print("Uso:")
    print("    python convert_parquet_to_csv.py <arquivo_entrada.parquet> [nome_arquivo_saida.csv]")
    sys.exit(1)

arquivo_entrada = Path("data/parquet/" + sys.argv[1])
arquivo_saida = Path("data/csv/" + sys.argv[2]) if len(sys.argv) == 3 else Path("data/csv/" + arquivo_entrada.stem + ".csv")


if not arquivo_entrada.exists():
    print("O arquivo de entrada não existe em data/")
    sys.exit(1)

print(f"Lendo {arquivo_entrada}...")
df = pd.read_parquet(arquivo_entrada)
df.to_csv(arquivo_saida, index=False)
print(f"Arquivo {arquivo_entrada} convertido com sucesso para {arquivo_saida}")
