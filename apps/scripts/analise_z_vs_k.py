"""
apps/scripts/analise_z_vs_k.py

Varredura de K usando paralelismo nos 24 cores do servidor.
Todo output vai para logs/z_vs_k.log.
Resultados parciais sao salvos em CSV apos cada K concluido.

Uso:
    nohup python apps/scripts/analise_z_vs_k.py <arquivo_calibrado.csv> <parametros.json> &
    tail -f logs/z_vs_k.log

Entrada:
    - <arquivo_calibrado.csv> : base calibrada em data/csv/
    - <parametros.json>       : parametros do modelo em apps/algoritmo_simplex/input/

Saida:
    - logs/z_vs_k.log          : log completo da execucao
    - artefatos/z_vs_k_resultados.csv   : resultados parciais por K
    - artefatos/z_vs_k_final.csv        : tabela final ordenada
    - artefatos/figuras/z_vs_k.png : grafico
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent.parent
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

log_path = LOG_DIR / "z_vs_k.log"


class Logger:
    """Escreve simultaneamente no arquivo de log e no stdout original."""

    def __init__(self, filepath):
        """Abre o arquivo de log em modo append e guarda o stdout original.

        Args:
            filepath: Caminho do arquivo de log (aberto com ``buffering=1``,
                line-buffered, para refletir o progresso em tempo real).
        """
        self.terminal = sys.stdout
        self.log = open(filepath, "a", buffering=1)

    def write(self, msg):
        """Escreve a mensagem no stdout original e no arquivo de log.

        Args:
            msg: Texto a ser escrito em ambos os destinos.
        """
        self.terminal.write(msg)
        self.log.write(msg)

    def flush(self):
        """Faz flush dos dois destinos (stdout original e arquivo de log)."""
        self.terminal.flush()
        self.log.flush()


sys.stdout = Logger(log_path)
sys.stderr = sys.stdout

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from joblib import Parallel, delayed
from sklearn.tree import DecisionTreeRegressor

DATA_DIR = ROOT / "data" / "csv"
JSON_DIR = ROOT / "apps" / "algoritmo_simplex" / "input"
FIG_DIR = ROOT / "artefatos" / "figuras"
OUT_DIR = ROOT / "artefatos"
FIG_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(ROOT / "apps" / "algoritmo_simplex"))
from models import Problema
from simplex import simplex

if len(sys.argv) < 3:
    print(
        "Uso: python analise_z_vs_k.py <arquivo_calibrado.csv> <parametros.json>"
    )
    sys.exit(1)

csv_name = sys.argv[1]
json_name = sys.argv[2]

with open(JSON_DIR / json_name) as f:
    params = json.load(f)

T = params["T"]
t_int = params["t"]
LGD = params["LGD"]
u_bar = params["u_bar"]
L_max = params["L_max"]

print(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"CSV: {csv_name} | JSON: {json_name}")
print(f"Params: T={T}, t={t_int}, LGD={LGD}, u_bar={u_bar}, L_max={L_max}")

print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Carregando {csv_name}...")
df_full = pd.read_csv(DATA_DIR / csv_name)
df = df_full[df_full["flag_filtros"] == 0].copy()
print(f"  {len(df):,} elegiveis")

df["pi"] = ((df["score_propensao_contrato"].astype(float) - 3.0) / 843.0).clip(0, 1)
df["cp_proxy"] = df["capacidade_pagamento"].where(
    df["capacidade_pagamento"].notna(), df["renda_estimada"] * 0.30
)
df["ck_guia"] = df["pi"] * (u_bar * t_int * T - df["pd_calibrada"] * LGD)

feature_cols = ["pd_calibrada", "pi", "cp_proxy", "score_credito_cross"]
df_feat = df[feature_cols].copy()
for col in feature_cols:
    if df_feat[col].isna().any():
        mediana = df_feat[col].median()
        df_feat[col] = df_feat[col].fillna(mediana)
        print(f"  Imputacao: {col} -- mediana={mediana:.4f}")

X = df_feat.values
y = df["ck_guia"].values
pd_calibrada_arr = df["pd_calibrada"].values
pi_vals = df["pi"].values
cp_proxy_arr = df["cp_proxy"].values
score_cross = df["score_credito_cross"].values
pd_fin_atual = float(df["pd_calibrada"].mean())

print(f"  pd_fin_atual = {pd_fin_atual:.4f}")


def score_to_m(score, s_low=300.0, s_high=900.0, m_low=0.3, m_high=1.8):
    """Mapeia um score de crédito para um fator de alavancagem ``m``.

    Interpola linearmente o score no intervalo ``[s_low, s_high]`` (com clip nas
    bordas) para o intervalo de alavancagem ``[m_low, m_high]``.

    Args:
        score: Score de crédito do cluster (média).
        s_low: Score mínimo do mapeamento (vira ``m_low``).
        s_high: Score máximo do mapeamento (vira ``m_high``).
        m_low: Alavancagem mínima.
        m_high: Alavancagem máxima.

    Returns:
        O fator de alavancagem ``m`` (``float``) correspondente ao score.
    """
    x = float(np.clip((score - s_low) / (s_high - s_low), 0.0, 1.0))
    return m_low + x * (m_high - m_low)


def rodar_k(k: int) -> dict:
    """Executa o pipeline completo (clustering + LP) para um valor de K.

    Treina uma árvore de regressão com até ``k`` folhas para agrupar os
    elegíveis, agrega as features por cluster, monta o problema de otimização
    (restrição de inadimplência R1 + bounds por cluster) e resolve com o
    Simplex próprio do projeto.

    Args:
        k: Número máximo de folhas (clusters) da árvore.

    Returns:
        ``dict`` com K, número real de clusters (``n_real``), valor ótimo ``z``,
        ``status`` do solver e tempos de clustering/simplex/total em segundos.
    """
    t0 = time.time()

    arvore = DecisionTreeRegressor(
        max_leaf_nodes=k,
        min_samples_leaf=500,
        random_state=42,
    )
    arvore.fit(X, y)
    folhas_raw = arvore.apply(X)
    folhas_unicas = np.unique(folhas_raw)
    mapa = {f: i for i, f in enumerate(folhas_unicas)}
    cids = np.vectorize(mapa.get)(folhas_raw)
    n_real = len(folhas_unicas)
    t_clust = time.time() - t0

    def p5(arr):
        """Retorna o 5º percentil de ``arr`` (ignorando NaN), como ``float``."""
        return float(np.nanquantile(arr.astype(float), 0.05))

    n_k_arr = np.zeros(n_real)
    PD_arr = np.zeros(n_real)
    pi_arr = np.zeros(n_real)
    CP_arr = np.zeros(n_real)
    m_arr = np.zeros(n_real)

    for cid in range(n_real):
        mask = cids == cid
        n_k_arr[cid] = mask.sum()
        PD_arr[cid] = pd_calibrada_arr[mask].mean()
        pi_arr[cid] = pi_vals[mask].mean()
        CP_arr[cid] = p5(cp_proxy_arr[mask])
        m_arr[cid] = score_to_m(float(score_cross[mask].mean()))

    c_vec = list(n_k_arr * pi_arr * (u_bar * t_int * T - PD_arr * LGD))

    A, b = [], []
    A.append(list(n_k_arr * (PD_arr - pd_fin_atual)))
    b.append(0.0)
    for i in range(n_real):
        linha = [0.0] * n_real
        linha[i] = 1.0
        A.append(linha)
        b.append(float(m_arr[i] * CP_arr[i]))
    for i in range(n_real):
        linha = [0.0] * n_real
        linha[i] = 1.0
        A.append(linha)
        b.append(L_max)

    t1 = time.time()
    try:
        _, z, status = simplex(Problema(c=c_vec, A=A, b=b))
    except Exception as e:
        z, status = float("nan"), f"erro: {e}"
    t_simp = time.time() - t1

    return {
        "K": k,
        "n_real": n_real,
        "z": z,
        "status": status,
        "t_clust": round(t_clust, 2),
        "t_simp": round(t_simp, 2),
        "t_total": round(time.time() - t0, 2),
    }


candidatos = (
    list(range(50, 300, 25))
    + list(range(300, 600, 50))
    + list(range(600, 1000, 100))
    + list(range(1000, 1500, 100))
    + list(range(1500, 2100, 100))
)

print(
    f"\n[{datetime.now().strftime('%H:%M:%S')}] Candidatos: {len(candidatos)} valores de K"
)
print(f"  Menor K: {min(candidatos)} | Maior K: {max(candidatos)} | n_jobs: 24")

csv_parcial = OUT_DIR / "z_vs_k_resultados.csv"


def salvar_resultado(resultado: dict) -> None:
    """Anexa um resultado de K ao CSV parcial (escrita incremental).

    Escreve o cabeçalho apenas quando o arquivo ainda não existe, permitindo
    acumular resultados conforme cada K termina.

    Args:
        resultado: Dicionário retornado por :func:`rodar_k`.

    Returns:
        None. O efeito é a escrita em ``csv_parcial``.
    """
    df_linha = pd.DataFrame([resultado])
    header = not csv_parcial.exists()
    df_linha.to_csv(csv_parcial, mode="a", header=header, index=False)


def rodar_k_com_log(k: int) -> dict:
    """Executa :func:`rodar_k`, persiste o parcial e loga o progresso.

    Wrapper usado pelas tarefas paralelas: roda o K, salva o resultado
    incrementalmente e imprime uma linha de log formatada.

    Args:
        k: Número de clusters a avaliar.

    Returns:
        O mesmo ``dict`` de resultado retornado por :func:`rodar_k`.
    """
    resultado = rodar_k(k)
    salvar_resultado(resultado)
    ts = datetime.now().strftime("%H:%M:%S")
    print(
        f"[{ts}] K={k:>5} | n_real={resultado['n_real']:>5} | "
        f"z={resultado['z']:>16.2f} | status={resultado['status']:<10} | "
        f"t_clust={resultado['t_clust']:>6.1f}s | t_simp={resultado['t_simp']:>7.1f}s"
    )
    return resultado


print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Iniciando varredura paralela...\n")
t_inicio = time.time()

resultados_raw = Parallel(n_jobs=24, verbose=0)(
    delayed(rodar_k_com_log)(k) for k in candidatos
)

t_total = time.time() - t_inicio
print(
    f"\n[{datetime.now().strftime('%H:%M:%S')}] Varredura concluida em {t_total/3600:.2f}h"
)

resultados = sorted(resultados_raw, key=lambda r: r["K"])
df_res = pd.DataFrame(resultados)
df_res["delta_z%"] = df_res["z"].pct_change() * 100

print(f"\nTABELA FINAL")
print(f"{'K':>6} {'n_real':>8} {'z':>18} {'delta_z%':>10} {'t_simp':>10}")
print("-" * 58)
for _, row in df_res.iterrows():
    delta_str = (
        f"{row['delta_z%']:>9.3f}%" if not np.isnan(row["delta_z%"]) else "         --"
    )
    print(
        f"{int(row['K']):>6} {int(row['n_real']):>8} {row['z']:>18.2f} {delta_str} {row['t_simp']:>9.1f}s"
    )

threshold = 0.5
df_delta = df_res[["K", "n_real", "z", "delta_z%"]].dropna(subset=["delta_z%"])
k_otimo = None
idx_otimo = None

for i in range(len(df_delta)):
    restante = df_delta.iloc[i:]["delta_z%"]
    if (restante < threshold).all():
        idx_otimo = i
        break

print(f"\nRECOMENDACAO (threshold = {threshold}%)")
if idx_otimo is not None:
    k_otimo = int(df_delta.iloc[idx_otimo]["K"])
    z_k_otimo = float(df_res[df_res["K"] == k_otimo]["z"].values[0])
    z_max = float(df_res["z"].max())
    k_max_z = int(df_res.loc[df_res["z"].idxmax(), "K"])
    perda = 100 * (z_max - z_k_otimo) / z_max
    print(f"K otimo:              {k_otimo}")
    print(f"z em K={k_otimo}:     R$ {z_k_otimo:,.2f}")
    print(f"z maximo (K={k_max_z}): R$ {z_max:,.2f}")
    print(f"Perda vs maximo:      {perda:.4f}%")
    print(f"Justificativa:        a partir de K={k_otimo}, todos os incrementos")
    print(
        f"                      adicionam menos de {threshold}% ao retorno da carteira."
    )
else:
    print("Nenhum cotovelo claro encontrado no range testado.")
    print(
        f"z maximo: R$ {df_res['z'].max():,.2f} em K={int(df_res.loc[df_res['z'].idxmax(), 'K'])}"
    )

csv_final = OUT_DIR / "z_vs_k_final.csv"
df_res.to_csv(csv_final, index=False)
print(f"\nResultados salvos em: {csv_final}")

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

ax = axes[0]
ax.plot(
    df_res["n_real"],
    df_res["z"] / 1e6,
    "o-",
    color="#1f77b4",
    linewidth=2,
    markersize=4,
)
if k_otimo:
    z_ot = df_res[df_res["K"] == k_otimo]["z"].values[0]
    ax.axvline(
        k_otimo,
        color="red",
        linestyle="--",
        linewidth=1.5,
        label=f"K otimo = {k_otimo}",
    )
    ax.plot(k_otimo, z_ot / 1e6, "r*", markersize=14)
ax.set_xlabel("K (numero de clusters)")
ax.set_ylabel("Valor otimo z (R$ milhoes)")
ax.set_title("Retorno otimo da carteira vs K")
ax.legend()
ax.grid(alpha=0.3)

ax = axes[1]
df_plot = df_res.dropna(subset=["delta_z%"])
cores = ["#d62728" if d >= threshold else "#2ca02c" for d in df_plot["delta_z%"]]
largura = df_plot["K"].diff().median() * 0.7
ax.bar(df_plot["K"], df_plot["delta_z%"], color=cores, alpha=0.8, width=largura)
ax.axhline(
    threshold,
    color="red",
    linestyle="--",
    linewidth=1.5,
    label=f">= {threshold}% (relevante)",
)
ax.axhline(0.1, color="orange", linestyle="--", linewidth=1.5, label=">= 0.1%")
if k_otimo:
    ax.axvline(k_otimo, color="red", linestyle="--", linewidth=1.5)
ax.set_xlabel("K")
ax.set_ylabel("Ganho marginal em z (%)")
ax.set_title(f"Ganho marginal de retorno por incremento de K")
ax.legend()
ax.grid(alpha=0.3)

plt.suptitle(
    f"Analise K otimo -- {csv_name} -- {datetime.now().strftime('%Y-%m-%d')}",
    fontsize=13,
    y=1.01,
)
plt.tight_layout()
out_fig = FIG_DIR / "z_vs_k.png"
plt.savefig(out_fig, dpi=150, bbox_inches="tight")
print(f"Grafico salvo em: {out_fig}")

print(f"\n[{datetime.now().strftime('%H:%M:%S')}] FIM")
