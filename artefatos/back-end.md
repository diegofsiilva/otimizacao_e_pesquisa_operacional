# Otimizador e Back-end

## Contextualização

O Banco Pan oferece cartões de crédito pré-aprovados a clientes correntistas. A decisão de qual limite de crédito oferecer a cada cliente é hoje tomada com base em tabelas fixas, que não consideram a heterogeneidade entre perfis e não controlam o risco agregado da carteira.

O objetivo deste projeto é substituir essa regra empírica por uma decisão matemática: encontrar, para cada grupo de clientes com perfil semelhante, o limite que **maximize o retorno líquido esperado do banco**, definido como a receita de interchange menos a perda esperada por inadimplência, respeitando restrições de risco e capacidade de pagamento definidas pelo parceiro.

Para isso, o problema foi formulado como um **Problema de Programação Linear (PL)**, onde as variáveis de decisão são os limites de crédito a serem atribuídos a cada grupo de clientes. A solução desse PL é encontrada por meio do **algoritmo Simplex**, implementado neste artefato.

---

## O problema de programação linear

### Variáveis de decisão

Os mais de um milhão de clientes elegíveis são agrupados em $K$ clusters com perfis semelhantes. Para cada cluster $k$, a variável de decisão é:

$$L_k \geq 0 \quad \text{(limite de crédito a ser ofertado ao cluster } k\text{)}$$

### Função objetivo

O banco busca maximizar o retorno líquido total esperado da carteira:

$$\max \sum_{k=1}^{K} n_k \cdot \pi_k \cdot (\bar{u} \cdot t \cdot T - PD_k \cdot \text{LGD}) \cdot L_k$$

O coeficiente de cada cluster, $c_k = n_k \cdot \pi_k \cdot (\bar{u} \cdot t \cdot T - PD_k \cdot \text{LGD})$, representa o retorno líquido unitário esperado por real alocado ao cluster $k$. Clusters com $c_k > 0$ são rentáveis; clusters com $c_k \leq 0$ destroem valor a cada real adicional de limite e recebem $L_k = 0$ como solução natural do modelo.

Os parâmetros utilizados são:

| Parâmetro    | Descrição                                                               | Valor padrão      |
| ------------ | ----------------------------------------------------------------------- | ----------------- |
| $n_k$        | Número de clientes no cluster $k$                                       | calculado da base |
| $\pi_k$      | Propensão média de contratação do cluster $k$                           | calculado da base |
| $\bar{u}$    | Fração esperada de utilização do limite pelo cliente                    | 0,75              |
| $t$          | Taxa de interchange recebida pelo banco sobre o volume transacionado    | 1,75%             |
| $T$          | Horizonte de uso do limite em meses, definido pelo parceiro             | 22                |
| $PD_k$       | Probabilidade de inadimplência calibrada média do cluster $k$           | calculado da base |
| $\text{LGD}$ | Fração do saldo exposto perdida em caso de default (Loss Given Default) | 0,80              |

### Restrições

**R1 - Teto de inadimplência financeira:** a inadimplência financeira ponderada da carteira otimizada não pode superar a inadimplência atual da carteira. Isso garante que o modelo não piore o risco do banco em relação ao cenário atual:

$$\sum_{k=1}^{K} n_k \cdot (PD_k - \overline{PD}_{fin}^{atual}) \cdot L_k \leq 0$$

onde $\overline{PD}_{fin}^{atual}$ é calculado como a média de `pd_calibrada` dos clientes elegíveis da base.

**R2 - Capacidade de pagamento com alavancagem diferenciada:** o limite de cada cluster é restrito pela capacidade de pagamento de seus membros, multiplicada por um fator de alavancagem $m_k$ que varia de 0,3 a 1,8 conforme o score de crédito médio do cluster. Clusters de menor risco recebem $m_k$ próximo de 1,8; clusters de maior risco recebem $m_k$ próximo de 0,3:

$$L_k \leq m_k \cdot CP_k, \quad \forall k$$

onde $CP_k$ é o percentil 5 da capacidade de pagamento dos clientes do cluster $k$.

**R3 - Teto máximo de limite:** nenhum cluster pode receber um limite acima do teto absoluto definido pelo parceiro:

$$L_k \leq L^{max}, \quad \forall k$$

---

## O algoritmo Simplex

### Ideia central

O Simplex parte de uma propriedade fundamental da programação linear: a solução ótima de um problema linear sempre se encontra em um **vértice da região viável**. A região viável é o conjunto de todos os pontos que satisfazem simultaneamente todas as restrições do problema.

O algoritmo navega pelos vértices da região viável da seguinte forma:

1. Começa em um vértice inicial (a origem, onde todos os limites $L_k = 0$).
2. A cada iteração, avalia se existe algum vértice vizinho com retorno maior.
3. Se existir, salta para esse vértice.
4. Repete até que nenhum vértice vizinho seja melhor que o atual - nesse momento, a solução ótima foi encontrada.

### Variáveis de folga

Para que o algoritmo possa trabalhar algebricamente, as restrições do tipo $\leq$ são convertidas em igualdades pela introdução de **variáveis de folga**. Por exemplo, a restrição R2 de um cluster $k$:

$$L_k \leq m_k \cdot CP_k$$

é reescrita como:

$$L_k + s_k = m_k \cdot CP_k, \quad s_k \geq 0$$

onde $s_k$ representa a folga remanescente - a diferença entre o limite máximo permitido e o limite efetivamente alocado. Na origem, todas as variáveis de decisão são zero e todas as folgas assumem seu valor máximo.

### A tabela do Simplex

O estado atual do algoritmo é mantido em uma tabela com a seguinte estrutura:

| Contribution | Base  | Value | $L_1$    | $L_2$    | ... | $s_1$ | $s_2$ | ... |
| ------------ | ----- | ----- | -------- | -------- | --- | ----- | ----- | --- |
| $c_{B_1}$    | $s_1$ | $b_1$ | $a_{11}$ | $a_{12}$ | ... | 1     | 0     | ... |
| $c_{B_2}$    | $s_2$ | $b_2$ | $a_{21}$ | $a_{22}$ | ... | 0     | 1     | ... |

Onde:

- **Contribution:** o coeficiente da variável da base dessa linha na função objetivo
- **Base:** a variável que está ativa nessa linha
- **Value:** o valor atual dessa variável
- As demais colunas: os coeficientes das variáveis nas equações de restrição

### Critério de entrada e saída da base

A cada iteração, o algoritmo calcula para cada variável $j$ o **ganho líquido** $c_j - z_j$, onde:

$$z_j = \sum_{i} c_{B_i} \cdot a_{ij}$$

representa o lucro destruído nas variáveis atualmente na base ao trazer uma unidade de $j$. Se $c_j - z_j > 0$, trazer $j$ para a base aumenta o retorno. O algoritmo utiliza a **Regra de Bland** para escolher qual variável entra: seleciona a de menor índice com $c_j - z_j > 0$, o que garante a terminação do algoritmo mesmo em casos de degeneração.

Para determinar qual variável sai, o algoritmo aplica o **teste da razão mínima**: divide o valor atual de cada variável da base pelo coeficiente correspondente da variável que entra, e seleciona a linha com menor razão positiva. Isso garante que nenhuma variável fique negativa após o pivotamento.

### Pivotamento

O pivotamento é a operação que reescreve o tableau para refletir a nova base. Consiste em dois passos:

1. **Normalizar a linha pivô:** dividir todos os valores da linha pelo elemento pivô, fazendo o coeficiente da variável que entra valer 1 nessa linha.
2. **Zerar a coluna pivô nas demais linhas:** para cada outra linha, subtrair um múltiplo da linha pivô de forma que o coeficiente da variável que entra vire 0.

### Tratamento de casos especiais

**Problema ilimitado:** quando nenhuma linha apresenta coeficiente positivo para a variável que entraria na base, o retorno pode crescer infinitamente sem violar nenhuma restrição. O algoritmo lança um erro informando que o problema é ilimitado.

**Múltiplas soluções:** quando o algoritmo atinge o ótimo e alguma variável fora da base ainda apresenta $c_j - z_j = 0$, existe outro ponto com o mesmo retorno ótimo. O algoritmo retorna uma das soluções e informa o status `multiplas_solucoes`.

**Degeneração:** quando duas ou mais linhas empatam no teste da razão mínima, uma variável entra na base com valor zero. Sem tratamento, isso pode causar ciclagem infinita. A Regra de Bland, já mencionada no critério de entrada, resolve esse problema.

---

## Estrutura da implementação do otimizador

Os arquivos do otimizador estão em `apps/algoritmo_simplex/`:

```
apps/algoritmo_simplex/
├── models.py          # estruturas de dados (Problema, Tableau)
├── simplex.py         # implementação do algoritmo Simplex
├── clustering.py      # clusterização CART e agregação dos parâmetros por cluster
├── main.py            # orquestração do pipeline completo
└── input/
    └── parametros.json    # parâmetros padrão do modelo
```

Os scripts de suporte estão em `scripts/`:

```
scripts/
├── calibrar_pd.py         # aplica gammas por decil sobre o parquet bruto
├── setup_tabela_gamma.py  # setup único: estima gammas das safras históricas
└── utils/
    └── convert_parquet_to_csv.py   # utilitário avulso de conversão
```

Os dados transitam pelas pastas:

```
data/
├── parquet/     # parquets brutos das safras (entrada do pipeline)
├── cache/       # parquets calibrados e clusterizados (gerados automaticamente)
└── csv/
    └── tabela_gamma_decil.csv   # artefato de modelo, versionado no repositório
```

### `models.py`

Define as estruturas de dados:

- `Problema`: agrupa os dados de entrada do LP - o vetor de coeficientes da função objetivo `c`, a matriz de coeficientes das restrições `A` e o vetor dos lados direitos `b`. Esses dados nunca mudam durante a execução.
- `Tableau`: representa o estado atual da tabela do Simplex - as colunas das variáveis de decisão e de folga, a base atual, as contributions e os valores. Esse estado é atualizado a cada pivotamento.

### `simplex.py`

Implementação pura do algoritmo Simplex, sem nenhuma dependência da lógica de negócio do projeto. Recebe um `Problema` e devolve a solução ótima, o valor da função objetivo e o status da solução.

### `clustering.py`

Agrupa os clientes elegíveis em $K$ clusters usando CART e calcula os parâmetros agregados necessários para o LP: $n_k$, $PD_k$, $\pi_k$, $CP_k$ e $m_k$. Lê o parquet calibrado de `data/cache/` e salva os resultados de volta em `data/cache/`. Detalhes na seção de Clusterização.

### `main.py`

Orquestra o pipeline completo e expõe duas interfaces:

- **CLI:** `python main.py <arquivo.parquet> <parametros.json>` - uso direto no terminal
- **`executar_pipeline(parquet_path, params)`:** função pública chamada pelo back-end, recebe um `Path` e um dicionário de parâmetros, retorna um dicionário estruturado com o resultado

O pipeline interno segue os passos:

1. Verificação de cache da calibração: se o parquet calibrado não existir em `data/cache/`, chama `calibrar_pd.py` automaticamente
2. Verificação de cache da clusterização: se o parquet clusterizado não existir, chama `clustering.py` automaticamente
3. Cálculo de $\overline{PD}_{fin}^{atual}$
4. Montagem do problema ($c$, $A$, $b$) a partir dos clusters - restrições R1, R2 e R3
5. Execução do Simplex
6. Pós-otimização e retorno dos resultados

---

## Parâmetros de entrada

### Parquet de clientes

Arquivo com os dados individuais dos clientes, localizado em `data/parquet/` (uso via CLI) ou em `apps/backend/uploads/` (quando enviado pelo front-end). As colunas utilizadas pelo modelo são:

| Coluna                     | Descrição                                                                              |
| -------------------------- | -------------------------------------------------------------------------------------- |
| `pd_produto`               | Probabilidade de inadimplência no produto                                              |
| `pd_calibrada`             | PD corrigida pelos fatores gamma por decil de risco                                    |
| `capacidade_pagamento`     | Estimativa de capacidade de pagamento do cliente                                       |
| `score_credito_cross`      | Score de crédito multiproduto, usado para calcular $m_k$ e como feature de clustering  |
| `score_propensao_contrato` | Score de propensão à contratação, normalizado para obter $\pi_k$                       |
| `flag_filtros`             | Indicador de perfil restrito: apenas clientes com `flag_filtros == 0` são elegíveis    |
| `renda_estimada`           | Usada como proxy de capacidade de pagamento quando `capacidade_pagamento` está ausente |

### JSON de parâmetros

Arquivo de configuração localizado em `apps/algoritmo_simplex/input/`, que permite customizar os parâmetros do modelo sem alterar o código. O arquivo padrão `parametros.json` contém:

```json
{
  "t": 0.0175,
  "LGD": 0.8,
  "u_bar": 0.75,
  "L_max": 25000.0,
  "T": 22.0
}
```

Onde:

- `t`: taxa de interchange (1,75%), fornecida pelo parceiro
- `LGD`: fração da exposição perdida em caso de default (80%)
- `u_bar`: fração esperada de utilização do limite (75%)
- `L_max`: teto máximo absoluto de limite por cluster (R$25.000), definido pelo parceiro
- `T`: horizonte de uso do limite em meses (22), definido pelo parceiro

---

## Clusterização de Clientes Elegíveis

### O problema: por que agrupar clientes?

O modelo de otimização (LP) precisa decidir, para cada cliente elegível, qual limite de crédito oferecer, de forma a **maximizar o lucro esperado do banco**. Em teoria, poderíamos rodar o LP tratando cada cliente individualmente. Na prática, isso é inviável: com dezenas de milhares de clientes, o problema se tornaria grande demais para ser resolvido em tempo útil.

A solução é **clusterização**: agrupar clientes parecidos em segmentos e tratar cada segmento como uma única unidade representativa no LP. Em vez de otimizar 50.000 decisões individuais, o LP otimiza, por exemplo, 100 decisões (uma por cluster).

> **Analogia:** Podemos comparar com eleições. Em vez de contar a opinião de cada habitante de cada bairro individualmente, pesquisas agrupam a população em perfis representativos e trabalham com esses grupos. O resultado é uma boa aproximação com muito menos custo computacional.

A chave para que essa aproximação seja boa é: **os clientes dentro de um mesmo cluster devem ser realmente parecidos naquilo que importa para o LP.** E o que importa para o LP não é necessariamente o que parece óbvio à primeira vista.

---

### O que significa "parecido" no contexto do LP?

O LP não se importa com se dois clientes têm renda parecida ou idade parecida. Ele se importa com uma única coisa: **quanto valor econômico cada cliente representa para o banco?**

Esse valor é capturado pelo **score composto** `c_k`, definido como:

```
c_k = π · (ū · t · T − PD_calib · LGD)
```

Decodificando cada termo:

| Símbolo     | Significado                                                                                     |
| ----------- | ----------------------------------------------------------------------------------------------- |
| `π`         | Taxa de juros: o quanto o banco ganha se o cliente pagar normalmente                            |
| `ū · t · T` | Valor esperado do crédito utilizado ao longo do tempo (quanto o cliente tende a usar do limite) |
| `PD_calib`  | Probabilidade de Inadimplência calibrada: a chance do cliente não pagar                         |
| `LGD`       | _Loss Given Default_: quanto o banco efetivamente perde quando o cliente não paga               |

Em linguagem direta: **receita esperada menos perda esperada**. Um cliente com `c_k` alto é valioso: usa bastante o crédito e tem baixo risco. Um cliente com `c_k` baixo é arriscado ou pouco lucrativo.

> `c_k` é exatamente o coeficiente que aparece na função objetivo do LP. É a "linguagem" que o LP usa para tomar decisões. Portanto, a clusterização só faz sentido se agrupar clientes que sejam parecidos em `c_k`, e não em renda, idade ou qualquer outra dimensão que o LP não usa diretamente.

---

### Por que não usamos K-Means?

O **K-Means** é o algoritmo de clusterização mais clássico. A versão original do modelo o utilizava, e ele tem um problema fundamental nesse contexto.

#### Como o K-Means funciona

O K-Means divide a população em `k` grupos minimizando a **distância euclidiana** entre os clientes e o centróide (ponto central) do seu cluster. Basicamente: clientes "próximos no espaço das variáveis" ficam no mesmo grupo.

#### O problema da versão original

Na versão anterior do modelo, o K-Means rodava sobre as features brutas dos clientes: renda, PD, LGD, tempo de relacionamento, etc. Distância euclidiana nessas variáveis não tem nenhuma relação com `c_k`. Dois clientes podem ter renda e PD parecidas, mas `c_k` muito diferente, e mesmo assim o K-Means os jogaria no mesmo cluster.

O resultado são clusters internamente heterogêneos em `c_k`, o que faz o LP tomar decisões "médias" ruins: restritivo demais para os clientes bons do cluster e leniente demais para os ruins.

#### E se usássemos K-Means apenas sobre `c_k`?

Essa é a pergunta certa. K-Means rodando em uma única dimensão (`c_k`) minimizaria a variância de `c_k` dentro dos clusters, que é o objetivo correto. A crítica conceitual ao K-Means cai nesse cenário.

Porém, mesmo nesse caso, o K-Means apresenta problemas práticos relevantes:

**1. Cortes artificialmente espaçados**

O K-Means encontra centróides e define clusters como os clientes mais próximos de cada centróide. Em distribuições assimétricas (e a distribuição de `c_k` em carteiras de crédito tipicamente é assimétrica: muitos clientes mediocres, poucos excelentes), o K-Means tende a criar cortes igualmente espaçados no eixo de `c_k`, mesmo que não haja nenhum motivo para isso. O CART, por sua vez, **busca ativamente os pontos de corte que mais reduzem a variância interna**, encontrando onde "faz sentido" dividir em vez de dividir de forma uniforme.

**2. Não produz regras interpretáveis nas features originais**

O resultado do K-Means é um conjunto de centróides. Para classificar um cliente novo, você calcula a distância dele a cada centróide e o aloca no mais próximo: duas etapas, e o resultado não tem interpretação direta em termos das features do cliente.

O CART produz uma **árvore de decisão**, que é essencialmente uma sequência de regras do tipo:

```
Se PD_calib < 0.03 e renda > 8.000 → Cluster A
Se PD_calib < 0.03 e renda ≤ 8.000 → Cluster B
Se PD_calib ≥ 0.03                  → Cluster C
```

Isso tem valor operacional real: qualquer sistema consegue classificar um cliente novo percorrendo a árvore com operações simples de comparação.

**3. Sensibilidade a outliers**

O K-Means é sensível a valores extremos: um cliente com `c_k` excepcionalmente alto puxa o centróide do seu cluster, distorcendo os limites de todos os grupos. O CART é mais robusto porque trabalha com partições binárias sucessivas, de modo que um outlier fica isolado numa folha da árvore sem afetar os demais cortes.

---

### Por que não usamos HDBSCAN?

O **HDBSCAN** é um algoritmo de clusterização por densidade: ele identifica "nuvens naturais" nos dados sem que você precise definir o número de clusters de antemão. Em teoria, seria ideal: deixar os dados revelarem sua própria estrutura.

Na prática, realizamos uma análise empírica com HDBSCAN sobre a base de clientes elegíveis. O resultado: independentemente do valor do parâmetro `min_cluster_size`, o algoritmo encontrou **no máximo 22 clusters**.

O que isso significa? Os dados simplesmente não possuem estrutura de densidade natural suficiente para suportar 100 ou mais clusters. Forçar 100+ clusters com HDBSCAN produziria agrupamentos artificiais sem significado estatístico.

Além disso, o HDBSCAN sofreria do mesmo problema conceitual do K-Means original: agrupa por densidade geométrica nos dados, não por homogeneidade em `c_k`. A segmentação precisa ser **guiada pelo objetivo do LP**, não pela estrutura geométrica dos dados.

---

### A solução: CART guiado por `c_k`

#### O que é o CART

**CART** (_Classification and Regression Trees_) é um algoritmo que constrói uma árvore de decisão dividindo recursivamente a população. Em cada etapa, ele escolhe uma variável e um ponto de corte que **minimiza a variância de uma variável-guia** nas duas metades resultantes.

Diferente do K-Means (que minimiza distância euclidiana) e do HDBSCAN (que busca densidade geométrica), o CART permite que você **especifique explicitamente em qual dimensão quer homogeneidade**.

#### Por que o CART com `c_k` como variável-guia resolve o problema

Ao definir `c_k` como variável-guia do CART, cada divisão da árvore é escolhida para que os dois grupos resultantes sejam o mais homogêneos possível em `c_k`. Ao final do processo, cada folha da árvore (cada cluster) contém clientes com scores `c_k` muito parecidos entre si.

Isso é exatamente o que o LP precisa: quando ele tomar uma decisão de limite para um cluster, essa decisão será uma boa aproximação para todos os clientes dentro dele, porque todos têm `c_k` semelhante.

#### Como o CART constrói os clusters na prática

O processo é recursivo e pode ser visualizado assim:

```
População completa (c_k varia de -200 a +800)
│
├── Corte 1: PD_calib < 0.05
│   ├── [c_k alto] → subdividir mais...
│   │   ├── Corte 2: renda > 5.000 → Cluster A (c_k ≈ 600–800)
│   │   └── Corte 2: renda ≤ 5.000 → Cluster B (c_k ≈ 400–600)
│   └── [c_k médio] → subdividir mais...
│       └── ...
│
└── Corte 1: PD_calib ≥ 0.05
    ├── [c_k baixo ou negativo] → subdividir mais...
    │   └── ...
    └── ...
```

Em cada nó, o CART testa todas as variáveis disponíveis e todos os pontos de corte possíveis, e escolhe a combinação que mais reduz a variância de `c_k`. O processo continua até atingir o número desejado de clusters (folhas da árvore).

---

### Quantos clusters usar? A escolha de K = 800

Definido o algoritmo (CART com `c_k`), ainda resta uma pergunta: **quantos clusters criar?**

Mais clusters significa maior fidelidade: cada grupo fica menor e mais homogêneo, e o LP aproxima melhor a realidade individual de cada cliente. Mas mais clusters também significam mais tempo de processamento, tanto na clusterização quanto na execução do Simplex.

A escolha de K não tem resposta teórica direta. Por isso, adotamos uma **varredura empírica**: executamos o pipeline completo (clusterização + Simplex) para cada valor de K entre 50 e 2000, em incrementos de 50, e registramos o valor ótimo `z` da função objetivo em cada execução.

O que observamos foi um padrão claro de **retorno marginal decrescente**:

- Nos primeiros incrementos (K = 50 a ~400), cada bloco adicional de 50 clusters aumenta `z` de forma relevante.
- A partir de K = 800, cada incremento adicional de 50 clusters aumenta `z` em menos de 0,5%.
- K = 800 captura **98,4% do retorno máximo** encontrado com K = 2000.

Em outras palavras: depois de 800 clusters, o pipeline continua melhorando, mas de forma cada vez mais marginal, enquanto o custo computacional continua crescendo linearmente. O ganho não justifica o custo.

**K = 800 é o ponto onde o trade-off entre qualidade da solução e tempo de processamento é mais favorável.**

### Comparativo final das abordagens

| Critério                                 | K-Means (features brutas) | K-Means (`c_k`) |   HDBSCAN    | **CART (`c_k`)** |
| ---------------------------------------- | :-----------------------: | :-------------: | :----------: | :--------------: |
| Alinhado com o objetivo do LP            |            ❌             |       ✅        |      ❌      |        ✅        |
| Encontra cortes naturais (não uniformes) |            ❌             |       ❌        |      ✅      |        ✅        |
| Produz regras interpretáveis             |            ❌             |       ❌        |      ❌      |        ✅        |
| Robusto a outliers                       |            ❌             |       ❌        |      ✅      |        ✅        |
| Escala para 100+ clusters                |            ✅             |       ✅        |      ❌      |        ✅        |
| Suportado empiricamente nos dados        |            N/A            |       N/A       | ❌ (máx. 22) |        ✅        |

O CART com `c_k` como variável-guia é o único método que satisfaz todos os requisitos simultaneamente: alinhamento com o LP, cortes adaptativos não uniformes, interpretabilidade operacional, robustez a outliers e capacidade de gerar o número de clusters necessário.

---

### Resumo da clusterização

A clusterização existe para tornar o LP computacionalmente viável, substituindo decisões individuais por decisões por grupo. Para que essa substituição introduza o mínimo de erro, os grupos precisam ser homogêneos exatamente na dimensão que o LP usa: o score `c_k` (valor econômico líquido esperado por cliente).

O CART, usando `c_k` como variável-guia, é o algoritmo que garante essa homogeneidade. Ele supera o K-Means por encontrar cortes naturais e produzir regras interpretáveis, e supera o HDBSCAN por escalar para o número de clusters necessário e por ser guiado pelo objetivo do negócio, e não pela geometria dos dados.

---

## Calibração da PD

Antes da clusterização, a `pd_produto` de cada cliente é calibrada pelo script `calibrar_pd.py`, que aplica fatores gamma por decil de risco calculados em `setup_tabela_gamma.py`.

A calibração segue dois passos:

1. Os decis são definidos pelos percentis de `pd_produto` da **população elegível completa** (6,7 milhões de clientes das 3 safras combinadas), garantindo que cada decil contenha ~10% dos elegíveis.
2. O gamma empírico de cada decil é estimado a partir das observações de `over30mob3` que caem naquele decil, usando a razão entre defaults observados e PD esperada.

Os decis D1-D4 possuem estimativas empíricas robustas (2.200 a 6.500 observações cada). D5 tem 103 observações com IC95 mais largo. D6-D10 têm menos de 16 observações cada e recebem gamma por extrapolação linear - limitação estrutural dos dados, pois clientes de alto risco raramente foram aprovados historicamente.

---

## Execução do otimizador

### Dependências

```bash
pip install -r apps/algoritmo_simplex/requirements.txt
```

| Biblioteca     | Uso                                            |
| -------------- | ---------------------------------------------- |
| `pandas`       | Leitura e manipulação dos parquets             |
| `scikit-learn` | Algoritmo CART para clusterização dos clientes |
| `numpy`        | Cálculo de percentis na agregação dos clusters |
| `pyarrow`      | Leitura e escrita de arquivos parquet          |

O algoritmo Simplex em si não utiliza nenhuma biblioteca externa, foi implementado do zero com Python puro.

### Executando via CLI

A partir do diretório raíz do projeto:

```bash
python apps/algoritmo_simplex/main.py <arquivo.parquet> <parametros.json>
```

Exemplo:

```bash
python apps/algoritmo_simplex/main.py base_ref_M1_v2.parquet parametros.json
```

O parquet deve estar em `data/parquet/`. Na primeira execução, a calibração e a clusterização são geradas automaticamente e salvas em `data/cache/`. Nas execuções seguintes, os arquivos em cache são reutilizados, tornando a execução significativamente mais rápida.

### Saída

```
Status: otimo
Valor ótimo (z): 36183592.28

Limites ótimos por cluster:
  Cluster 0: R$ 250 (n=891)
  Cluster 1: R$ 250 (n=855)
  Cluster 2: R$ 1950 (n=906)
  Cluster 3: R$ 0 (n=653)
  ...
```

Os limites exibidos já passaram pela pós-otimização definida pelo parceiro:

- Limites abaixo de R$200 são convertidos para R$0, indicando que o cluster não deve receber oferta
- Limites acima de R$200 são arredondados para o múltiplo de R$50 mais próximo

---

## Testes realizados no otimizador

### Teste 1: Validação do algoritmo com problema de solução conhecida

Antes de aplicar o algoritmo ao problema real, foi utilizado um problema clássico com solução analítica conhecida para validar a corretude da implementação:

**Entrada:**

```
Max z = 40x1 + 35x2
s.t.
2x1 + 3x2 <= 60
4x1 + 3x2 <= 96
x1, x2 >= 0
```

**Saída esperada:** $x_1 = 18$, $x_2 = 8$, $z = 1000$

**Saída obtida:**

```
x: [18.0, 8.0]
z: 1000.0
status: otimo
```

O algoritmo produziu o resultado correto.

### Teste 2: Detecção de problema ilimitado

**Entrada:**

```python
Problema(
    c=[40.0, 35.0],
    A=[[-1.0, 0.0],
       [0.0, -1.0]],
    b=[60.0, 96.0],
)
```

**Saída obtida:**

```
Erro: O problema é ilimitado.
```

O algoritmo detectou e reportou corretamente o caso ilimitado.

### Teste 3: Detecção de múltiplas soluções

**Entrada:**

```python
Problema(
    c=[2.0, 4.0],
    A=[[1.0, 2.0],
       [1.0, 0.0]],
    b=[4.0, 2.0],
)
```

**Saída obtida:**

```
x: [2.0, 1.0]
z: 8.0
status: multiplas_solucoes
```

O algoritmo detectou corretamente a existência de múltiplas soluções e retornou uma delas.

### Teste 4: Execução com base M1, parâmetros padrão

**Entrada:** `base_ref_M1_v2.parquet` com parâmetros `t=0.0175`, `LGD=0.8`, `u_bar=0.75`, `T=22`, `L_max=25000`.

**Saída obtida:**

```
Status: otimo
Valor otimo (z): 36183592.28
```

Estatísticas dos clusters com oferta (L > 0):

| Métrica | Limite ofertado | Clientes por cluster |
| ------- | --------------- | -------------------- |
| Mínimo  | R$ 200          | 502                  |
| Máximo  | R$ 4.300        | 11.202               |
| Média   | R$ 844          | 2.295                |
| Mediana | R$ 400          | 1.826                |

382 clusters receberam oferta, totalizando 876.520 clientes (47,7% dos 1.836.085 elegíveis). O cluster com maior número de clientes (n=11.202) recebeu limite de R$3.600. Clusters com limite zero apresentam perfil de alto risco onde a perda esperada por inadimplência supera a receita de interchange dado o teto de inadimplência financeira da carteira (R1).

### Teste 5: Sensibilidade a parâmetros - M1 com parâmetros alternativos

**Entrada:** `base_ref_M1_v2.parquet` com parâmetros `t=0.018`, `LGD=0.7`, `u_bar=0.8`, `T=22`, `L_max=25000`.

**Saída obtida:**

```
Status: otimo
Valor otimo (z): 43003817.89
```

Estatísticas dos clusters com oferta (L > 0):

| Métrica | Limite ofertado | Clientes por cluster |
| ------- | --------------- | -------------------- |
| Mínimo  | R$ 200          | 502                  |
| Máximo  | R$ 4.300        | 11.202               |
| Média   | R$ 840          | 2.289                |
| Mediana | R$ 400          | 1.821                |

385 clusters receberam oferta, totalizando 881.147 clientes (48,0% dos elegíveis). O aumento de $t$ e a redução de LGD tornaram a carteira mais rentável (+18,9% em z), com distribuição de limites praticamente idêntica à do Teste 4, confirmando a robustez da clusterização a variações de parâmetros.

### Teste 6: Execução com base M2, parâmetros padrão

**Entrada:** `base_ref_M2_v2.parquet` com parâmetros `t=0.0175`, `LGD=0.8`, `u_bar=0.75`, `T=22`, `L_max=25000`.

**Saída obtida:**

```
Status: otimo
Valor otimo (z): 36925407.73
```

Estatísticas dos clusters com oferta (L > 0):

| Métrica | Limite ofertado | Clientes por cluster |
| ------- | --------------- | -------------------- |
| Mínimo  | R$ 200          | 507                  |
| Máximo  | R$ 4.050        | 10.581               |
| Média   | R$ 920          | 2.343                |
| Mediana | R$ 450          | 1.844                |

356 clusters receberam oferta, totalizando 834.225 clientes (46,2% dos 1.805.274 elegíveis de M2). O valor ótimo de M2 (R$36,9M) é comparável ao de M1 (R$36,2M), indicando consistência do modelo entre safras.

### Teste 7: Execução com base M3, parâmetros padrão

**Entrada:** `base_ref_M3_v2.parquet` com parâmetros `t=0.0175`, `LGD=0.8`, `u_bar=0.75`, `T=22`, `L_max=25000`.

**Saída obtida:**

```
Status: otimo
Valor otimo (z): 60765092.37
```

Estatísticas dos clusters com oferta (L > 0):

| Métrica | Limite ofertado | Clientes por cluster |
| ------- | --------------- | -------------------- |
| Mínimo  | R$ 200          | 503                  |
| Máximo  | R$ 3.700        | 14.240               |
| Média   | R$ 727          | 4.012                |
| Mediana | R$ 550          | 3.646                |

437 clusters receberam oferta, totalizando 1.753.121 clientes (55,9% dos 3.137.258 elegíveis de M3). O valor ótimo de M3 (R$60,8M) é significativamente maior que o de M1 e M2 porque a safra M3 possui quase o dobro de clientes elegíveis.

---

## Back-end

### Visão geral

O back-end é uma API REST construída com **FastAPI** que expõe o pipeline de otimização ao front-end. Quando o usuário faz upload de um parquet, a API salva o arquivo, cria um registro de consulta no banco de dados e dispara o pipeline de otimização **de forma assíncrona** - o endpoint retorna imediatamente com o status `pendente`, sem bloquear a aplicação enquanto o Simplex executa.

O front-end pode então consultar o status da execução a qualquer momento, e quando ela concluir, acessar os resultados por consulta, cluster ou cliente individual.

### Estrutura de pastas

```
apps/backend/
├── main.py              # ponto de entrada FastAPI, lifespan com pool asyncpg
├── run_server.py        # script de inicialização via uvicorn
├── config.py            # variáveis de ambiente
├── requirements.txt     # dependências Python
├── .env.example         # template de variáveis de ambiente
├── api/
│   └── routes.py        # definição de todos os endpoints
├── db/
│   ├── storage.py       # pool asyncpg, execução de migrations
│   └── migrations/      # arquivos SQL de criação das tabelas
│       ├── 001_create_safras.sql
│       ├── 002_create_consultas.sql
│       ├── 003_create_clusters_resultado.sql
│       ├── 004_create_clientes_resultado.sql
│       ├── 005_create_config.sql
│       └── 006_seed_config.sql
├── model/
│   └── schemas.py       # schemas Pydantic de entrada e saída
├── services/
│   └── credit_service.py   # lógica de negócio e integração com o otimizador
└── uploads/             # parquets recebidos via upload
```

### Banco de dados

O back-end utiliza **PostgreSQL** com acesso via `asyncpg`. As migrations são executadas automaticamente na inicialização da aplicação. O esquema é composto por cinco tabelas:

**`safras`** - cada safra representa um conjunto de clientes de um período (M1, M2, M3...). Ao fazer upload, o usuário pode informar um número de safra ou deixar o back-end atribuir automaticamente o próximo disponível.

**`consultas`** - cada execução do pipeline é uma consulta. Registra os parâmetros utilizados, o status do processamento (`pendente`, `executando`, `concluido`, `erro`), o resultado da otimização (valor ótimo `z`, status do LP) e estatísticas da base processada.

**`clusters_resultado`** - os 800 clusters gerados pelo CART, com todos os parâmetros agregados ($n_k$, $PD_k$, $\pi_k$, $CP_k$, $m_k$) e o limite otimizado pelo Simplex.

**`clientes_resultado`** - todos os clientes elegíveis da base, com seus dados originais do parquet, os campos derivados pelo pipeline (`pd_calibrada`, `pi_normalizado`, `cp_proxy`) e a atribuição de cluster e limite. Permite buscar o histórico de um cliente específico por token ao longo de múltiplas consultas.

**`parametros_modelo`** - tabela de configuração com uma única linha, contendo os parâmetros padrão do modelo. Pode ser atualizada via `PUT /api/config`.

### Integração assíncrona com o otimizador

A integração entre o back-end e o otimizador é realizada de forma assíncrona usando `BackgroundTasks` do FastAPI combinado com `asyncio.run_in_executor`. O pipeline do otimizador é bloqueante (execução do Simplex pode levar minutos), então ele é executado numa thread pool separada, sem bloquear a event loop do FastAPI. O fluxo é:

1. `POST /api/consultas` recebe o parquet e retorna imediatamente com `status_consulta: "pendente"`
2. A `BackgroundTask` inicia e atualiza o status para `"executando"`
3. O pipeline roda em thread pool: calibração → clusterização → Simplex
4. Os resultados são persistidos no banco via bulk insert (`copy_records_to_table`)
5. O status é atualizado para `"concluido"` com todos os campos de resultado
6. Em caso de erro, o status vai para `"erro"` com `erro_etapa` e `erro_mensagem`

O front-end acompanha o progresso fazendo polling em `GET /api/consultas/{id}`.

### Endpoints

Todos os endpoints têm o prefixo `/api`.

#### Saúde

| Método | Rota      | Descrição                    |
| ------ | --------- | ---------------------------- |
| `GET`  | `/health` | Verifica se a API está no ar |

#### Safras

| Método | Rota      | Descrição                         |
| ------ | --------- | --------------------------------- |
| `GET`  | `/safras` | Lista todas as safras cadastradas |

#### Consultas

| Método | Rota                              | Descrição                                                                |
| ------ | --------------------------------- | ------------------------------------------------------------------------ |
| `GET`  | `/consultas`                      | Lista todas as consultas, da mais recente para a mais antiga             |
| `POST` | `/consultas`                      | Upload do parquet e criação da consulta (dispara pipeline em background) |
| `GET`  | `/consultas/{id}`                 | Status e resultado de uma consulta específica                            |
| `GET`  | `/consultas/{id}/clusters`        | Clusters com parâmetros e limites otimizados                             |
| `GET`  | `/consultas/{id}/clientes`        | Clientes da consulta, paginados (`limit` e `offset`)                     |
| `GET`  | `/consultas/{id}/clientes/export` | Download dos clientes da consulta em CSV                                 |

#### Clientes

| Método | Rota                | Descrição                                              |
| ------ | ------------------- | ------------------------------------------------------ |
| `GET`  | `/clientes/{token}` | Histórico completo de um cliente em todas as consultas |

#### Configuração

| Método | Rota      | Descrição                               |
| ------ | --------- | --------------------------------------- |
| `GET`  | `/config` | Retorna os parâmetros padrão do modelo  |
| `PUT`  | `/config` | Atualiza os parâmetros padrão do modelo |

#### Parâmetros do `POST /consultas`

Todos os campos são opcionais. Se omitidos, o back-end usa os valores padrão.

| Parâmetro              | Tipo     | Descrição                                                                         |
| ---------------------- | -------- | --------------------------------------------------------------------------------- |
| `file`                 | arquivo  | Parquet da safra a ser processada (obrigatório)                                   |
| `safra_numero`         | inteiro  | Número da safra (ex: 1 para M1). Se omitido, usa MAX+1 ou M1                      |
| `usar_safra_existente` | booleano | Se `true` e o número já existir, vincula à safra existente em vez de retornar 409 |
| `t`                    | número   | Override da taxa de interchange                                                   |
| `LGD`                  | número   | Override do Loss Given Default                                                    |
| `u_bar`                | número   | Override da fração de utilização                                                  |
| `L_max`                | número   | Override do teto máximo de limite                                                 |
| `T`                    | número   | Override do horizonte em meses                                                    |

Quando `safra_numero` informado já existe e `usar_safra_existente` é `false`, a API retorna `409 Conflict`. O front-end deve exibir um popup perguntando se o usuário quer usar a safra existente ou criar uma nova, e reenviar a requisição com `usar_safra_existente=true` ou sem `safra_numero`.

### Dependências

```bash
pip install -r apps/backend/requirements.txt
```

| Biblioteca          | Uso                                                |
| ------------------- | -------------------------------------------------- |
| `fastapi`           | Framework web assíncrono                           |
| `uvicorn[standard]` | Servidor ASGI                                      |
| `asyncpg`           | Driver PostgreSQL assíncrono                       |
| `pandas`            | Leitura do parquet e construção do bulk insert     |
| `pyarrow`           | Leitura de metadados do parquet sem carregar dados |
| `python-multipart`  | Upload de arquivos via multipart/form-data         |
| `numpy`             | Operações vetorizadas no pipeline                  |
| `scikit-learn`      | CART para clusterização (chamado pelo otimizador)  |

### Variáveis de ambiente

Copie `.env.example` para `.env` e preencha os valores:

```bash
cp apps/backend/.env.example apps/backend/.env
```

| Variável           | Descrição                                      | Padrão                  |
| ------------------ | ---------------------------------------------- | ----------------------- |
| `APP_HOST`         | Endereço de bind do servidor                   | `127.0.0.1`             |
| `APP_PORT`         | Porta do servidor                              | `8000`                  |
| `FRONTEND_ORIGINS` | Origens CORS permitidas, separadas por vírgula | `http://localhost:3000` |
| `UPLOAD_DIR`       | Pasta onde os parquets enviados são salvos     | `./uploads`             |
| `DB_HOST`          | Endereço do servidor PostgreSQL                | -                       |
| `DB_PORT`          | Porta do PostgreSQL                            | `5432`                  |
| `DB_DATABASE`      | Nome do banco de dados                         | -                       |
| `DB_USER`          | Usuário do banco                               | -                       |
| `DB_PASSWORD`      | Senha do banco                                 | -                       |

### Execução do back-end

A partir do diretório `apps/backend/`:

```bash
python run_server.py
```

Na inicialização, o servidor:

1. Cria o pool de conexões com o PostgreSQL
2. Executa as migrations pendentes (cria as tabelas se não existirem)
3. Inicia o servidor na porta configurada

A documentação interativa dos endpoints fica disponível em `http://127.0.0.1:8000/docs`.

### Testes realizados no back-end

#### Teste 1: Upload e pipeline completo com M1

**Requisição:**

```bash
curl -X POST "http://127.0.0.1:8000/api/consultas" \
  -F "file=@apps/backend/uploads/base_ref_M1_v2.parquet"
```

**Resultado:**

```json
{
  "id": "3cf613e8-6197-4213-841d-62f1d9e890af",
  "status_consulta": "concluido",
  "status_lp": "otimo",
  "z_otimo": 34071836.0,
  "n_clientes_total": 14569142,
  "n_clientes_elegiveis": 1836085,
  "n_clientes_ofertados": 876677,
  "n_clusters": 150
}
```

Pipeline completo executado com sucesso. Status transitou de `pendente` → `executando` → `concluido`.

#### Teste 2: Listagem de clusters

```bash
curl "http://127.0.0.1:8000/api/consultas/3cf613e8-.../clusters"
```

Retornou 150 clusters com todos os campos (`cluster_id`, `n_clientes`, `pd_media`, `pi_media`, `cp_percentil5`, `score_credito_cross_medio`, `ck_medio`, `fator_alavancagem`, `limite_otimizado`).

#### Teste 3: Listagem paginada de clientes

```bash
curl "http://127.0.0.1:8000/api/consultas/3cf613e8-.../clientes?limit=5"
```

Retornou 5 clientes com todos os campos do parquet original, campos derivados pelo pipeline e atribuição de cluster e limite.

#### Teste 4: Histórico de cliente por token

```bash
curl "http://127.0.0.1:8000/api/clientes/3"
```

Retornou o histórico do token 3 com todos os dados da consulta em que apareceu.

#### Teste 5: Consulta de token inexistente

```bash
curl "http://127.0.0.1:8000/api/clientes/0"
```

Retornou `404 Not Found` - token 0 é inelegível (`flag_filtros != 0`) e não foi persistido, comportamento correto.

---

## Conclusões

A escolha do Simplex como algoritmo de otimização é adequada à natureza do problema: o LP de limites de crédito tem estrutura totalmente linear, com variáveis contínuas e não-negatividade garantida pela formulação. Algoritmos exatos como o Simplex convergem para o ótimo global nessa classe de problemas, o que é essencial num contexto regulatório onde o banco precisa justificar as decisões de crédito.

A clusterização via CART com K=800 e variável-guia c_k resolve um desafio prático central: tornar o LP viável computacionalmente sem comprometer a qualidade da solução. A escolha de K=800 não é arbitrária - decorre de uma varredura empírica sobre as três safras que identificou o ponto de retorno marginal decrescente, capturando 98,4% do retorno máximo teórico.
Os testes com as safras M1, M2 e M3 mostram consistência do modelo entre períodos distintos: os valores ótimos são comparáveis entre M1 e M2 (R$36,2M e R$36,9M respectivamente) e o modelo se comporta de forma previsível ao variar os parâmetros, com o z aumentando 18,9% ao relaxar LGD e elevar t no Teste 5.

Os próximos passos previstos são:

- Alinhamento com o parceiro sobre a formulação de R1, dado que a correlação positiva observada entre `pd_calibrada` e `pi` na base faz com que a restrição de inadimplência financeira exclua clusters de alta propensão
- Incorporação das restrições adicionais mapeadas no TAPI, como teto de inadimplência física, metas de produção mínima e rentabilidade mínima da carteira
