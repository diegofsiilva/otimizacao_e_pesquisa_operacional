"""
Análise exploratória 3: Correlação entre capacidade de pagamento (CP) e PD na base real.

Objetivo: verificar empiricamente se existe correlação negativa entre capacidade_pagamento
e pd_produto, validando a premissa da Seção 4.4 de que choques macroeconômicos movem
CP e PD em direções opostas (CP cai, PD sobe).

Suporta: Seção 4.4 (cenários macroeconômicos e correlação entre parâmetros).
"""

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pathlib

DATA_DIR = pathlib.Path(__file__).resolve().parent.parent / "data"
OUTPUT_DIR = pathlib.Path(__file__).resolve().parent.parent / "artefatos" / "figuras"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SAFRAS = ["M1", "M2", "M3"]

FAIXAS_SCORE = [100, 700, 800, 850, 900, 960]
FAIXAS_LABELS = ["100–700", "700–800", "800–850", "850–900", "900–960"]

# ── 1. Carregar dados ────────────────────────────────────────────────────────
frames = []
for safra in SAFRAS:
    df = pd.read_parquet(DATA_DIR / f"base_ref_{safra}_v2.parquet")
    elig = df[df["flag_filtros"] == 0].copy()
    elig["safra"] = safra
    frames.append(elig)

dados = pd.concat(frames, ignore_index=True)
# Filtrar registros com CP válida
dados_cp = dados[dados["capacidade_pagamento"].notna() & (dados["capacidade_pagamento"] > 0)].copy()
dados_cp["faixa_score"] = pd.cut(
    dados_cp["score_credito_cross"],
    bins=FAIXAS_SCORE,
    labels=FAIXAS_LABELS,
    right=True,
)

print(f"Registros com CP válida: {len(dados_cp):,} / {len(dados):,}")
print()

# ── 2. Correlação global ────────────────────────────────────────────────────
corr_global = dados_cp["capacidade_pagamento"].corr(dados_cp["pd_produto"])
corr_spearman = dados_cp["capacidade_pagamento"].corr(dados_cp["pd_produto"], method="spearman")

print("=" * 80)
print("CORRELAÇÃO ENTRE CAPACIDADE DE PAGAMENTO E PD")
print("=" * 80)
print(f"Correlação de Pearson (global):  {corr_global:.4f}")
print(f"Correlação de Spearman (global): {corr_spearman:.4f}")
print()

# ── 3. Correlação por faixa de score ─────────────────────────────────────────
print("=" * 80)
print("CORRELAÇÃO POR FAIXA DE SCORE")
print("=" * 80)
print(f"{'Faixa':<15} {'N':>10} {'Pearson':>10} {'Spearman':>10} {'CP mediana':>12} {'PD mediana':>12}")
print("-" * 69)

for faixa in FAIXAS_LABELS:
    sub = dados_cp[dados_cp["faixa_score"] == faixa]
    if len(sub) > 100:
        pearson = sub["capacidade_pagamento"].corr(sub["pd_produto"])
        spearman = sub["capacidade_pagamento"].corr(sub["pd_produto"], method="spearman")
        cp_med = sub["capacidade_pagamento"].median()
        pd_med = sub["pd_produto"].median()
        print(f"{faixa:<15} {len(sub):>10,} {pearson:>10.4f} {spearman:>10.4f} {cp_med:>12.0f} {pd_med:>12.4f}")

print()

# ── 4. Correlação por safra ──────────────────────────────────────────────────
print("=" * 80)
print("CORRELAÇÃO POR SAFRA (evidência de co-movimento temporal)")
print("=" * 80)
print(f"{'Safra':<8} {'N':>10} {'Pearson':>10} {'Spearman':>10} {'CP mediana':>12} {'PD mediana':>12}")
print("-" * 62)

for safra in SAFRAS:
    sub = dados_cp[dados_cp["safra"] == safra]
    pearson = sub["capacidade_pagamento"].corr(sub["pd_produto"])
    spearman = sub["capacidade_pagamento"].corr(sub["pd_produto"], method="spearman")
    cp_med = sub["capacidade_pagamento"].median()
    pd_med = sub["pd_produto"].median()
    print(f"{safra:<8} {len(sub):>10,} {pearson:>10.4f} {spearman:>10.4f} {cp_med:>12.0f} {pd_med:>12.4f}")

print()

# ── 5. Tabela cruzada: PD média por quartil de CP ───────────────────────────
print("=" * 80)
print("PD MÉDIA POR QUARTIL DE CAPACIDADE DE PAGAMENTO")
print("=" * 80)

dados_cp["cp_quartil"] = pd.qcut(dados_cp["capacidade_pagamento"], q=4, labels=["Q1 (menor)", "Q2", "Q3", "Q4 (maior)"])
tabela = dados_cp.groupby("cp_quartil", observed=False).agg(
    n=("pd_produto", "count"),
    pd_media=("pd_produto", "mean"),
    pd_mediana=("pd_produto", "median"),
    cp_media=("capacidade_pagamento", "mean"),
).reset_index()
print(tabela.to_string(index=False))
print()

# ── 6. Gráficos ──────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

# 6a. Scatter (amostra para performance)
sample = dados_cp.sample(n=min(50000, len(dados_cp)), random_state=42)
axes[0].scatter(sample["capacidade_pagamento"], sample["pd_produto"],
                alpha=0.05, s=1, color="#4C72B0")
axes[0].set_xlabel("Capacidade de pagamento (R$)")
axes[0].set_ylabel("pd_produto")
axes[0].set_title(f"CP vs PD (Spearman = {corr_spearman:.3f})")
axes[0].set_xlim(0, 15000)

# 6b. PD média por quartil de CP
axes[1].bar(range(4), tabela["pd_media"].values, color=["#d62728", "#DD8452", "#2ca02c", "#1f77b4"], alpha=0.8)
axes[1].set_xticks(range(4))
axes[1].set_xticklabels(["Q1\n(menor CP)", "Q2", "Q3", "Q4\n(maior CP)"])
axes[1].set_ylabel("PD média")
axes[1].set_title("PD média por quartil de capacidade de pagamento")

# 6c. Heatmap: PD média por faixa de score × quartil de CP
pivot = dados_cp.groupby(["faixa_score", "cp_quartil"], observed=False)["pd_produto"].mean().unstack()
im = axes[2].imshow(pivot.values, cmap="RdYlGn_r", aspect="auto")
axes[2].set_xticks(range(4))
axes[2].set_xticklabels(["Q1", "Q2", "Q3", "Q4"], fontsize=8)
axes[2].set_yticks(range(len(FAIXAS_LABELS)))
axes[2].set_yticklabels(FAIXAS_LABELS, fontsize=8)
axes[2].set_xlabel("Quartil de CP")
axes[2].set_ylabel("Faixa de score")
axes[2].set_title("PD média: score × CP")
for i in range(pivot.shape[0]):
    for j in range(pivot.shape[1]):
        val = pivot.values[i, j]
        if not np.isnan(val):
            axes[2].text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=7,
                        color="white" if val > 0.5 else "black")
plt.colorbar(im, ax=axes[2], shrink=0.8)

plt.tight_layout()
output_path = OUTPUT_DIR / "correlacao_cp_pd.png"
plt.savefig(output_path, dpi=150, bbox_inches="tight")
print(f"Gráfico salvo em: {output_path}")
