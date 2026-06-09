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
