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

    # constrói as colunas x1, x2, ... transpondo A (que é organizado por linhas)
    x = []

    for i in range(n):
        coluna = []

        for j in range(m):
            coluna.append(problema.A[j][i])

        x.append(coluna)

    # constrói as colunas s1, s2, ... como matriz identidade (cada folga aparece em apenas uma restrição)
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


def calcular_cj_zj(coluna: list[float], cj: float, contributions: list[float]) -> float:
    """
    Calcula o ganho líquido de trazer uma variável para a base.

    Parâmetros:
        coluna       : coeficientes da variável em cada restrição
        cj           : coeficiente da variável na função objetivo
        contributions: contributions das variáveis atualmente na base

    Retorna:
        cj - zj : ganho líquido da variável
    """
    zj = 0.0
    for i in range(len(coluna)):
        zj += coluna[i] * contributions[i]
    return cj - zj


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

    tableau = construir_tableau_inicial(problema)

    while True:
        cj_zj_x = []
        for j in range(n):
            cj_zj_x.append(calcular_cj_zj(tableau.x[j], problema.c[j], tableau.contributions))

        cj_zj_s = []
        for j in range(m):
            cj_zj_s.append(calcular_cj_zj(tableau.s[j], 0.0, tableau.contributions))

        todos_cj_zj = cj_zj_x + cj_zj_s

        todos_negativos = True
        for valor in todos_cj_zj:
            if valor > 0:
                todos_negativos = False
                break

        # se todos os valores forem negativos, não há mais ponto de melhoria
        if todos_negativos:
            break

        # encontra o índice da variável com maior cj_zj (ela entra na base)
        indice_entra = 0
        for j in range(1, len(todos_cj_zj)):
            if todos_cj_zj[j] > todos_cj_zj[indice_entra]:
                indice_entra = j

    pass


if __name__ == "__main__":
    problema = Problema(
        c=[40.0, 35.0],
        A=[[2.0, 3.0], [4.0, 3.0]],
        b=[60.0, 96.0],
    )

    tableau = construir_tableau_inicial(problema)
    print("contributions:", tableau.contributions)
    print("base:", tableau.base)
    print("values:", tableau.values)
    print("x:", tableau.x)
    print("s:", tableau.s)
