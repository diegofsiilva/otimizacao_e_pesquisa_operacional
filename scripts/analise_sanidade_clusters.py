"""
scripts/analise_sanidade_clusters.py

Verifica se o LP esta otimizando corretamente apos a clusterizacao:
  1. Clusters com limite alto tem PD_k baixo e pi_k alto?
  2. A restricao R1 (inadimplencia) esta sendo respeitada?
  3. Os limites fazem sentido economico?

Uso:
    python analise_sanidade_clusters.py <arquivo_calibrado.csv> <parametros.json>
"""

import sys
import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "csv"
JSON_DIR = ROOT / "apps" / "algoritmo_simplex" / "input"
FIG_DIR = ROOT / "artefatos" / "figuras"
FIG_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(ROOT / "apps" / "algoritmo_simplex"))
from models import Problema
from simplex import simplex

if len(sys.argv) < 3:
    print(
        "Uso: python analise_sanidade_clusters.py <arquivo_calibrado.csv> <parametros.json>"
    )
    sys.exit(1)

with open(JSON_DIR / sys.argv[2]) as f:
    params = json.load(f)

T = params["T"]
t_int = params["t"]
LGD = params["LGD"]
u_bar = params["u_bar"]
L_max = params["L_max"]

stem = Path(sys.argv[1]).stem
clusters = pd.read_csv(DATA_DIR / f"{stem}_clusters.csv")

df_base = pd.read_csv(DATA_DIR / sys.argv[1])
pd_fin_atual = df_base[df_base["flag_filtros"] == 0]["pd_calibrada"].mean()

print(f"Clusters carregados: {len(clusters)}")
print(f"pd_fin_atual: {pd_fin_atual:.4f}")

# monta e resolve LP
c_vec = [
    row["n_k"] * row["pi_k"] * (u_bar * t_int * T - row["PD_k"] * LGD)
    for _, row in clusters.iterrows()
]
A, b = [], []
A.append([row["n_k"] * (row["PD_k"] - pd_fin_atual) for _, row in clusters.iterrows()])
b.append(0.0)
for _, row in clusters.iterrows():
    linha = [0.0] * len(clusters)
    linha[int(row["cluster_id"])] = 1.0
    A.append(linha)
    b.append(row["m_k"] * row["CP_k"])
for _, row in clusters.iterrows():
    linha = [0.0] * len(clusters)
    linha[int(row["cluster_id"])] = 1.0
    A.append(linha)
    b.append(L_max)

x_opt, z_opt, status = simplex(Problema(c=c_vec, A=A, b=b))
print(f"Status: {status} | z = R$ {z_opt:,.2f}")

clusters["L_raw"] = x_opt
clusters["L_final"] = clusters["L_raw"].apply(
    lambda v: 50 * round(v / 50) if v >= 200 else 0
)
clusters["c_k"] = c_vec
clusters["recebe_oferta"] = clusters["L_final"] > 0

ofertados = clusters[clusters["recebe_oferta"]]
nao_ofertados = clusters[~clusters["recebe_oferta"]]

print(f"\nSANIDADE 1: correlacao limite x perfil do cluster")
print(f"\n  Clusters com oferta (L>0): {len(ofertados):,}")
print(f"  Clusters sem oferta (L=0): {len(nao_ofertados):,}")
print(f"\n  Perfil medio dos ofertados vs nao ofertados:")
print(f"  {'Metrica':<20} {'Ofertados':>12} {'Nao ofertados':>15}")
print(f"  {'-'*48}")
for col, label in [
    ("PD_k", "PD_k"),
    ("pi_k", "pi_k"),
    ("CP_k", "CP_k (p5)"),
    ("m_k", "m_k"),
    ("c_k", "c_k"),
]:
    v_of = ofertados[col].mean()
    v_nao = nao_ofertados[col].mean()
    print(f"  {label:<20} {v_of:>12.4f} {v_nao:>15.4f}")

print(f"\n  Correlacao de Spearman (L_final x variaveis, clusters com L>0):")
for col in ["PD_k", "pi_k", "CP_k", "c_k"]:
    corr = ofertados["L_final"].corr(ofertados[col], method="spearman")
    ok = (col == "PD_k" and corr < 0) or (col != "PD_k" and corr > 0)
    sinal = "OK" if ok else "ATENCAO"
    print(f"    L_final x {col:<10}: {corr:>7.4f}  [{sinal}]")

print(f"\nSANIDADE 2: restricao R1 (inadimplencia financeira)")
r1_valor = sum(
    clusters.loc[i, "n_k"]
    * (clusters.loc[i, "PD_k"] - pd_fin_atual)
    * clusters.loc[i, "L_raw"]
    for i in range(len(clusters))
)
print(f"\n  Soma n_k*(PD_k - PD_atual)*L_k = {r1_valor:.4f}  (deve ser <= 0)")
print(f"  R1 {'RESPEITADA' if r1_valor <= 1e-6 else 'VIOLADA'}")

pd_otimizada = sum(
    clusters.loc[i, "PD_k"] * clusters.loc[i, "n_k"] * clusters.loc[i, "L_raw"]
    for i in range(len(clusters))
) / max(
    sum(
        clusters.loc[i, "n_k"] * clusters.loc[i, "L_raw"] for i in range(len(clusters))
    ),
    1e-9,
)

print(f"\n  PD financeira atual:      {pd_fin_atual:.4f}")
print(f"  PD financeira otimizada:  {pd_otimizada:.4f}")
print(
    f"  Variacao:                 {100*(pd_otimizada - pd_fin_atual)/pd_fin_atual:+.2f}%"
)

print(f"\nSANIDADE 3: distribuicao dos limites otimizados")
print(f"\n  {'Faixa':<25} {'Clusters':>10} {'Clientes':>12} {'% clientes':>12}")
print(f"  {'-'*60}")

total_clientes = clusters["n_k"].sum()
faixas = [
    ("R$ 0 (sem oferta)", clusters[clusters["L_final"] == 0]),
    ("R$ 200-500", clusters[(clusters["L_final"] > 0) & (clusters["L_final"] <= 500)]),
    (
        "R$ 500-1000",
        clusters[(clusters["L_final"] > 500) & (clusters["L_final"] <= 1000)],
    ),
    (
        "R$ 1000-2000",
        clusters[(clusters["L_final"] > 1000) & (clusters["L_final"] <= 2000)],
    ),
    (
        "R$ 2000-5000",
        clusters[(clusters["L_final"] > 2000) & (clusters["L_final"] <= 5000)],
    ),
    ("R$ 5000+", clusters[clusters["L_final"] > 5000]),
]
for label, sub in faixas:
    n_cl = len(sub)
    n_cli = sub["n_k"].sum()
    pct = 100 * n_cli / total_clientes
    print(f"  {label:<25} {n_cl:>10,} {n_cli:>12,} {pct:>11.1f}%")

print(f"\n  Limite medio (ofertados):   R$ {ofertados['L_final'].mean():,.0f}")
print(f"  Limite mediano (ofertados): R$ {ofertados['L_final'].median():,.0f}")
print(f"  Limite maximo:              R$ {clusters['L_final'].max():,.0f}")

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

ax = axes[0, 0]
ax.scatter(
    clusters["PD_k"],
    clusters["L_final"],
    alpha=0.3,
    s=10,
    c=clusters["pi_k"],
    cmap="RdYlGn",
)
ax.set_xlabel("PD_k (risco medio do cluster)")
ax.set_ylabel("Limite otimizado (R$)")
ax.set_title("Limite vs PD_k\n(esperado: correlacao negativa)")
ax.grid(alpha=0.3)

ax = axes[0, 1]
ax.scatter(
    clusters["pi_k"],
    clusters["L_final"],
    alpha=0.3,
    s=10,
    c=clusters["PD_k"],
    cmap="RdYlGn_r",
)
ax.set_xlabel("pi_k (propensao media do cluster)")
ax.set_ylabel("Limite otimizado (R$)")
ax.set_title("Limite vs pi_k\n(esperado: correlacao positiva)")
ax.grid(alpha=0.3)

ax = axes[1, 0]
ax.scatter(clusters["c_k"], clusters["L_final"], alpha=0.3, s=10, color="#1f77b4")
ax.set_xlabel("c_k (coeficiente na funcao objetivo)")
ax.set_ylabel("Limite otimizado (R$)")
ax.set_title("Limite vs c_k\n(esperado: correlacao positiva)")
ax.grid(alpha=0.3)

ax = axes[1, 1]
limites_pos = clusters[clusters["L_final"] > 0]["L_final"]
ax.hist(limites_pos, bins=40, color="#2ca02c", alpha=0.7, edgecolor="none")
ax.axvline(
    limites_pos.mean(),
    color="red",
    linestyle="--",
    label=f"media R${limites_pos.mean():,.0f}",
)
ax.axvline(
    limites_pos.median(),
    color="blue",
    linestyle="--",
    label=f"mediana R${limites_pos.median():,.0f}",
)
ax.set_xlabel("Limite otimizado (R$)")
ax.set_ylabel("Numero de clusters")
ax.set_title("Distribuicao dos limites\n(clusters com L > 0)")
ax.legend()
ax.grid(alpha=0.3)

plt.suptitle(f"Analise de sanidade -- {sys.argv[1]} -- K=800", fontsize=13, y=1.01)
plt.tight_layout()
out = FIG_DIR / "sanidade_clusters.png"
plt.savefig(out, dpi=150, bbox_inches="tight")
print(f"\nGrafico salvo em: {out}")
