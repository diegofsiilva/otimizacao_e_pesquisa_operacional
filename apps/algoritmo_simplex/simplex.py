"""
algoritmo_simplex/simplex.py
Implementação do algoritmo Simplex para problemas de programação linear.
"""


def simplex(
    c: list[float], A: list[list[float]], b: list[float]
) -> tuple[list[float], float]:
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

    n_variaveis_decisao = len(c)
    n_restricoes = len(A)

    for i in range(n_restricoes):
        variaveis_folga = [0] * n_restricoes
        variaveis_folga[i] = 1
        A[i].extend(variaveis_folga)

    c.extend([0] * n_restricoes)

    indices_base = list(range(n_variaveis_decisao, n_variaveis_decisao + n_restricoes))

    contributions_base = []
    for i in indices_base:
        contributions_base.append(c[i])
