# Algoritmo Simplex

## Contextualização

O Banco Pan oferece cartões de crédito pré-aprovados a clientes correntistas. A decisão de qual limite de crédito oferecer a cada cliente é hoje tomada com base em tabelas fixas, que não consideram a heterogeneidade entre perfis e não controlam o risco agregado da carteira.

O objetivo deste projeto é substituir essa regra empírica por uma decisão matemática: encontrar, para cada grupo de clientes com perfil semelhante, o limite que **maximize o retorno líquido esperado do banco**, definido como a receita de interchange menos a perda esperada por inadimplência, respeitando restrições de risco e capacidade de pagamento definidas pelo parceiro.

Para isso, o problema foi formulado como um **Problema de Programação Linear (PL)**, onde as variáveis de decisão são os limites de crédito a serem atribuídos a cada grupo de clientes. A solução desse PL é encontrada por meio do **algoritmo Simplex**, implementado neste artefato.

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

## Estrutura da implementação

A implementação está organizada em três arquivos dentro de `apps/algoritmo_simplex/`:

### `models.py`

Define as estruturas de dados:

- `Problema`: agrupa os dados de entrada do LP - o vetor de coeficientes da função objetivo `c`, a matriz de coeficientes das restrições `A` e o vetor dos lados direitos `b`. Esses dados nunca mudam durante a execução.
- `Tableau`: representa o estado atual da tabela do Simplex - as colunas das variáveis de decisão e de folga, a base atual, as contributions e os valores. Esse estado é atualizado a cada pivotamento.

### `simplex.py`

Implementação pura do algoritmo Simplex, sem nenhuma dependência da lógica de negócio do projeto. Recebe um `Problema` e devolve a solução ótima, o valor da função objetivo e o status da solução.

### `clustering.py`

Agrupa os clientes elegíveis em $K$ clusters usando CART e calcula os parâmetros agregados necessários para o LP: $n_k$, $PD_k$, $\pi_k$, $CP_k$ e $m_k$. Detalhes na seção de Clusterização.

### `main.py`

Orquestra o pipeline completo:

1. Leitura do CSV de clientes e do JSON de parâmetros
2. Cálculo de $\overline{PD}_{fin}^{atual}$
3. Verificação de cache: se o arquivo clusterizado já existir, a clusterização é pulada
4. Montagem do problema ($c$, $A$, $b$) a partir dos clusters - restrições R1, R2 e R3
5. Execução do Simplex
6. Pós-otimização e exibição dos resultados

## Parâmetros de entrada

A solução recebe dois arquivos como entrada:

### CSV de clientes

Arquivo com os dados individuais dos clientes calibrados, localizado em `data/csv/`. As colunas utilizadas pelo modelo são:

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

## Clusterização

A clusterização é feita usando **CART** (Classification and Regression Trees), agrupando clientes elegíveis em segmentos homogêneos na dimensão que o LP maximiza.

### Motivação da escolha do CART

O K-Means, usado em versões anteriores, minimiza distância euclidiana no espaço das features — métrica sem relação direta com o objetivo do LP. O CART particiona o espaço de features minimizando a variância de uma variável guia escolhida, que neste caso é o score composto:

$$c_k = \pi \cdot (\bar{u} \cdot t \cdot T - PD_{calib} \cdot \text{LGD})$$

Esse é exatamente o coeficiente da função objetivo do LP (sem o fator $n_k$, que só existe após a clusterização). Ao usar $c_k$ como variável guia, o CART garante que cada cluster seja internamente homogêneo na dimensão que o LP otimiza — e não em distância euclidiana, que não tem significado econômico aqui.

Além disso, uma análise empírica com HDBSCAN confirmou que os dados não possuem estrutura de densidade natural suficiente para produzir 100 ou mais clusters: o algoritmo encontrou no máximo 22 clusters independente do parâmetro `min_cluster_size`. A segmentação precisa ser guiada pelo objetivo do LP, não por densidade geométrica dos dados.

### Escolha de K = 800

O número de clusters foi definido por varredura empírica. Para cada valor de $K$ de 50 a 2000, o pipeline completo (clustering + Simplex) foi executado e o valor ótimo $z$ da função objetivo registrado. O resultado mostrou que a partir de $K = 800$, cada incremento adicional de clusters aumenta $z$ em menos de 0,5%. $K = 800$ captura 98,4% do retorno máximo encontrado com $K = 2000$.

A justificativa para o banco: a partir de $K = 800$, clusters adicionais não aumentam o retorno esperado da carteira de forma relevante — o ganho marginal cai abaixo de 0,5% por incremento de 50 clusters.

### População considerada

A base é filtrada para incluir apenas clientes elegíveis (`flag_filtros == 0`) antes de qualquer processamento. Os clientes inelegíveis não participam da clusterização nem do LP.

### Variáveis usadas na clusterização

O CART é treinado usando as seguintes features de split:

- `pd_calibrada`: probabilidade de inadimplência calibrada por decil de risco
- `pi`: propensão normalizada, derivada de `score_propensao_contrato`
- `cp_proxy`: proxy de capacidade de pagamento
- `score_credito_cross`: score multiproduto, também usado para derivar $m_k$

A variável `fx_idade` foi excluída porque não tem impacto direto nas variáveis que o LP consome ($PD_k$, $\pi_k$, $CP_k$, $m_k$).

### Pré-processamento

A variável `pi` é criada normalizando `score_propensao_contrato` para o intervalo [0, 1]. O `cp_proxy` utiliza `capacidade_pagamento` quando disponível; quando nula, usa `renda_estimada * 0,30` como fallback.

Nulos residuais nas features de split são imputados pela mediana antes do treinamento. O CART não requer padronização (StandardScaler) nem codificação de variáveis categóricas (OneHotEncoder) porque seus critérios de split são baseados em limiares ordinais, invariantes a transformações monotônicas.

### Parâmetros do CART

| Parâmetro          | Valor | Justificativa                                                                  |
| ------------------ | ----- | ------------------------------------------------------------------------------ |
| `max_leaf_nodes`   | 800   | K ótimo identificado empiricamente via varredura de z vs K                     |
| `min_samples_leaf` | 500   | Garante que cada cluster tenha pelo menos 500 clientes para agregados estáveis |
| `random_state`     | 42    | Reproducibilidade                                                              |

## Calibração da PD

Antes da clusterização, a `pd_produto` de cada cliente é calibrada pelo script `calibrar_pd.py`, que aplica fatores gamma por decil de risco calculados em `analise_09_calibracao_final.py`.

A calibração segue dois passos:

1. Os decis são definidos pelos percentis de `pd_produto` da **população elegível completa** (6,7 milhões de clientes das 3 safras combinadas), garantindo que cada decil contenha ~10% dos elegíveis.
2. O gamma empírico de cada decil é estimado a partir das observações de `over30mob3` que caem naquele decil, usando a razão entre defaults observados e PD esperada.

Os decis D1-D4 possuem estimativas empíricas robustas (2.200 a 6.500 observações cada). D5 tem 103 observações com IC95 mais largo. D6-D10 têm menos de 16 observações cada e recebem gamma por extrapolação linear — limitação estrutural dos dados, pois clientes de alto risco raramente foram aprovados historicamente.

## Dependências

As dependências do projeto estão listadas em `apps/algoritmo_simplex/requirements.txt`. Para instalá-las:

```bash
pip install -r requirements.txt
```

As bibliotecas utilizadas são:

| Biblioteca     | Uso                                            |
| -------------- | ---------------------------------------------- |
| `pandas`       | Leitura e manipulação dos arquivos CSV         |
| `scikit-learn` | Algoritmo CART para clusterização dos clientes |
| `numpy`        | Cálculo de percentis na agregação dos clusters |

O algoritmo Simplex em si não utiliza nenhuma biblioteca externa, foi implementado do zero com Python puro.

## Execução

A partir do diretório raíz do projeto (`g04/`):

```bash
python apps/algoritmo_simplex/main.py <arquivo_clientes_calibrado.csv> <parametros.json>
```

Exemplo:

```bash
python apps/algoritmo_simplex/main.py clientes_m1_calibrado.csv parametros.json
```

Na primeira execução, a clusterização é gerada automaticamente e salva em `data/csv/<nome>_clusters.csv`. Nas execuções seguintes, o arquivo clusterizado é reutilizado, tornando a execução significativamente mais rápida.

## Saída dos dados

Ao final da execução, o algoritmo exibe no console o status da solução, o valor ótimo da função objetivo e o limite otimizado para cada cluster:

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

## Testes realizados

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

### Teste 4: Execução completa com base de clientes calibrada

**Entrada:** `clientes_m1_calibrado.csv` com `parametros.json` padrão (K=800 clusters).

**Saída obtida:**

```
Status: otimo
Valor otimo (z): 36183592.28

Limites otimos por cluster:
  Cluster 0: R$ 250 (n=891)
  Cluster 1: R$ 250 (n=855)
  Cluster 2: R$ 1950 (n=906)
  Cluster 3: R$ 0 (n=653)
  Cluster 4: R$ 1150 (n=630)
  ...
  Cluster 387: R$ 3600 (n=11202)
  ...
  Cluster 720: R$ 4300 (n=3403)
  ...
```

O algoritmo convergiu para o ótimo com 800 clusters e 1.836.085 clientes elegíveis. Clusters com limite zero apresentam perfil de alto risco onde a perda esperada por inadimplência supera a receita de interchange dado o teto de inadimplência financeira da carteira (R1). Os clusters com limite positivo concentram os perfis com melhor relação risco-retorno compatível com as restrições do modelo.

## Conclusões

O algoritmo Simplex foi implementado do zero, sem uso de bibliotecas de otimização, e validado contra problemas com solução analítica conhecida. O pipeline completo — calibração da PD, clusterização por CART com K=800, montagem do LP e execução do Simplex — está funcional e documentado para a base completa de elegíveis.

Os próximos passos previstos são:

- Alinhamento com o parceiro sobre a formulação de R1, dado que a correlação positiva observada entre `pd_calibrada` e `pi` na base faz com que a restrição de inadimplência financeira exclua clusters de alta propensão
- Incorporação das restrições adicionais mapeadas no TAPI, como teto de inadimplência física, metas de produção mínima e rentabilidade mínima da carteira
- Execução e comparação dos resultados para as safras M2 e M3
