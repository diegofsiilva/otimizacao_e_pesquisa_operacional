"""
scripts/setup_tabela_gamma.py

Calibracao da PD por decil usando a base completa de elegiveis.

Os decis sao definidos pelos percentis de pd_produto da populacao elegivel
completa. O gamma empirico por decil e estimado usando os clientes com
over30mob3 preenchido que caem em cada decil.

Setup inicial: estima os fatores gamma de calibracao da PD por decil
a partir das 3 safras historicas combinadas.

Deve ser rodado uma unica vez (ou quando os dados historicos mudarem).
O output tabela_gamma_decil.csv e versionado no repositorio e consumido
pelo pipeline de calibracao em cada execucao.

Uso:
    python setup_tabela_gamma.py

Saidas:
    - data/csv/tabela_gamma_decil.csv
    - artefatos/figuras/calibracao_final.png
"""

import csv
import gc
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "parquet"
FIG_DIR = ROOT / "artefatos" / "figuras"
FIG_DIR.mkdir(parents=True, exist_ok=True)

u_bar = 0.75
t_int = 0.0175
LGD = 0.80
T_NEW = 22
PI_MIN, PI_MAX = 3, 846

COLS = [
    "flag_filtros",
    "pd_produto",
    "over30mob3",
    "flag_contrato",
    "limite_ofertado",
    "score_propensao_contrato",
]

# carrega todos os arrays necessarios sem amostragem para calculo dos gammas
# amostra pequena mantida apenas para plots
print("Carregando base completa das 3 safras (sem amostragem)...")
elig_pd_list = []  # pd_produto de TODOS os elegiveis (para definir edges dos decis)
obs_pd_list, obs_ov_list = [], []  # elegiveis com over30mob3 (para estimar gamma)
apr_pd_list, apr_pi_list, apr_L_list = [], [], []
smp_pd_list, smp_pi_list = [], []
rng = np.random.RandomState(42)

for safra in ["M1", "M2", "M3"]:
    pf = pq.ParquetFile(DATA_DIR / f"base_ref_{safra}_v2.parquet")
    for batch in pf.iter_batches(batch_size=100_000, columns=COLS):
        ff = batch.column("flag_filtros").to_numpy(zero_copy_only=False)
        elig = ff == 0
        if not elig.any():
            continue

        pd_v = (
            batch.column("pd_produto").to_numpy(zero_copy_only=False).astype(np.float32)
        )
        prop = (
            batch.column("score_propensao_contrato")
            .to_numpy(zero_copy_only=False)
            .astype(np.float32)
        )
        contrato = batch.column("flag_contrato").to_numpy(zero_copy_only=False)
        ov_col = batch.column("over30mob3")
        ov_arr = ov_col.to_numpy(zero_copy_only=False).astype(np.float32)
        ov_null = ov_col.is_null().to_numpy(zero_copy_only=False)
        L_col = batch.column("limite_ofertado")
        L_arr = L_col.to_numpy(zero_copy_only=False).astype(np.float32)
        L_null = L_col.is_null().to_numpy(zero_copy_only=False)

        # pd_produto de todos os elegiveis - define os edges dos decis
        elig_pd_list.append(pd_v[elig])

        # elegiveis com over30mob3 preenchido - estimam gamma empirico
        obs = elig & ~ov_null
        if obs.any():
            obs_pd_list.append(pd_v[obs])
            obs_ov_list.append(ov_arr[obs].astype(np.int8))

        # aprovados com limite - backtesting economico
        ap = elig & (contrato == 1) & ~L_null
        if ap.any():
            apr_pd_list.append(pd_v[ap])
            apr_pi_list.append(prop[ap])
            apr_L_list.append(L_arr[ap])

        # amostra para plots apenas
        idx_e = np.where(elig)[0]
        if len(idx_e) > 0:
            n_take = min(len(idx_e), 5_000)
            pick = rng.choice(idx_e, n_take, replace=False)
            smp_pd_list.append(pd_v[pick])
            smp_pi_list.append(prop[pick])

        del pd_v, prop, contrato, ov_arr, ov_null, L_arr, L_null, elig
        gc.collect()
    print(f"  {safra} OK")

elig_pd = np.concatenate(elig_pd_list)
obs_pd = np.concatenate(obs_pd_list)
obs_ov = np.concatenate(obs_ov_list)
apr_pd = np.concatenate(apr_pd_list)
apr_pi = np.clip((np.concatenate(apr_pi_list) - PI_MIN) / (PI_MAX - PI_MIN), 0, 1)
apr_L = np.concatenate(apr_L_list)
smp_pd = np.concatenate(smp_pd_list)
smp_pi = np.clip((np.concatenate(smp_pi_list) - PI_MIN) / (PI_MAX - PI_MIN), 0, 1)
del (
    elig_pd_list,
    obs_pd_list,
    obs_ov_list,
    apr_pd_list,
    apr_pi_list,
    apr_L_list,
    smp_pd_list,
    smp_pi_list,
)
gc.collect()

if len(smp_pd) > 200_000:
    idx_sub = np.random.RandomState(11).choice(len(smp_pd), 200_000, replace=False)
    smp_pd = smp_pd[idx_sub]
    smp_pi = smp_pi[idx_sub]
    gc.collect()

smp_pd_f64 = smp_pd.astype(np.float64)

print(f"\nElegiveis totais: {len(elig_pd):,}")
print(
    f"Observacoes over30: N={len(obs_pd):,}, defaults={int((obs_ov==1).sum()):,}, taxa={(obs_ov==1).mean()*100:.2f}%"
)
print(
    f"Aprovados: N={len(apr_pd):,}, PD media={apr_pd.mean()*100:.2f}%, L medio=R${apr_L.mean():.0f}"
)

# edges dos decis calculados sobre a populacao elegivel completa
# gamma estimado usando obs_pd mapeado para esses mesmos decis
deciles = np.percentile(elig_pd, np.arange(10, 100, 10))
edges = np.concatenate([[0.0], deciles, [1.01]])

print(f"\nEdges dos decis (percentis da populacao elegivel completa):")
for d in range(10):
    print(f"  D{d+1:>2}: [{edges[d]:.4f}, {edges[d+1]:.4f})")

gamma_emp = np.full(10, np.nan)
n_obs_dec = np.zeros(10, dtype=int)
pd_mean_dec = np.zeros(10)
ic_lo = np.full(10, np.nan)
ic_hi = np.full(10, np.nan)
rng2 = np.random.RandomState(123)

# mapeia obs_pd para os decis definidos pela populacao elegivel completa
obs_indices = np.digitize(obs_pd, edges[1:])
obs_indices = np.clip(obs_indices, 0, 9)

for d in range(10):
    mask = obs_indices == d
    pd_d = obs_pd[mask]
    ov_d = obs_ov[mask]
    n = len(pd_d)
    n_obs_dec[d] = n
    pd_mean_dec[d] = pd_d.mean() if n > 0 else float(edges[d] + edges[d + 1]) / 2

    if n >= 30:
        gamma_emp[d] = (ov_d == 1).sum() / pd_d.mean() / n
        bs = []
        for _ in range(500):
            idx_b = rng2.randint(0, n, n)
            bs.append((ov_d[idx_b] == 1).sum() / max(pd_d[idx_b].mean(), 1e-9) / n)
        bs = np.array(bs)
        ic_lo[d], ic_hi[d] = np.percentile(bs, [2.5, 97.5])

ok = ~np.isnan(gamma_emp)

if ok.all():
    gamma_final = np.clip(gamma_emp, 0.15, 0.50)
    print("\nTodos os decis com estimativa empirica.")
else:
    b_fit, a_fit = np.polyfit(pd_mean_dec[ok], gamma_emp[ok], 1)
    gamma_final = np.where(
        ok, gamma_emp, np.clip(a_fit + b_fit * pd_mean_dec, 0.15, 0.50)
    )
    n_extrap = (~ok).sum()
    print(
        f"\n{n_extrap} decis sem observacoes suficientes - extrapolacao linear aplicada."
    )
    print(f"Ajuste linear: gamma = {a_fit:.4f} + {b_fit:.4f} * PD_media_decil")

gamma_final = np.clip(gamma_final, 0.15, 0.50)

print()
print(
    "Decil  PD_min   PD_max  PD_mean   N_obs   gamma_emp     IC95               gamma_FINAL  fonte"
)
for d in range(10):
    ic_str = f"[{ic_lo[d]:.3f}, {ic_hi[d]:.3f}]" if not np.isnan(ic_lo[d]) else "--"
    emp_str = f"{gamma_emp[d]:.4f}" if not np.isnan(gamma_emp[d]) else "  --  "
    fonte = "empirico" if ok[d] else "extrapolacao"
    print(
        f"D{d+1:<5} {edges[d]:6.4f}  {edges[d+1]:6.4f}  {pd_mean_dec[d]:6.4f}  {n_obs_dec[d]:6d}"
        f"   {emp_str}   {ic_str:<18} {gamma_final[d]:.4f}  [{fonte}]"
    )

# verifica distribuicao dos elegiveis pelos decis (deve ser ~10% cada)
elig_indices = np.digitize(elig_pd, edges[1:])
elig_indices = np.clip(elig_indices, 0, 9)
print(f"\nDistribuicao dos elegiveis pelos decis (deve ser ~10% cada):")
for d in range(10):
    n = (elig_indices == d).sum()
    pct = 100 * n / len(elig_pd)
    barra = "#" * int(pct / 0.5)
    print(f"  D{d+1:>2}: {n:>10,} ({pct:>5.1f}%)  {barra}")

# salva tabela
tabela_path = ROOT / "data" / "csv" / "tabela_gamma_decil.csv"
with open(tabela_path, "w", newline="") as fp:
    w = csv.writer(fp)
    w.writerow(
        [
            "decil",
            "pd_min",
            "pd_max",
            "pd_mean_decil",
            "n_obs",
            "gamma_empirico",
            "ic95_low",
            "ic95_high",
            "gamma_final",
            "fonte",
        ]
    )
    for d in range(10):
        fonte = "empirico" if ok[d] else "extrapolacao_linear"
        w.writerow(
            [
                d + 1,
                edges[d],
                edges[d + 1],
                pd_mean_dec[d],
                n_obs_dec[d],
                gamma_emp[d] if not np.isnan(gamma_emp[d]) else "",
                ic_lo[d] if not np.isnan(ic_lo[d]) else "",
                ic_hi[d] if not np.isnan(ic_hi[d]) else "",
                gamma_final[d],
                fonte,
            ]
        )
print(f"\nSalvo: {tabela_path}")


# backtesting economico
def apply_decil(pd_arr, gamma_arr=gamma_final, ed=edges):
    bins = np.digitize(pd_arr, ed[1:-1])
    return pd_arr * gamma_arr[bins]


T_VALUES = [12, 15, 18, 22, 24, 30]
modelos = [
    ("A) PD x 0.24 (uniforme)", lambda pd, T: pd * 0.24),
    ("B) PD x gamma_decil (FINAL)", lambda pd, T: apply_decil(pd)),
    ("C) PD raw (sem calibrar)", lambda pd, T: pd),
]

print()
print("=" * 80)
print("RETORNO CARTEIRA APROVADA por T (R$ x10^3)")
print("=" * 80)
header = "Modelo                               " + "".join(
    [f"    T={T:<3}" for T in T_VALUES]
)
print(header)
for nome, func in modelos:
    line = f"{nome:<37}"
    for T in T_VALUES:
        rec = T * u_bar * t_int
        ret = (apr_pi * (rec - func(apr_pd, T) * LGD) * apr_L).sum() / 1e3
        line += f"  {ret:>6.0f}k"
    print(line)

print()
print("=" * 80)
print("% ELEGIVEIS RENTAVEIS por T")
print("=" * 80)
print(header)
for nome, func in modelos:
    line = f"{nome:<37}"
    for T in T_VALUES:
        rec = T * u_bar * t_int
        ck = smp_pi * (rec - func(smp_pd_f64, T) * LGD)
        pct = 100 * (ck > 0).mean()
        line += f"   {pct:>6.2f}%"
    print(line)

# graficos
print("\nGerando figuras...")
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

ax = axes[0]
xs = np.arange(1, 11)
ax.errorbar(
    xs[ok],
    gamma_emp[ok],
    yerr=[gamma_emp[ok] - ic_lo[ok], ic_hi[ok] - gamma_emp[ok]],
    fmt="o",
    color="#1f77b4",
    label="Empirico (IC95 bootstrap)",
    capsize=4,
    markersize=6,
)
ax.plot(
    xs,
    gamma_final,
    "-s",
    color="#2ca02c",
    linewidth=2,
    markersize=7,
    label="Calibracao FINAL",
)
ax.axhline(0.24, color="#ff7f0e", ls="--", label="Uniforme 0.24 (parceiro)")
ax.set_xlabel("Decil de pd_produto (populacao elegivel)")
ax.set_ylabel("gamma = razao over30/PD")
ax.set_title("Calibracao da PD por decil (base completa)")
ax.set_xticks(xs)
ax.legend(fontsize=9)
ax.grid(alpha=0.3)
for i, n in enumerate(n_obs_dec):
    ax.annotate(
        f"n={n}", (xs[i], gamma_final[i] + 0.01), fontsize=7, ha="center", color="gray"
    )

T_range = np.arange(3, 37)
ax = axes[1]
for nome, color, func in [
    ("Uniforme 0.24", "#ff7f0e", lambda pd, T: pd * 0.24),
    ("gamma_decil (FINAL)", "#2ca02c", lambda pd, T: apply_decil(pd)),
    ("PD raw", "#d62728", lambda pd, T: pd),
]:
    rets = [
        (apr_pi * (T * u_bar * t_int - func(apr_pd, T) * LGD) * apr_L).sum() / 1e6
        for T in T_range
    ]
    ax.plot(T_range, rets, color=color, linewidth=2, label=nome)
ax.axhline(0, color="black", linewidth=1)
ax.axvline(T_NEW, color="gray", ls=":", label=f"T={T_NEW} (escolhido)")
ax.set_xlabel("T (meses)")
ax.set_ylabel("Retorno carteira aprovada (R$ milhoes)")
ax.set_title("Validacao economica")
ax.legend(fontsize=8)
ax.grid(alpha=0.3)

plt.suptitle("Calibracao da PD por decil -- base completa", fontsize=13, y=1.01)
plt.tight_layout()
out = FIG_DIR / "calibracao_final.png"
plt.savefig(out, dpi=130, bbox_inches="tight")
print(f"Salvo: {out}")
plt.close(fig)

print()
print("=" * 60)
print("RESUMO DA CALIBRACAO FINAL")
print("=" * 60)
print(f"T = {T_NEW} meses")
print(f"gamma_decil = {[float(round(g, 4)) for g in gamma_final]}")
print("PD_calibrada(i) = pd_produto(i) * gamma(decil(i))")
print(
    f"Decis definidos pelos percentis de pd_produto da populacao elegivel ({len(elig_pd):,} clientes)"
)
print(f"Gamma estimado com {len(obs_pd):,} observacoes de over30mob3")
