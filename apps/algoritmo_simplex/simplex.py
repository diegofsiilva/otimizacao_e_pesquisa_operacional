"""
algoritmo_simplex/simplex.py
Simplex de variáveis limitadas (bounded-variable simplex), vetorizado em NumPy.

Reescrito a partir da versão original (tableau em listas Python puras), aplicando
técnicas que solvers industriais como o HiGHS usam para resolver LPs rápido,
mas mantendo a implementação "na mão": nenhuma biblioteca de programação linear
é usada. O NumPy entra apenas como álgebra vetorizada, no lugar dos loops Python
do pivotamento — o algoritmo (escolha de variável que entra/sai, teste da razão,
detecção de ótimo/ilimitado) continua todo escrito aqui.

Técnicas aplicadas (e onde o HiGHS faz o mesmo):
  1. PRESOLVE de bounds. Restrições que envolvem uma única variável (linhas
     "singleton", ex.: L_k <= m_k·CP_k e L_k <= L_max) NÃO viram linhas da
     matriz — viram limites (bounds) da variável. Isso derruba o número de
     restrições de (1 + 2K) para ~1, encolhendo o tableau de m≈1601 para m≈1.
     É o ganho estrutural mais importante.
  2. VARIÁVEIS LIMITADAS (bounded-variable simplex). Cada variável tem
     [lower, upper]; variáveis não-básicas ficam em um dos limites e podem
     "trocar de lado" (bound flip) sem trocar a base. É assim que o upper bound
     de R2/R3 é tratado sem custar uma linha de restrição.
  3. VETORIZAÇÃO. O pivotamento é uma atualização rank-1 vetorizada
     (T -= outer(coluna, linha_pivô)) em vez de três loops aninhados em Python.
  4. PRICING de Dantzig (maior custo reduzido) com fallback para a regra de
     Bland quando há estagnação, evitando ciclagem em problemas degenerados.
     (O HiGHS usa Devex/steepest-edge; Dantzig+Bland é a versão "na mão" da
     mesma ideia: priorizar progresso e garantir terminação.)

Contrato idêntico ao da versão original:
    simplex(Problema(c, A, b)) -> (x, z, status)
    status ∈ {"otimo", "multiplas_solucoes"}; ValueError("...ilimitado...") se ilimitado.
Bounds opcionais entram via Problema.lower / Problema.upper.

Pressuposto (igual ao da versão original): b >= 0 nas linhas que sobram após o
presolve, de modo que a base inicial de folgas já é factível (sem Fase I).
"""

from __future__ import annotations

import numpy as np

from models import Problema, Tableau

_TOL = 1e-9          # tolerância numérica geral
_INF = float("inf")


# ---------------------------------------------------------------------------
# Compatibilidade: tableau inicial em listas (matriz de folga identidade m×m).
# A versão original construía isso explicitamente; era um dos gargalos (a
# identidade m×m era materializada e atualizada a cada pivô). O motor novo NÃO
# usa esta representação — a função permanece apenas para o teste estrutural e
# para fins didáticos.
# ---------------------------------------------------------------------------
def construir_tableau_inicial(problema: Problema) -> Tableau:
    """Tableau inicial com a base formada pelas variáveis de folga (forma didática)."""
    n = len(problema.c)
    m = len(problema.b)

    valores_iniciais = list(problema.b)
    indices_variaveis_folga = list(range(n, n + m))
    contribuicao_variaveis_folga = [0.0] * m

    x = []
    for i in range(n):
        x.append([problema.A[j][i] for j in range(m)])

    s = []
    for i in range(m):
        coluna = [0.0] * m
        coluna[i] = 1.0
        s.append(coluna)

    return Tableau(
        contributions=contribuicao_variaveis_folga,
        base=indices_variaveis_folga,
        values=valores_iniciais,
        x=x,
        s=s,
    )


# ---------------------------------------------------------------------------
# Leitura dos bounds do problema
# ---------------------------------------------------------------------------
def _ler_bounds(problema: Problema, n: int) -> tuple[np.ndarray, np.ndarray]:
    """Extrai os vetores de limite inferior e superior das variáveis.

    Normaliza os bounds do problema para arrays NumPy de tamanho ``n``: ausência
    de ``lower`` vira 0.0 (e ``None`` por variável também vira 0.0); ausência de
    ``upper`` vira ``+infinito`` (``_INF``), assim como ``None`` por variável.

    Args:
        problema: Instância do problema com os atributos ``lower``/``upper``.
        n: Número de variáveis de decisão.

    Returns:
        Tupla ``(lo, hi)`` de arrays ``float`` com os limites inferior e superior.
    """
    if problema.lower is None:
        lo = np.zeros(n, dtype=float)
    else:
        lo = np.array(
            [0.0 if v is None else float(v) for v in problema.lower], dtype=float
        )
    if problema.upper is None:
        hi = np.full(n, _INF, dtype=float)
    else:
        hi = np.array(
            [_INF if v is None else float(v) for v in problema.upper], dtype=float
        )
    return lo, hi


# ---------------------------------------------------------------------------
# Presolve: dobra linhas singleton em bounds e remove linhas vazias
# ---------------------------------------------------------------------------
def _presolve(
    A: np.ndarray, b: np.ndarray, lo: np.ndarray, hi: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Transforma toda restrição `a · x_j <= b_i` (linha com um único coeficiente
    não-nulo) em um bound da variável j, e descarta linhas totalmente nulas.
    Retorna (A_reduzida, b_reduzida, lo, hi). Levanta ValueError se inviável.
    """
    lo = lo.copy()
    hi = hi.copy()
    m, n = A.shape
    linhas_estruturais: list[int] = []

    for i in range(m):
        nz = np.nonzero(np.abs(A[i]) > _TOL)[0]
        if nz.size == 0:
            # linha vazia: 0 <= b_i. Se b_i < 0, inviável; senão, redundante.
            if b[i] < -_TOL:
                raise ValueError("O problema é inviável.")
            continue
        if nz.size == 1:
            j = int(nz[0])
            a = A[i, j]
            limite = b[i] / a
            if a > 0:
                hi[j] = min(hi[j], limite)   # x_j <= b_i/a
            else:
                lo[j] = max(lo[j], limite)   # x_j >= b_i/a
            continue
        linhas_estruturais.append(i)

    if linhas_estruturais:
        A_red = A[linhas_estruturais, :].copy()
        b_red = b[linhas_estruturais].copy()
    else:
        A_red = np.zeros((0, n), dtype=float)
        b_red = np.zeros(0, dtype=float)

    if np.any(lo > hi + _TOL):
        raise ValueError("O problema é inviável.")

    return A_red, b_red, lo, hi


# ---------------------------------------------------------------------------
# Caso sem restrições estruturais (apenas bounds): solução fechada
# ---------------------------------------------------------------------------
def _resolver_sem_restricoes(
    c: np.ndarray, lo: np.ndarray, hi: np.ndarray
) -> tuple[np.ndarray, str]:
    """
    Sem nenhuma linha de restrição, cada variável vai sozinha para o bound que
    melhora a FO: c_j > 0 -> upper; c_j < 0 -> lower; c_j = 0 -> indiferente.
    Se algum c_j > 0 tem upper = +inf, o problema é ilimitado.
    """
    n = c.size
    x = lo.copy()
    multiplo = False
    for j in range(n):
        if c[j] > _TOL:
            if not np.isfinite(hi[j]):
                raise ValueError("O problema é ilimitado.")
            x[j] = hi[j]
        elif c[j] < -_TOL:
            x[j] = lo[j]
        else:
            x[j] = lo[j]
            if hi[j] > lo[j] + _TOL:  # variável livre sem efeito na FO
                multiplo = True
    return x, ("multiplas_solucoes" if multiplo else "otimo")


# ---------------------------------------------------------------------------
# Motor: bounded-variable primal simplex (tableau denso vetorizado)
# ---------------------------------------------------------------------------
def _resolver_bounded(
    c: np.ndarray, A: np.ndarray, b: np.ndarray, lo: np.ndarray, hi: np.ndarray
) -> tuple[np.ndarray, str]:
    """Resolve ``min cᵀx s.a. Ax <= b, lo <= x <= hi`` (simplex primal limitado).

    Motor central do solver: monta o tableau denso ``M = [A | I]`` com variáveis
    de folga, parte da base de folgas e itera pivôs com variáveis não-básicas em
    seus limites (lower/upper). Inclui anti-ciclagem via regra de Bland após
    estagnação.

    Args:
        c: Vetor de custos das variáveis estruturais (minimização).
        A: Matriz de restrições (``<=``), forma ``(m, n)``.
        b: Lado direito das restrições, tamanho ``m``.
        lo: Limites inferiores das ``n`` variáveis estruturais.
        hi: Limites superiores (``_INF`` quando ilimitado).

    Returns:
        Tupla ``(x, status)`` onde ``x`` é o vetor solução das variáveis
        estruturais e ``status`` é ``"otimo"`` ou ``"ilimitado"``. O caso sem
        restrições é delegado a :func:`_resolver_sem_restricoes`.

    Raises:
        ValueError: se o simplex não convergir dentro do limite de iterações.
    """
    m, n = A.shape

    if m == 0:
        return _resolver_sem_restricoes(c, lo, hi)

    # Variáveis: n estruturais + m de folga. M = [A | I], custo [c | 0].
    N = n + m
    M = np.hstack([A, np.eye(m)])
    custo = np.concatenate([c, np.zeros(m)])
    lo_all = np.concatenate([lo, np.zeros(m)])
    hi_all = np.concatenate([hi, np.full(m, _INF)])

    # Base inicial = folgas. Não-básicas (estruturais) começam no lower bound.
    base = np.arange(n, N)                      # índices das básicas (uma por linha)
    em_base = np.zeros(N, dtype=bool)
    em_base[base] = True
    no_upper = np.zeros(N, dtype=bool)          # não-básica está no upper? (senão lower)

    # Tableau T = B^{-1} M (inicialmente B = I -> T = M).
    T = M.copy()

    # Valor das não-básicas (lo/hi) e das básicas.
    valor_nb = lo_all.copy()                    # estruturais no lower; folgas idem
    # básicas: x_B = b - (parte não-básica). Como estruturais no lower (0 aqui),
    # x_B = b. Caso geral: x_B = b - A[:, nb] · valor_nb[nb].
    contrib_nb = A @ valor_nb[:n]
    xB = b - contrib_nb

    if np.any(xB < -1e-6):
        # b >= 0 não vale após mover não-básicas: precisaria de Fase I.
        raise ValueError(
            "Base inicial de folgas infactível (b < 0). "
            "Esta formulação pressupõe b >= 0; uma restrição do tipo >= "
            "(ex.: meta de produção R6 com V_min > 0) exigiria Fase I."
        )

    max_iter = 50 * (N + m) + 1000
    estagnado = 0
    usar_bland = False

    for _ in range(max_iter):
        cB = custo[base]
        # custos reduzidos d_j = c_j - cB · T[:, j]
        d = custo - cB @ T
        d[base] = 0.0

        # Candidatas a entrar (direção de melhora p/ MAXIMIZAÇÃO):
        #   não-básica no lower com d_j > 0  -> aumentar melhora
        #   não-básica no upper com d_j < 0  -> diminuir melhora
        melhora = np.where(no_upper, -d, d)
        melhora[em_base] = -np.inf
        # variável fixa (lower == upper) não pode melhorar; excluí-la evita
        # ciclagem em "bound flips" de passo zero (ocorre quando m_k·CP_k = 0).
        candidatas = (melhora > _TOL) & (hi_all - lo_all > _TOL)

        if not np.any(candidatas):
            # Ótimo. Múltiplas soluções: alguma não-básica (que pode se mover)
            # com custo reduzido nulo.
            movel = (~em_base) & (hi_all > lo_all + _TOL)
            status = (
                "multiplas_solucoes"
                if np.any(movel & (np.abs(d) <= 1e-7))
                else "otimo"
            )
            x = _extrair_x(n, N, base, xB, valor_nb, no_upper, lo_all, hi_all)
            return x[:n], status

        # Escolha da variável que entra:
        if usar_bland:
            entra = int(np.argmax(candidatas))            # menor índice candidato
        else:
            entra = int(np.argmax(np.where(candidatas, melhora, -np.inf)))  # Dantzig

        sobe = not no_upper[entra]                        # entra subindo (do lower)?
        # direção das básicas em função do passo t >= 0
        dir_B = -T[:, entra] if sobe else T[:, entra]

        # --- teste da razão (com bounds dos dois lados) ---
        t_max = hi_all[entra] - lo_all[entra]             # limite por bound flip
        linha_sai = -1
        sai_para_upper = False

        # básica sobe (dir_B>0) -> esbarra no upper; básica desce (dir_B<0) -> no lower
        for i in range(m):
            taxa = dir_B[i]
            if taxa > _TOL:
                ub = hi_all[base[i]]
                if np.isfinite(ub):
                    razao = (ub - xB[i]) / taxa
                    if razao < t_max - _TOL or (linha_sai == -1 and razao <= t_max + _TOL):
                        t_max = razao
                        linha_sai = i
                        sai_para_upper = True
            elif taxa < -_TOL:
                lb = lo_all[base[i]]
                razao = (xB[i] - lb) / (-taxa)
                if razao < t_max - _TOL or (linha_sai == -1 and razao <= t_max + _TOL):
                    t_max = razao
                    linha_sai = i
                    sai_para_upper = False

        if not np.isfinite(t_max):
            raise ValueError("O problema é ilimitado.")

        t = max(t_max, 0.0)

        # avança as básicas
        xB = xB + t * dir_B

        if linha_sai == -1:
            # bound flip: a própria variável que entra trocou de lower<->upper;
            # base inalterada.
            no_upper[entra] = not no_upper[entra]
            valor_nb[entra] = hi_all[entra] if no_upper[entra] else lo_all[entra]
            # conta apenas passos sem progresso (degenerados, t≈0); um bound flip
            # com t>0 melhora a FO e zera o contador.
            estagnado = estagnado + 1 if t <= _TOL else 0
        else:
            # pivô: 'entra' entra na base na linha 'linha_sai'; a básica que sai
            # vira não-básica no bound que atingiu.
            sai = int(base[linha_sai])
            valor_entrada = (
                (lo_all[entra] if sobe else hi_all[entra]) + (t if sobe else -t)
            )

            piv = T[linha_sai, entra]
            T[linha_sai, :] /= piv
            col = T[:, entra].copy()
            col[linha_sai] = 0.0
            T -= np.outer(col, T[linha_sai, :])

            base[linha_sai] = entra
            em_base[sai] = False
            em_base[entra] = True
            xB[linha_sai] = valor_entrada

            no_upper[sai] = sai_para_upper
            valor_nb[sai] = hi_all[sai] if sai_para_upper else lo_all[sai]

            # pivô degenerado (t≈0) não progride: conta para o gatilho de Bland.
            estagnado = estagnado + 1 if t <= _TOL else 0

        # anti-ciclagem: muita estagnação -> regra de Bland
        usar_bland = estagnado > 2 * N

    raise ValueError("Simplex não convergiu (limite de iterações atingido).")


def _extrair_x(n, N, base, xB, valor_nb, no_upper, lo_all, hi_all) -> np.ndarray:
    """Reconstrói o vetor solução completo a partir do estado do tableau.

    As variáveis não-básicas já carregam seu valor (em lower ou upper) em
    ``valor_nb``; as básicas recebem o valor corrente ``xB``.

    Args:
        n: Número de variáveis estruturais (mantido por simetria de assinatura).
        N: Número total de variáveis (estruturais + folgas).
        base: Índices das variáveis básicas.
        xB: Valores das variáveis básicas.
        valor_nb: Valores correntes de todas as variáveis não-básicas.
        no_upper: Máscara indicando não-básicas fixadas no limite superior.
        lo_all: Limites inferiores de todas as variáveis.
        hi_all: Limites superiores de todas as variáveis.

    Returns:
        O vetor ``x`` (tamanho ``N``) com o valor de todas as variáveis.
    """
    x = valor_nb.copy()
    x[base] = xB
    return x


# ---------------------------------------------------------------------------
# Função pública
# ---------------------------------------------------------------------------
def simplex(problema: Problema) -> tuple[list[float], float, str]:
    """
    Resolve um LP de maximização pelo método Simplex (variáveis limitadas).

    max  c · x   s.t.  A x <= b,  lower <= x <= upper

    Retorna:
        x      : valor ótimo de cada variável de decisão (lista de tamanho n)
        z      : valor ótimo da função objetivo
        status : "otimo" ou "multiplas_solucoes"

    Raises:
        ValueError: se o problema for ilimitado (mensagem contém "ilimitado")
                    ou inviável.
    """
    n = len(problema.c)
    c = np.array(problema.c, dtype=float)
    m = len(problema.b)
    A = (
        np.array(problema.A, dtype=float).reshape(m, n)
        if m > 0
        else np.zeros((0, n), dtype=float)
    )
    b = np.array(problema.b, dtype=float)

    lo, hi = _ler_bounds(problema, n)

    # presolve: linhas singleton -> bounds; descarta linhas vazias
    A, b, lo, hi = _presolve(A, b, lo, hi)

    x_arr, status = _resolver_bounded(c, A, b, lo, hi)

    x = [float(v) for v in x_arr]
    z = float(np.dot(c, x_arr))
    return x, z, status


if __name__ == "__main__":
    # problema do professor (solução única)
    problema = Problema(c=[40.0, 35.0], A=[[2.0, 3.0], [4.0, 3.0]], b=[60.0, 96.0])
    print("Problema do professor ->", simplex(problema))

    # problema ilimitado
    try:
        simplex(Problema(c=[40.0, 35.0], A=[[-1.0, 0.0], [0.0, -1.0]], b=[60.0, 96.0]))
    except ValueError as e:
        print("Problema ilimitado ->", e)

    # problema com múltiplas soluções
    print(
        "Problema múltiplas ->",
        simplex(Problema(c=[2.0, 4.0], A=[[1.0, 2.0], [1.0, 0.0]], b=[4.0, 2.0])),
    )

    # bounds nativos (R2/R3): max 1·x0 + 1·x1, x0<=5, x1<=7  -> x=[5,7], z=12
    print(
        "Problema com bounds ->",
        simplex(Problema(c=[1.0, 1.0], A=[], b=[], upper=[5.0, 7.0])),
    )
