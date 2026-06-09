# Complexidade e Corretude da Implementação com PuLP

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

# 2. Análise de Complexidade

## 2.1 Construção das Variáveis

As variáveis são criadas pelo trecho:

```python
x_vars = [
    pulp.LpVariable(f"x_{j}", lowBound=0.0)
    for j in range(n)
]
```

São criadas exatamente $n$ variáveis.

$$
T_1(n)=\Theta(n)
$$

## 2.2 Construção da Função Objetivo

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

## 2.3 Construção das Restrições

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

## 2.4 Resolução do Modelo

O trecho:

```python
modelo.solve(solver)
```

transfere o problema para o solver externo.

O custo desta etapa depende do algoritmo interno utilizado pelo solver selecionado.

No caso do CBC (solver padrão), o método utilizado é baseado em variantes do Simplex e Branch-and-Bound.

Assim, não é possível determinar uma complexidade exata apenas analisando o código Python.

Denotando por $T_{solver}(n,m)$ o custo do solver:

$$
T_4(n,m)=T_{solver}(n,m)
$$

## 2.5 Extração da Solução

Após a resolução, os valores são copiados para listas Python:

```python
x = [float(pulp.value(v)) for v in x_vars]
```

O custo é proporcional ao número de variáveis.

$$
T_5(n)=\Theta(n)
$$

## 2.6 Melhor Caso

O melhor caso ocorre quando:

- a construção do modelo é realizada normalmente;
- o solver encontra rapidamente uma solução ótima.

Como a etapa de construção das restrições precisa sempre percorrer toda a matriz $A$, existe um limite inferior:

$$
\Omega(mn)
$$

## 2.7 Pior Caso

O pior caso ocorre quando o solver precisa explorar grande quantidade de bases ou nós internos para encontrar a solução ótima.

Como o CBC utiliza algoritmos derivados do Simplex, seu pior caso teórico continua sendo exponencial.

Assim:

$$
O(T_{solver}(n,m))
$$

onde, no pior caso, o custo pode ser exponencial.

## 2.8 Complexidade Total

A construção do modelo possui custo:

$$
\Theta(mn)
$$

A resolução é dominada pelo solver:

$$
T(n,m)=
\Theta(mn)+
T_{solver}(n,m)
\]

Portanto:

$$
\boxed{
T(n,m)=\Theta(mn + T_{solver}(n,m))
}
$$

## 2.9 Complexidade de Espaço

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

# 3. Corretude

A corretude da implementação com PuLP será demonstrada em duas etapas:

1. Corretude da construção do modelo de Programação Linear;
2. Corretude da solução retornada pelo solver.

Como o módulo `simplex_pulp.py` não implementa diretamente um algoritmo de otimização, mas sim constrói um modelo matemático e o envia para um solver externo, o objetivo da prova é demonstrar que o modelo construído é exatamente equivalente ao problema original.

## 3.1 Pré-condição

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

## 3.2 Invariante do Laço Principal

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

### Invariante P

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

### P1

Todas as variáveis do problema original já foram criadas no modelo.

### P2

A função objetivo do modelo é exatamente a função objetivo do problema original.

### P3

As primeiras $k$ restrições do problema original foram adicionadas corretamente ao modelo.

### P4

Nenhuma restrição previamente inserida foi removida ou modificada.


## 3.3 Prova do Invariante por Indução

### Caso Base

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


### Hipótese de Indução

Suponha que após a iteração $k$ o invariante seja verdadeiro.

Ou seja:

- todas as variáveis continuam presentes;
- a função objetivo permanece correta;
- as primeiras $k$ restrições foram adicionadas corretamente;
- nenhuma delas foi alterada.


### Passo Indutivo

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


### Conclusão da Indução

Como:

1. o invariante é verdadeiro no caso base;
2. sua validade após uma iteração implica sua validade na próxima;

segue pelo Princípio da Indução Matemática que o invariante é verdadeiro para todas as iterações do laço.

Ao término da última iteração, quando $k = m$, o modelo contém:

- todas as variáveis do problema;
- a função objetivo original;
- todas as restrições do problema original.

Portanto, o modelo construído é matematicamente equivalente ao problema de programação linear fornecido como entrada.