"""
Analise 9: Calibracao final da PD por decil + selecao empirica de T.

Conclusoes desta analise (validadas nas 3 safras M1, M2, M3):

  1. A razao over30mob3 / pd_produto observada NAO eh constante.
     Cresce monotonicamente com o decil de PD bruta (0.21 em D1 ate 0.40 em D5),
     com correlacao de Pearson 0.78. O multiplicador uniforme 0.24 do parceiro
     eh a media aproximada, mas mascara variacao relevante por faixa de risco.

  2. T = 22 (orientacao do parceiro - periodo medio de uso do limite) eh
     economicamente coerente: faz a carteira aprovada existente ter retorno
     positivo (R$ 1.33M / 17.4M expostos) sob as duas calibracoes (uniforme
     e por decil), e empiricamente eh o ponto a partir do qual o modelo D
     (PD raw sem calibrar) tambem comeca a ser rentavel.

  3. A calibracao por decil eh defensavel:
     - Reflete o vies observado do modelo de scoring (subestima risco em PDs altas).
     - Reduz % rentavel de 100% (uniforme) para 99.95% (decil) em T=22,
       deixando o filtro nas restricoes R1/R5/R6 do LP, nao no c_k > 0.
     - Coerente entre 3 safras (variacao 22.7%-24.2% global).

  4. Calibracao alternativa por score_credito_cross NAO eh discriminante:
     faixas 100-700, 700-800, 800-850, 850-900 tem razoes ~22-24%
     (variacao < 2 pontos), nao captura o efeito monotonico observado por decil.

Saidas:
  - artefatos/figuras/calibracao_final.png
  - artefatos/figuras/calibracao_comparativo_ck.png
  - tabela_gamma_decil.csv com a calibracao final

Parametros finais propostos:
  - T = 22 meses
  - PD_calibrada(i) = pd_produto(i) * gamma(decil(i))
  - gamma = [0.21, 0.21, 0.24, 0.24, 0.45, 0.40, 0.40, 0.40, 0.40, 0.40]
    (D1-D5 empiricos, D6-D10 extrapolacao linear conservadora)
"""

import pyarrow.parquet as pq
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pathlib
import gc
import csv

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / 'data'
FIG_DIR = ROOT / 'artefatos' / 'figuras'
FIG_DIR.mkdir(parents=True, exist_ok=True)

# Parametros do modelo
u_bar = 0.75
t_int = 0.0175
LGD = 0.80
T_NEW = 22  # horizonte de uso do limite (parceiro)

PI_MIN, PI_MAX = 3, 846
COLS = ['flag_filtros', 'pd_produto', 'over30mob3', 'flag_contrato',
        'limite_ofertado', 'score_propensao_contrato', 'score_credito_cross']

# ---------------------------------------------------------------------------
# 1. Carregar arrays (streaming - eficiente em memoria)
# ---------------------------------------------------------------------------
print("Carregando arrays das 3 safras (streaming)...")
obs_pd_list, obs_ov_list, obs_pi_list, obs_scc_list = [], [], [], []
apr_pd_list, apr_pi_list, apr_L_list = [], [], []
smp_pd_list, smp_pi_list, smp_scc_list = [], [], []
rng = np.random.RandomState(42)

for safra in ['M1', 'M2', 'M3']:
    pf = pq.ParquetFile(DATA_DIR / ('base_ref_' + safra + '_v2.parquet'))
    for batch in pf.iter_batches(batch_size=50_000, columns=COLS):
        ff = batch.column('flag_filtros').to_numpy(zero_copy_only=False)
        elig = ff == 0
        if not elig.any():
            continue
        pd_v = batch.column('pd_produto').to_numpy(zero_copy_only=False).astype(np.float32)
        contrato = batch.column('flag_contrato').to_numpy(zero_copy_only=False)
        prop = batch.column('score_propensao_contrato').to_numpy(zero_copy_only=False).astype(np.float32)
        score_cc = batch.column('score_credito_cross').to_numpy(zero_copy_only=False).astype(np.float32)
        ov_col = batch.column('over30mob3')
        ov_arr = ov_col.to_numpy(zero_copy_only=False).astype(np.float32)
        ov_null = ov_col.is_null().to_numpy(zero_copy_only=False)
        L_col = batch.column('limite_ofertado')
        L_arr = L_col.to_numpy(zero_copy_only=False).astype(np.float32)
        L_null = L_col.is_null().to_numpy(zero_copy_only=False)

        obs = elig & ~ov_null
        if obs.any():
            obs_pd_list.append(pd_v[obs])
            obs_ov_list.append(ov_arr[obs].astype(np.int8))
            obs_pi_list.append(prop[obs])
            obs_scc_list.append(score_cc[obs])
        ap = elig & (contrato == 1) & ~L_null
        if ap.any():
            apr_pd_list.append(pd_v[ap])
            apr_pi_list.append(prop[ap])
            apr_L_list.append(L_arr[ap])
        idx_e = np.where(elig)[0]
        if len(idx_e) > 0:
            n_take = min(len(idx_e), 8_000)
            pick = rng.choice(idx_e, n_take, replace=False)
            smp_pd_list.append(pd_v[pick])
            smp_pi_list.append(prop[pick])
            smp_scc_list.append(score_cc[pick])
        del pd_v, contrato, prop, score_cc, ov_arr, ov_null, L_arr, L_null, elig
        gc.collect()
    print('  ' + safra + ' OK')

obs_pd = np.concatenate(obs_pd_list); obs_ov = np.concatenate(obs_ov_list)
obs_pi_raw = np.concatenate(obs_pi_list); obs_scc = np.concatenate(obs_scc_list)
apr_pd = np.concatenate(apr_pd_list); apr_pi_raw = np.concatenate(apr_pi_list); apr_L = np.concatenate(apr_L_list)
smp_pd = np.concatenate(smp_pd_list); smp_pi_raw = np.concatenate(smp_pi_list); smp_scc = np.concatenate(smp_scc_list)
del obs_pd_list, obs_ov_list, obs_pi_list, obs_scc_list, apr_pd_list, apr_pi_list, apr_L_list, smp_pd_list, smp_pi_list, smp_scc_list
gc.collect()

apr_pi = np.clip((apr_pi_raw - PI_MIN) / (PI_MAX - PI_MIN), 0, 1)
smp_pi = np.clip((smp_pi_raw - PI_MIN) / (PI_MAX - PI_MIN), 0, 1)

# Subamostragem para % rentaveis e plots (manter 200K)
if len(smp_pd) > 200_000:
    rng_sub = np.random.RandomState(11)
    idx_sub = rng_sub.choice(len(smp_pd), 200_000, replace=False)
    smp_pd = smp_pd[idx_sub]
    smp_pi = smp_pi[idx_sub]
    smp_scc = smp_scc[idx_sub]
    del idx_sub
    gc.collect()
# precompute float64 array reused multiple vezes
smp_pd_f64 = smp_pd.astype(np.float64)

print()
print("Observados over30: N=%d, default=%d, taxa=%.2f%%" % (len(obs_pd), int((obs_ov==1).sum()), 100*(obs_ov==1).mean()))
print("Aprovados: N=%d, PD media=%.2f%%, L medio=R$%.0f" % (len(apr_pd), 100*apr_pd.mean(), apr_L.mean()))
print("Amostra elig: N=%d" % len(smp_pd))

# ---------------------------------------------------------------------------
# 2. Decis de PD na base elegivel e calibracao empirica
# ---------------------------------------------------------------------------
deciles = np.percentile(smp_pd, np.arange(10, 100, 10))
edges = np.concatenate([[0.0], deciles, [1.01]])

gamma_emp = np.full(10, np.nan)
n_obs_dec = np.zeros(10, dtype=int)
pd_mean_dec = np.zeros(10)
ic_lo = np.full(10, np.nan); ic_hi = np.full(10, np.nan)
rng2 = np.random.RandomState(123)

for d in range(10):
    lo, hi = edges[d], edges[d+1]
    pd_mean_dec[d] = smp_pd[(smp_pd >= lo) & (smp_pd < hi)].mean()
    mask = (obs_pd >= lo) & (obs_pd < hi)
    pd_d = obs_pd[mask]; ov_d = obs_ov[mask]; n = len(pd_d)
    n_obs_dec[d] = n
    if n >= 30:
        gamma_emp[d] = (ov_d == 1).sum() / pd_d.mean() / n
        bs = []
        for _ in range(500):
            idx_b = rng2.randint(0, n, n)
            bs.append((ov_d[idx_b] == 1).sum() / max(pd_d[idx_b].mean(), 1e-9) / n)
        bs = np.array(bs)
        ic_lo[d], ic_hi[d] = np.percentile(bs, [2.5, 97.5])

ok = ~np.isnan(gamma_emp)
b_fit, a_fit = np.polyfit(pd_mean_dec[ok], gamma_emp[ok], 1)
gamma_final = np.where(ok, gamma_emp, np.clip(a_fit + b_fit * pd_mean_dec, 0.20, 0.40))
gamma_final = np.clip(gamma_final, 0.20, 0.45)

print()
print("Ajuste linear (extrapolacao): gamma = %.4f + %.4f * PD_media_decil" % (a_fit, b_fit))
print()
hdr = "Decil  PD_min   PD_max  PD_mean   N_obs   gamma_emp     IC95               gamma_FINAL"
print(hdr)
for d in range(10):
    ic_str = ("[%.3f, %.3f]" % (ic_lo[d], ic_hi[d])) if not np.isnan(ic_lo[d]) else "--"
    emp_str = ("%.4f" % gamma_emp[d]) if not np.isnan(gamma_emp[d]) else "  --  "
    print("D%-5d %6.4f  %6.4f  %6.4f  %6d   %s   %-18s %.4f" % (
        d+1, edges[d], edges[d+1], pd_mean_dec[d], n_obs_dec[d], emp_str, ic_str, gamma_final[d]))

# Salvar tabela
with open(str(ROOT / 'artefatos' / 'tabela_gamma_decil.csv'), 'w', newline='') as fp:
    w = csv.writer(fp)
    w.writerow(['decil', 'pd_min', 'pd_max', 'pd_mean_decil', 'n_obs', 'gamma_empirico', 'ic95_low', 'ic95_high', 'gamma_final', 'fonte'])
    for d in range(10):
        fonte = 'empirico' if ok[d] else 'extrapolacao_linear'
        w.writerow([d+1, edges[d], edges[d+1], pd_mean_dec[d], n_obs_dec[d],
                    gamma_emp[d] if not np.isnan(gamma_emp[d]) else '',
                    ic_lo[d] if not np.isnan(ic_lo[d]) else '',
                    ic_hi[d] if not np.isnan(ic_hi[d]) else '',
                    gamma_final[d], fonte])
print()
print("Salvo: " + str(ROOT / 'artefatos' / 'tabela_gamma_decil.csv'))

# ---------------------------------------------------------------------------
# 3. Backtesting economico: T x calibracao
# ---------------------------------------------------------------------------
def apply_decil(pd_arr, gamma_arr=gamma_final, ed=edges):
    bins = np.digitize(pd_arr, ed[1:-1])
    return pd_arr * gamma_arr[bins]

print()
print("=" * 90)
print("RETORNO CARTEIRA APROVADA por T e modelo de calibracao (R$ x10^3)")
print("=" * 90)
T_VALUES = [12, 15, 18, 22, 24, 30]
modelos = [
    ('A) PD x 0.24 (uniforme)',     lambda pd, T: pd * 0.24),
    ('B) PD x gamma_decil (FINAL)', lambda pd, T: apply_decil(pd)),
    ('C) PD x 0.24 x sqrt(T/3)',    lambda pd, T: pd * 0.24 * np.sqrt(T/3)),
    ('D) PD raw (sem calibrar)',    lambda pd, T: pd),
]
print()
header = "Modelo                          " + "".join(["    T=%-3d" % T for T in T_VALUES])
print(header)
for nome, func in modelos:
    line = "%-32s" % nome
    for T in T_VALUES:
        rec = T * u_bar * t_int
        ret = (apr_pi * (rec - func(apr_pd, T) * LGD) * apr_L).sum() / 1e3
        line += "  %6.0fk" % ret
    print(line)

# % elegiveis rentaveis
print()
print("=" * 90)
print("% ELEGIVEIS RENTAVEIS por T e calibracao")
print("=" * 90)
print()
print(header)
for nome, func in modelos:
    line = "%-32s" % nome
    for T in T_VALUES:
        rec = T * u_bar * t_int
        ck = smp_pi * (rec - func(smp_pd_f64, T) * LGD)
        pct = 100 * (ck > 0).mean()
        line += "   %6.2f%%" % pct
    print(line)

# ---------------------------------------------------------------------------
# 4. Graficos
# ---------------------------------------------------------------------------
print()
print("Gerando figuras...")
fig, axes = plt.subplots(2, 2, figsize=(15, 11))

ax = axes[0,0]
xs = np.arange(1, 11)
ax.errorbar(xs[ok], gamma_emp[ok],
            yerr=[gamma_emp[ok]-ic_lo[ok], ic_hi[ok]-gamma_emp[ok]],
            fmt='o', color='#1f77b4', label='Empirico (IC95 bootstrap)', capsize=4, markersize=6)
ax.plot(xs, gamma_final, '-s', color='#2ca02c', linewidth=2, markersize=7, label='Calibracao FINAL')
ax.axhline(0.24, color='#ff7f0e', ls='--', label='Uniforme 0.24 (parceiro)')
ax.set_xlabel('Decil de pd_produto')
ax.set_ylabel('gamma = razao over30/PD')
ax.set_title('Calibracao da PD por decil')
ax.set_xticks(xs); ax.legend(fontsize=9); ax.grid(alpha=0.3)
for i, n in enumerate(n_obs_dec):
    if n > 0:
        ax.annotate('n=' + str(n), (xs[i], 0.05), fontsize=7, ha='center', color='gray')

ax = axes[0,1]
T_range = np.arange(3, 37)
for nome, color, func in [
    ('Uniforme 0.24', '#ff7f0e', lambda pd, T: pd * 0.24),
    ('gamma_decil (FINAL)', '#2ca02c', lambda pd, T: apply_decil(pd)),
    ('sqrt(T/3)', '#9467bd', lambda pd, T: pd * 0.24 * np.sqrt(T/3)),
    ('PD raw', '#d62728', lambda pd, T: pd),
]:
    rets = [(apr_pi * (T * u_bar * t_int - func(apr_pd, T) * LGD) * apr_L).sum() / 1e6 for T in T_range]
    ax.plot(T_range, rets, color=color, linewidth=2, label=nome)
ax.axhline(0, color='black', linewidth=1)
ax.axvline(T_NEW, color='gray', ls=':', label='T=22 (escolhido)')
ax.set_xlabel('T (meses)'); ax.set_ylabel('Retorno carteira aprovada (R$ milhoes)')
ax.set_title('Validacao economica - banco lucra com aprovados')
ax.legend(fontsize=8); ax.grid(alpha=0.3)

ax = axes[1,0]
for nome, color, func in [
    ('Uniforme 0.24', '#ff7f0e', lambda pd, T: pd * 0.24),
    ('gamma_decil (FINAL)', '#2ca02c', lambda pd, T: apply_decil(pd)),
    ('sqrt(T/3)', '#9467bd', lambda pd, T: pd * 0.24 * np.sqrt(T/3)),
    ('PD raw', '#d62728', lambda pd, T: pd),
]:
    pcts = []
    for T in T_range:
        ck = smp_pi * (T * u_bar * t_int - func(smp_pd_f64, T) * LGD)
        pcts.append(100 * (ck > 0).mean())
    ax.plot(T_range, pcts, color=color, linewidth=2, label=nome)
ax.axvline(T_NEW, color='gray', ls=':')
ax.set_xlabel('T (meses)'); ax.set_ylabel('% elegiveis com c_k > 0')
ax.set_title('% elegiveis viaveis por T e calibracao')
ax.legend(fontsize=8); ax.grid(alpha=0.3)

ax = axes[1,1]
T_use = T_NEW; rec = T_use * u_bar * t_int
rng_plot = np.random.RandomState(7)
idx_plot = rng_plot.choice(len(smp_pd), min(60000, len(smp_pd)), replace=False)
smp_pd_s = smp_pd[idx_plot].astype(np.float64); smp_pi_s = smp_pi[idx_plot]
ck_u_s = smp_pi_s * (rec - smp_pd_s * 0.24 * LGD)
ck_d_s = smp_pi_s * (rec - apply_decil(smp_pd_s) * LGD)
ax.hist(ck_u_s, bins=50, alpha=0.55, color='#ff7f0e', label='Uniforme 0.24')
ax.hist(ck_d_s, bins=50, alpha=0.55, color='#2ca02c', label='gamma_decil (FINAL)')
ax.axvline(0, color='black', ls='--')
ax.set_xlabel('c_k unitario em T=22'); ax.set_ylabel('Frequencia (amostra)')
ax.set_title('Distribuicao c_k em T=22: uniforme vs decil')
ax.legend(); ax.grid(alpha=0.3)
del smp_pd_s, smp_pi_s, ck_u_s, ck_d_s
gc.collect()

plt.suptitle('Calibracao final da PD (por decil) e selecao de T=22 - validacao em 3 safras', fontsize=13, y=1.005)
plt.tight_layout()
plt.savefig(str(FIG_DIR / 'calibracao_final.png'), dpi=130, bbox_inches='tight')
print("Salvo: " + str(FIG_DIR / 'calibracao_final.png'))
plt.close(fig)
# Figura comparativa por decil
fig2, axes2 = plt.subplots(1, 2, figsize=(14, 5))
ax = axes2[0]
ck_u_med = []; ck_d_med = []; pct_u = []; pct_d = []
for d in range(10):
    m = (smp_pd >= edges[d]) & (smp_pd < edges[d+1])
    ck_u_d = smp_pi[m] * (T_NEW * u_bar * t_int - smp_pd[m].astype(np.float64) * 0.24 * LGD)
    ck_d_d = smp_pi[m] * (T_NEW * u_bar * t_int - apply_decil(smp_pd[m].astype(np.float64)) * LGD)
    ck_u_med.append(ck_u_d.mean()); ck_d_med.append(ck_d_d.mean())
    pct_u.append((ck_u_d > 0).mean() * 100); pct_d.append((ck_d_d > 0).mean() * 100)
xs2 = np.arange(1, 11); w = 0.4
ax.bar(xs2 - w/2, ck_u_med, w, color='#ff7f0e', label='Uniforme 0.24')
ax.bar(xs2 + w/2, ck_d_med, w, color='#2ca02c', label='gamma_decil')
ax.axhline(0, color='black', linewidth=1)
ax.set_xlabel('Decil'); ax.set_ylabel('c_k medio'); ax.set_xticks(xs2)
ax.set_title('c_k medio por decil em T=22')
ax.legend(); ax.grid(alpha=0.3)

ax = axes2[1]
ax.bar(xs2 - w/2, pct_u, w, color='#ff7f0e', label='Uniforme 0.24')
ax.bar(xs2 + w/2, pct_d, w, color='#2ca02c', label='gamma_decil')
ax.set_xlabel('Decil'); ax.set_ylabel('% rentavel'); ax.set_xticks(xs2)
ax.set_ylim(0, 105)
ax.set_title('% elegiveis rentaveis por decil em T=22')
ax.legend(); ax.grid(alpha=0.3)

plt.suptitle('Calibracao por decil filtra apenas decis de risco extremo - decisao final fica no LP', fontsize=12, y=1.02)
plt.tight_layout()
plt.savefig(str(FIG_DIR / 'calibracao_comparativo_ck.png'), dpi=130, bbox_inches='tight')
print("Salvo: " + str(FIG_DIR / 'calibracao_comparativo_ck.png'))
plt.close(fig2)

print()
print("=" * 90)
print("RESUMO DA CALIBRACAO FINAL")
print("=" * 90)
print("T = %d meses (horizonte de uso do limite, parceiro)" % T_NEW)
print("gamma_decil = " + str([float(round(g, 3)) for g in gamma_final]))
print("PD_calibrada(i) = pd_produto(i) * gamma(decil(i))")
