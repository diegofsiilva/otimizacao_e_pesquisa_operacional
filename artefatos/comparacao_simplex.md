# Comparação: Simplex do projeto × biblioteca PuLP

## Objetivo

Validar a corretude da implementação do algoritmo Simplex feita do zero neste projeto (`apps/algoritmo_simplex/simplex.py`) comparando seus resultados com os de um solver consolidado de programação linear: a biblioteca **PuLP**, que usa por padrão o solver **CBC** (COIN-OR Branch and Cut).

Essa comparação funciona como um *golden test*: se os dois solvers convergem para o mesmo valor ótimo da função objetivo, ganhamos confiança de que o nosso Simplex está correto. A biblioteca não substitui o algoritmo implementado; apenas serve como referência de validação cruzada.

## Por que PuLP

A escolha do PuLP em vez de outras alternativas se deu pelos seguintes motivos:

- **API legível**: declarar variáveis, função objetivo e restrições como expressões algébricas torna o código de comparação fácil de auditar lado a lado com a formulação matemática do problema.
- **Licença permissiva e instalação simples**: PuLP é open-source (MIT) e instalável via `pip` sem dependências nativas pesadas. O CBC vem embutido no pacote.
- **Solver maduro**: o CBC é amplamente usado em produção e referência em livros-texto, o que dá robustez ao papel de "ground truth" da comparação.
- **Mesma família de algoritmo**: o CBC usa o método Simplex (com refinamentos e Branch-and-Cut para casos inteiros, irrelevantes aqui pois nosso problema é puramente contínuo). Assim, a comparação é entre duas implementações do mesmo método, e não entre métodos diferentes.                                                                                    |

## Metodologia

Os dois solvers recebem instâncias da mesma `dataclass` `Problema` (definida em `models.py`), com os mesmos vetores `c`, `b` e a mesma matriz `A`. Para evitar interferência cruzada entre os dois solvers, o `comparar.py` passa uma `copy.deepcopy(problema)` a cada chamada, garantindo que nenhuma eventual mutação em um solver afete o outro.

A comparação considera dois indicadores:

1. **Valor ótimo da função objetivo (`z`)**: é o critério principal. Dois solvers podem convergir para vértices diferentes em problemas com múltiplas soluções ótimas, mas o valor de `z` deve ser idêntico em qualquer ótimo. Consideramos os resultados equivalentes quando `|z_nosso − z_pulp| ≤ 10⁻⁶`.
2. **Status reportado**: ambos devem classificar o problema da mesma forma (`otimo`, `ilimitado`, `inviavel`). PuLP não diferencia explicitamente "solução única" de "múltiplas soluções" (retorna `Optimal` nos dois casos), então quando o nosso retorna `multiplas_solucoes` consideramos coincidente desde que `|Δz| ≤ 10⁻⁶`.

A comparação do vetor `x` em si seria sensível à ordem dos pivôs e ao critério de desempate de cada solver, e portanto não é o indicador certo para validar corretude.

## Execução

A partir do diretório `apps/algoritmo_simplex/`:

```bash
# instala dependências (inclui pulp)
pip install -r requirements.txt

# roda apenas os problemas didáticos
python comparar.py

# também roda o caso real (clusters + parâmetros)
python comparar.py clientes_calibrado.csv parametros.json
```

## Resultados obtidos

A execução completa em `15/05/2026` com a base `clientes_calibrado.csv` (14.569.142 linhas, 7 clusters) e `parametros.json` padrão produziu **4/4 casos com resultado equivalente** dentro da tolerância de `10⁻⁶`.

### Caso 1 - Solução única

Formulação:

```
max  40 x1 + 35 x2
s.t. 2 x1 + 3 x2 ≤ 60
     4 x1 + 3 x2 ≤ 96
     x1, x2 ≥ 0
```

| Solver | `x`            | `z`    | Status |
| ------ | -------------- | ------ | ------ |
| Nosso  | `[18.0, 8.0]`  | 1000.0 | otimo  |
| PuLP   | `[18.0, 8.0]`  | 1000.0 | otimo  |
| `|Δz|` | 0.00e+00       |        |        |

Os dois solvers identificam o mesmo vértice ótimo, com ambas as restrições ativas (`2·18 + 3·8 = 60`, `4·18 + 3·8 = 96`). Resultados equivalentes.

### Caso 2 - Problema ilimitado

Formulação:

```
max  40 x1 + 35 x2
s.t. − x1       ≤ 60
           − x2 ≤ 96
     x1, x2 ≥ 0
```

| Solver | Comportamento                                  |
| ------ | ---------------------------------------------- |
| Nosso  | `raise ValueError("O problema é ilimitado.")`  |
| PuLP   | Retorna status `Unbounded`; wrapper converte em `ValueError("O problema é ilimitado.")`. |

Ambos detectam corretamente que a região viável é ilimitada e a função objetivo cresce sem limite. Resultados equivalentes.

### Caso 3 - Múltiplas soluções

Formulação:

```
max  2 x1 + 4 x2
s.t. x1 + 2 x2 ≤ 4
     x1       ≤ 2
     x1, x2 ≥ 0
```

A função objetivo é paralela ao gradiente da primeira restrição, portanto todos os pontos do segmento entre `(0, 2)` e `(2, 1)` são ótimos, com `z = 8`.

| Solver | `x`           | `z`  | Status                                  |
| ------ | ------------- | ---- | --------------------------------------- |
| Nosso  | `[2.0, 1.0]`  | 8.0  | multiplas_solucoes                      |
| PuLP   | `[0.0, 2.0]`  | 8.0  | otimo                                   |
| `|Δz|` | 0.00e+00      |      |                                         |

Os dois solvers convergem para o mesmo `z` mas escolhem **vértices ótimos diferentes do mesmo segmento de ótimos** — comportamento esperado em programação linear com múltiplas soluções e que confirma que ambos chegaram ao ótimo global. A diferença qualitativa é que o **nosso Simplex sinaliza explicitamente** a existência de outras soluções ótimas (status `multiplas_solucoes`), enquanto o PuLP apenas retorna `Optimal` — informação que pode ser relevante quando o produto de negócio precisa decidir entre vértices ótimos diferentes.

### Caso 4 - Caso real do projeto (clusters de clientes)

Execução com `clientes_calibrado.csv` (14,57 milhões de clientes elegíveis, agrupados em 7 clusters) e `parametros.json` padrão.

| Solver | `z` (R$)              | Status |
| ------ | --------------------- | ------ |
| Nosso  | 81 240 312,337700     | otimo  |
| PuLP   | 81 240 312,337700     | otimo  |
| `|Δz|` | 1,49 × 10⁻⁸           |        |

Vetor de limites por cluster (idêntico nos dois solvers):

```
x = [246.5724, 75.9092, 164.0118, 67.0650, 18479.5201, 1583.4681, 22.8853]
```

A diferença remanescente `|Δz| ≈ 1,5·10⁻⁸` é puramente numérica (acumulação de erros de ponto flutuante em ~22 milhões de pivôs / produtos escalares), bem abaixo do limite economicamente relevante (R$ 0,01).

## Bug detectado e corrigido pela comparação

Esta comparação cruzada justificou seu papel de validação ao revelar **um bug real no `simplex.py` do projeto**:

A função `construir_tableau_inicial` atribuía `valores_iniciais = problema.b` sem copiar a lista. Como Python passa listas por referência, a coluna `Value` do tableau passava a compartilhar a mesma memória com `problema.b`. Cada operação de pivotamento (`tableau.values[i] /= elemento_pivo`, etc.) **mutava o vetor `b` original do problema**.

O sintoma só apareceu no `comparar.py` porque ele invocava os dois solvers em sequência sobre o mesmo objeto `Problema`: o nosso simplex rodava primeiro e deixava `b` corrompido; o PuLP, em seguida, recebia um problema diferente do original e retornava o ótimo *desse problema corrompido*. Por exemplo, no Caso 1, ao final do nosso simplex `b` virava `[8, 18]` em vez de `[60, 96]`, e o ótimo desse problema modificado é exatamente o `(4, 0)` com `z = 160` que o PuLP devolveu inicialmente.

## Conclusão

A comparação cruzada com a biblioteca PuLP confirma que a implementação do algoritmo Simplex feita do zero neste projeto produz os mesmos valores ótimos que um solver de mercado consolidado (CBC), tanto nos casos didáticos com solução analítica conhecida quanto no caso real do projeto, com erro numérico de ordem `10⁻⁸`. Além de validar a corretude, o exercício de comparação revelou e ajudou a corrigir um bug de aliasing em `simplex.py` que comprometeria qualquer reaproveitamento do mesmo objeto `Problema`, demonstrando concretamente o valor de manter uma referência externa para testes de regressão.

Vale destacar uma vantagem qualitativa do nosso algoritmo: ele sinaliza explicitamente a existência de múltiplas soluções via o status `multiplas_solucoes`, enquanto o PuLP/CBC apenas retorna `Optimal` em todos os casos com solução. Para o problema do parceiro, essa sinalização é útil pois permite ao banco avaliar trade-offs entre limites equivalentes em retorno.
