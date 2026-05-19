"""
algoritmo_simplex/simplex.py
Implementação do algoritmo Simplex para problemas de programação linear.
"""

from models import Problema, Tableau

EPSILON = 1e-9

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
# 1. Calcula Z_j e C_j - Z_j
        todos_cj_zj = []

        # Para variáveis de decisão x
        for j in range(n):
            zj = sum(tableau.contributions[i] * tableau.x[j][i] for i in range(m))
            todos_cj_zj.append(problema.c[j] - zj)

        # Para variáveis de folga s
        for j in range(m):
            zj = sum(tableau.contributions[i] * tableau.s[j][i] for i in range(m))
            todos_cj_zj.append(0.0 - zj)

        # 2. Verifica critério de parada (Regra de Bland com EPSILON)
        indice_entra = -1
        for j in range(len(todos_cj_zj)):
            if todos_cj_zj[j] > EPSILON:
                indice_entra = j
                break

        if indice_entra == -1:
            status = "otimo"
            break

        # 3. Determina a variável que sai da base (Razão Mínima)
        indice_sai = -1
        menor_razao = float("inf")

        for i in range(m):
            # Obtém o coeficiente correto da variável que entra
            if indice_entra < n:
                coeficiente = tableau.x[indice_entra][i]
            else:
                coeficiente = tableau.s[indice_entra - n][i]

            if coeficiente > EPSILON:
                razao = tableau.values[i] / coeficiente
                if razao < menor_razao:
                    menor_razao = razao
                    indice_sai = i

        if indice_sai == -1:
            status = "ilimitado"
            break

        # 4. Operações de Pivoteamento (Eliminação Gaussiana Dinâmica)
        if indice_entra < n:
            elemento_pivo = tableau.x[indice_entra][indice_sai]
        else:
            elemento_pivo = tableau.s[indice_entra - n][indice_sai]

        # Divide a linha do pivô
        tableau.values[indice_sai] /= elemento_pivo
        for j in range(n):
            tableau.x[j][indice_sai] /= elemento_pivo
        for j in range(m):
            tableau.s[j][indice_sai] /= elemento_pivo

        # Zera os elementos acima e abaixo do pivô nas outras linhas
        for i in range(m):
            if i != indice_sai:
                if indice_entra < n:
                    fator = tableau.x[indice_entra][i]
                else:
                    fator = tableau.s[indice_entra - n][i]

                tableau.values[i] -= fator * tableau.values[indice_sai]
                for j in range(n):
                    tableau.x[j][i] -= fator * tableau.x[j][indice_sai]
                for j in range(m):
                    tableau.s[j][i] -= fator * tableau.s[j][indice_sai]

        # Atualiza a base
        tableau.base[indice_sai] = indice_entra
        tableau.contributions[indice_sai] = (
            problema.c[indice_entra] if indice_entra < n else 0.0
        )

    # Monta o vetor de solução final
    x_final = [0.0] * n
    for i in range(m):
        if tableau.base[i] < n:
            x_final[tableau.base[i]] = max(0.0, tableau.values[i])

    # Calcula o valor ótimo de Z
    z_otimo = sum(problema.c[j] * x_final[j] for j in range(n))

    return x_final, z_otimo, status


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
