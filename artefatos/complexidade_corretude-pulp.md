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
    pulp.LpVariable(f"x_{j}", lowBound=0.0, cat=pulp.LpContinuous)
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

Para o PL específico do projeto, $n = K$ e $m = 2K + 1$, de modo que a construção do modelo é:

$$
T_3(K)=\Theta(K\cdot(2K+1)) = \Theta(K^2).
$$

## 2.4 Resolução do Modelo

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

## 2.5 Extração da Solução

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

## 2.6 Melhor Caso

O melhor caso ocorre quando:

- a construção do modelo é realizada normalmente;
- o solver encontra rapidamente uma solução ótima.

Como a etapa de construção das restrições precisa sempre percorrer toda a matriz $A$, existe um limite inferior:

$$
\Omega(mn)
$$

## 2.7 Pior Caso

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

## 2.8 Regimes de Solver

| Solver | Regime teórico principal | Observação |
| ------ | ------------------------ | ---------- |
| CBC | Simplex / pivoteamento | para LP contínuo; não aciona Branch-and-Bound aqui |
| GLPK | Simplex / pivoteamento | para LP contínuo; não aciona Branch-and-Bound aqui |
| HiGHS | pontos interiores / simplex | fallback com potencial regime polinomial |

Branch-and-Bound só se aplicaria se o modelo tivesse variáveis inteiras; em `simplex_pulp.py` o modelo é contínuo.

## 2.9 Complexidade Total

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

## 2.9 Quadro-resumo de Complexidade

| Etapa | Complexidade | Nota |
| ------ | ------------ | ---- |
| Construção do modelo | $\Theta(mn)$ | $\Theta(K^2)$ para $n=K$, $m=2K+1$ |
| Resolução pelo solver | $T_{solver}(n,m)$ | depende do solver selecionado no ambiente |
| Extração de $x$, $z$ e status | $\Theta(n)$ | custo linear no número de variáveis |

## 2.10 Complexidade de Espaço

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

Esse é o laço principal a ser analisado neste módulo porque a otimização em si é delegada ao solver externo.

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

## 3.4 Terminação

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

## 3.5 Corretude Parcial

Pela demonstração do invariante, ao final do laço o modelo PuLP é exatamente equivalente ao problema original.

Essa análise assume explicitamente que o solver externo resolve corretamente o problema contínuo de programação linear. Essa é a mesma premissa de corretude do Simplex e da dualidade em Dantzig (1963) para LP contínuo.

Consequentemente:

- toda solução viável do modelo corresponde a uma solução viável do problema original;
- toda solução ótima do modelo corresponde a uma solução ótima do problema original.

Logo, caso o solver retorne uma solução ótima, essa solução é correta para o problema originalmente recebido pela implementação.

## 3.6 Corretude Total

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

# 4. Referências

BAZARAA, Mokhtar S.; JARVIS, John J.; SHERALI, Hanif D. Linear Programming and Network Flows. 4. ed. Hoboken: John Wiley & Sons, 2010.

BRASIL. Associação Brasileira de Normas Técnicas. ABNT NBR 6023: Informação e documentação – Referências – Elaboração. Rio de Janeiro: ABNT, 2018.

BRASIL. Associação Brasileira de Normas Técnicas. ABNT NBR 10520: Informação e documentação – Citações em documentos – Apresentação. Rio de Janeiro: ABNT, 2023.

COIN-OR FOUNDATION. PuLP: a Linear Programming Toolkit for Python. [S. l.], 2025. Disponível em: https://coin-or.github.io/pulp/. Acesso em: 09 jun. 2026.

CORMEN, Thomas H.; LEISERSON, Charles E.; RIVEST, Ronald L.; STEIN, Clifford. Algoritmos: Teoria e Prática. 3. ed. Rio de Janeiro: Elsevier, 2012.

HILLIER, Frederick S.; LIEBERMAN, Gerald J. Introduction to Operations Research. 11. ed. New York: McGraw-Hill Education, 2021.

KLEINBERG, Jon; TARDOS, Éva. Algorithm Design. Boston: Pearson Addison-Wesley, 2006.

MITCHELL, Stuart; DEDMAN, Franco; KEARNES, Daniel. PuLP Documentation. COIN-OR Foundation, 2025. Disponível em: https://coin-or.github.io/pulp/guides/index.html. Acesso em: 09 jun. 2026.

ROSEN, Kenneth H. Discrete Mathematics and Its Applications. 8. ed. New York: McGraw-Hill Education, 2019.

SIPSER, Michael. Introdução à Teoria da Computação. 3. ed. São Paulo: Cengage Learning, 2013.

SKIENA, Steven S. The Algorithm Design Manual. 3. ed. Cham: Springer, 2020.

TAHA, Hamdy A. Pesquisa Operacional. 8. ed. São Paulo: Pearson Prentice Hall, 2008.