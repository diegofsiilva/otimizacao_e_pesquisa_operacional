"""
scripts/calibrar_pd.py

Calibra a pd_produto de cada cliente usando os fatores gamma por decil,
calculados pelo script setup_tabela_gamma.py.

A pd_calibrada e calculada como:
    pd_calibrada(i) = pd_produto(i) * gamma(decil(i))

Os limites dos decis sao os percentis de pd_produto calculados sobre a
populacao elegivel completa (flag_filtros == 0) nas 3 safras combinadas.

Uso:
    python calibrar_pd.py <arquivo.parquet>

Arquivos parquet de entrada devem estar em data/parquet/
Arquivos parquet de saida serao salvos em data/cache/ com o sufixo _calibrado
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
TABELA_GAMMA = ROOT / "data" / "csv" / "tabela_gamma_decil.csv"
INPUT_DIR = ROOT / "data" / "parquet"
CACHE_DIR = ROOT / "data" / "cache"


def calibrar(parquet_nome: str) -> Path:
    """
    Le o parquet de entrada, aplica gammas por decil e salva parquet calibrado em cache.
    Retorna o path do arquivo calibrado.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    arquivo_entrada = INPUT_DIR / parquet_nome

    if not arquivo_entrada.exists():
        raise FileNotFoundError(
            f"[calibracao] {parquet_nome} nao encontrado em data/parquet/"
        )

    if not TABELA_GAMMA.exists():
        raise FileNotFoundError(
            "[calibracao] tabela_gamma_decil.csv nao encontrada em data/csv/. "
            "Rode primeiro: python scripts/setup_tabela_gamma.py"
        )

    print(f"[INFO] Lendo: {arquivo_entrada.name}")
    df = pd.read_parquet(arquivo_entrada)
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

    # diagnostico apenas sobre elegiveis - os inelegiveis tem pd_produto mais alto
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

    arquivo_saida = CACHE_DIR / (Path(parquet_nome).stem + "_calibrado.parquet")
    df.to_parquet(arquivo_saida, index=False)
    print(f"\n[OK] Arquivo salvo em: {arquivo_saida.name}")
    return arquivo_saida


def main() -> None:
    if len(sys.argv) != 2:
        print("Uso:")
        print("    python calibrar_pd.py <arquivo.parquet>")
        sys.exit(1)
    calibrar(sys.argv[1])


if __name__ == "__main__":
    main()
