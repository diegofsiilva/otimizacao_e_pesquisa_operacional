"""
algoritmo_simplex/simplex.py
Implementação do algoritmo Simplex para problemas de programação linear.
"""

from models import Problema, Tableau


def construir_tableau_inicial(problema: Problema) -> Tableau:
    """
    Constrói o tableau inicial a partir de um problema de programação linear.
    No tableau inicial, a base é formada pelas variáveis de folga.

    Parâmetros:
        problema: instância de Problema contendo c, A e b

    Retorna:
        Tableau inicial pronto para o algoritmo Simplex
    """
    n = len(problema.c)  # número de variáveis de decisão
    m = len(problema.b)  # número de restrições

    valores_iniciais = problema.b
    indices_variaveis_folga = list(range(n, n + m))
    contribuicao_variaveis_folga = [0.0] * m

    x = []

    for i in range(n):
        coluna = []

        for j in range(m):
            coluna.append(problema.A[j][i])

        x.append(coluna)

    s = []

    for i in range(m):
        coluna = [0.0] * m
        coluna[i] = 1.0
        s.append(coluna)

    return Tableau(
        contributions=contribuicao_variaveis_folga,
        base=indices_variaveis_folga,
        values=valores_iniciais,
        x=x,
        s=s,
    )


def simplex(problema: Problema) -> tuple[list[float], float]:
    """
    Resolve um problema de programação linear pelo método Simplex.

    Parâmetros:
        problema: instância de Problema contendo c, A e b

    Retorna:
        x: instância de Problema contendo c, A e b (tamanho N)
        z: valor ótimo da função objetivo
    """
    n = len(problema.c)  # número de variáveis de decisão
    m = len(problema.b)  # número de restrições
    pass
