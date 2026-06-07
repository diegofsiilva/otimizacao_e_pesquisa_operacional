# Complexidade e Corretude do Algoritmo Simplex

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

