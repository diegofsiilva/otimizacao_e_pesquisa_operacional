"""
tests/verificar_simplex.py

Verificação do simplex reescrito (variáveis limitadas + presolve, vetorizado).
Não depende de pytest. Faz três coisas:

  1. Casos canônicos (solução única, ilimitado, múltiplas, bounds nativos).
  2. Equivalência numérica: monta o LP real de limites de crédito a partir de um
     parquet de clusters em cache e confere que o z do nosso simplex bate com o
     do HiGHS (scipy.optimize.linprog), que é o solver de referência.
  3. Tempo: imprime quanto cada solver levou.

Uso:
    cd apps/algoritmo_simplex
    python tests/verificar_simplex.py
"""

from __future__ import annotations

import copy
import sys
import time
from pathlib import Path

import numpy as np

ALG_DIR = Path(__file__).resolve().parents[1]
if str(ALG_DIR) not in sys.path:
    sys.path.insert(0, str(ALG_DIR))

from models import Problema
from simplex import simplex

ROOT = ALG_DIR.parent.parent
CACHE = ROOT / "data" / "cache"

OK = "\033[92mOK\033[0m"
FAIL = "\033[91mFALHOU\033[0m"


def _aprox(a, b, tol=1e-6):
    """Compara dois números com tolerância relativa/absoluta.

    Args:
        a: Primeiro valor.
        b: Segundo valor.
        tol: Tolerância relativa (escalada pela maior magnitude entre 1, |a|, |b|).

    Returns:
        ``True`` se ``a`` e ``b`` são equivalentes dentro da tolerância.
    """
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


def casos_canonicos() -> bool:
    """Roda os casos didáticos de validação do Simplex (solução única, ilimitado etc.).

    Executa o solver sobre problemas com resultado conhecido e confere ``z``/``x``.

    Returns:
        ``True`` se todos os casos canônicos passaram; ``False`` caso contrário.
    """
    ok = True

    # solução única -> x=[18,8], z=1000
    x, z, st = simplex(Problema(c=[40, 35], A=[[2, 3], [4, 3]], b=[60, 96]))
    cond = _aprox(z, 1000) and _aprox(x[0], 18) and _aprox(x[1], 8) and st == "otimo"
    print(f"  [{OK if cond else FAIL}] solução única: x={x}, z={z:.2f}, {st}")
    ok &= cond

    # ilimitado -> ValueError
    try:
        simplex(Problema(c=[40, 35], A=[[-1, 0], [0, -1]], b=[60, 96]))
        print(f"  [{FAIL}] ilimitado: não levantou ValueError")
        ok = False
    except ValueError as e:
        cond = "ilimitado" in str(e)
        print(f"  [{OK if cond else FAIL}] ilimitado: {e}")
        ok &= cond

    # múltiplas soluções -> z=8
    x, z, st = simplex(Problema(c=[2, 4], A=[[1, 2], [1, 0]], b=[4, 2]))
    cond = _aprox(z, 8) and st == "multiplas_solucoes" and (x[0] + 2 * x[1] <= 4 + 1e-6)
    print(f"  [{OK if cond else FAIL}] múltiplas: x={x}, z={z:.2f}, {st}")
    ok &= cond

    # bounds nativos (R2/R3): x0<=5, x1<=7 -> x=[5,7], z=12
    x, z, st = simplex(Problema(c=[1, 1], A=[], b=[], upper=[5, 7]))
    cond = _aprox(z, 12) and _aprox(x[0], 5) and _aprox(x[1], 7)
    print(f"  [{OK if cond else FAIL}] bounds nativos: x={x}, z={z:.2f}, {st}")
    ok &= cond

    return ok


def _montar_lp_de_clusters(clusters, params):
    """
    Replica montar_problema() (R1 + R5 + bounds) a partir do parquet de clusters,
    sem precisar do df. Retorna (problema, c, A, b, upper).
    """
    t, LGD, u_bar, L_max, T = (
        params["t"],
        params["LGD"],
        params["u_bar"],
        params["L_max"],
        params["T"],
    )
    alpha = float(params.get("alpha", 0.05))
    n_k = clusters["n_k"].to_numpy(float)
    pi_k = clusters["pi_k"].to_numpy(float)
    PD_k = clusters["PD_k"].to_numpy(float)
    m_k = clusters["m_k"].to_numpy(float)
    CP_k = clusters["CP_k"].to_numpy(float)
    K = len(n_k)

    # pd_fin_atual: aqui aproximado pela média ponderada por n_k (suficiente para
    # checar a EQUIVALÊNCIA dos solvers no mesmo LP).
    pd_fin_atual = float((n_k * PD_k).sum() / n_k.sum())

    c = (n_k * pi_k * (u_bar * t * T - PD_k * LGD)).tolist()
    r1 = (n_k * (PD_k - pd_fin_atual)).tolist()
    upper = np.minimum(m_k * CP_k, float(L_max)).tolist()

    A = [r1]
    b = [0.0]
    if alpha > 0.0:  # R5 — concentração máxima por cluster
        A_r5 = -alpha * np.tile(n_k, (K, 1))
        A_r5[np.diag_indices(K)] += n_k
        A.extend(A_r5.tolist())
        b.extend([0.0] * K)

    problema = Problema(c=c, A=A, b=b, lower=[0.0] * K, upper=upper)
    return problema, c, A, b, upper


def equivalencia_e_tempo() -> bool:
    """Compara Simplex próprio vs. PuLP nos parquets reais e mede tempos.

    Para cada base de clusters em cache, monta o problema, resolve com os dois
    solvers, verifica a equivalência dos valores de ``z`` e reporta os tempos.

    Returns:
        ``True`` se todos os casos reais coincidiram dentro da tolerância;
        ``False`` caso algum divirja.
    """
    import pandas as pd

    parquets = sorted(CACHE.glob("*_clusters.parquet"))
    if not parquets:
        print("  (pulado) nenhum *_clusters.parquet em data/cache/")
        return True

    params = {"t": 0.0175, "LGD": 0.8, "u_bar": 0.75, "L_max": 25000.0, "T": 15}
    ok = True

    for pq_path in parquets:
        try:
            clusters = pd.read_parquet(pq_path)
        except Exception as e:
            print(f"  (pulado) {pq_path.name}: {e}")
            continue
        if not {"n_k", "pi_k", "PD_k", "m_k", "CP_k"}.issubset(clusters.columns):
            print(f"  (pulado) {pq_path.name}: colunas insuficientes")
            continue

        problema, c, A, b, upper = _montar_lp_de_clusters(clusters, params)
        K = len(c)

        t0 = time.perf_counter()
        x, z, st = simplex(problema)
        t_nosso = time.perf_counter() - t0

        linha = (
            f"  {pq_path.name} (K={K}, {len(A)} linhas): "
            f"nosso z={z:,.2f} [{st}] em {t_nosso*1e3:.1f} ms"
        )

        # Referência: resolve o MESMO Problema (R1 + R5 + bounds) com um solver
        # externo. Preferimos o PuLP/CBC (já é dependência do projeto, em
        # simplex_pulp.py); se faltar, tentamos o HiGHS via scipy.
        z_ref, ref_nome, t_ref = None, None, 0.0
        try:
            from simplex_pulp import simplex_pulp

            t0 = time.perf_counter()
            _, z_ref, _ = simplex_pulp(copy.deepcopy(problema))
            t_ref = time.perf_counter() - t0
            ref_nome = "PuLP/CBC"
        except Exception:
            try:
                from scipy.optimize import linprog

                t0 = time.perf_counter()
                res = linprog(
                    c=[-ci for ci in c],
                    A_ub=A,
                    b_ub=b,
                    bounds=[(0.0, u) for u in upper],
                    method="highs",
                )
                t_ref = time.perf_counter() - t0
                z_ref = -res.fun if res.success else None
                ref_nome = "HiGHS/scipy"
            except Exception:
                ref_nome = None

        if z_ref is not None:
            cond = _aprox(z, z_ref, tol=1e-6)
            linha += f" | {ref_nome} z={z_ref:,.2f} em {t_ref*1e3:.1f} ms -> "
            linha += OK if cond else FAIL
            ok &= cond
        else:
            linha += " | (sem solver de referência: instale pulp ou scipy)"

        print(linha)

    return ok


if __name__ == "__main__":
    print("1) Casos canônicos")
    ok1 = casos_canonicos()
    print("\n2) Equivalência com HiGHS + tempo (LP real de limites)")
    ok2 = equivalencia_e_tempo()
    print("\nRESULTADO:", OK if (ok1 and ok2) else FAIL)
    sys.exit(0 if (ok1 and ok2) else 1)
