"""
algoritmo_simplex/comparar.py
Script de comparação entre o Simplex implementado do zero neste projeto e a
biblioteca PuLP. Executa os dois solvers sobre os mesmos problemas e imprime
uma tabela com o resultado de cada um e o erro absoluto entre eles.

Uso:
    # rodar apenas os problemas didáticos
    python comparar.py

    # rodar também o problema real (clusters + parâmetros)
    python comparar.py <arquivo_calibrado.parquet> <parametros.json>

Os problemas didáticos são os mesmos usados em `simplex.py` (e documentados em
artefatos/algoritmo_simplex.md). O caso real reusa a mesma pipeline de
montagem do problema usada em `main.py`.
"""

import copy
import sys
from pathlib import Path

from models import Problema
from simplex import simplex
from simplex_pulp import simplex_pulp


# tolerância absoluta para considerar dois valores iguais na comparação
TOLERANCIA = 1e-6


def comparar_resultados(
    nome: str,
    problema: Problema,
) -> dict:
    """
    Roda os dois solvers no mesmo problema e devolve um resumo da comparação.
    Captura exceções (ex.: problema ilimitado), de forma que os dois solvers
    possam ser comparados mesmo nos casos limites.
    """
    resultado = {"nome": nome}

    # passa uma cópia profunda para cada solver - garante que um não corrompa
    # o problema visto pelo outro (defesa contra eventuais mutações in-place)
    try:
        x_nosso, z_nosso, status_nosso = simplex(copy.deepcopy(problema))
        resultado["nosso"] = {
            "x": x_nosso,
            "z": z_nosso,
            "status": status_nosso,
            "erro": None,
        }
    except Exception as e:
        resultado["nosso"] = {
            "x": None,
            "z": None,
            "status": "erro",
            "erro": str(e),
        }

    try:
        x_pulp, z_pulp, status_pulp = simplex_pulp(copy.deepcopy(problema))
        resultado["pulp"] = {
            "x": x_pulp,
            "z": z_pulp,
            "status": status_pulp,
            "erro": None,
        }
    except Exception as e:
        resultado["pulp"] = {
            "x": None,
            "z": None,
            "status": "erro",
            "erro": str(e),
        }

    # erro absoluto entre os valores ótimos da função objetivo
    if resultado["nosso"]["z"] is not None and resultado["pulp"]["z"] is not None:
        resultado["delta_z"] = abs(resultado["nosso"]["z"] - resultado["pulp"]["z"])
        resultado["coincidem"] = resultado["delta_z"] <= TOLERANCIA
    else:
        resultado["delta_z"] = None
        # se ambos falharam pelo mesmo motivo (ex.: ilimitado), consideramos coincidentes
        resultado["coincidem"] = (
            resultado["nosso"]["status"] == resultado["pulp"]["status"]
        )

    return resultado


def imprimir_resultado(resultado: dict) -> None:
    """Imprime um bloco formatado da comparação para um problema."""
    print(f"\n=== {resultado['nome']} ===")

    nosso = resultado["nosso"]
    pulp_r = resultado["pulp"]

    if nosso["erro"]:
        print(f"  Nosso  : ERRO -> {nosso['erro']}")
    else:
        x_str = ", ".join(f"{v:.4f}" for v in nosso["x"])
        print(f"  Nosso  : z = {nosso['z']:.6f} | status = {nosso['status']}")
        print(f"           x = [{x_str}]")

    if pulp_r["erro"]:
        print(f"  PuLP   : ERRO -> {pulp_r['erro']}")
    else:
        x_str = ", ".join(f"{v:.4f}" for v in pulp_r["x"])
        print(f"  PuLP   : z = {pulp_r['z']:.6f} | status = {pulp_r['status']}")
        print(f"           x = [{x_str}]")

    if resultado["delta_z"] is not None:
        print(f"  |Δz|  = {resultado['delta_z']:.2e}")
    coinc = "SIM" if resultado["coincidem"] else "NÃO"
    print(f"  Coincidem (tol={TOLERANCIA:.0e}): {coinc}")


def problemas_didaticos() -> list[tuple[str, Problema]]:
    """Problemas pequenos com solução conhecida, idênticos aos de simplex.py."""
    return [
        (
            "Problema do professor (solução única)",
            Problema(
                c=[40.0, 35.0],
                A=[[2.0, 3.0], [4.0, 3.0]],
                b=[60.0, 96.0],
            ),
        ),
        (
            "Problema ilimitado",
            Problema(
                c=[40.0, 35.0],
                A=[[-1.0, 0.0], [0.0, -1.0]],
                b=[60.0, 96.0],
            ),
        ),
        (
            "Problema com múltiplas soluções",
            Problema(
                c=[2.0, 4.0],
                A=[[1.0, 2.0], [1.0, 0.0]],
                b=[4.0, 2.0],
            ),
        ),
    ]


def problema_real(arquivo_parquet_nome: str, arquivo_json_nome: str) -> Problema:
    """
    Reaproveita as funções de main.py para montar o problema real do projeto
    (otimização de limites de crédito) e devolvê-lo no mesmo formato esperado
    pelos dois solvers.

    Parâmetros:
        arquivo_parquet_nome : nome do parquet calibrado em data/cache/
                               (ex: base_ref_M1_v2_calibrado.parquet)
        arquivo_json_nome    : nome do JSON de parâmetros em algoritmo_simplex/input/
                               (ex: parametros.json)
    """
    import json
    import pandas as pd
    from main import garantir_clusters, montar_problema

    arquivo_parquet = (
        Path(__file__).resolve().parent.parent.parent / "data" / "cache" / arquivo_parquet_nome
    )
    arquivo_json = Path(__file__).resolve().parent / "input" / arquivo_json_nome

    df = pd.read_parquet(arquivo_parquet)
    with open(arquivo_json) as f:
        params = json.load(f)

    clusters = garantir_clusters(arquivo_parquet_nome, arquivo_json_nome)
    return montar_problema(clusters, params, df)


def main() -> None:
    print("Comparação: Simplex do projeto vs. PuLP (CBC)")
    print("=" * 60)

    resultados = []
    for nome, problema in problemas_didaticos():
        resultados.append(comparar_resultados(nome, problema))

    if len(sys.argv) >= 3:
        try:
            problema = problema_real(sys.argv[1], sys.argv[2])
            resultados.append(comparar_resultados("Caso real (clusters + parâmetros)", problema))
        except Exception as e:
            print(f"\n[!] Não foi possível montar o caso real: {e}")

    for r in resultados:
        imprimir_resultado(r)

    print("\n" + "=" * 60)
    total = len(resultados)
    iguais = sum(1 for r in resultados if r["coincidem"])
    print(f"Resumo: {iguais}/{total} casos com resultado equivalente (tol={TOLERANCIA:.0e})")


if __name__ == "__main__":
    main()
