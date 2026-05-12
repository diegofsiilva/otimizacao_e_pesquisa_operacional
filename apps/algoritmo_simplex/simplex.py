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
    float(sys.argv[i + 2]) if i + 2 < len(sys.argv) else DEFAULTS[i] for i in range(4)
]

print(f"t={t}, LGD={LGD}, u_bar={u_bar}, L_max={L_max}")


def simplex(c: list[float], A: list[list[float]], b: list[float]):
    """
    Resolve um problema de programação linear na forma:
        max  c[0]*x[0] + c[1]*x[1] + ... + c[n]*x[n]
        s.t. A[i][0]*x[0] + A[i][1]*x[1] + ... <= b[i]  para cada restrição i
             x[j] >= 0  para cada variável j

    Parâmetros:
        c  : lista de coeficientes da função objetivo        (tamanho n)
        A  : matriz de coeficientes das restrições           (tamanho m x n)
        b  : lista dos lados direitos das restrições         (tamanho m)

    Retorna:
        x  : lista com o valor ótimo de cada variável        (tamanho n)
        z  : valor ótimo da função objetivo
    """

    n_variaveis_decisao = len(c)  # = 2, ou seja, x1 e x2
    n_restricoes = len(A)  # = 2, ou seja, s1 e s2

    for i in range(n_restricoes):
        # Para cada linha `i` de `A`, adiciona uma lista de zeros com um 1 na posição `i`
        variaveis_folga = [0] * n_restricoes
        variaveis_folga[i] = 1

        A[i].extend(variaveis_folga)

    indices_base = list(range(n_variaveis_decisao, n_variaveis_decisao + n_restricoes))
    c.extend([0] * n_restricoes)

    contributions_base = []
    for i in indices_base:
        contributions_base.append(c[i])
