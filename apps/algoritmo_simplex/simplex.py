"""
algoritmo_simplex/simplex.py
Implementação do algoritmo Simplex para problemas de programação linear.
"""

from models import Problema, Tableau

def construir_tableau_inicial(problema: Problema) -> Tableau:
    """
    Constrói o tableau inicial a partir de um problema de programação linear.
    No tableau inicial, a base é formada pelas variáveis de folga.

    Parâmetros:
        problema: instância de Problema contendo c, A e b

    Retorna:
        Tableau inicial pronto para o algoritmo Simplex
    """
    pass

def simplex(problema: Problema) -> tuple[list[float], float]:
    """
    Resolve um problema de programação linear pelo método Simplex.

    Parâmetros:
        problema: instância de Problema contendo c, A e b

    Retorna:
        x: instância de Problema contendo c, A e b (tamanho N)
        z: valor ótimo da função objetivo
    """
    pass
