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

    valores_iniciais = list(problema.b)  # cópia para não mutar o Problema original
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


def simplex(problema: Problema) -> tuple[list[float], float, str]:
    """
    Resolve um problema de programação linear pelo método Simplex.

    Parâmetros:
        problema: instância de Problema contendo c, A e b

    Retorna:
        x      : lista com o valor ótimo de cada variável de decisão (tamanho n)
        z      : valor ótimo da função objetivo
        status : "otimo", "multiplas_solucoes" ou "ilimitado"

    Raises:
        ValueError: se o problema for ilimitado
    """
    n = len(problema.c)  # número de variáveis de decisão
    m = len(problema.b)  # número de restrições

    tableau = construir_tableau_inicial(problema)

    while True:
        cj_zj_x = []
        for j in range(n):
            cj_zj_x.append(
                calcular_cj_zj(tableau.x[j], problema.c[j], tableau.contributions)
            )

        cj_zj_s = []
        for j in range(m):
            cj_zj_s.append(calcular_cj_zj(tableau.s[j], 0.0, tableau.contributions))

        todos_cj_zj = cj_zj_x + cj_zj_s

        # se todos os valores forem não-positivos, não há mais ponto de melhoria
        todos_nao_positivos = True
        for valor in todos_cj_zj:
            if valor > 0:
                todos_nao_positivos = False
                break

        if todos_nao_positivos:
            # verifica se há múltiplas soluções: alguma variável fora da base tem cj_zj == 0
            status = "otimo"
            for j in range(len(todos_cj_zj)):
                if j not in tableau.base and todos_cj_zj[j] == 0.0:
                    status = "multiplas_solucoes"
                    break
            break

        # regra de Bland: escolhe o menor índice com cj_zj positivo (evita ciclagem por degeneração)
        indice_entra = -1
        for j in range(len(todos_cj_zj)):
            if todos_cj_zj[j] > 0:
                indice_entra = j
                break

        # pega a coluna da variável que entra
        if indice_entra < n:
            # Se indice_entra < n, é um x
            coluna_entra = tableau.x[indice_entra]
        else:
            # Se indice_entra >= n, é um s
            coluna_entra = tableau.s[indice_entra - n]

        # teste da razão mínima
        # encontra a linha da variável que sai
        indice_sai = -1
        menor_razao = -1.0

        for i in range(m):
            if coluna_entra[i] > 0:
                razao = tableau.values[i] / coluna_entra[i]
                if indice_sai == -1 or razao < menor_razao:
                    menor_razao = razao
                    indice_sai = i

        # se nenhuma linha foi escolhida, o problema é ilimitado
        if indice_sai == -1:
            raise ValueError("O problema é ilimitado.")

        # elemento pivô (coeficiente da variável que entra na linha que sai)
        elemento_pivo = coluna_entra[indice_sai]

        # normaliza a linha pivô dividindo tudo pelo elemento pivô
        tableau.values[indice_sai] /= elemento_pivo

        for j in range(n):
            tableau.x[j][indice_sai] /= elemento_pivo

        for j in range(m):
            tableau.s[j][indice_sai] /= elemento_pivo

        # zera a coluna pivô em todas as outras linhas
        for i in range(m):
            if i == indice_sai:
                continue

            fator = coluna_entra[i]

            tableau.values[i] -= fator * tableau.values[indice_sai]

            for j in range(n):
                tableau.x[j][i] -= fator * tableau.x[j][indice_sai]

            for j in range(m):
                tableau.s[j][i] -= fator * tableau.s[j][indice_sai]

        # atualiza a base e a contribution da linha que mudou
        tableau.base[indice_sai] = indice_entra
        tableau.contributions[indice_sai] = (
            problema.c[indice_entra] if indice_entra < n else 0.0
        )

    # monta o vetor de solução
    # variáveis que não estão na base valem 0
    x = [0.0] * n
    for i in range(m):
        if tableau.base[i] < n:  # se a variável da base é uma variável de decisão
            x[tableau.base[i]] = tableau.values[i]

    # calcula o valor ótimo da função objetivo
    z = 0.0
    for j in range(n):
        z += problema.c[j] * x[j]

    return x, z, status


if __name__ == "__main__":
    # problema do professor (solução única)
    problema = Problema(
        c=[40.0, 35.0],
        A=[[2.0, 3.0], [4.0, 3.0]],
        b=[60.0, 96.0],
    )

    x, z, status = simplex(problema)
    print("Problema do professor")
    print("x:", x)
    print("z:", z)
    print("status:", status)

    # problema ilimitado
    problema_ilimitado = Problema(
        c=[40.0, 35.0],
        A=[[-1.0, 0.0], [0.0, -1.0]],
        b=[60.0, 96.0],
    )

    print("\nProblema ilimitado")
    try:
        x, z, status = simplex(problema_ilimitado)
    except ValueError as e:
        print("Erro:", e)

    # problema com múltiplas soluções
    problema_multiplas = Problema(
        c=[2.0, 4.0],
        A=[[1.0, 2.0], [1.0, 0.0]],
        b=[4.0, 2.0],
    )

    print("\nProblema com múltiplas soluções")
    x, z, status = simplex(problema_multiplas)
    print("x:", x)
    print("z:", z)
    print("status:", status)
