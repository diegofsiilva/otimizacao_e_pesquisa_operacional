"""
scripts/calibrar_pd.py

Calibra a pd_produto de cada cliente usando os fatores gamma por decil,
calculados pelo script analise_09_calibracao_final.py.

A pd_calibrada e calculada como:
    pd_calibrada(i) = pd_produto(i) * gamma(decil(i))

Os limites dos decis sao os percentis de pd_produto calculados sobre a
populacao elegivel completa (flag_filtros == 0) nas 3 safras combinadas.

Uso:
    python calibrar_pd.py <arquivo_clientes.csv>

Arquivos CSV de entrada devem estar em data/csv/
Arquivos CSV de saida serao salvos em data/csv/ com o sufixo _calibrado
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
TABELA_GAMMA = ROOT / "data" / "csv" / "tabela_gamma_decil.csv"
DATA_DIR = ROOT / "data" / "csv"

if len(sys.argv) != 2:
    print("Uso:")
    print("    python calibrar_pd.py <arquivo_clientes.csv>")
    sys.exit(1)

arquivo_entrada = DATA_DIR / sys.argv[1]

if not arquivo_entrada.exists():
    print(f"Erro: arquivo {sys.argv[1]} nao encontrado em data/csv/")
    sys.exit(1)

if not TABELA_GAMMA.exists():
    print(f"Erro: tabela_gamma_decil.csv nao encontrada em data/csv/")
    print("Rode primeiro: python scripts/analise_09_calibracao_final.py")
    sys.exit(1)

print(f"[INFO] Lendo clientes: {arquivo_entrada.name}")
df = pd.read_csv(arquivo_entrada)
print(f"[INFO] {len(df):,} linhas carregadas")

print(f"[INFO] Lendo tabela de gamma: {TABELA_GAMMA.name}")
gamma = pd.read_csv(TABELA_GAMMA)

pd_min = gamma["pd_min"].values
pd_max = gamma["pd_max"].values
gamma_final = gamma["gamma_final"].values

edges = np.concatenate([pd_min, [pd_max[-1]]])
indices = np.digitize(df["pd_produto"].values, edges[1:])
indices = np.clip(indices, 0, 9)

df["pd_calibrada"] = df["pd_produto"].values * gamma_final[indices]

# diagnostico apenas sobre elegiveis — os inelegiveis tem pd_produto mais alto
# por definicao e cairiam desproporcionalmente nos decis altos, o que e esperado
elegiveis = df["flag_filtros"] == 0
n_elig = elegiveis.sum()
indices_elig = indices[elegiveis.values]

print(f"\n[INFO] Distribuicao dos elegiveis por decil (esperado ~10% cada):")
print(f"       Base: {n_elig:,} elegiveis (flag_filtros == 0)")
for d in range(10):
    n = (indices_elig == d).sum()
    pct = 100 * n / n_elig
    barra = "#" * int(pct / 0.5)
    print(f"  D{d+1:>2}: {n:>8,} ({pct:>5.1f}%)  {barra}")

arquivo_saida = DATA_DIR / (Path(sys.argv[1]).stem + "_calibrado.csv")
df.to_csv(arquivo_saida, index=False)
print(f"\n[OK] Arquivo salvo em: {arquivo_saida.name}")
