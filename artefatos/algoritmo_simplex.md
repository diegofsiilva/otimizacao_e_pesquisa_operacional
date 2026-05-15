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

$$\max \sum_{k=1}^{K} n_k \cdot \pi_k \cdot (\bar{u} \cdot t - PD_k \cdot \text{LGD}) \cdot L_k$$

O coeficiente de cada cluster, $c_k = n_k \cdot \pi_k \cdot (\bar{u} \cdot t - PD_k \cdot \text{LGD})$, representa o retorno líquido unitário esperado por real alocado ao cluster $k$. Clusters com $c_k > 0$ são rentáveis; clusters com $c_k \leq 0$ destroem valor a cada real adicional de limite e recebem $L_k = 0$ como solução natural do modelo.

Os parâmetros utilizados são:

| Parâmetro    | Descrição                                                               | Valor padrão      |
| ------------ | ----------------------------------------------------------------------- | ----------------- |
| $n_k$        | Número de clientes no cluster $k$                                       | calculado da base |
| $\pi_k$      | Propensão média de contratação do cluster $k$                           | calculado da base |
| $\bar{u}$    | Fração esperada de utilização do limite pelo cliente                    | 0,75              |
| $t$          | Taxa de interchange recebida pelo banco sobre o volume transacionado    | 1,75%             |
| $PD_k$       | Probabilidade de inadimplência média do cluster $k$                     | calculado da base |
| $\text{LGD}$ | Fração do saldo exposto perdida em caso de default (Loss Given Default) | 0,60              |

### Restrições

**R1 - Teto de inadimplência financeira:** a inadimplência financeira ponderada da carteira otimizada não pode superar a inadimplência atual da carteira. Isso garante que o modelo não piore o risco do banco em relação ao cenário atual:

$$\sum_{k=1}^{K} n_k \cdot (PD_k - \overline{PD}_{fin}^{atual}) \cdot L_k \leq 0$$

onde $\overline{PD}_{fin}^{atual}$ é calculado como a média de `pd_produto` dos clientes elegíveis da base.

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

### `main.py`

Orquestra o pipeline completo:

1. Leitura do CSV de clientes e do JSON de parâmetros
2. Cálculo de $\overline{PD}_{fin}^{atual}$
3. Verificação de cache: se o arquivo clusterizado já existir, a clusterização é pulada
4. Montagem do problema ($c$, $A$, $b$) a partir dos clusters
5. Execução do Simplex
6. Pós-otimização e exibição dos resultados

## Parâmetros de entrada

A solução recebe dois arquivos como entrada:

### CSV de clientes

Arquivo com os dados individuais dos clientes elegíveis, localizado em `apps/data/csv/`. As colunas utilizadas pelo modelo são:

| Coluna                     | Descrição                                                                              |
| -------------------------- | -------------------------------------------------------------------------------------- |
| `pd_produto`               | Probabilidade de inadimplência no produto                                              |
| `capacidade_pagamento`     | Estimativa de capacidade de pagamento do cliente                                       |
| `score_credito_cross`      | Score de crédito multiproduto, usado para calcular $m_k$                               |
| `score_propensao_contrato` | Score de propensão à contratação, normalizado para obter $\pi_k$                       |
| `fx_idade`                 | Faixa etária do cliente                                                                |
| `flag_filtros`             | Indicador de perfil restrito: apenas clientes com `flag_filtros == 0` são elegíveis    |
| `renda_estimada`           | Usada como proxy de capacidade de pagamento quando `capacidade_pagamento` está ausente |

### JSON de parâmetros

Arquivo de configuração localizado em `apps/algoritmo_simplex/input/`, que permite customizar os parâmetros do modelo sem alterar o código. O arquivo padrão `parametros.json` contém:

```json
{
  "t": 0.0175,
  "LGD": 0.6,
  "u_bar": 0.75,
  "L_max": 25000.0
}
```

Onde:

- `t`: taxa de interchange (1,75%), fornecida pelo parceiro
- `LGD`: fração da exposição perdida em caso de default (60%), padrão de modelos de risco de crédito
- `u_bar`: fração esperada de utilização do limite (75%)
- `L_max`: teto máximo absoluto de limite por cluster (R$25.000), definido pelo parceiro

## Simplificações realizadas

De acordo com os requisitos do parceiro, a solução final deve operar com pelo menos 100 clusters para a base completa de mais de um milhão de clientes. Nesta versão simplificada, foram adotadas as seguintes reduções de escopo:

**Número de clusters:** foram utilizados 7 clusters em vez dos pelo menos 100 exigidos na entrega final. Essa simplificação reduz a dimensão do problema de programação linear, tornando a validação do algoritmo mais direta.

**Tamanho da base:** nos casos de teste, a base foi reduzida para aproximadamente 10% dos clientes originais, mantendo a proporcionalidade das características da base completa.

As restrições do modelo e o algoritmo Simplex implementado são independentes dessas simplificações e funcionarão sem alterações quando o número de clusters for expandido.

## Clusterização

A clusterização é feita de forma **não supervisionada**, utilizando **K-means**, visando juntar clientes elegíveis e com perfis semelhantes de **risco, capacidade de pagamento e propensão**, buscando viabilizar a otimização no nível de cluster.

### População considerada

Inicialmente, a base de dados é filtrada para incluir apenas clientes elegíveis (flag_filtros = 0). Além disso, apenas as 10% primeiras linhas da base de dados foram consideradas.

### Variáveis usadas na clusterização

O K-Means é treinado usando:

* pd_produto: (proxy de risco / probabilidade padrão do produto)

* cp_proxy: (proxy de capacidade de pagamento)

* score_credito_cross: (score multiproduto, também usado para derivar alavancagem)

* pi: (propensão nnormalizada)

* fx_idade (variável categórica, transformada com _one-hot encoding_)

### Pré-processamento

Antes do K-Means atuar em si, a variável pi é criada, na qual o score_propensao_contrato é normallizado para o intervalo [0, 1]. O cp_proxy também é definido, utiliznado a capacidade_pagamento quando existente. No caso de estar nula, o valor é substituido por renda_estimada * 0,3.

### Tratamento das variáveis

Para as variáveis numéricas, é aplicado a imputação de valores faltanates pela mediana, e os valores são padronizados pelo StandardScaler (média 0, desvio padrão 1). Já para a variável categórica, o OneHotEncoder transforma os valores de forma binária, permitindo que os mesmos funcionem com o K-means.

## Dependências

As dependências do projeto estão listadas em `apps/algoritmo_simplex/requirements.txt`. Para instalá-las:

```bash
pip install -r requirements.txt
```

As bibliotecas utilizadas são:

| Biblioteca     | Uso                                               |
| -------------- | ------------------------------------------------- |
| `pandas`       | Leitura e manipulação dos arquivos CSV            |
| `scikit-learn` | Algoritmo K-Means para clusterização dos clientes |
| `numpy`        | Cálculo de percentis na agregação dos clusters    |

O algoritmo Simplex em si não utiliza nenhuma biblioteca externa, foi implementado do zero com Python puro.

## Execução

A partir do diretório `apps/algoritmo_simplex/`:

```bash
python main.py <arquivo_clientes.csv> <parametros.json>
```

Exemplo:

```bash
python main.py clientes_reduzido.csv parametros.json
```

Na primeira execução, a clusterização é gerada automaticamente e salva em `apps/data/csv/<nome>_clusters.csv`. Nas execuções seguintes, o arquivo clusterizado é reutilizado, tornando a execução significativamente mais rápida.

## Saída dos dados

Ao final da execução, o algoritmo exibe no console o status da solução, o valor ótimo da função objetivo e o limite otimizado para cada cluster:

```
Status: otimo
Valor ótimo (z): 1234567.89

Limites ótimos por cluster:
  Cluster 0: R$ 1500 (n=72426)
  Cluster 1: R$ 800 (n=40096)
  Cluster 2: R$ 2050 (n=10897)
  Cluster 3: R$ 0 (n=40468)
  Cluster 4: R$ 1200 (n=97178)
  Cluster 5: R$ 650 (n=31288)
  Cluster 6: R$ 3000 (n=59103)
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

### Teste 4: Execução completa com base de clientes reduzida

**Entrada:** `clientes_reduzido.csv` com `parametros.json` padrão.

**Saída obtida:**

```
Status: otimo
Valor ótimo (z): 0.00

Limites ótimos por cluster:
  Cluster 0: R$ 0 (n=72426)
  Cluster 1: R$ 0 (n=40096)
  Cluster 2: R$ 0 (n=10897)
  Cluster 3: R$ 0 (n=40468)
  Cluster 4: R$ 0 (n=97178)
  Cluster 5: R$ 0 (n=31288)
  Cluster 6: R$ 0 (n=59103)
```

O algoritmo convergiu corretamente para o ótimo. O resultado com todos os limites zerados é matematicamente consistente com os dados da base atual: para que um cluster seja rentável, é necessário que seu $PD_k$ satisfaça:

$$PD_k < \frac{\bar{u} \cdot t}{\text{LGD}} = \frac{0{,}75 \times 0{,}0175}{0{,}60} \approx 2{,}19\%$$

A calibração dos parâmetros e a revisão dos dados de entrada serão realizadas em conjunto com o parceiro nas próximas sprints, com base nos dados reais da carteira.

## Conclusões

O algoritmo Simplex foi implementado do zero, sem uso de bibliotecas de otimização, e validado contra problemas com solução analítica conhecida. O pipeline completo, desde a leitura dos dados até a exibição dos limites otimizados por cluster, está funcional e documentado.

Os próximos passos previstos são:

- Revisão e calibração dos parâmetros do modelo com o parceiro
- Expansão do número de clusters para pelo menos 100, conforme requisito da entrega final
- Incorporação das restrições adicionais mapeadas no TAPI, como teto de inadimplência física, metas de produção mínima e rentabilidade mínima da carteira
