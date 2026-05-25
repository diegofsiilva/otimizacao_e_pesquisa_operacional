"""
algoritmo_simplex/simplex.py
Implementação do algoritmo Simplex para problemas de programação linear.
"""
import logging
from models import Problema, Tableau

EPSILON = 1e-9

# Configuração padrão do logger para o módulo do otimizador
logger = logging.getLogger("otimizador_simplex")
logger.setLevel(logging.INFO)

# Formato limpo e profissional para os logs do terminal/back-end
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [Simplex] %(message)s", "%H:%M:%S")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

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

    logger.info(f"Iniciando Simplex. Variáveis de decisão (N): {n} | Restrições (M): {m}")

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
    Executa o algoritmo Simplex clássico exato com captura de logs por iteração.
    """
    n = len(problema.c)
    m = len(problema.b)

    logger.info(f"Iniciando Simplex. Variáveis de decisão (N): {n} | Restrições (M): {m}")
    
    tableau = construir_tableau_inicial(problema)
    
    # CORREÇÃO AQUI: Iniciamos em 1 e controlamos o incremento com segurança
    iteracao = 1

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

        # Calcula o valor atual de Z para o log de progresso
        # Encontra o valor atual de cada x se ele estiver na base, caso contrário 0
        z_atual = 0.0
        for j in range(n):
            if j in tableau.base:
                idx_base = tableau.base.index(j)
                z_atual += problema.c[j] * tableau.values[idx_base]
        
        # 2. Verifica critério de parada (Regra de Bland com EPSILON)
        indice_entra = -1
        for j in range(len(todos_cj_zj)):
            if todos_cj_zj[j] > EPSILON:
                indice_entra = j
                break

        # LOG DA ITERAÇÃO CORRENTE
        nome_variavel_entra = f"x{indice_entra + 1}" if indice_entra < n else f"s{indice_entra - n + 1}"
        if indice_entra != -1:
            logger.info(f"Iteração {iteracao:03d} | Z Atual = {z_atual:12.2f} | Candidata a entrar: {nome_variavel_entra} (C_j - Z_j = {todos_cj_zj[indice_entra]:.4f})")
        else:
            logger.info(f"Iteração {iteracao:03d} | Z Atual = {z_atual:12.2f} | Nenhuma variável candidata a entrar. Condição de otimalidade atingida.")
            status = "otimo"
            break

        # 3. Determina a variável que sai da base (Razão Mínima)
        indice_sai = -1
        menor_razao = float("inf")

        for i in range(m):
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
            logger.warning(f"Iteração {iteracao:03d} | Erro: Coeficientes da coluna {nome_variavel_entra} são todos <= 0. O problema é ilimitado.")
            status = "ilimitado"
            break

        # Identifica o nome da variável que está saindo da base para o log
        id_variavel_sai = tableau.base[indice_sai]
        nome_variavel_sai = f"x{id_variavel_sai + 1}" if id_variavel_sai < n else f"s{id_variavel_sai - n + 1}"
        logger.info(f"             └──> Pivotagem: {nome_variavel_entra} entra na base no lugar de {nome_variavel_sai} (Razão Mínima = {menor_razao:.4f})")

        # 4. Operações de Pivoteamento (Eliminação Gaussiana Dinâmica)
        if indice_entra < n:
            elemento_pivo = tableau.x[indice_entra][indice_sai]
        else:
            elemento_pivo = tableau.s[indice_entra - n][indice_sai]

        # Divide a linha do pivô pelo elemento pivô
        tableau.values[indice_sai] /= elemento_pivo
        for j in range(n):
            tableau.x[j][indice_sai] /= elemento_pivo
        for j in range(m):
            tableau.s[j][indice_sai] /= elemento_pivo

        # Zera os elements acima e abaixo do pivô nas outras linhas
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

        # Atualiza as estruturas da base
        tableau.base[indice_sai] = indice_entra
        tableau.contributions[indice_sai] = (
            problema.c[indice_entra] if indice_entra < n else 0.0
        )
        
        # Incrementa o número da iteração para o próximo ciclo
        iteracao += 1

    # Monta o vetor de solução final
    x_final = [0.0] * n
    for i in range(m):
        if tableau.base[i] < n:
            x_final[tableau.base[i]] = max(0.0, tableau.values[i])

    # Calcula o valor ótimo final de Z
    z_otimo = sum(problema.c[j] * x_final[j] for j in range(n))
    
    logger.info(f"Simplex finalizado com status: '{status.upper()}'. Total de iterações: {iteracao}. Z Ótimo = {z_otimo:.2f}")

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
