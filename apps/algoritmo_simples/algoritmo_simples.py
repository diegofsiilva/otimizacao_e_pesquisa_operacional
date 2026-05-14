"""
Algoritmo simples: LP de otimizacao de limites pre-aprovados com calibracao
T=22 + gamma_decil por decil de pd_produto.

Le arquivos cenario_*.csv (clusters com PD, propensao, CP, m), aplica a
formulacao calibrada (Secao 1.5.1 e 1.6 da modelagem_matematica.md) e grava
resultado_cenario_*.csv com limite otimo, c_k calibrado e retorno esperado.

Uso:
  python algoritmo_simples.py                  # roda todos os cenarios
  python algoritmo_simples.py cenario_base     # roda apenas o indicado

Requer scipy (HiGHS via scipy.optimize.linprog).
"""

import csv
import os
import sys
import pathlib

import numpy as np
from scipy.optimize import linprog

# Parametros do modelo (em sincronia com modelagem_matematica.md)
T = 22                # horizonte de uso do limite (meses) - parceiro
U_BAR = 0.75          # utilizacao esperada
T_INT = 0.0175        # taxa de interchange mensal
LGD = 0.80            # loss given default
L_MAX = 25_000.0      # teto maximo de limite
ALPHA_CONC = 0.05     # concentracao maxima por cluster
PISO_OFERTA = 200.0   # abaixo de R$200 nao oferta
ARRED_MULT = 50.0     # arredondamento para multiplos de R$50

# Calibracao gamma_decil (extraida de analise_09_calibracao_final.py /
# tabela_gamma_decil.csv). Edges em pd_produto bruta na base elegivel M1+M2+M3.
GAMMA_DECIL = np.array([0.21, 0.21, 0.24, 0.24, 0.44, 0.40, 0.40, 0.40, 0.40, 0.40])
# Edges = 9 quantis (decis P10..P90) + extremos 0 e 1
EDGES_PD = np.array([0.0, 0.211, 0.296, 0.378, 0.461, 0.543, 0.619, 0.687, 0.746, 0.804, 1.01])


def decil_de_pd(pd_val: float) -> int:
    """Retorna o indice 0..9 do decil de pd_produto."""
    return int(np.clip(np.digitize([pd_val], EDGES_PD[1:-1])[0], 0, 9))


def gamma_de_pd(pd_val: float) -> float:
    return float(GAMMA_DECIL[decil_de_pd(pd_val)])


def resolver_lp(clusters, pd_fin_max=None, vol_min=None, alpha_conc=None, verbose=False):
    """
    clusters: lista de dicts com chaves
       cluster_id, n_clientes, pd_medio, propensao_media,
       capacidade_pagamento_p5, multiplicador_alavancagem
    Retorna lista de dicts com resultado por cluster.
    """
    K = len(clusters)
    nk = np.array([c['n_clientes'] for c in clusters], dtype=float)
    pd_k = np.array([c['pd_medio'] for c in clusters], dtype=float)
    pi_k = np.array([c['propensao_media'] for c in clusters], dtype=float)
    cp_k = np.array([c['capacidade_pagamento_p5'] for c in clusters], dtype=float)
    m_k = np.array([c['multiplicador_alavancagem'] for c in clusters], dtype=float)

    # Calibracao por decil
    gamma_k = np.array([gamma_de_pd(p) for p in pd_k])
    pd_cal = pd_k * gamma_k

    receita_unit = T * U_BAR * T_INT
    perda_unit = pd_cal * LGD
    c_k = pi_k * (receita_unit - perda_unit)

    # Coeficiente objetivo do LP (linprog minimiza, queremos maximizar)
    obj = -(nk * c_k)

    # R1: teto inadimplencia financeira (linearizado)
    A_ub = []
    b_ub = []
    if pd_fin_max is not None:
        A_ub.append(nk * (pd_k - pd_fin_max))
        b_ub.append(0.0)

    # R5: concentracao maxima por cluster (opcional - util para K >= 20)
    if alpha_conc is not None and alpha_conc > 0:
        for k in range(K):
            row = -alpha_conc * nk.copy()
            row[k] += nk[k]
            A_ub.append(row)
            b_ub.append(0.0)

    # R2 + R3: bounds individuais
    L_upper = np.minimum(m_k * cp_k, L_MAX)
    bounds = [(0.0, float(ub)) for ub in L_upper]

    # R6: volume minimo
    A_eq = None; b_eq = None
    if vol_min is not None and vol_min > 0:
        A_ub.append(-nk)
        b_ub.append(-float(vol_min))

    A_ub = np.array(A_ub) if A_ub else None
    b_ub = np.array(b_ub) if b_ub else None

    res = linprog(c=obj, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
    if not res.success:
        raise RuntimeError(f"LP infactivel: {res.message}")

    L_opt = res.x
    # Pos-otimizacao: arredondar e aplicar piso
    L_final = np.where(L_opt >= PISO_OFERTA,
                       ARRED_MULT * np.ceil(L_opt / ARRED_MULT),
                       0.0)
    retorno = nk * c_k * L_final

    out = []
    for k, c in enumerate(clusters):
        out.append({
            'cluster_id': c['cluster_id'],
            'n_clientes': int(nk[k]),
            'pd': pd_k[k],
            'pi': pi_k[k],
            'cp': cp_k[k],
            'm': m_k[k],
            'decil_pd': decil_de_pd(pd_k[k]) + 1,
            'gamma_decil': gamma_k[k],
            'pd_calibrada': pd_cal[k],
            'c_k': round(float(c_k[k]), 8),
            'limite_lp': round(float(L_opt[k]), 2),
            'limite_final': float(L_final[k]),
            'oferta': bool(L_final[k] > 0),
            'retorno_esperado': round(float(retorno[k]), 2),
        })
    if verbose:
        z = -res.fun
        print(f"  LP otimo: Z* = R$ {z:,.2f} | volume = R$ {(nk * L_final).sum():,.2f} | clusters com oferta: {int((L_final > 0).sum())}/{K}")
    return out


def ler_cenario(path):
    rows = []
    with open(path, newline='') as fp:
        r = csv.DictReader(fp)
        for row in r:
            rows.append({
                'cluster_id': int(row['cluster_id']),
                'n_clientes': int(row['n_clientes']),
                'pd_medio': float(row['pd_medio']),
                'propensao_media': float(row['propensao_media']),
                'capacidade_pagamento_p5': float(row['capacidade_pagamento_p5']),
                'multiplicador_alavancagem': float(row['multiplicador_alavancagem']),
            })
    return rows


def gravar_resultado(path, rows):
    if not rows:
        return
    with open(path, 'w', newline='') as fp:
        w = csv.DictWriter(fp, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)


def main():
    root = pathlib.Path(__file__).resolve().parent
    dados_dir = root / 'dados'
    res_dir = root / 'resultados'
    res_dir.mkdir(exist_ok=True)

    cenarios = sorted(p for p in dados_dir.glob('cenario_*.csv'))
    if len(sys.argv) > 1:
        nomes = set(sys.argv[1:])
        cenarios = [p for p in cenarios if p.stem in nomes or p.name in nomes]

    print(f"Parametros: T={T}, u_bar={U_BAR}, t={T_INT}, LGD={LGD}")
    print(f"gamma_decil = {GAMMA_DECIL.tolist()}")
    print(f"Receita unitaria T*u*t = {T*U_BAR*T_INT:.5f}")
    print()
    for c_path in cenarios:
        clusters = ler_cenario(c_path)
        print(f"== {c_path.stem} (K={len(clusters)} clusters) ==")
        result = resolver_lp(clusters, pd_fin_max=None, vol_min=None, verbose=True)
        out_path = res_dir / f"resultado_{c_path.stem}.csv"
        gravar_resultado(out_path, result)
        print(f"  -> {out_path}")
        print()


if __name__ == '__main__':
    main()
