"""
algoritmo_simplex/main.py
Entrada de dados e execução do modelo de otimização de limites de crédito.

Uso:
    python main.py <arquivo.parquet> <parametros.json>

    Exemplo:
        python main.py base_ref_M1_v2.parquet parametros_producao.json
        python main.py base_ref_M1_v2.parquet parametros_teste.json

Arquivos parquet devem estar em data/parquet/
Arquivos JSON devem estar em apps/algoritmo_simplex/input/
"""

import sys
import json
import traceback
from pathlib import Path
import numpy as np
import pandas as pd

import time

from models import Problema
from simplex import simplex
from simplex_pulp import simplex_pulp

# calibrar_pd está em scripts/ - adicionado ao path uma única vez no nível do módulo
_SCRIPTS_DIR = str(Path(__file__).resolve().parent.parent.parent / "scripts")
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)
from calibrar_pd import calibrar as _calibrar_pd


def calcular_pd_fin_atual(df: pd.DataFrame) -> float:
    """
    Inadimplência financeira ATUAL da carteira — é o teto de referência de R1
    (doc 1.7: PD média da carteira vigente).

    O ideal documentado é a PD ponderada por limite da carteira vigente, mas
    `limite_ofertado` é ~97-99% nulo na base (ver migration 004), então não há
    como ponderar por limite. A melhor aproximação computável é a média simples
    de `pd_calibrada` da CARTEIRA VIGENTE — os clientes que hoje têm o produto
    (`flag_contrato == 1`). Isso corrige a versão anterior, que usava a média dos
    ELEGÍVEIS a uma nova oferta (`flag_filtros == 0`) — população diferente e, por
    incluir candidatos de alto risco, sistematicamente mais alta.

    Fallback seguro: se `flag_contrato` faltar ou não houver carteira vigente com
    PD válida, cai para a média dos elegíveis (comportamento anterior) com aviso.
    """
    if "flag_contrato" in df.columns:
        carteira = df.query("flag_contrato == 1")["pd_calibrada"].dropna()
        if len(carteira) > 0:
            pd_fin_atual = float(carteira.mean())
            ref_eleg = float(df.query("flag_filtros == 0")["pd_calibrada"].mean())
            print(
                f"PD_fin_atual (carteira vigente, flag_contrato==1): {pd_fin_atual:.4f} "
                f"| antes (elegíveis): {ref_eleg:.4f}"
            )
            return pd_fin_atual
        print("[PD_fin_atual] carteira vigente vazia; usando elegíveis (fallback).")
    else:
        print("[PD_fin_atual] coluna flag_contrato ausente; usando elegíveis (fallback).")

    pd_fin_atual = float(df.query("flag_filtros == 0")["pd_calibrada"].mean())
    print(f"PD_fin_atual (elegíveis, fallback): {pd_fin_atual:.4f}")
    return pd_fin_atual


def garantir_calibrado(parquet_path: Path) -> Path:
    """
    Verifica se o parquet calibrado existe em data/cache/.
    Se não existir, roda a calibração.
    Retorna o path do parquet calibrado.
    """
    cache_dir = Path(__file__).resolve().parent.parent.parent / "data" / "cache"
    stem = parquet_path.stem
    arquivo_calibrado = cache_dir / f"{stem}_calibrado.parquet"

    if not arquivo_calibrado.exists():
        print(f"Calibrando {parquet_path.name}...")
        _calibrar_pd(parquet_path)
        print("Calibração concluída.")
    else:
        print(f"{arquivo_calibrado.name} encontrado. Pulando calibração.")

    return arquivo_calibrado


def garantir_clusters(
    parquet_calibrado_nome: str, params_json_nome: str
) -> pd.DataFrame:
    """
    Verifica se o arquivo clusterizado já existe em data/cache/. Se não existir, roda o clustering.
    Passa o parametros.json para o clustering para garantir que T seja consistente.

    Retorna:
        clusters : DataFrame com os parâmetros agregados por cluster
    """
    stem = Path(parquet_calibrado_nome).stem
    arquivo_clusters = (
        Path(__file__).resolve().parent.parent.parent
        / "data"
        / "cache"
        / f"{stem}_clusters.parquet"
    )

    if not arquivo_clusters.exists():
        print(f"Gerando clusters para {arquivo_clusters.name}...")
        from clustering import main as clustering_main

        clustering_main(parquet_calibrado_nome, params_json_nome)
        print("Clustering concluído.")
    else:
        print(f"Arquivo {arquivo_clusters.name} encontrado. Pulando clustering.")

    clusters = pd.read_parquet(arquivo_clusters)
    print(f"Clusters carregados: {len(clusters)} clusters")
    return clusters


def montar_problema(clusters: pd.DataFrame, params: dict, df: pd.DataFrame) -> Problema:
    """
    Monta o problema de programação linear a partir dos parâmetros dos clusters.

    Restrições (conforme modelagem_matematica.md, seção 1.7):
        R1: teto de inadimplência financeira — 1 linha (carteira inteira).
        R2: capacidade de pagamento (L_k <= m_k·CP_k) — bound por variável.
        R3: teto máximo (L_k <= L_max) — bound por variável.
        R5: concentração máxima por cluster (n_k·L_k <= α·Σ n_j·L_j) — K linhas.
        R6: meta de produção mínima (Σ n_k·L_k >= V_min) — 1 linha; inativa
            quando V_min = 0 (cenário de referência).
        R4: teto de inadimplência física — pós-otimização (depende de um teto
            PD_fis ainda não parametrizado; não aplicada aqui).
    """
    pd_fin_atual = calcular_pd_fin_atual(df)
    t = params["t"]
    LGD = params["LGD"]
    u_bar = params["u_bar"]
    L_max = params["L_max"]
    T = params["T"]

    n_k = clusters["n_k"].to_numpy()
    pi_k = clusters["pi_k"].to_numpy()
    PD_k = clusters["PD_k"].to_numpy()
    m_k = clusters["m_k"].to_numpy()
    CP_k = clusters["CP_k"].to_numpy()
    n = len(clusters)

    # vetor de coeficientes da função objetivo
    c = (n_k * pi_k * (u_bar * t * T - PD_k * LGD)).tolist()

    # R1: teto de inadimplência financeira — ÚNICA restrição de acoplamento,
    # vale para a carteira inteira (uma linha de A).
    r1 = (n_k * (PD_k - pd_fin_atual)).tolist()

    # R2 (capacidade de pagamento, L_k <= m_k·CP_k) e R3 (teto, L_k <= L_max)
    # são limites por variável, NÃO restrições de acoplamento. Em vez de
    # virarem 2K linhas com matrizes identidade (que faziam m saltar de 1 para
    # 1+2K e inflavam o tableau), entram como o upper bound de cada L_k:
    #     0 <= L_k <= min(m_k·CP_k, L_max)
    # O simplex de variáveis limitadas trata isso nativamente.
    upper = np.minimum(m_k * CP_k, float(L_max)).tolist()
    lower = [0.0] * n

    # Linhas de acoplamento do LP: R1 e, conforme o doc, R5 e R6.
    A_rows = [r1]
    b_rows = [0.0]

    # R5 — concentração máxima por cluster: n_k·L_k <= α·Σ_j n_j·L_j.
    # Linearizado (doc 1.7): Σ_j n_j·(1[j=k] − α)·L_j <= 0, ∀k.
    # Coef. de L_j na linha k: n_j·(1−α) se j==k; −α·n_j se j≠k.
    # α vem dos parâmetros (sugerido 0,05); α<=0 desliga R5.
    alpha = float(params.get("alpha", 0.05))
    if alpha > 0.0:
        A_r5 = -alpha * np.tile(n_k.astype(float), (n, 1))
        A_r5[np.diag_indices(n)] += n_k
        A_rows.extend(A_r5.tolist())
        b_rows.extend([0.0] * n)

    # R6 — meta de produção mínima: Σ_k n_k·L_k >= V_min, escrito como
    # −Σ n_k·L_k <= −V_min. No cenário de referência V_min = 0 (R6 inativa);
    # só entra quando V_min > 0. (V_min > 0 exige Fase I no simplex — ver nota lá.)
    V_min = float(params.get("V_min", 0.0))
    if V_min > 0.0:
        A_rows.append((-n_k.astype(float)).tolist())
        b_rows.append(-V_min)

    return Problema(
        c=c,
        A=A_rows,
        b=b_rows,
        lower=lower,
        upper=upper,
    )


def exibir_resultado(
    x: list[float], z: float, status: str, clusters: pd.DataFrame
) -> None:
    """
    Exibe os limites ótimos por cluster após pós-otimização:
    arredonda para múltiplo de 50, ou 0 se menor que 200.
    """
    print(f"\nStatus: {status}")
    print(f"Valor ótimo (z): {z:.2f}")
    print(f"\nLimites ótimos por cluster:")

    limites = np.where(
        np.array(x) >= 200,
        (np.array(x) / 50).round().astype(int) * 50,
        0,
    )

    for segmento_id, n_clientes, limite in zip(
        clusters["segmento_id"].astype(int),
        clusters["n_k"].astype(int),
        limites,
    ):
        print("  Cluster {}: R$ {} (n={})".format(segmento_id, limite, n_clientes))


def executar_pipeline(parquet_path: Path, params: dict) -> dict:
    """
    Executa o pipeline completo de otimização a partir de um parquet e um
    dicionário de parâmetros. Retorna um dicionário estruturado com o resultado.

    NÃO grava arquivos de saída além do que o clustering já produz em cache
    (_calibrado, _com_cluster, _clusters). A persistência dos limites é
    responsabilidade do chamador:
      - a CLI (main) grava os parquets _clusters_resultado e _resultado_final
        via escrever_resultados_finais();
      - o backend persiste tudo no Postgres a partir de parquet_com_cluster.
    Manter executar_pipeline como cálculo puro evita I/O desnecessário no
    caminho do backend (que não usaria os arquivos de resultado).

    Usado pelo backend para chamar o otimizador sem depender de sys.argv
    nem de arquivo JSON em disco.

    Retorna:
        status              : status do Simplex ("otimo" ou "multiplas_solucoes")
        z                   : valor ótimo da função objetivo
        clusters            : lista de dicts com os parâmetros de cada cluster,
                              o limite otimizado (simplex) e o limite_pulp (PuLP)
        parquet_com_cluster : path do parquet _com_cluster gerado pelo clustering,
                              usado pelo backend para persistir a atribuição de
                              cada cliente ao seu cluster
        z_pulp              : valor ótimo retornado pelo PuLP (referência)
        status_pulp         : status retornado pelo PuLP
        delta_z_pct         : diferença relativa entre z e z_pulp em % (0.0 se z_pulp == 0)
    """
    json_dir = Path(__file__).resolve().parent / "input"
    json_temp = json_dir / "_params_temp.json"

    try:
        # escreve os parâmetros num JSON temporário para o clustering
        json_temp.write_text(json.dumps(params), encoding="utf-8")

        _t = time.perf_counter()
        parquet_calibrado = garantir_calibrado(parquet_path)
        print(f"[TIMING] calibração: {time.perf_counter() - _t:.1f}s")
        # O df só é usado por calcular_pd_fin_atual (3 colunas). Ler a base
        # calibrada inteira (~14M linhas x ~20 colunas) só pra isso era o maior
        # custo do estágio; aqui lemos apenas as colunas necessárias. Usamos
        # só pandas (sem depender de pyarrow no import) e com fallback caso a
        # coluna opcional flag_contrato não exista no parquet.
        _cols_pd_fin = ["flag_contrato", "pd_calibrada", "flag_filtros"]
        _t = time.perf_counter()
        try:
            df = pd.read_parquet(parquet_calibrado, columns=_cols_pd_fin)
        except (ValueError, KeyError):
            df = pd.read_parquet(
                parquet_calibrado, columns=["pd_calibrada", "flag_filtros"]
            )
        print(f"[TIMING] read df p/ pd_fin ({len(df.columns)} cols): {time.perf_counter() - _t:.1f}s")
        _t = time.perf_counter()
        clusters = garantir_clusters(parquet_calibrado.name, json_temp.name)
        print(f"[TIMING] segmentação (CART): {time.perf_counter() - _t:.1f}s")
    finally:
        if json_temp.exists():
            json_temp.unlink()

    problema = montar_problema(clusters, params, df)
    # O simplex reescrito não muta a entrada (faz cópias NumPy internas; ver
    # test_nao_muta_b), então o deepcopy da matriz R5 (800x800) era desperdício.
    _t = time.perf_counter()
    x, z, status = simplex(problema)
    print(f"[TIMING] simplex: {time.perf_counter() - _t:.1f}s")

    x_arr = np.array(x)
    limites = np.where(x_arr >= 200, (x_arr / 50).round().astype(int) * 50, 0)

    # Comparação com PuLP é OPCIONAL (toggle "comparar_pulp" no config). Por
    # padrão fica DESLIGADA: rodar um segundo solver (CBC/HiGHS via PuLP) dobra
    # o tempo do pipeline e serve apenas como validação cruzada do nosso simplex.
    # Quando ligada, resolve o MESMO problema (com os mesmos bounds) via PuLP.
    comparar_pulp = bool(params.get("comparar_pulp", False))

    if comparar_pulp:
        try:
            x_pulp, z_pulp, status_pulp = simplex_pulp(problema)
        except Exception:
            print("[PuLP] ERRO ao resolver — usando fallback z_pulp=0:")
            traceback.print_exc()
            x_pulp = [0.0] * len(x)
            z_pulp = 0.0
            status_pulp = "erro"
        delta_z_pct = abs(z - z_pulp) / abs(z_pulp) * 100 if z_pulp != 0.0 else 0.0
        x_pulp_arr = np.array(x_pulp)
        limites_pulp = np.where(
            x_pulp_arr >= 200, (x_pulp_arr / 50).round().astype(int) * 50, 0
        )
    else:
        z_pulp = None
        status_pulp = "desativado"
        delta_z_pct = None
        limites_pulp = None

    resultado_clusters = [
        {
            "segmento_id": int(clusters["segmento_id"].iloc[i]),
            "n_clientes": int(clusters["n_k"].iloc[i]),
            "pd_media": float(clusters["PD_k"].iloc[i]),
            "pi_media": float(clusters["pi_k"].iloc[i]),
            "cp_percentil5": float(clusters["CP_k"].iloc[i]),
            "score_credito_cross_medio": float(clusters["score_cross_mean"].iloc[i]),
            "ck_medio": float(clusters["ck_medio"].iloc[i]),
            "fator_alavancagem": float(clusters["m_k"].iloc[i]),
            "limite_otimizado": int(limites[i]),
            "limite_otimizado_pulp": (
                int(limites_pulp[i]) if limites_pulp is not None else None
            ),
        }
        for i in range(len(clusters))
    ]

    cache_dir = Path(__file__).resolve().parent.parent.parent / "data" / "cache"
    stem = parquet_calibrado.stem
    parquet_com_cluster = cache_dir / f"{stem}_com_cluster.parquet"
    parquet_clusters = cache_dir / f"{stem}_clusters.parquet"

    # grava os dois limites (nosso Simplex e PuLP) DENTRO dos arquivos que o
    # clustering já produziu (_com_cluster e _clusters), sem criar arquivos
    # novos. Feito aqui dentro para que QUALQUER chamador (CLI ou backend/front)
    # deixe os limites em disco de forma idêntica.
    _t = time.perf_counter()
    gravar_limites_nos_arquivos(
        parquet_com_cluster, parquet_clusters, resultado_clusters
    )
    print(f"[TIMING] gravar limites (agregado): {time.perf_counter() - _t:.1f}s")

    return {
        "status": status,
        "z": z,
        "clusters": resultado_clusters,
        "parquet_com_cluster": parquet_com_cluster,
        "parquet_clusters": parquet_clusters,
        "z_pulp": z_pulp,
        "status_pulp": status_pulp,
        "delta_z_pct": delta_z_pct,
    }


def gravar_limites_nos_arquivos(
    parquet_com_cluster: Path,
    parquet_clusters: Path,
    resultado_clusters: list[dict],
) -> None:
    """
    Grava limite_otimizado e limite_otimizado_pulp apenas no arquivo agregado
    por segmento ({stem}_clusters.parquet). O arquivo por cliente (_com_cluster)
    NÃO é reescrito: o limite é por segmento e qualquer consumidor o obtém
    mapeando segmento_id -> limite (ver credit_service), então regravar ~1,8M
    linhas aqui seria redundante. Idempotente.
    """
    map_nosso = {c["segmento_id"]: c["limite_otimizado"] for c in resultado_clusters}
    map_pulp = {c["segmento_id"]: c["limite_otimizado_pulp"] for c in resultado_clusters}

    df_clusters = pd.read_parquet(parquet_clusters)
    df_clusters["limite_otimizado"] = (
        df_clusters["segmento_id"].astype(int).map(map_nosso)
    )
    df_clusters["limite_otimizado_pulp"] = (
        df_clusters["segmento_id"].astype(int).map(map_pulp)
    )
    df_clusters.to_parquet(parquet_clusters, index=False)

    # O arquivo por cliente (_com_cluster) NÃO recebe mais os limites: o limite é
    # por segmento e todo consumidor (inclusive o backend, em credit_service) já o
    # obtém mapeando segmento_id -> limite. Reescrever ~1,8M linhas aqui era
    # redundante e caro, então foi removido.
    _ = parquet_com_cluster  # mantido na assinatura por compatibilidade


def main() -> None:
    if len(sys.argv) < 3:
        print("Uso:")
        print("    python main.py <arquivo.parquet> <parametros.json>")
        print("Exemplo:")
        print("    python main.py base_ref_M1_v2.parquet parametros.json")
        sys.exit(1)

    arquivo_parquet = (
        Path(__file__).resolve().parent.parent.parent / "data" / "parquet" / sys.argv[1]
    )
    arquivo_json = Path(__file__).resolve().parent / "input" / sys.argv[2]

    if not arquivo_parquet.exists():
        print(f"Erro: arquivo {sys.argv[1]} não encontrado em data/parquet/")
        sys.exit(1)

    if not arquivo_json.exists():
        print(
            f"Erro: arquivo JSON {sys.argv[2]} não encontrado em algoritmo_simplex/input/"
        )
        sys.exit(1)

    # executa o pipeline completo
    try:
        with open(arquivo_json) as f:
            params = json.load(f)

        print(
            f"t={params['t']}, LGD={params['LGD']}, u_bar={params['u_bar']}, "
            f"L_max={params['L_max']}, T={params['T']}"
        )

        resultado = executar_pipeline(arquivo_parquet, params)

        # lê os clusters do cache para exibição no terminal
        cache_dir = Path(__file__).resolve().parent.parent.parent / "data" / "cache"
        stem = Path(sys.argv[1]).stem
        clusters = pd.read_parquet(cache_dir / f"{stem}_calibrado_clusters.parquet")
        x = [c["limite_otimizado"] for c in resultado["clusters"]]
        exibir_resultado(x, resultado["z"], resultado["status"], clusters)

        # os limites já foram gravados dentro de executar_pipeline. Apenas o
        # arquivo agregado por cluster (_clusters) recebe limite_otimizado /
        # _pulp; o _com_cluster (por cliente) não é mais reescrito (limite é por
        # segmento, obtido via segmento_id).
        print("\nLimites gravados em data/cache/:")
        print(f"  {resultado['parquet_clusters'].name}  (por cluster, + limite_otimizado / _pulp)")
    except FileNotFoundError as e:
        print(f"Erro: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Erro inesperado no pipeline: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
