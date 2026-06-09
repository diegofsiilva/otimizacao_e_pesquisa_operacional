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

---

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

---

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

---

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

---

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

---

## 2.7 Pior Caso

O pior caso ocorre quando o solver precisa explorar grande quantidade de bases ou nós internos para encontrar a solução ótima.

Como o CBC utiliza algoritmos derivados do Simplex, seu pior caso teórico continua sendo exponencial.

Assim:

$$
O(T_{solver}(n,m))
$$

onde, no pior caso, o custo pode ser exponencial.

---

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