"""
Análise exploratória: fatores de alavancagem (m_k) por faixa de score_credito_cross.

Objetivo: identificar, a partir da política vigente do banco (limite_ofertado / capacidade_pagamento),
qual alavancagem é praticada em cada faixa de score, e derivar as faixas de m_k para o modelo de otimização.

Dados: base_ref_M1_v2.parquet, base_ref_M2_v2.parquet, base_ref_M3_v2.parquet
Filtros: flag_filtros == 0 (elegíveis), limite_ofertado não nulo, capacidade_pagamento > 0.
"""

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pathlib

# ── Configuração ──────────────────────────────────────────────────────────────
DATA_DIR = pathlib.Path(__file__).resolve().parent.parent / "data"
OUTPUT_DIR = pathlib.Path(__file__).resolve().parent.parent / "artefatos" / "figuras"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FAIXAS_SCORE = [100, 600, 700, 800, 850, 900, 960]
FAIXAS_LABELS = ["100–600", "600–700", "700–800", "800–850", "850–900", "900–960"]

SAFRAS = ["M1", "M2", "M3"]

# ── 1. Carregar e filtrar ─────────────────────────────────────────────────────
frames_oferta = []
frames_elig = []
for safra in SAFRAS:
    df = pd.read_parquet(DATA_DIR / f"base_ref_{safra}_v2.parquet")
    elig = df[df["flag_filtros"] == 0].copy()
    elig["safra"] = safra
    frames_elig.append(elig)

    oferta = elig[
        (elig["limite_ofertado"].notna()) & (elig["capacidade_pagamento"] > 0)
    ].copy()
    frames_oferta.append(oferta)

# Base elegível inteira (para PD por faixa de score, sem viés de seleção)
elegiveis = pd.concat(frames_elig, ignore_index=True)
elegiveis["faixa_score"] = pd.cut(
    elegiveis["score_credito_cross"],
    bins=FAIXAS_SCORE,
    labels=FAIXAS_LABELS,
    right=True,
)

# Subconjunto com oferta (para alavancagem observada)
dados = pd.concat(frames_oferta, ignore_index=True)
dados["alavancagem"] = dados["limite_ofertado"] / dados["capacidade_pagamento"]
dados["faixa_score"] = pd.cut(
    dados["score_credito_cross"],
    bins=FAIXAS_SCORE,
    labels=FAIXAS_LABELS,
    right=True,
)

# Nota: pd_produto = 1 - score_interno / 1000 (transformação linear exata, verificada em M1)

print(f"Total de registros (3 safras): {len(dados):,}")
print(f"Score range: [{dados['score_credito_cross'].min()}, {dados['score_credito_cross'].max()}]")
print()

# ── 2. Estatísticas de alavancagem por faixa de score ─────────────────────────
# PD da base elegível inteira (sem viés de seleção da oferta)
pd_elig = (
    elegiveis.groupby("faixa_score", observed=False)
    .agg(
        n_elig=("pd_produto", "count"),
        pd_mediana_elig=("pd_produto", "median"),
    )
    .reset_index()
)

stats = (
    dados.groupby("faixa_score", observed=False)
    .agg(
        n=("alavancagem", "count"),
        alav_p10=("alavancagem", lambda x: x.quantile(0.10)),
        alav_p25=("alavancagem", lambda x: x.quantile(0.25)),
        alav_mediana=("alavancagem", "median"),
        alav_media=("alavancagem", "mean"),
        alav_p75=("alavancagem", lambda x: x.quantile(0.75)),
        alav_p90=("alavancagem", lambda x: x.quantile(0.90)),
        score_mediana=("score_credito_cross", "median"),
        limite_mediano=("limite_ofertado", "median"),
        cp_mediana=("capacidade_pagamento", "median"),
    )
    .reset_index()
    .merge(pd_elig, on="faixa_score")
)

print("=" * 100)
print("ALAVANCAGEM OBSERVADA (limite_ofertado / capacidade_pagamento) POR FAIXA DE SCORE")
print("Fonte: M1 + M2 + M3 combinados, elegíveis com oferta e CP > 0")
print("=" * 100)
pd.set_option("display.float_format", lambda x: f"{x:.3f}")
print(stats.to_string(index=False))
print()

# ── 3. Consistência entre safras ──────────────────────────────────────────────
print("=" * 80)
print("CONSISTÊNCIA ENTRE SAFRAS (mediana da alavancagem por faixa)")
print("=" * 80)
safra_stats = (
    dados.groupby(["faixa_score", "safra"], observed=False)["alavancagem"]
    .median()
    .unstack(fill_value=float("nan"))
)
print(safra_stats.to_string())
print()

# ── 4. Derivação das faixas de m_k ───────────────────────────────────────────
# Critério: usar o p75 da alavancagem observada como teto, arredondado para
# múltiplos de 0.05. O p75 reflete o comportamento da política vigente sem
# se contaminar por outliers (p90/p95 incluem casos atípicos).
print("=" * 80)
print("FAIXAS DE ALAVANCAGEM m_k PROPOSTAS")
print("Critério: p75 da alavancagem observada, arredondado para múltiplo de 0.05")
print("=" * 80)

propostas = []
for _, row in stats.iterrows():
    p75 = row["alav_p75"]
    m_proposto = round(p75 * 20) / 20  # arredondar para múltiplo de 0.05
    m_proposto = max(m_proposto, 0.15)  # piso mínimo
    propostas.append(
        {
            "faixa_score": row["faixa_score"],
            "n": int(row["n"]),
            "alav_p75_obs": round(p75, 3),
            "m_proposto": m_proposto,
            "pd_mediana_elig": round(row["pd_mediana_elig"], 3),
        }
    )

df_propostas = pd.DataFrame(propostas)
print(df_propostas.to_string(index=False))
print()

# ── 5. Validação: % de clientes que seriam bloqueados por m_k ────────────────
print("=" * 80)
print("VALIDAÇÃO: % de ofertas vigentes que excederiam m_k proposto")
print("(alavancagem observada > m_proposto => oferta atual seria cortada)")
print("=" * 80)
for _, row in df_propostas.iterrows():
    faixa = row["faixa_score"]
    m = row["m_proposto"]
    sub = dados[dados["faixa_score"] == faixa]
    if len(sub) > 0:
        excede = (sub["alavancagem"] > m).mean() * 100
        print(f"  {faixa}: m={m:.2f}, {excede:.1f}% das ofertas atuais excederiam o teto")

print()

# ── 6. Gráficos ──────────────────────────────────────────────────────────────

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 6a. Boxplot de alavancagem por faixa
bp_data = [
    dados[dados["faixa_score"] == f]["alavancagem"].clip(upper=1.5).values
    for f in FAIXAS_LABELS
]
axes[0].boxplot(bp_data, labels=FAIXAS_LABELS, showfliers=False, patch_artist=True,
                boxprops=dict(facecolor="#4C72B0", alpha=0.7),
                medianprops=dict(color="red", linewidth=1.5))
# Overlay m_k propostos
m_vals = df_propostas["m_proposto"].values
axes[0].plot(range(1, len(m_vals) + 1), m_vals, "D--", color="orange", markersize=6, label="$m_k$ proposto")
axes[0].set_xlabel("Faixa de score_credito_cross")
axes[0].set_ylabel("Alavancagem (limite / CP)")
axes[0].set_title("Distribuição da alavancagem observada por faixa de score")
axes[0].legend()
axes[0].tick_params(axis="x", rotation=30)

# 6b. m_k proposto vs PD mediana
ax2 = axes[1]
color1 = "#4C72B0"
color2 = "#DD8452"
ax2.bar(range(len(FAIXAS_LABELS)), m_vals, color=color1, alpha=0.7, label="$m_k$ proposto")
ax2.set_ylabel("$m_k$ (alavancagem máxima)", color=color1)
ax2.set_xlabel("Faixa de score_credito_cross")
ax2.set_xticks(range(len(FAIXAS_LABELS)))
ax2.set_xticklabels(FAIXAS_LABELS, rotation=30)
ax2.set_title("$m_k$ proposto e PD mediana por faixa")

ax2b = ax2.twinx()
ax2b.plot(range(len(FAIXAS_LABELS)), df_propostas["pd_mediana_elig"].values, "s-", color=color2, markersize=6, label="PD mediana")
ax2b.set_ylabel("PD mediana", color=color2)
ax2b.set_ylim(0, 1.0)

lines1, labels1 = ax2.get_legend_handles_labels()
lines2, labels2 = ax2b.get_legend_handles_labels()
ax2.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "alavancagem_por_score.png", dpi=150, bbox_inches="tight")
print(f"Gráfico salvo em: {OUTPUT_DIR / 'alavancagem_por_score.png'}")

plt.show()
