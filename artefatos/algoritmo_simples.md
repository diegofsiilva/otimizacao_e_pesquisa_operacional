# Contextualização

Após a realização da modelagem matemática, o próximo passo para a implementação da solução se trata da **resolução de umaa versão simplificada do problema**. Com a execução em um escopo simplificado, o **tratamento de erros** e **identificação de pontos de melhoria** se torna mais fácil, assim permitindo uma maior agilidade de desenvolvimento e robustez da entrega.

# Seleção do algoritmo

O algoritmo definido para ser implementado se trata do **Simplex**. Ele se trata de um **método iterativo** para a solução de **problemas lineares**, repetindo as suas etapas até encontrar a solução ótima. Ele atua **navegando através dos vértices** existentes dentro da região viável (que é definida por meio das restrições do problema, mapeadas na modelagem matemática), buscando maximizar ou minimizar a função objetivo. No caso do projeto, o objetivo é **maximizar o lucro** durante a oferta de limites de crédito.

# Simplificações realizadas

As principal simplificação realizada está relacionada à **formação dos _clusters_**. De acordo com as requisições do parceiro, a solução precisa atuar com, no mínimo, **100 _clusters_** para os mais de um milhão de clientes. Dessa maneira, a base de dados foi limitada para por volta de **50.000 clientes**, tendo um número proporcional de **5 _clusters_**. 

## Critérios de clusterização

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

## Tratamento das variáveis

Para as variáveis numéricas, é aplicado a imputação de valores faltanates pela mediana, e os valores são padronizados pelo StandardScaler (média 0, desvio padrão 1). Já para a variável categórica, o OneHotEncoder transforma os valores de forma binária, permitindo que os mesmos funcionem com o K-means.

# Parâmetros de entrada

Além da base de dados, a solução também permitirá a **customização** de certos **parâmetros** do modelo. A configuração poderá ser feita através de um **arquivo .json**, localizado ao lado do código para a execução do algoritmo e a base de dados. Assim, a primeira etapa será a **leitura parcial da base de dados** (de acordo com as simplificações mencionadas anteriormente), **divisão dos clientes em _clusters_**, e **customização da função objetivo** com base nos parâmetros alterados. No caso do arquivo .json não estar presente, a função objetivo adotará os parâmetros padrão também mapeados durante a modelagem matemática.

Os parâmetros que podem ser customizados são:

* Taxa de _interchange_ - padrão: 0,0175

* LGD (_Loss Given Default_) - valor entre 0 e 1, padrão: 0,60


* Utilização esperada do limite - valor entre 0 e 1, padrão: 0,75

* Teto máximo do limite - padrão: 25.000

# Execução do algoritmo

# Saída dos dados

# Testes realizados 

# Conclusões   