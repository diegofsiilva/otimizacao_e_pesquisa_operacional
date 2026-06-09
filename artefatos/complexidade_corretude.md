# Complexidade e Corretude

## Introdução

Este artefato analisa formalmente a **complexidade computacional** e a **corretude** de duas implementações que resolvem o mesmo problema de Programação Linear do projeto — a alocação ótima de limites de crédito por cluster de clientes do Banco Pan, na forma canônica de maximização:

$$
\max \; z = c^\top x \qquad \text{sujeito a} \qquad A x \le b, \quad x \ge 0.
$$

A primeira é o **Simplex implementado do zero pelo grupo** (`apps/algoritmo_simplex/simplex.py`): um método de *tableau* denso, com variáveis de folga e a regra anticiclagem de Bland. A segunda é a **implementação de referência com a biblioteca PuLP** (`apps/algoritmo_simplex/simplex_pulp.py`), que constrói o modelo e delega a otimização a um solver externo (CBC, HiGHS ou GLPK).

As duas foram desenvolvidas em paralelo e validadas cruzadamente por um *golden test* ([`comparacao_simplex.md`](./comparacao_simplex.md)): convergem ao mesmo ótimo dentro de $10^{-6}$. Para cada implementação apresentamos a análise de complexidade de pior e melhor caso (com notação $O$, $\Omega$, $\Theta$), o invariante do laço principal e a demonstração de corretude por **indução sobre esse invariante**. A Parte III compara as duas abordagens e discute os *trade-offs*.

> **Observação de leitura.** As Partes I e II preservam a numeração interna de seções de cada análise original. As referências de cada parte estão consolidadas ao final do documento.

---

# Parte I — Simplex implementado pelo grupo

Este artefato analisa formalmente a **complexidade computacional** e a **corretude** da implementação do método Simplex desenvolvida pelo grupo em `apps/algoritmo_simplex/simplex.py`. A análise toma como objeto exatamente o código implementado (e não uma versão idealizada de livro-texto), explicita quais partes vêm das fontes clássicas do método, e discute o impacto das adaptações feitas pelo grupo sobre o custo e a correção do algoritmo.

A análise é consistente com os demais artefatos do projeto: a descrição do algoritmo em [`algoritmo_simplex.md`](./algoritmo_simplex.md), a validação cruzada com a biblioteca PuLP/CBC em [`comparacao_simplex.md`](./comparacao_simplex.md) e a fundamentação teórica do artigo em [`artigo.md`](./artigo.md). O método base — tableau, variáveis de folga, critérios de entrada/saída, teste da razão, condição de otimalidade e teorema da dualidade — é o **Simplex clássico de Dantzig** (DANTZIG, 1951; DANTZIG, 1963, cap. 5 e 6); a única adaptação na regra de pivoteamento é a **regra de Bland (1977)**, adotada para garantir a finitude do método sob degeneração. Ao longo do texto, as afirmações sobre "o Simplex original" são ancoradas em páginas específicas dessas fontes (ver Seção 6).

---

## 1. Notação e dimensões do problema

A implementação resolve problemas de programação linear (PL) na **forma canônica de maximização**, conforme `models.py`:

$$
\max \; z = c^\top x
\qquad \text{sujeito a} \qquad
A x \le b, \quad x \ge 0,
$$

com a pré-condição $b \ge 0$ (justificada na Seção 5.1). Define-se:

| Símbolo | Significado | No código | No problema do parceiro |
| ------- | ----------- | --------- | ----------------------- |
| $n$ | nº de variáveis de decisão | `len(problema.c)` | $n = K$ (clusters) |
| $m$ | nº de restrições $\le$ | `len(problema.b)` | $m = 2K + 1$ |
| $N$ | nº total de variáveis (decisão + folga) | $n + m$ | $N = 3K + 1$ |
| $p$ | nº de pivôs (iterações que trocam a base) | — | depende da instância |

A contagem $m = 2K + 1$ decorre de `montar_problema` em `main.py`: uma restrição agregada **R1** (teto de inadimplência), $K$ restrições **R2** (capacidade de pagamento, uma por cluster) e $K$ restrições **R3** (teto de limite, uma por cluster), totalizando $1 + K + K = 2K + 1$.

Ao introduzir as $m$ variáveis de folga, o sistema padrão torna-se $[A \mid I]\,y = b$ com $y = (x_1,\dots,x_n,\,s_1,\dots,s_m) \in \mathbb{R}^{N}$ e vetor objetivo estendido $\hat c = (c,\,0) \in \mathbb{R}^{N}$. O **tableau** mantém, a cada iteração, a matriz $B^{-1}[A\mid I]$ e o vetor $B^{-1}b$, onde $B$ é a submatriz das colunas básicas atuais (índices em `tableau.base`). Essa representação em forma canônica relativa a uma base, com variáveis de folga compondo a base inicial, é exatamente a do Simplex original (DANTZIG, 1963, cap. 5, p. 94–119).

---

## 2. Análise de complexidade

A estratégia é decompor o custo em **(a)** custo de cada operação elementar, **(b)** custo de uma iteração, **(c)** número de iterações, e então combinar os fatores.

### 2.1 Custo das operações elementares

Lendo `simplex.py` linha a linha, observa-se que **nenhum dos laços internos possui `break` antecipado** — todos percorrem o intervalo completo. Isso é o que torna cada operação um $\Theta$ exato (cota superior e inferior coincidem), e não apenas um $O$:

- **Construção do tableau inicial** (`construir_tableau_inicial`): montar as $n$ colunas de decisão custa $\Theta(nm)$; a identidade das $m$ folgas custa $\Theta(m^2)$; copiar `b` custa $\Theta(m)$. Total: $\Theta(nm + m^2) = \Theta\big(m(n+m)\big) = \Theta(mN)$.

- **Custo reduzido de uma variável** (`calcular_cj_zj`): produto escalar de uma coluna de tamanho $m$ pelas `contributions`, $\Theta(m)$.

- **Custos reduzidos de todas as variáveis** (laço `while`, início): chama `calcular_cj_zj` para as $n$ colunas de decisão e as $m$ de folga, ou seja, $N$ colunas de tamanho $m$: $\Theta(Nm) = \Theta\big(m(n+m)\big)$.

- **Escolha da variável entrante** (regra de Bland): varredura linear até o primeiro índice com custo reduzido positivo, $O(N)$.

- **Teste da razão mínima**: uma passada sobre as $m$ linhas, $\Theta(m)$.

- **Pivoteamento** (Gauss–Jordan): normalizar a linha pivô percorre as $N$ colunas, $\Theta(N)$; eliminar a coluna pivô nas outras $m-1$ linhas percorre $N$ colunas em cada uma, $\Theta(mN)$. Total: $\Theta(mN) = \Theta\big(m(n+m)\big)$.

### 2.2 Custo de uma iteração

Cada iteração do laço `while` executa: cálculo dos custos reduzidos $\Theta(mN)$ + seleção $O(N)$ + teste da razão $\Theta(m)$ + pivoteamento $\Theta(mN)$. O termo dominante é o cálculo dos custos reduzidos e o pivoteamento, ambos $\Theta(mN)$. Logo:

$$
T_{\text{iter}} = \Theta\big(m(n+m)\big) = \Theta(mN).
$$

Esse é exatamente o custo de "tocar" todo o tableau, que possui $m \times N$ entradas — coerente com o fato de a implementação ser do tipo **tableau denso** (todas as colunas são mantidas e atualizadas explicitamente).

### 2.3 Número de iterações

O laço realiza $p$ pivôs e $p+1$ avaliações da condição de parada (a última encerra). Combinando com a construção inicial:

$$
T(\text{instância}) \;=\; \underbrace{\Theta(mN)}_{\text{build}} \;+\; \underbrace{(p+1)\,\Theta(mN)}_{\text{custos reduzidos}} \;+\; \underbrace{p\,\Theta(mN)}_{\text{pivôs}} \;=\; \boxed{\;\Theta\big((p+1)\,m(n+m)\big)\;}
$$

Toda a análise de pior/melhor/médio caso reduz-se, portanto, a **limitar $p$**.

**Cota superior universal sobre $p$.** Cada base corresponde à escolha de $m$ variáveis básicas dentre $N$, logo existem no máximo $\binom{N}{m} = \binom{n+m}{m}$ bases. A **regra de Bland (1977)** garante que nenhuma base se repete (Seção 5.4), portanto cada iteração visita uma base inédita e

$$
p \;\le\; \binom{n+m}{m} - 1 .
$$

Esse limite é finito — o que prova a terminação — mas é **exponencial** em $n+m$.

### 2.4 Pior caso

Substituindo a cota de $p$ em $T$:

$$
T_{\text{pior}}(n,m) \;=\; O\!\left( \binom{n+m}{m} \cdot m\,(n+m) \right),
$$

um custo **exponencial**. Essa cota não é um artefato da análise: existem famílias de instâncias (do tipo *cubo de Klee–Minty* e suas variantes para regras anticiclagem) que forçam o Simplex a visitar uma fração exponencial dos vértices, estabelecendo também uma cota inferior $\Omega(\cdot)$ exponencial para o método no pior caso. Não se conhece nenhuma regra de pivoteamento que torne o Simplex polinomial no pior caso; a escolha da regra de Bland prioriza **robustez (terminação garantida)** e não complexidade de pior caso.

### 2.5 Melhor caso

O melhor caso ocorre quando $p = 0$, isto é, quando a origem (base inicial de folgas) já é ótima. Isso acontece exatamente quando todos os custos reduzidos iniciais são não-positivos. Como na base inicial `contributions = 0`, tem-se $z_j = 0$ e o custo reduzido de cada variável de decisão é o próprio $c_j$; portanto a condição de melhor caso é $c_j \le 0$ para todo $j$. Nesse cenário o laço calcula os custos reduzidos uma vez e encerra:

$$
T_{\text{melhor}}(n,m) \;=\; \Theta\big(m(n+m)\big) \;=\; \Theta(mN).
$$

Como qualquer execução precisa, no mínimo, construir o tableau e verificar otimalidade uma vez, esse também é o **piso de custo universal**: para toda entrada, $T = \Omega\big(m(n+m)\big)$.

### 2.6 Caso médio / prático

Para o PL deste projeto, $p$ é muito pequeno por causa da **estrutura quase-separável** das restrições: R2 e R3 são restrições-caixa ($L_k \le m_k CP_k$ e $L_k \le L^{max}$), e o único acoplamento entre clusters é a restrição agregada R1. Na origem, só entram na base clusters com custo reduzido positivo ($c_k > 0$); clusters com $c_k \le 0$ nunca são candidatos pela regra de Bland e permanecem em $L_k = 0$. Assim, $p$ é da ordem do número de clusters rentáveis, e empiricamente $p = O(K)$.

Medições com instâncias geradas no formato do projeto ($n = K$, $m = 2K+1$, $b \ge 0$, 20 sementes por tamanho) confirmam esse comportamento sublinear–linear:

| $K$ | $n$ | $m = 2K+1$ | pivôs médios | pivôs máx |
| --- | --- | ---------- | ------------ | --------- |
| 5   | 5   | 11  | 0,1 | 1 |
| 7   | 7   | 15  | 0,5 | 2 |
| 10  | 10  | 21  | 0,8 | 3 |
| 20  | 20  | 41  | 1,1 | 3 |
| 40  | 40  | 81  | 3,1 | 6 |
| 80  | 80  | 161 | 5,0 | 8 |

Com $p = O(K)$ e $m(n+m) = \Theta(K^2)$ (Seção 2.7), o custo prático é

$$
T_{\text{prático}} \;=\; O\!\big(K \cdot K^2\big) \;=\; O(K^3).
$$

Esse resultado é coerente com a teoria do caso médio do Simplex (análise probabilística de Borgwardt e análise *smoothed* de Spielman–Teng), que explica por que o método é eficiente na prática apesar do pior caso exponencial.

### 2.7 Especialização para o problema do parceiro

Substituindo $n = K$ e $m = 2K+1$:

$$
m(n+m) = (2K+1)(3K+1) = 6K^2 + 5K + 1 = \Theta(K^2).
$$

Logo, para o problema do Banco Pan:

- **Custo por pivô:** $\Theta(K^2)$.
- **Melhor caso (origem ótima):** $\Theta(K^2)$.
- **Custo prático (com $p = O(K)$ pivôs):** $O(K^3)$.
- **Pior caso teórico:** exponencial em $K$.

Para a entrega final ($K \ge 100$ clusters, base de mais de um milhão de clientes), $m \approx 201$ e o custo por pivô $\Theta(K^2)$ permanece pequeno (dezenas de milhares de operações por pivô). O número de clientes ($>10^6$) **não** entra na complexidade do Simplex: ele afeta apenas a etapa de clusterização (K-Means) e a agregação por cluster, anteriores ao PL. O Simplex opera somente sobre os $K$ clusters agregados.

### 2.8 Complexidade de espaço

O tableau armazena explicitamente as $n$ colunas de decisão ($n \times m$), as $m$ colunas de folga ($m \times m$) e os vetores `values`, `base`, `contributions` ($\Theta(m)$ cada):

$$
S(n,m) = \Theta\big(m(n+m)\big) = \Theta(mN), \qquad \text{e } \Theta(K^2) \text{ no problema do parceiro.}
$$

### 2.9 Quadro-resumo

| Cenário | Cota sobre $p$ | Complexidade de tempo | Notação | No problema ($n=K,\,m=2K+1$) |
| ------- | -------------- | --------------------- | ------- | ----------------------------- |
| Melhor caso | $p = 0$ | $m(n+m)$ | $\Theta\big(m(n+m)\big)$ | $\Theta(K^2)$ |
| Caso prático | $p = O(K)$ | $K\cdot m(n+m)$ | $O(K^3)$ | $O(K^3)$ |
| Pior caso | $p \le \binom{n+m}{m}-1$ | $\binom{n+m}{m}\,m(n+m)$ | $O(\cdot)$ exponencial | exponencial em $K$ |
| Piso universal | — | $m(n+m)$ | $\Omega\big(m(n+m)\big)$ | $\Omega(K^2)$ |
| Por instância (genérica) | $p$ pivôs | $(p+1)\,m(n+m)$ | $\Theta\big(p\,m(n+m)\big)$ | $\Theta(p\,K^2)$ |
| Espaço | — | — | $\Theta\big(m(n+m)\big)$ | $\Theta(K^2)$ |

---

## 3. Corretude

A corretude é demonstrada em duas partes, no padrão clássico: **(i) corretude parcial** — *se* o algoritmo termina, a saída é uma solução ótima (ou o status correto); **(ii) terminação** — o algoritmo de fato termina. A corretude parcial é provada por **indução sobre o invariante do laço**; a terminação apoia-se na regra de Bland (1977), exatamente a fonte usada pelo grupo.

### 3.1 Forma padrão e pré-condição

A implementação **não usa Fase I nem variáveis artificiais**: ela inicia diretamente na origem, com a base formada pelas variáveis de folga e `values = b`. Para que essa base inicial seja **factível**, é necessário que $b \ge 0$ (caso contrário alguma folga inicial seria negativa). Essa é a pré-condição do algoritmo.

O PL do projeto a satisfaz **por construção** (ver `montar_problema`): R1 tem lado direito exatamente $0$; R2 tem lado direito $m_k\,CP_k \ge 0$ (fator de alavancagem e capacidade de pagamento não-negativos); R3 tem lado direito $L^{max} > 0$. Portanto $b = [\,0,\; m_k CP_k,\; L^{max}\,] \ge 0$ e a origem é sempre factível.

### 3.2 Invariante principal do laço

> **Invariante $\mathcal{P}$.** No início de cada iteração do laço `while`, o tableau representa uma **solução básica factível (SBF)** do PL. Formalmente, sendo $B$ a submatriz das colunas de $[A\mid I]$ indexadas por `base`:
>
> - **(P1) Base válida em forma canônica.** Os $m$ índices de `base` são distintos e as colunas correspondentes de $[A\mid I]$ são linearmente independentes (formam uma base $B$). No tableau, cada coluna básica é o vetor unitário da sua linha; equivalentemente, o tableau armazena $B^{-1}[A\mid I]$ e `values` $= B^{-1}b$.
> - **(P2) Factibilidade.** `values`$[i] \ge 0$ para todo $i$.
> - **(P3) Contribuições coerentes.** `contributions`$[i] = \hat c_{\,\texttt{base}[i]}$ para todo $i$.
> - **(P4) Equivalência ao sistema original.** O ponto $y^*$ com $y^*_{\texttt{base}[i]} = \texttt{values}[i]$ e $y^*_j = 0$ para $j$ não-básico satisfaz $[A\mid I]\,y^* = b$ e $y^* \ge 0$ — ou seja, $y^*$ é uma SBF do PL.

### 3.3 Prova do invariante por indução

**Base da indução (tableau inicial).** Em `construir_tableau_inicial`, `base` $= (n, n+1, \dots, n+m-1)$ são as $m$ folgas, cujas colunas em $[A\mid I]$ formam a identidade $I$; logo $B = I$, $B^{-1} = I$ e o tableau armazenado é $[A \mid I \mid b]$ — exatamente as colunas `x` $= A$, `s` $= I$ e `values` $= b$. Assim **(P1)** vale (colunas unitárias e independentes). **(P2)** vale porque `values` $= b \ge 0$ pela pré-condição da Seção 3.1. **(P3)** vale porque `contributions` $= 0 = \hat c$ das folgas. **(P4)** vale porque $I\cdot y^* = b$ é o próprio sistema padrão. $\checkmark$

**Passo indutivo.** Suponha $\mathcal{P}$ no início de uma iteração que executa um pivô (se o laço encerra, nada há a provar). Seja $j_e$ a variável entrante (custo reduzido $c_{j_e} - z_{j_e} > 0$) e `col` sua coluna no tableau. O teste da razão mínima escolhe a linha de saída

$$
i^* = \arg\min_i \left\{ \frac{\texttt{values}[i]}{\texttt{col}[i]} \;:\; \texttt{col}[i] > 0 \right\},
$$

com elemento pivô $p = \texttt{col}[i^*] > 0$. (Se nenhum $\texttt{col}[i] > 0$, cai-se no caso ilimitado da Seção 3.6.) O pivoteamento normaliza a linha $i^*$ por $p$ e elimina a coluna $j_e$ das demais linhas. Verifica-se que $\mathcal{P}$ se mantém:

- **(P1).** Após o pivô, a coluna $j_e$ vira $e_{i^*}$ (vale $1$ na linha $i^*$ e $0$ nas demais). Para qualquer outra coluna básica $e_q$ ($q \ne i^*$), sua entrada na linha $i^*$ já era $0$; logo a normalização da linha $i^*$ e as eliminações `linha_i -= col[i]·linha_{i^*}` não a alteram, e ela permanece unitária. A nova base (igual à anterior com $j_e$ no lugar de `base`$[i^*]$) tem, portanto, colunas unitárias. Ela é de fato uma base porque trocar a coluna `base`$[i^*]$ por $j_e$ preserva a invertibilidade — possível justamente porque a entrada pivô $p \ne 0$. Assim o tableau passa a ser $B'^{-1}[A\mid I]$ para a nova base $B'$. $\checkmark$
- **(P2) — esta é a razão de ser do teste da razão mínima.** A nova linha pivô: $\texttt{values}[i^*] \leftarrow \texttt{values}[i^*]/p \ge 0$ (ambos $\ge 0$, $p>0$). Para $i \ne i^*$: $\texttt{values}[i] \leftarrow \texttt{values}[i] - \texttt{col}[i]\cdot \dfrac{\texttt{values}[i^*]}{p}$.
  - Se $\texttt{col}[i] \le 0$: subtrai-se um termo $\le 0$, logo `values`$[i]$ **não diminui** e permanece $\ge 0$.
  - Se $\texttt{col}[i] > 0$: $\texttt{values}[i] \leftarrow \texttt{col}[i]\left(\dfrac{\texttt{values}[i]}{\texttt{col}[i]} - \dfrac{\texttt{values}[i^*]}{p}\right) \ge 0$, pois $\dfrac{\texttt{values}[i^*]}{p}$ é o **mínimo** das razões, $\le \dfrac{\texttt{values}[i]}{\texttt{col}[i]}$.
  
  Em ambos os casos `values` permanece $\ge 0$. $\checkmark$
- **(P3).** `contributions`$[i^*]$ é atualizada para $\hat c_{j_e}$ (`problema.c[indice_entra]` se for decisão, $0$ se for folga); as demais não mudam e continuam coerentes com suas variáveis básicas inalteradas. $\checkmark$
- **(P4).** Cada passo do pivô é uma operação elementar de linha, isto é, multiplicação à esquerda por matriz invertível; isso **preserva o conjunto-solução** de $[A\mid I]y = b$. A nova SBF continua satisfazendo o sistema, e por (P2) é $\ge 0$. $\checkmark$

Por indução, $\mathcal{P}$ vale no início de **toda** iteração. $\blacksquare$

### 3.4 Terminação

> **Lema (Bland, 1977).** Se, em todo pivô, (i) a variável **entrante** é a de menor índice com custo reduzido positivo **e** (ii) entre as linhas que empatam no teste da razão mínima escolhe-se como **saínte** a variável básica de menor índice, então nenhuma base se repete ao longo da execução; em particular, não há ciclagem.

A implementação aplica **integralmente a cláusula (i)**: `indice_entra` é o primeiro $j$ com `todos_cj_zj[j] > 0`, e como os índices globais $0,\dots,n-1$ correspondem a $x_1,\dots,x_n$ e $n,\dots,n+m-1$ às folgas $s_1,\dots,s_m$, "primeiro $j$" é exatamente "menor índice de variável". Pelo Lema, como há no máximo $\binom{n+m}{m}$ bases e cada iteração produz uma base inédita (Seção 3.3 garante que cada iteração resulta numa base válida), o laço executa um número finito de iterações e **termina**. Esse é o motivo de a regra de Bland ser adotada em vez da regra de Dantzig (maior custo reduzido): a regra de Dantzig pode **ciclar** sob degeneração, que é frequente neste PL — R2 e R3 impõem dois tetos sobre a mesma variável $L_k$, gerando empates no teste da razão. O próprio Dantzig tratou a finitude sob degeneração por um **método de perturbação** dos lados direitos (DANTZIG, 1963, cap. 10, "Finiteness of the Simplex Method Under Perturbation"); o grupo optou pela alternativa combinatória de Bland (1977), mais simples de implementar por ser apenas uma regra de desempate por índice, sem alterar os dados do problema. A terminação aqui **não é cosmética**: depende criticamente de Bland (1977), fonte citada em [`artigo.md`](./artigo.md).

> **Ressalva de rigor (diferença implementação × teoria).** A cláusula (ii) é implementada apenas **parcialmente**. O teste da razão em `simplex.py` (linhas 145–150) usa desempate estrito (`razao < menor_razao`), de modo que, entre razões empatadas, mantém a **primeira linha** encontrada — ou seja, o **menor índice de linha** $i$, e não a variável básica de menor índice `tableau.base[i]`. Como `base` deixa de ser ordenado após o primeiro pivô, esses dois critérios podem divergir. Estritamente, o teorema de finitude de Bland (1977) pressupõe a cláusula (ii) por **índice de variável**; com desempate por posição de linha, a garantia formal anticiclagem não está plenamente coberta pela fonte. Na prática, nenhuma ciclagem foi observada nos casos testados (Seção 3.5 e [`comparacao_simplex.md`](./comparacao_simplex.md)), e o número de pivôs manteve-se baixo (Seção 2.6); ainda assim, **para uma garantia teórica completa**, recomenda-se ajustar o desempate da saínte para o menor `tableau.base[i]` entre as razões mínimas. Esse ajuste é $O(m)$ e não altera a complexidade.

### 3.5 Corretude parcial: condição de otimalidade

> **Lema (otimalidade — Simplex clássico).** Para qualquer ponto factível $y$ do PL, vale a identidade
> $$ z(y) \;=\; z(y^*) \;+\; \sum_{j \in \mathcal{N}} (c_j - z_j)\, y_j, $$
> onde $y^*$ é a SBF corrente, $\mathcal{N}$ é o conjunto de variáveis não-básicas e $c_j - z_j$ é o custo reduzido (exatamente o que `calcular_cj_zj` computa, pois $z_j = \sum_i \texttt{contributions}[i]\cdot \texttt{col}_j[i]$). Essa identidade e o critério dela derivado ($c_j - z_j \le 0\ \forall j \Rightarrow$ ótimo) constituem o resultado central do Simplex original, cuja prova formal — junto ao teorema da dualidade — está em Dantzig (1963, cap. 6, "Proof of the Simplex Algorithm and the Duality Theorem", p. 120–146).

*Dedução.* Particionando $y = (y_B, y_N)$, de $[A\mid I]y = b$ vem $y_B = B^{-1}b - B^{-1}N\,y_N$. Substituindo na função objetivo:

$$
z(y) = \hat c_B^\top y_B + \hat c_N^\top y_N = \hat c_B^\top B^{-1}b + \sum_{j\in\mathcal{N}} \big(\hat c_j - \hat c_B^\top B^{-1}[A\mid I]_j\big) y_j = z(y^*) + \sum_{j\in\mathcal{N}} (c_j - z_j)\,y_j. \qquad\square
$$

O laço só encerra quando **todos** os custos reduzidos são $\le 0$ (`todos_nao_positivos`). Nesse momento, para qualquer $y$ factível: cada $y_j \ge 0$ e cada $(c_j - z_j) \le 0$, logo $\sum_{j\in\mathcal{N}}(c_j - z_j)y_j \le 0$ e portanto

$$
z(y) \le z(y^*) \quad \text{para todo } y \text{ factível.}
$$

Ou seja, $y^*$ é um **maximizador global** do PL. O vetor retornado `x` é a projeção de $y^*$ sobre as variáveis de decisão (linhas 191–194 de `simplex.py`), e $z$ é recomputado como $c^\top x$. Combinando com a terminação (Seção 3.4): **o algoritmo termina e retorna a solução ótima**. $\blacksquare$

A prova é coerente com a validação empírica de [`comparacao_simplex.md`](./comparacao_simplex.md): nos quatro casos testados (incluindo o caso real com 7 clusters), o valor ótimo $z$ coincidiu com o do solver CBC/PuLP dentro de $10^{-6}$, com diferença residual $\approx 1{,}5\times 10^{-8}$ atribuível apenas a aritmética de ponto flutuante.

### 3.6 Casos especiais

**Problema ilimitado.** Se em alguma iteração existe entrante $j_e$ com custo reduzido $> 0$ mas $\texttt{col}[i] \le 0$ para toda linha $i$, então a semirreta $y(\theta) = y^* + \theta d$ (que aumenta $y_{j_e}$ em $\theta$ e ajusta as básicas em $-\theta\,\texttt{col}[i] \ge 0$) é factível para todo $\theta \ge 0$, e $z(y(\theta)) = z(y^*) + \theta\,(c_{j_e} - z_{j_e}) \to +\infty$. O PL é genuinamente ilimitado e a implementação corretamente lança `ValueError("O problema é ilimitado.")`. $\checkmark$

**Múltiplas soluções.** Ao atingir a otimalidade, se alguma variável **não-básica** $j$ tem custo reduzido exatamente $0$, então mover-se nessa direção mantém $z$ constante (o termo correspondente no Lema da Seção 3.5 é nulo), gerando um ótimo alternativo. A implementação sinaliza isso com o status `multiplas_solucoes`. A sinalização é **correta** quanto à *existência* de uma direção ótima alternativa, mas há duas diferenças em relação à teoria, discutidas na Seção 5: (i) ela não enumera nem parametriza a face ótima — retorna apenas um vértice e o status; (ii) usa comparação exata `== 0.0`, numericamente frágil.

---

## 4. Origem nas fontes e impacto das adaptações

A tabela a seguir mapeia cada componente do resolvedor à sua origem e ao impacto das adaptações do grupo. As colunas de impacto respondem diretamente ao requisito de explicar "o que vem do Simplex original e como as adaptações afetam complexidade e corretude".

| Componente | Origem | Adaptação do grupo | Impacto em complexidade | Impacto em corretude |
| ---------- | ------ | ------------------ | ----------------------- | -------------------- |
| Tableau, folgas, teste da razão, condição de otimalidade, dualidade | Simplex clássico — Dantzig (1951; 1963, cap. 5–6, p. 94–146) | tableau **denso** explícito | $\Theta(mN)$ por pivô e $\Theta(mN)$ de memória | nenhum (mesma álgebra) |
| Regra de entrada na base | **Bland (1977)** | cláusula da entrante integral; desempate da saínte por linha | pior caso continua exponencial; pode exigir mais pivôs que Dantzig | **garante terminação** sob degeneração (com ressalva da Seção 3.4) |
| Início na origem sem Fase I | simplificação da forma canônica | sem variáveis artificiais | elimina um PL auxiliar (fator constante) | correto **somente se** $b \ge 0$ |
| Status `multiplas_solucoes` | extensão própria | adicionada | $+O(N)$ por término (desprezível) | correta na existência; frágil por `== 0.0` |
| Cópia defensiva de `b` | correção de bug (via PuLP) | `list(problema.b)` | $+\Theta(m)$ (desprezível) | **necessária** para chamadas repetidas |
| Pós-otimização (arredondamento) | regra de negócio do parceiro | fora do núcleo do Simplex | $O(K)$ após o PL | move a solução para fora do ótimo contínuo de forma limitada |

### 4.1 Início na origem sem Fase I — a adaptação de maior impacto

A formulação original resolve PLs gerais via **duas fases** (Fase I encontra uma SBF inicial com variáveis artificiais; Fase II otimiza), conforme Dantzig (1963, cap. 5, p. 94–119). O grupo eliminou a Fase I e inicia diretamente na origem com a base de folgas, aproveitando que o PL deste projeto já está na forma canônica com $b \ge 0$.

- **Complexidade:** remove-se a resolução de um PL auxiliar — economia de um **fator constante** (na prática, quase metade do trabalho de uma execução em duas fases). Não há mudança assintótica: o custo é governado pela Fase II.
- **Corretude:** a adaptação é correta **se e somente se** $b \ge 0$ (Seção 3.1). Esta é uma **pré-condição não verificada em tempo de execução**: se alguma instância tivesse $b_i < 0$, a base da indução (P2) falharia silenciosamente (`values[i] < 0`) e o algoritmo retornaria um resultado infactível **sem emitir erro**. Para o PL do projeto isso nunca ocorre, pois R1/R2/R3 garantem $b \ge 0$ por construção. **Recomendação:** documentar a pré-condição e, idealmente, adicionar uma checagem `assert all(bi >= 0 for bi in b)` para tornar a falha explícita caso o modelo evolua e passe a admitir restrições $\ge$ ou lados direitos negativos.

### 4.2 Regra de Bland

Adotada de Bland (1977). É o que sustenta a **terminação** (Seção 3.4) num PL estruturalmente degenerado (dois tetos por cluster). A cláusula da variável entrante é implementada integralmente; a do desempate da saínte é parcial (por posição de linha, não por índice de variável — ver ressalva na Seção 3.4), o que recomenda um pequeno ajuste para garantia teórica plena. O custo é não ter a melhor velocidade de pivoteamento possível — a regra de Bland costuma exigir mais pivôs que a de Dantzig e seu pior caso permanece exponencial — mas, dada a estrutura quase-separável do problema, o número de pivôs medido é pequeno ($p = O(K)$, Seção 2.6), de modo que o trade-off robustez × velocidade é favorável aqui.

### 4.3 Detecção de múltiplas soluções — diferença implementação × teoria

É uma extensão além do Simplex clássico. Em relação à teoria há duas consequências práticas:

1. **Não enumera a face ótima.** O status apenas avisa que existe outra direção ótima; o produto de negócio, se precisar escolher entre limites equivalentes, teria de explorar a face ótima manualmente (p.ex. pivoteando na variável de custo reduzido nulo). Isso é uma limitação de escopo, não um erro.
2. **Comparação exata `== 0.0`.** Por usar igualdade exata em ponto flutuante, um ótimo alternativo genuíno com custo reduzido $\approx 10^{-12}$ (resíduo numérico) pode **não** ser sinalizado, e, simetricamente, um resíduo de arredondamento poderia ser lido como zero. Como a detecção é apenas informativa (não altera $x$ nem $z$), o impacto sobre a otimalidade é nulo; mas, para robustez, o ideal seria um teste por tolerância (`abs(cj_zj) <= eps`), consistente com a tolerância de $10^{-6}$ já usada na comparação com o PuLP.

### 4.4 Tableau denso × Simplex revisado

A escolha do tableau denso (manter e atualizar todas as colunas) é deliberada e alinhada à justificativa do [`artigo.md`](./artigo.md): **transparência e auditabilidade** das regras de entrada/saída e do pivoteamento. A consequência é custo $\Theta(mN)$ por pivô e memória $\Theta(mN)$. Um **Simplex revisado** (mantendo apenas $B^{-1}$ em forma-produto) reduziria o trabalho por iteração e o consumo de memória em problemas esparsos e grandes. Para a escala atual ($K = 7$) e mesmo para a entrega final ($K \ge 100$, $m \approx 201$), o tableau denso é perfeitamente viável; a migração para Simplex revisado (ou para um solver consolidado como `scipy.optimize.linprog` / PuLP) só se justificaria em escalas substancialmente maiores. **A corretude é idêntica** — a diferença é puramente de eficiência, pois a álgebra subjacente é a mesma.

### 4.5 Cópia defensiva de `b` (correção de aliasing)

Conforme documentado em [`comparacao_simplex.md`](./comparacao_simplex.md), a comparação cruzada com o PuLP revelou um bug de **aliasing**: sem `valores_iniciais = list(problema.b)`, a coluna `Value` compartilhava memória com `problema.b`, e cada pivô mutava o vetor `b` original. O sintoma só aparecia ao reusar o mesmo objeto `Problema` em chamadas sucessivas. A correção custa $\Theta(m)$ (desprezível) e é **essencial para a corretude sob invocações repetidas** — exatamente o cenário de produção, em que o backend chama o resolvedor a cada requisição. Em termos do invariante: a cópia garante que (P4) se refira ao sistema **original** $[A\mid I]y = b$, e não a um $b$ corrompido por execuções anteriores.

### 4.6 Pós-otimização (fora do núcleo)

O arredondamento dos limites (zerar abaixo de R\$200, arredondar para múltiplo de R\$50) ocorre **depois** do Simplex (`exibir_resultado` / `executar_pipeline`) e **não afeta** a prova de otimalidade do PL contínuo. É uma discretização de negócio que pode deslocar a solução do ótimo contínuo por uma quantia limitada (no máximo R\$50 por cluster), aceitável operacionalmente. Vale registrar que essa etapa torna a solução **entregue** uma aproximação do ótimo do PL, não o ótimo exato — uma diferença entre o "ótimo matemático" e o "limite ofertado".

---

## 5. Síntese

A implementação do grupo é o **Simplex clássico de Dantzig com a regra anticiclagem de Bland (1977)**, operando sobre um tableau denso na forma canônica de maximização. A análise estabelece:

**Complexidade.** O custo por iteração é $\Theta\big(m(n+m)\big)$ e o custo total de uma instância resolvida em $p$ pivôs é $\Theta\big((p+1)\,m(n+m)\big)$. O pior caso é exponencial ($p \le \binom{n+m}{m}-1$), o melhor caso é $\Theta\big(m(n+m)\big)$ (origem ótima, $p=0$), e o piso universal é $\Omega\big(m(n+m)\big)$. Para o PL do parceiro ($n=K$, $m=2K+1$), isso é $\Theta(K^2)$ por pivô e, com os $p=O(K)$ pivôs observados empiricamente, $O(K^3)$ na prática — confirmando viabilidade tanto para $K=7$ quanto para a meta de $K\ge100$.

**Corretude.** Provou-se, por indução sobre o invariante do laço, que o tableau mantém sempre uma SBF (corretude parcial); a regra de entrada de Bland garante a terminação (com a ressalva da Seção 3.4 sobre o desempate da saínte, que recomenda um ajuste $O(m)$ para garantia teórica plena); e a condição de parada (todos os custos reduzidos $\le 0$) implica otimalidade global pelo Lema da Seção 3.5. Os casos ilimitado e de múltiplas soluções são tratados corretamente pela implementação (Seções 3.6), preservando a corretude global.

---

# Parte II — Implementação com PuLP

## 1. Notação

Considere:

- $n$: número de variáveis de decisão;
- $m$: número de restrições;
- $A \in \mathbb{R}^{m \times n}$: matriz de coeficientes;
- $c \in \mathbb{R}^{n}$: vetor da função objetivo;
- $b \in \mathbb{R}^{m}$: vetor dos lados direitos das restrições.

O algoritmo implementado em `simplex_pulp.py` executa as seguintes etapas:

1. Criação do modelo de programação linear;
2. Criação das variáveis de decisão;
3. Construção da função objetivo;
4. Construção das restrições;
5. Chamada do solver externo;
6. Extração da solução ótima.

## 2. Análise de Complexidade

### 2.1 Construção das Variáveis

As variáveis são criadas pelo trecho:

```python
x_vars = [
    pulp.LpVariable(f"x_{j}", lowBound=0.0, cat=pulp.LpContinuous)
    for j in range(n)
]
```

São criadas exatamente $n$ variáveis.

$$
T_1(n)=\Theta(n)
$$

### 2.2 Construção da Função Objetivo

A função objetivo é montada por:

```python
modelo += pulp.lpSum(
    problema.c[j] * x_vars[j]
    for j in range(n)
)
```

O laço percorre todas as variáveis.

$$
T_2(n)=\Theta(n)
$$

### 2.3 Construção das Restrições

As restrições são adicionadas por:

```python
for i in range(m):
    modelo += (
        pulp.lpSum(
            problema.A[i][j] * x_vars[j]
            for j in range(n)
        ) <= problema.b[i]
    )
```

Para cada uma das $m$ restrições são percorridas as $n$ variáveis.

$$
T_3(n,m)=\Theta(mn)
$$

Para o PL específico do projeto, $n = K$ e $m = 2K + 1$, de modo que a construção do modelo é:

$$
T_3(K)=\Theta(K\cdot(2K+1)) = \Theta(K^2).
$$

### 2.4 Resolução do Modelo

O trecho:

```python
modelo.solve(solver)
```

transfere o problema para o solver externo.

O custo desta etapa depende do solver que for selecionado em tempo de execução. O código tenta, na ordem:

- CBC (`PULP_CBC_CMD`);
- HiGHS via `highspy` (`HiGHS`);
- HiGHS externo (`HiGHS_CMD`);
- GLPK externo (`GLPK_CMD`).

Para o problema contínuo modelado em `simplex_pulp.py`, o solver não aciona o Branch-and-Bound, pois não há variáveis inteiras. O CBC e o GLPK resolvem o PL contínuo por métodos baseados em Simplex/pivoteamento; o HiGHS pode usar algoritmos de pontos interiores ou simplex, e por isso tem regimes de pior caso diferentes.

Assim, não é possível determinar uma única complexidade exata apenas analisando o código Python: o custo real depende do solver disponível no ambiente.

Denotando por $T_{solver}(n,m)$ o custo do solver selecionado:

$$
T_4(n,m)=T_{solver}(n,m)
$$

### 2.5 Extração da Solução

Após a resolução, os valores são copiados para listas Python:

```python
x = [float(pulp.value(v)) for v in x_vars]
```

O valor da função objetivo também é extraído:

```python
z = float(pulp.value(modelo.objective))
```

Além disso, o status do solver é lido e mapeado para o vocabulário do projeto:

- `Optimal` → `otimo`;
- `Unbounded` → `ilimitado`;
- `Infeasible` → `inviavel`;
- outros status → `erro`.

O custo dessa extração é dominado pela leitura das $n$ variáveis e pela avaliação do objetivo.

$$
T_5(n)=\Theta(n)
$$

### 2.6 Melhor Caso

O melhor caso ocorre quando:

- a construção do modelo é realizada normalmente;
- o solver encontra rapidamente uma solução ótima.

Como a etapa de construção das restrições precisa sempre percorrer toda a matriz $A$, existe um limite inferior:

$$
\Omega(mn)
$$

### 2.7 Pior Caso

O pior caso depende do solver selecionado para o ambiente.

- Se o solver usado for CBC ou GLPK, o modelo contínuo é resolvido por métodos baseados em Simplex/pivoteamento, cujo pior caso teórico pode ser exponencial em $n+m$.
- Se o solver usado for HiGHS, ele pode empregar algoritmos de pontos interiores em vez de Simplex puro, o que muda o regime teórico do pior caso para uma classe polinomial de métodos de programação linear.

Para este projeto, o código não escolhe um único regime: ele tenta CBC primeiro e usa o primeiro solver disponível entre CBC, HiGHS, HiGHS_CMD e GLPK_CMD.

Branch-and-Bound só seria relevante se o modelo contivesse variáveis inteiras, o que não ocorre aqui. Portanto, a afirmação de que o solver externo faz Branch-and-Bound aplica-se apenas a casos inteiros, não à formulação contínua usada em `simplex_pulp.py`.

Assim:

$$
T_{solver}(n,m)
$$

onde o pior caso pode ser exponencial para solvers baseados em Simplex, enquanto o uso de HiGHS pode levar a um regime teórico polinomial.

### 2.8 Regimes de Solver

| Solver | Regime teórico principal | Observação |
| ------ | ------------------------ | ---------- |
| CBC | Simplex / pivoteamento | para LP contínuo; não aciona Branch-and-Bound aqui |
| GLPK | Simplex / pivoteamento | para LP contínuo; não aciona Branch-and-Bound aqui |
| HiGHS | pontos interiores / simplex | fallback com potencial regime polinomial |

Branch-and-Bound só se aplicaria se o modelo tivesse variáveis inteiras; em `simplex_pulp.py` o modelo é contínuo.

### 2.9 Complexidade Total

A construção do modelo possui custo:

$$
\Theta(mn)
$$

A resolução é dominada pelo solver:

$$
T(n,m)=
\Theta(mn)+
T_{solver}(n,m)
$$

Portanto:

$$
\boxed{
T(n,m)=\Theta(mn + T_{solver}(n,m))
}
$$

### 2.9 Quadro-resumo de Complexidade

| Etapa | Complexidade | Nota |
| ------ | ------------ | ---- |
| Construção do modelo | $\Theta(mn)$ | $\Theta(K^2)$ para $n=K$, $m=2K+1$ |
| Resolução pelo solver | $T_{solver}(n,m)$ | depende do solver selecionado no ambiente |
| Extração de $x$, $z$ e status | $\Theta(n)$ | custo linear no número de variáveis |

### 2.10 Complexidade de Espaço

O modelo armazena:

- $n$ variáveis;
- $m$ restrições;
- matriz $A$ com $m \times n$ coeficientes.

Logo:

$$
\boxed{
S(n,m)=\Theta(mn)
}
$$

## 3. Corretude

A corretude da implementação com PuLP será demonstrada em duas etapas:

1. Corretude da construção do modelo de Programação Linear;
2. Corretude da solução retornada pelo solver.

Como o módulo `simplex_pulp.py` não implementa diretamente um algoritmo de otimização, mas sim constrói um modelo matemático e o envia para um solver externo, o objetivo da prova é demonstrar que o modelo construído é exatamente equivalente ao problema original.

### 3.1 Pré-condição

Antes da execução do algoritmo, assume-se que a instância do problema satisfaz as seguintes condições:

- A matriz $A$ possui $m$ linhas e $n$ colunas;
- O vetor $b$ possui $m$ componentes;
- O vetor $c$ possui $n$ componentes;
- Todas as restrições estão definidas na forma

$$
Ax \le b
$$

- Todas as variáveis possuem limite inferior igual a zero.

Essas condições garantem que o problema de programação linear está bem definido.

### 3.2 Invariante do Laço Principal

O principal laço da implementação é responsável pela inserção das restrições no modelo:

```python
for i in range(m):
    modelo += (
        pulp.lpSum(
            problema.A[i][j] * x_vars[j]
            for j in range(n)
        ) <= problema.b[i]
    )
```

Esse é o laço principal a ser analisado neste módulo porque a otimização em si é delegada ao solver externo.

#### Invariante P

Após a conclusão da iteração $k$ do laço, o modelo PuLP representa exatamente o problema composto por:

- todas as variáveis originais;
- a função objetivo original;
- as primeiras $k$ restrições do problema original.

Formalmente:

$$
Modelo_k =
\{
FO,\;
R_1,\;
R_2,\;
\ldots,\;
R_k
\}
$$

onde:

- $FO$ representa a função objetivo;
- $R_i$ representa a restrição $i$ do problema original.

Para facilitar a demonstração, dividimos o invariante nas seguintes propriedades.

#### P1

Todas as variáveis do problema original já foram criadas no modelo.

#### P2

A função objetivo do modelo é exatamente a função objetivo do problema original.

#### P3

As primeiras $k$ restrições do problema original foram adicionadas corretamente ao modelo.

#### P4

Nenhuma restrição previamente inserida foi removida ou modificada.


### 3.3 Prova do Invariante por Indução

#### Caso Base

Antes da primeira iteração ($k = 0$):

- todas as variáveis já foram criadas;
- a função objetivo já foi construída;
- nenhuma restrição foi adicionada.

Logo:

- P1 é verdadeira;
- P2 é verdadeira;
- P3 é verdadeira, pois existem zero restrições inseridas;
- P4 é verdadeira, pois nenhuma restrição existe ainda.

Portanto, o invariante vale antes do início do laço.


#### Hipótese de Indução

Suponha que após a iteração $k$ o invariante seja verdadeiro.

Ou seja:

- todas as variáveis continuam presentes;
- a função objetivo permanece correta;
- as primeiras $k$ restrições foram adicionadas corretamente;
- nenhuma delas foi alterada.


#### Passo Indutivo

Na iteração $k+1$, o algoritmo executa:

```python
modelo += (
    pulp.lpSum(
        problema.A[k][j] * x_vars[j]
        for j in range(n)
    ) <= problema.b[k]
)
```

Essa instrução adiciona ao modelo exatamente a restrição $R_{k+1}$.

Além disso:

- nenhuma variável é removida;
- a função objetivo não é alterada;
- nenhuma restrição previamente inserida é modificada;
- apenas uma nova restrição é acrescentada.

Portanto:

- P1 continua verdadeira;
- P2 continua verdadeira;
- P3 passa a valer para as primeiras $k+1$ restrições;
- P4 continua verdadeira.

Logo, o invariante permanece válido após a iteração $k+1$.


#### Conclusão da Indução

Como:

1. o invariante é verdadeiro no caso base;
2. sua validade após uma iteração implica sua validade na próxima;

segue pelo Princípio da Indução Matemática que o invariante é verdadeiro para todas as iterações do laço.

Ao término da última iteração, quando $k = m$, o modelo contém:

- todas as variáveis do problema;
- a função objetivo original;
- todas as restrições do problema original.

Portanto, o modelo construído é matematicamente equivalente ao problema de programação linear fornecido como entrada.

### 3.4 Terminação

O laço principal possui a forma:

```python
for i in range(m):
```

onde $m$ é o número de restrições do problema.

Como:

- $m$ é finito;
- a variável de controle aumenta de uma unidade a cada iteração;
- nenhuma instrução altera o valor de $m$;

o número de iterações é exatamente igual a $m$.

Assim, o laço termina após um número finito de passos.

Além disso, as demais operações da implementação consistem apenas em construções de listas, criação de objetos e uma chamada ao solver.

Portanto, a construção do modelo sempre termina.

### 3.5 Corretude Parcial

Pela demonstração do invariante, ao final do laço o modelo PuLP é exatamente equivalente ao problema original.

Essa análise assume explicitamente que o solver externo resolve corretamente o problema contínuo de programação linear. Essa é a mesma premissa de corretude do Simplex e da dualidade em Dantzig (1963) para LP contínuo.

Consequentemente:

- toda solução viável do modelo corresponde a uma solução viável do problema original;
- toda solução ótima do modelo corresponde a uma solução ótima do problema original.

Logo, caso o solver retorne uma solução ótima, essa solução é correta para o problema originalmente recebido pela implementação.

### 3.6 Corretude Total

A corretude total exige:

1. Corretude parcial;
2. Terminação.

A corretude parcial foi demonstrada na Seção 3.5.

A terminação foi demonstrada na Seção 3.4.

Portanto, conclui-se que:

- o modelo construído representa corretamente o problema original;
- a construção do modelo sempre termina;
- a solução retornada corresponde à solução do problema modelado.

Assim, a implementação com PuLP é correta.

$$
\boxed{\text{A implementação é correta}}
$$

---

# Parte III — Conclusão: comparação e reflexões

As Partes I e II analisaram duas implementações que resolvem **o mesmo** problema de PL do projeto. Esta parte sintetiza as diferenças de complexidade, contrasta as duas estratégias de prova de corretude e discute os *trade-offs* de engenharia entre **implementar o algoritmo do zero** e **delegar a uma biblioteca**.

## 1. Complexidade — quadro comparativo

Sejam $n$ o número de variáveis de decisão, $m$ o número de restrições e, no PL do parceiro, $n = K$ e $m = 2K+1$ (logo $m(n+m) = \Theta(K^2)$). No Simplex do grupo, $N = n+m$ é o número total de variáveis (decisão + folga) e $p$ é o número de pivôs.

| Aspecto | Simplex (grupo) | PuLP (biblioteca) |
| ------- | --------------- | ----------------- |
| Construção / estrutura de dados | *build* do tableau $\Theta(mN) = \Theta(K^2)$ | *build* do modelo $\Theta(mn) = \Theta(K^2)$ |
| Custo da otimização | $(p+1)\,\Theta(mN)$ — número de pivôs $p$ **explícito** | $T_{solver}(n,m)$ — **caixa-preta** do solver |
| Melhor caso | $\Theta(K^2)$ (origem já ótima, $p=0$) | $\Omega(mn) = \Omega(K^2)$ (sempre percorre $A$) |
| Pior caso | exponencial, $p \le \binom{n+m}{m}-1$ | depende do solver: exponencial (CBC/GLPK, simplex) ou polinomial (HiGHS, pontos interiores) |
| Caso prático | $O(K^3)$ com $p = O(K)$ medido | dominado pelo solver, tipicamente eficiente |
| Espaço | $\Theta(mN) = \Theta(K^2)$ | $\Theta(mn) = \Theta(K^2)$ |

Ambas compartilham o **piso $\Theta(K^2)$** de construção e memória. A diferença essencial está em **onde mora o custo da otimização**: no Simplex do grupo ele é explícito e contável (o número de pivôs $p$), enquanto no PuLP fica encapsulado em $T_{solver}$, fora do código Python.

Um ponto que merece reflexão: o **pior caso teórico do PuLP pode ser melhor que o do nosso Simplex**. Se o ambiente usar HiGHS com pontos interiores, o pior caso é polinomial, ao passo que o nosso Simplex com regra de Bland permanece exponencial no pior caso. Na prática, porém, a estrutura quase-separável do problema (restrições-caixa R2/R3 acopladas apenas pela restrição agregada R1) mantém $p$ pequeno ($p = O(K)$), e o nosso Simplex roda em $O(K^3)$ — perfeitamente viável tanto para $K=7$ quanto para a meta de $K \ge 100$.

## 2. Corretude — duas estratégias de prova diferentes

Embora ambas as provas usem **indução sobre o invariante do laço principal**, elas provam coisas distintas, porque o "laço principal" de cada implementação é diferente:

- **Simplex do grupo.** O invariante é sobre o estado do *algoritmo de otimização*: a cada iteração do `while`, o tableau mantém uma **solução básica factível (SBF)**. A indução prova que cada pivô preserva a factibilidade (corretude parcial); a regra de Bland garante a terminação; e a condição de parada (todos os custos reduzidos $\le 0$) implica otimalidade global. Ou seja, **prova-se que o algoritmo de fato encontra o ótimo**.

- **PuLP.** O invariante é sobre o laço de *construção do modelo*: após $k$ iterações, o modelo contém exatamente as $k$ primeiras restrições. A indução prova que o modelo construído é **equivalente** ao problema original. A otimalidade da solução é **delegada ao solver** e assumida como premissa (corretude do Simplex e da dualidade, Dantzig 1963; solvers consolidados CBC/HiGHS/GLPK).

Em uma frase: **nós provamos que o nosso algoritmo resolve o problema; no PuLP, provamos que modelamos o problema corretamente e confiamos num solver já provado.** Essa é a diferença inerente entre *implementar* e *delegar* — e é a razão de os dois invariantes (e os dois laços principais) serem distintos, ainda que a técnica de prova seja a mesma.

## 3. Trade-offs e reflexões de engenharia

**Transparência × robustez.** O Simplex próprio é *white-box*: cada regra de entrada/saída e cada pivô é inspecionável, o que importa para explicar ao parceiro **como** o limite de cada cluster foi decidido — requisito relevante num contexto de crédito. O PuLP é *black-box* no núcleo, mas é maduro, testado em produção há anos e trata casos de borda (degeneração, mau condicionamento) que a nossa implementação cobre apenas parcialmente — por exemplo, o desempate da variável saínte na regra de Bland está incompleto no nosso código (Parte I, Seção 3.4).

**Dependência externa.** O nosso Simplex não exige solver externo: não precisa de CBC/GLPK instalado nem sofre com o bug do CBC quando o caminho do Windows tem espaços — bug que a implementação PuLP teve de contornar com diretório temporário e cadeia de *fallback*. O PuLP carrega essa fragilidade de ambiente, mitigada (mas não eliminada) pelo *fallback* CBC -> HiGHS -> HiGHS_CMD -> GLPK_CMD.

**Papéis complementares.** A forma como o grupo usa as duas implementações é a mais sensata: o **Simplex próprio como motor de produção** (transparente, sem dependência) e o **PuLP como oráculo de validação** (*golden test*). A concordância dentro de $10^{-6}$ dá confiança empírica de que a prova de corretude da Parte I se reflete na prática.

**Escala.** Para a entrega final ($K \ge 100$, $m \approx 201$), ambas são viáveis — o custo por pivô fica na casa de dezenas de milhares de operações. Se o problema crescesse muito ou ficasse numericamente mal condicionado, o PuLP (ou um Simplex revisado mantendo apenas $B^{-1}$) seria preferível por robustez numérica.

## 4. Síntese final

Resolver o mesmo PL de dois jeitos — implementando e delegando — mostra os dois lados da moeda. Implementar do zero **força entender** o invariante, a terminação e a otimalidade (o *porquê* de o algoritmo funcionar). Usar uma biblioteca **desloca o ônus** da corretude para duas tarefas diferentes: modelar fielmente o problema e confiar num solver já provado. A validação cruzada amarra os dois: a teoria (as provas) e a prática (a concordância numérica) convergem para a mesma solução.

Para este projeto, a recomendação é manter o **Simplex próprio como motor**, pela transparência exigida no contexto de crédito do Banco Pan, com o **PuLP como rede de segurança** de validação — exatamente o arranjo adotado pelo grupo.

---

# Referências

As referências abaixo consolidam as fontes das Partes I e II.

DANTZIG, George B. *Linear Programming and Extensions*. Princeton: Princeton University Press, 1963.

BLAND, Robert G. New finite pivoting rules for the simplex method. *Mathematics of Operations Research*, v. 2, n. 2, p. 103-107, 1977.

KLEE, Victor; MINTY, George J. How good is the simplex algorithm? In: SHISHA, O. (ed.). *Inequalities III*. New York: Academic Press, 1972. p. 159-175.

BORGWARDT, Karl Heinz. *The Simplex Method: A Probabilistic Analysis*. Berlin: Springer-Verlag, 1987.

SPIELMAN, Daniel A.; TENG, Shang-Hua. Smoothed analysis of algorithms: why the simplex algorithm usually takes polynomial time. *Journal of the ACM*, v. 51, n. 3, p. 385-463, 2004.

HUANGFU, Qi; HALL, Julian A. J. Parallelizing the dual revised simplex method. *Mathematical Programming Computation*, v. 10, n. 1, p. 119-142, 2018.

BAZARAA, Mokhtar S.; JARVIS, John J.; SHERALI, Hanif D. *Linear Programming and Network Flows*. 4. ed. Hoboken: John Wiley & Sons, 2010.

COIN-OR FOUNDATION. *PuLP: a Linear Programming Toolkit for Python*. Disponível em: https://coin-or.github.io/pulp/. Acesso em: 09 jun. 2026.
