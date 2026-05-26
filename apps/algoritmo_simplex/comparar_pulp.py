"""
algoritmo_simplex/comparar_pulp.py
Resolve o mesmo problema de PL usando PuLP (solver CBC) para validar
o resultado do nosso Simplex implementado do zero.

Uso independente:
    python comparar_pulp.py

Uso como módulo (chamado por main.py):
    from comparar_pulp import resolver_pulp
    x, z, status, tempo_ms = resolver_pulp(problema)
"""

import time

try:
    import pulp
except ImportError:
    raise ImportError(
        "PuLP não está instalado. Execute:\n"
        "    pip install pulp"
    )

from models import Problema


def resolver_pulp(problema: Problema) -> tuple[list[float], float, str, float]:
    """
    Resolve um problema de PL em forma padrão (maximização) usando PuLP / CBC.

    O problema é equivalente ao resolvido pelo nosso Simplex:
        max   c · x
        s.t.  A x <= b
              x >= 0

    Parâmetros:
        problema: instância de Problema contendo c, A e b

    Retorna:
        x        : lista com o valor ótimo de cada variável de decisão
        z        : valor ótimo da função objetivo
        status   : "otimo", "multiplas_solucoes" ou "ilimitado"
        tempo_ms : tempo de resolução em milissegundos
    """
    n = len(problema.c)
    m = len(problema.b)

    lp = pulp.LpProblem("otimizacao_limites", pulp.LpMaximize)

    # variáveis de decisão x_0, x_1, ..., x_{n-1} >= 0
    xs = [pulp.LpVariable(f"x_{j}", lowBound=0) for j in range(n)]

    # função objetivo
    lp += pulp.lpSum(problema.c[j] * xs[j] for j in range(n))

    # restrições
    for i in range(m):
        lp += pulp.lpSum(problema.A[i][j] * xs[j] for j in range(n)) <= problema.b[i]

    t0 = time.perf_counter()
    # MSG=0 suprime o output do solver no terminal
    lp.solve(pulp.PULP_CBC_CMD(msg=0))
    tempo_ms = (time.perf_counter() - t0) * 1000

    # mapeia o status do PuLP para o mesmo vocabulário do nosso Simplex
    pulp_status = pulp.LpStatus[lp.status]
    if pulp_status == "Optimal":
        status = "otimo"
    elif pulp_status == "Unbounded":
        status = "ilimitado"
    else:
        status = pulp_status.lower()

    x = [pulp.value(xs[j]) or 0.0 for j in range(n)]
    z = pulp.value(lp.objective) or 0.0

    return x, z, status, tempo_ms


def comparar(problema: Problema, x_simplex: list[float], z_simplex: float) -> None:
    """
    Resolve com PuLP e imprime uma comparação lado a lado com o resultado
    do nosso Simplex.

    Parâmetros:
        problema   : o mesmo Problema enviado ao nosso Simplex
        x_simplex  : solução retornada pelo nosso Simplex
        z_simplex  : valor objetivo retornado pelo nosso Simplex
    """
    x_pulp, z_pulp, status_pulp, tempo_ms = resolver_pulp(problema)

    delta_z = abs(z_simplex - z_pulp)
    delta_z_pct = (delta_z / abs(z_pulp) * 100) if z_pulp != 0 else 0.0

    print("\n" + "=" * 56)
    print("  COMPARAÇÃO: Simplex próprio vs PuLP / CBC")
    print("=" * 56)
    print(f"  {'Métrica':<28} {'Simplex':>10}  {'PuLP/CBC':>10}")
    print(f"  {'-'*28} {'-'*10}  {'-'*10}")
    print(f"  {'z (valor objetivo)':<28} {z_simplex:>10.2f}  {z_pulp:>10.2f}")
    print(f"  {'Status':<28} {'otimo':>10}  {status_pulp:>10}")
    print(f"  {'Δz absoluto':<28} {delta_z:>10.4f}")
    print(f"  {'Δz relativo (%)':<28} {delta_z_pct:>10.6f}%")
    print("=" * 56)
    print(f"\n  Limites por cluster:")
    print(f"  {'Cluster':<12} {'Simplex (R$)':>14}  {'PuLP (R$)':>12}  {'Match':>6}")
    print(f"  {'-'*12} {'-'*14}  {'-'*12}  {'-'*6}")
    for j in range(len(x_simplex)):
        lim_s = x_simplex[j]
        lim_p = x_pulp[j]
        match = "✓" if abs(lim_s - lim_p) < 1.0 else "✗"
        print(f"  {j:<12} {lim_s:>14.2f}  {lim_p:>12.2f}  {match:>6}")
    print()


if __name__ == "__main__":
    # exemplo rápido com o problema do professor
    from models import Problema as P

    prob = P(
        c=[40.0, 35.0],
        A=[[2.0, 3.0], [4.0, 3.0]],
        b=[60.0, 96.0],
    )

    from simplex import simplex
    x_s, z_s, _ = simplex(prob)
    print(f"Simplex: x={x_s}, z={z_s}")

    comparar(prob, x_s, z_s)
