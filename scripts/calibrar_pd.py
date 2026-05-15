"""
scripts/calibrar_pd.py
Calibra a pd_produto de cada cliente usando os fatores gamma por decil,
calculados pelo script de análise e salvos em data/csv/tabela_gamma_decil.csv.

A pd_calibrada é calculada como:
    pd_calibrada(i) = pd_produto(i) * gamma(decil(i))

Uso:
    python calibrar_pd.py <arquivo_clientes.csv>

Arquivos CSV de entrada devem estar em data/csv/
Arquivos CSV de saída serão salvos em data/csv/ com o sufixo _calibrado
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
TABELA_GAMMA = ROOT / "data" / "csv" / "tabela_gamma_decil.csv"
DATA_DIR = ROOT / "data" / "csv"


if len(sys.argv) != 2:
    print("Uso:")
    print("    python calibrar_pd.py <arquivo_clientes.csv>")
    sys.exit(1)

arquivo_entrada = DATA_DIR / sys.argv[1]

if not arquivo_entrada.exists():
    print(f"Erro: arquivo {sys.argv[1]} não encontrado em data/csv/")
    sys.exit(1)

if not TABELA_GAMMA.exists():
    print(f"Erro: tabela_gamma_decil.csv não encontrada em data/csv/")
    print("Rode primeiro: python scripts/analise_09_calibracao_final.py")
    sys.exit(1)

print(f"[INFO] Lendo clientes: {arquivo_entrada.name}")
df = pd.read_csv(arquivo_entrada)
print(f"[INFO] {len(df):,} linhas carregadas")

print(f"[INFO] Lendo tabela de gamma: {TABELA_GAMMA.name}")
gamma = pd.read_csv(TABELA_GAMMA)

# monta os limites dos decis e os fatores gamma correspondentes
pd_min = gamma["pd_min"].values
pd_max = gamma["pd_max"].values
gamma_final = gamma["gamma_final"].values

# para cada cliente, descobre em qual decil o pd_produto se encaixa
# np.digitize retorna o índice do decil (1 a 10), ajustamos para 0 a 9
bins = np.concatenate([pd_min, [pd_max[-1]]])
indices = np.digitize(df["pd_produto"].values, bins[1:])
indices = np.clip(indices, 0, 9)

df["pd_calibrada"] = df["pd_produto"].values * gamma_final[indices]

arquivo_saida = DATA_DIR / (Path(sys.argv[1]).stem + "_calibrado.csv")
df.to_csv(arquivo_saida, index=False)
print(f"[OK] Arquivo salvo em: {arquivo_saida.name}")
