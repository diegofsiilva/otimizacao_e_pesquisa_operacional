"""
algoritmo_simplex/models.py
Estruturas de dados para o algoritmo Simplex.
"""

from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Problema:
    """
    Representa um problema de programação linear na forma:
        max  c[0]*x[0] + c[1]*x[1] + ... + c[n]*x[n]
        s.t. A[i][0]*x[0] + A[i][1]*x[1] + ... <= b[i]  para cada restrição i
             x[j] >= 0  para cada variável j

    Onde:
        n = número de variáveis de decisão = len(c) = número de colunas de A
        m = número de restrições          = len(b) = número de linhas de A

    Atributos:
        c  : lista de coeficientes da função objetivo        (tamanho n)
        A  : matriz de coeficientes das restrições           (tamanho m x n)
        b  : lista dos lados direitos das restrições         (tamanho m)
    """

    c: list[float]
    A: list[list[float]]
    b: list[float]


@dataclass
class Tableau:
    """
    Representa o estado atual da tabela do Simplex.

    Atributos:
        contributions  : coluna Contribution - contribuição de cada variável da base para o lucro  (tamanho m)
        base           : coluna Base - índices das variáveis atualmente na base                    (tamanho m)
        values         : coluna Value - valor atual de cada variável da base                       (tamanho m)
        x              : colunas x1, x2, ... - coeficientes das variáveis de decisão              (tamanho n x m)
        s              : colunas s1, s2, ... - coeficientes das variáveis de folga                 (tamanho m x m)
    """

    contributions: list[float]
    base: list[int]
    values: list[float]
    x: list[list[float]]
    s: list[list[float]]
