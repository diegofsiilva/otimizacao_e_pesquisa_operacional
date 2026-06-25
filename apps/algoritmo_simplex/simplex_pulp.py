"""
algoritmo_simplex/simplex_pulp.py
Implementação de referência do problema de programação linear usando a
biblioteca PuLP. Tem o mesmo contrato da função `simplex` em `simplex.py`,
permitindo comparar os resultados do Simplex implementado do zero contra
um solver consolidado (CBC, padrão do PuLP).

A intenção desta implementação NÃO é substituir o Simplex codado do projeto,
mas servir como referência de validação cruzada (golden test).

Notas de robustez:
    O CBC (solver padrão do PuLP) tem um bug conhecido no Windows quando o
    caminho do diretório do usuário contém espaços (ex.: C:\\Users\\luiz gustavo).
    Para contornar isso, este módulo:
      1. Cria um diretório temporário sem espaços (C:\\PulpTmp) e força o PuLP
         a usar esse caminho para os arquivos intermediários.
      2. Em caso de falha do CBC, tenta automaticamente outros solvers que o
         PuLP suporta (HiGHS via highspy, HiGHS_CMD, GLPK_CMD).
"""

import os
import tempfile

import pulp
from models import Problema


def _criar_tmpdir_sem_espacos() -> str:
    """
    Devolve um caminho de diretório temporário sem espaços. Necessário porque
    o CBC bundled com o PuLP falha no Windows quando o caminho contém espaço
    (caso clássico: `C:\\Users\\Nome Sobrenome\\AppData\\Local\\Temp`).
    """
    candidatos = [
        os.environ.get("PULP_TMPDIR"),
        "C:\\PulpTmp" if os.name == "nt" else None,
        "C:\\Temp" if os.name == "nt" else None,
        "C:\\Windows\\Temp" if os.name == "nt" else None,
        "/tmp" if os.name != "nt" else None,
        tempfile.gettempdir(),
    ]
    for c in candidatos:
        if c and " " not in c:
            try:
                os.makedirs(c, exist_ok=True)
                if os.path.isdir(c):
                    return c
            except OSError:
                continue

    # último recurso: cria um diretório curtinho na raiz do disco corrente
    fallback = "C:\\PulpTmp" if os.name == "nt" else "/tmp/pulp"
    os.makedirs(fallback, exist_ok=True)
    return fallback


def _obter_solver() -> tuple[object, str]:
    """
    Tenta selecionar um solver do PuLP que funcione no ambiente atual.
    Retorna o solver instanciado e o nome dele.
    """
    tmpdir = _criar_tmpdir_sem_espacos()

    tentativas = []

    # 1. CBC com tmpDir sem espaços - funciona na maioria dos Windows com nome de usuário com espaço
    def _tentar_cbc():
        # PuLP >= 2.0 NÃO aceita tmpDir no construtor (era válido só no PuLP 1.x).
        # A forma correta hoje é instanciar e setar o atributo tmpDir depois.
        solver = pulp.PULP_CBC_CMD(msg=0, keepFiles=False)
        solver.tmpDir = tmpdir
        return solver

    # 2. HiGHS via highspy (pip install highspy)
    def _tentar_highs_py():
        return pulp.HiGHS(msg=0)

    # 3. HiGHS_CMD (binário externo)
    def _tentar_highs_cmd():
        return pulp.HiGHS_CMD(msg=0)

    # 4. GLPK_CMD (caso o usuário tenha GLPK instalado)
    def _tentar_glpk():
        return pulp.GLPK_CMD(msg=0)

    candidatos = [
        ("CBC", _tentar_cbc),
        ("HiGHS", _tentar_highs_py),
        ("HiGHS_CMD", _tentar_highs_cmd),
        ("GLPK_CMD", _tentar_glpk),
    ]

    for nome, factory in candidatos:
        try:
            solver = factory()
            # alguns solvers expõem .available(); outros, não
            disponivel = True
            if hasattr(solver, "available"):
                try:
                    disponivel = bool(solver.available())
                except Exception:
                    disponivel = True
            if disponivel:
                return solver, nome
        except Exception as e:
            tentativas.append(f"{nome}: {e.__class__.__name__}")

    raise RuntimeError(
        "Nenhum solver do PuLP funcionou neste ambiente. Tentativas: "
        + "; ".join(tentativas)
    )


def simplex_pulp(problema: Problema) -> tuple[list[float], float, str]:
    """
    Resolve o mesmo problema de programação linear que a função `simplex`
    do projeto, mas usando a biblioteca PuLP (solver CBC por padrão,
    com fallback automático para HiGHS ou GLPK em caso de falha).

    Forma assumida (mesma da função `simplex` do projeto):
        max  c[0]*x[0] + ... + c[n-1]*x[n-1]
        s.t. A[i][0]*x[0] + ... + A[i][n-1]*x[n-1] <= b[i]   para cada i
             x[j] >= 0                                       para cada j

    Parâmetros:
        problema: instância de Problema contendo c, A e b

    Retorna:
        x      : lista com o valor ótimo de cada variável de decisão (tamanho n)
        z      : valor ótimo da função objetivo
        status : "otimo", "ilimitado", "inviavel" ou "erro"
                 (PuLP não diferencia "multiplas_solucoes" de "otimo" - quando
                 existem, retorna apenas uma das soluções ótimas com status "otimo")
    """
    n = len(problema.c)
    m = len(problema.b)

    # cria o modelo de maximização
    modelo = pulp.LpProblem("simplex_referencia", pulp.LpMaximize)

    # variáveis de decisão com bounds (lower/upper). Os bounds de R2/R3 entram
    # aqui — e NÃO como linhas de A — para o PuLP resolver o mesmo problema que
    # o nosso simplex de variáveis limitadas. lowBound padrão 0; upBound None = +inf.
    lower = problema.lower if problema.lower is not None else [0.0] * n
    upper = problema.upper if problema.upper is not None else [None] * n
    x_vars = [
        pulp.LpVariable(
            f"x_{j}",
            lowBound=(0.0 if lower[j] is None else float(lower[j])),
            upBound=(None if upper[j] is None else float(upper[j])),
            cat=pulp.LpContinuous,
        )
        for j in range(n)
    ]

    # função objetivo
    modelo += pulp.lpSum(problema.c[j] * x_vars[j] for j in range(n))

    # restrições do tipo <=
    for i in range(m):
        modelo += (
            pulp.lpSum(problema.A[i][j] * x_vars[j] for j in range(n)) <= problema.b[i],
            f"R_{i}",
        )

    # seleciona um solver que funcione no ambiente
    solver, _ = _obter_solver()
    codigo_status = modelo.solve(solver)

    # mapeia o status do PuLP para os mesmos rótulos usados no projeto
    status_pulp = pulp.LpStatus[codigo_status]
    if status_pulp == "Optimal":
        status = "otimo"
    elif status_pulp == "Unbounded":
        status = "ilimitado"
    elif status_pulp == "Infeasible":
        status = "inviavel"
    else:
        status = "erro"

    # se o solver não encontrou ótimo, levanta erro coerente com o `simplex` do projeto
    if status == "ilimitado":
        raise ValueError("O problema é ilimitado.")
    if status == "inviavel":
        raise ValueError("O problema é inviável.")
    if status == "erro":
        raise RuntimeError(f"Solver retornou status inesperado: {status_pulp}")

    # extrai a solução
    x = [float(pulp.value(v)) for v in x_vars]
    z = float(pulp.value(modelo.objective))

    return x, z, status


if __name__ == "__main__":
    # mesmos casos de teste de simplex.py, agora resolvidos com PuLP
    problema = Problema(
        c=[40.0, 35.0],
        A=[[2.0, 3.0], [4.0, 3.0]],
        b=[60.0, 96.0],
    )

    x, z, status = simplex_pulp(problema)
    print("Problema do professor (PuLP)")
    print("x:", x)
    print("z:", z)
    print("status:", status)

    problema_ilimitado = Problema(
        c=[40.0, 35.0],
        A=[[-1.0, 0.0], [0.0, -1.0]],
        b=[60.0, 96.0],
    )

    print("\nProblema ilimitado (PuLP)")
    try:
        x, z, status = simplex_pulp(problema_ilimitado)
        print("x:", x)
        print("z:", z)
        print("status:", status)
    except ValueError as e:
        print("Erro:", e)

    problema_multiplas = Problema(
        c=[2.0, 4.0],
        A=[[1.0, 2.0], [1.0, 0.0]],
        b=[4.0, 2.0],
    )

    print("\nProblema com múltiplas soluções (PuLP)")
    x, z, status = simplex_pulp(problema_multiplas)
    print("x:", x)
    print("z:", z)
    print("status:", status)