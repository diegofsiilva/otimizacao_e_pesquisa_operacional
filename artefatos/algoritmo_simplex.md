# Algoritmo Simplex

## Contextualização

O Banco Pan oferece cartões de crédito pré-aprovados a clientes correntistas. A decisão de qual limite de crédito oferecer a cada cliente é hoje tomada com base em tabelas fixas, que não consideram a heterogeneidade entre perfis e não controlam o risco agregado da carteira.

O objetivo deste projeto é substituir essa regra empírica por uma decisão matemática: encontrar, para cada grupo de clientes com perfil semelhante, o limite que **maximize o retorno líquido esperado do banco**, definido como a receita de interchange acumulada ao longo do horizonte de uso menos a perda esperada por inadimplência, respeitando restrições de risco, capacidade de pagamento e concentração definidas pelo parceiro.

O problema foi formulado como um **Problema de Programação Linear (PL)**, onde as variáveis de decisão são os limites de crédito a serem atribuídos a cada cluster. A solução desse PL é encontrada por meio do **algoritmo Simplex**, implementado neste artefato. A modelagem matemática completa, incluindo a calibração temporal e a derivação de $\gamma_d$ por decil, está em [`artefatos/modelagem_matematica.md`](modelagem_matematica.md) (Seções 1.5, 1.5.1 e 1.6) — este documento é a fonte da verdade e qualquer divergência observada deve ser resolvida a favor dele.

## O problema de programação linear

### Variáveis de decisão

Os clientes elegíveis são agrupados em $K = 10$ clusters por decil de `pd_produto` (alinhados com a calibração $\gamma_d$ da Seção 1.5.1 da modelagem). Para cada cluster $k$, a variável de decisão é:

$$L_k \geq 0 \quad \text{(limite de crédito a ser ofertado ao cluster } k\text{)}$$

### Função objetivo

O banco busca maximizar o retorno líquido total esperado da carteira no horizonte de $T$ meses:

$$\max \sum_{k=1}^{K} n_k \cdot \pi_k \cdot (T \cdot \bar{u} \cdot t - PD_k \cdot \gamma_{d(k)} \cdot \text{LGD}) \cdot L_k$$

O coeficiente de cada cluster é $c_k = n_k \cdot \pi_k \cdot (T \cdot \bar{u} \cdot t - PD_k \cdot \gamma_{d(k)} \cdot \text{LGD})$. Clusters com $c_k > 0$ são rentáveis; clusters com $c_k \leq 0$ destroem valor a cada real adicional de limite e recebem $L_k = 0$ como solução natural. A inclusão de $T$ (horizonte de receita em meses) e $\gamma_{d(k)}$ (calibração da PD anual do scoring para o horizonte de uso) corrige o mismatch temporal da formulação original: sem esses dois ajustes, o limiar de rentabilidade $\bar{u}t/\text{LGD} \approx 2{,}19\%$ ficava abaixo da PD mínima da base ($\approx 3\%$), e o solver retornava $L_k = 0$ para todos os clusters (solução trivial).

Os parâmetros utilizados na função objetivo:

| Parâmetro                       | Descrição                                                                  | Valor padrão |
| ------------------------------- | -------------------------------------------------------------------------- | -----------: |
| $n_k$                           | Número de clientes no cluster $k$                                          |   calculado |
| $\pi_k$                         | Propensão média de contratação do cluster $k$ (normalizada em [0,1])       |   calculado |
| $\bar{u}$                       | Fração esperada de utilização do limite                                    |       0,75   |
| $t$                             | Taxa de interchange mensal                                                 |     0,0175   |
| $T$                             | Horizonte de receita em meses (período médio de uso do limite)             |       22     |
| $PD_k$                          | Probabilidade de inadimplência média do cluster $k$ (anual, scoring bruto) |   calculado |
| $\gamma_{d(k)}$                 | Calibração da PD no decil $d$ (ver Seção 1.5.1 da modelagem)               |   por decil |
| $\text{LGD}$                    | Loss Given Default                                                         |       0,80   |
| $\overline{PD}_{fin}^{atual}$   | Teto de inadimplência financeira da carteira (RHS de R1)                   |       0,32   |
| $\alpha$                        | Concentração máxima por cluster (RHS de R5)                                |       0,30   |
| $L^{max}$                       | Teto absoluto de limite por cluster                                        |    25.000    |

**Calibração de $\gamma_d$ por decil:** valores adotados (D1..D10) = $[0{,}21,\; 0{,}21,\; 0{,}24,\; 0{,}24,\; 0{,}44,\; 0{,}40,\; 0{,}40,\; 0{,}40,\; 0{,}40,\; 0{,}40]$, derivados empiricamente da razão $\text{over30mob3}/\text{pd\_produto}$ por decil sobre 17.366 clientes observados e ~5,9M de elegíveis (Seção 1.5.1 da modelagem). Os decis D6–D10 usam extrapolação linear conservadora devido à amostra reduzida.

### Restrições

**R1 - Teto de inadimplência financeira ponderada (LP).** A inadimplência financeira ponderada da carteira otimizada não pode exceder o teto $\overline{PD}_{fin}^{atual} = 0{,}32$, definido como a PD média ponderada da carteira aprovada vigente do banco:

$$\sum_{k=1}^{K} n_k \cdot (PD_k - \overline{PD}_{fin}^{atual}) \cdot L_k \leq 0$$

A formulação linearizada parte da razão $\sum n_k PD_k L_k / \sum n_k L_k \leq 0{,}32$, multiplicando ambos os lados pelo denominador (positivo para qualquer solução não-trivial). O valor 0,32 vem da carteira aprovada vigente do banco, não da PD média dos elegíveis — esta última (~0,44–0,51) é mais alta e nunca seria binding, deixando o gargalo da carteira fora de controle.

**R2 - Capacidade de pagamento com alavancagem (LP).** O limite de cada cluster é limitado pelo percentil 5 da capacidade de pagamento dos seus membros, multiplicado pelo fator $m_k$:

$$L_k \leq m_k \cdot CP_k, \quad \forall k$$

O multiplicador $m_k \in [0{,}20;\; 0{,}45]$ é atribuído ao cluster conforme a média de `score_credito_cross` dos seus membros, em cinco faixas (Seção 1.5 da modelagem):

| Faixa de `score_credito_cross` | $m_k$ |
| :----------------------------- | ----: |
| 100 – 700                      | 0,20  |
| 700 – 800                      | 0,25  |
| 800 – 850                      | 0,30  |
| 850 – 900                      | 0,35  |
| 900 – 960                      | 0,45  |

Essas faixas foram calibradas a partir do percentil 75 da alavancagem observada na política vigente (`limite_ofertado / capacidade_pagamento`) sobre 480 mil registros elegíveis com oferta nas safras M1–M3.

**R3 - Teto máximo de limite (LP).** Teto absoluto definido pelo parceiro:

$$L_k \leq L^{max} = 25.000, \quad \forall k$$

Na prática, R2 é o gargalo dominante e R3 atua como salvaguarda.

**R5 - Concentração máxima por cluster (LP).** Nenhum cluster pode concentrar mais do que uma fração $\alpha$ da exposição total:

$$n_k \cdot L_k - \alpha \cdot \sum_{j=1}^{K} n_j \cdot L_j \leq 0, \quad \forall k$$

Equivale a $K$ restrições lineares adicionais. Sem R5, o solver tende a despejar a maior parte do orçamento de risco no cluster com maior $c_k$ e maior $CP$ (tipicamente D1), gerando uma carteira rentável mas concentrada e vulnerável a choques setoriais. Com $\alpha = 0{,}30$, nenhum cluster pode ter mais de 30 % da exposição total.

**R4 - Teto de inadimplência física (pós-otimização).** Tratada após a solução do LP por envolver indicadoras de cluster ativo (não-linear). Implementação descrita na Seção 1.7 da modelagem.

**R6 - Meta de produção mínima (opcional).** $\sum_k n_k L_k \geq V^{min}$. Não habilitada no cenário base ($V^{min} = 0$); pode ser incluída como restrição linear adicional se o parceiro estipular um piso de volume.

## O algoritmo Simplex

### Ideia central

O Simplex parte de uma propriedade fundamental da programação linear: a solução ótima de um problema linear sempre se encontra em um **vértice da região viável**. A região viável é o conjunto de todos os pontos que satisfazem simultaneamente todas as restrições do problema.

O algoritmo navega pelos vértices da região viável da seguinte forma:

1. Começa em um vértice inicial (a origem, onde todos os limites $L_k = 0$).
2. A cada iteração, avalia se existe algum vértice vizinho com retorno maior.
3. Se existir, salta para esse vértice.
4. Repete até que nenhum vértice vizinho seja melhor que o atual.

### Variáveis de folga

Restrições do tipo $\leq$ são convertidas em igualdades por variáveis de folga. Por exemplo, $L_k \leq m_k \cdot CP_k$ vira $L_k + s_k = m_k \cdot CP_k,\; s_k \geq 0$.

### A tabela do Simplex

| Contribution | Base  | Value | $L_1$    | $L_2$    | ... | $s_1$ | $s_2$ | ... |
| ------------ | ----- | ----- | -------- | -------- | --- | ----- | ----- | --- |
| $c_{B_1}$    | $s_1$ | $b_1$ | $a_{11}$ | $a_{12}$ | ... | 1     | 0     | ... |
| $c_{B_2}$    | $s_2$ | $b_2$ | $a_{21}$ | $a_{22}$ | ... | 0     | 1     | ... |

Onde **Contribution** é o coeficiente da variável da base na FO, **Base** é a variável ativa naquela linha, **Value** é o valor atual e as demais colunas são os coeficientes nas equações de restrição.

### Critério de entrada e saída da base

A cada iteração, o algoritmo calcula para cada variável $j$ o ganho líquido $c_j - z_j$, onde $z_j = \sum_i c_{B_i} \cdot a_{ij}$. Se $c_j - z_j > 0$, trazer $j$ para a base aumenta o retorno. A implementação usa a **Regra de Bland** (menor índice com $c_j - z_j > 0$), que garante terminação mesmo sob degeneração. Para a saída, aplica-se o **teste da razão mínima**: divide-se o valor de cada variável da base pelo coeficiente correspondente da variável que entra e seleciona-se a linha de menor razão positiva.

### Pivotamento

Em duas etapas: (i) normalizar a linha pivô dividindo pelo elemento pivô; (ii) zerar a coluna pivô nas demais linhas subtraindo múltiplos da linha pivô.

### Tratamento de casos especiais

**Problema ilimitado:** se nenhuma linha apresentar coeficiente positivo para a variável que entraria na base, o algoritmo lança erro. **Múltiplas soluções:** se ao atingir o ótimo alguma variável fora da base ainda apresentar $c_j - z_j = 0$, o solver retorna uma solução e informa o status `multiplas_solucoes`. **Degeneração:** resolvida pela Regra de Bland.

## Estrutura da implementação

A implementação está organizada em quatro arquivos dentro de `apps/algoritmo_simplex/`:

### `models.py`

- `Problema`: agrupa $c$, $A$, $b$. Esses dados nunca mudam durante a execução.
- `Tableau`: estado atual do Simplex, atualizado a cada pivotamento.

### `simplex.py`

Implementação pura do algoritmo, sem qualquer dependência da lógica de negócio do projeto e **sem nenhuma biblioteca de otimização**. Recebe um `Problema` e devolve $L_k^*$, $Z^*$ e o status. Este arquivo não é alterado pela atualização de modelagem: o algoritmo está correto e atende o requisito de "sem libs prontas".

### `clustering.py`

Faz o agrupamento primário **por decil de `pd_produto`** sobre os elegíveis (`flag_filtros == 0`), gerando 10 clusters alinhados com $\gamma_d$. Para cada cluster, agrega $n_k$, $PD_k$, $\pi_k$, $CP_k$ (percentil 5) e o score médio para mapeamento de $m_k$ por faixa. A coluna `gamma_decil` é incluída no CSV de saída, refletindo o $\gamma_d$ correspondente ao decil de cada cluster.

### `main.py`

Orquestra o pipeline completo: leitura do CSV de clientes e do JSON de parâmetros, geração ou reuso do CSV clusterizado, aplicação dos $\gamma_d$ correntes do JSON sobre o cluster CSV (útil para cenários de drift), montagem das matrizes do LP (FO + R1 + R2 + R3 + R5), execução do Simplex e exibição do resultado com volume total, PD ponderada e folgas das restrições.

## Parâmetros de entrada

### CSV de clientes

Arquivo com os dados individuais dos clientes elegíveis, em `apps/data/csv/`. Colunas utilizadas:

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

Em `apps/algoritmo_simplex/input/`. O arquivo `parametros_base.json` contém:

```json
{
  "t": 0.0175,
  "LGD": 0.80,
  "u_bar": 0.75,
  "L_max": 25000.0,
  "T": 22,
  "gamma_decil": [0.21, 0.21, 0.24, 0.24, 0.44, 0.40, 0.40, 0.40, 0.40, 0.40],
  "edges_pd": [0.0, 0.211, 0.296, 0.378, 0.461, 0.543, 0.619, 0.687, 0.746, 0.804, 1.01],
  "pd_fin_max": 0.32,
  "alpha_conc": 0.30
}
```

| Campo         | Descrição                                                                  |
| ------------- | -------------------------------------------------------------------------- |
| `t`           | Taxa de interchange mensal (1,75 %)                                        |
| `LGD`         | Loss Given Default                                                         |
| `u_bar`       | Fração esperada de utilização                                              |
| `L_max`       | Teto absoluto de limite por cluster                                        |
| `T`           | Horizonte de receita em meses                                              |
| `gamma_decil` | $\gamma_d$ por decil ($d=1..10$), calibração empírica da Seção 1.5.1       |
| `edges_pd`    | Bordas dos 10 decis de `pd_produto` (11 valores)                           |
| `pd_fin_max`  | Teto de inadimplência financeira ponderada da carteira (RHS de R1)         |
| `alpha_conc`  | Fração máxima de concentração por cluster (RHS de R5)                      |

## Clusterização

A clusterização é feita por **decil de `pd_produto`** (10 clusters), alinhando o número de clusters com a calibração $\gamma_d$ derivada na modelagem. Esta escolha tem três motivações: (i) a calibração $\gamma_d$ é definida por decil, então usar 10 clusters preserva a granularidade da calibração sem agregação adicional; (ii) os decis são determinísticos a partir das bordas em `edges_pd`, evitando a dependência de sementes aleatórias do K-Means; (iii) o agrupamento por PD captura a heterogeneidade de risco que mais impacta o LP (PD entra tanto na FO quanto em R1).

### População considerada

Apenas clientes elegíveis (`flag_filtros == 0`). Em cada decil, agrega-se $n_k$, $PD_k$ (média), $\pi_k$ (média), $CP_k$ (percentil 5 da `capacidade_pagamento`, com proxy `renda_estimada * 0,30` quando nula) e o score médio para mapeamento de $m_k$.

### Coluna `gamma_decil` no CSV de saída

O CSV `<base>_clusters.csv` inclui a coluna `gamma_decil` correspondente ao decil de cada cluster, lida diretamente do JSON de parâmetros. Em `main.py` o valor é atualizado a partir do JSON corrente antes da montagem do LP, de modo que cenários de drift (que alteram apenas $\gamma_d$) reutilizam o mesmo cluster CSV sem refazer a clusterização.

## Dependências

| Biblioteca     | Uso                                               |
| -------------- | ------------------------------------------------- |
| `pandas`       | Leitura e manipulação dos arquivos CSV            |
| `numpy`        | Cálculo de percentis na agregação dos clusters    |

O algoritmo Simplex em si não utiliza nenhuma biblioteca de otimização e foi implementado em Python puro a partir do tableau e da Regra de Bland, atendendo o requisito de "sem libs prontas".

## Execução

A partir do diretório `apps/algoritmo_simplex/`:

```bash
python main.py <arquivo_clientes.csv> <parametros.json>
```

Exemplos:

```bash
python main.py clientes_reduzido.csv parametros_base.json
python main.py clientes_reduzido.csv parametros_conservador.json
python main.py clientes_reduzido.csv parametros_agressivo.json
python main.py clientes_reduzido.csv parametros_drift.json
```

Na primeira execução com um CSV de clientes novo, a clusterização é gerada automaticamente. Nas execuções seguintes, o cluster CSV é reutilizado, e o $\gamma_d$ corrente do JSON é re-aplicado sobre o cluster CSV antes da montagem do LP.

## Saída dos dados

Ao final da execução, `main.py` imprime no console:

1. Status do solver (`otimo`, `multiplas_solucoes` ou `ilimitado`) e $Z^*$ em R\$.
2. Tabela por cluster com $n_k$, $PD_k$, $\gamma_d$, $m_k$, $m_k \cdot CP_k$, $L_k^*$, $L_k^{final}$ (após pós-otim) e $n_k \cdot L_k^*$.
3. Resumo: $Z^*$, volume total, PD ponderada resultante e número de clusters ativos.
4. Folgas e binding das restrições R1, R2 (por cluster) e R5 (por cluster).

A pós-otimização (Seção 1.7 da modelagem) é aplicada ao mostrar $L_k^{final}$: arredondamento para múltiplo de 50 quando $L_k \geq 200$ e zero caso contrário.

## Testes realizados

### Teste 1: Validação do algoritmo com problema de solução conhecida

Antes de aplicar o algoritmo ao problema real, foi utilizado um problema clássico com solução analítica conhecida:

```
Max z = 40x1 + 35x2
s.t.
2x1 + 3x2 <= 60
4x1 + 3x2 <= 96
x1, x2 >= 0
```

**Saída esperada:** $x_1 = 18$, $x_2 = 8$, $z = 1000$. **Saída obtida:** `x: [18.0, 8.0]`, `z: 1000.0`, `status: otimo`. ✓

### Teste 2: Detecção de problema ilimitado

`Problema(c=[40, 35], A=[[-1, 0], [0, -1]], b=[60, 96])` → `Erro: O problema é ilimitado.` ✓

### Teste 3: Detecção de múltiplas soluções

`Problema(c=[2, 4], A=[[1, 2], [1, 0]], b=[4, 2])` → `x: [2.0, 1.0]`, `z: 8.0`, `status: multiplas_solucoes`. ✓

### Teste 4: Execução do LP completo em quatro cenários paramétricos

Para validar a sensibilidade do modelo às escolhas de política, o LP completo (FO + R1 + R2 + R3 + R5) é resolvido em quatro cenários sobre a base real (10 clusters por decil, ~6,8 milhões de elegíveis). Cada cenário difere do `base` apenas em parâmetros de política — não na estrutura do problema — permitindo isolar o efeito de cada decisão.

**Resumo dos cenários:**

| Cenário         | `pd_fin_max` | `alpha_conc` | `LGD` | `gamma_decil`                  |
| :-------------- | -----------: | -----------: | ----: | :----------------------------- |
| `base`          |        0,32  |        0,30  |  0,80 | empírico (Seção 1.5.1)         |
| `conservador`   |        0,25  |        0,15  |  0,85 | empírico                       |
| `agressivo`     |        0,40  |        0,50  |  0,70 | empírico                       |
| `drift`         |        0,32  |        0,30  |  0,80 | empírico × 1,25 em todos decis |

**Resultados comparativos:**

| Cenário       | $Z^*$ (R\$)         | Volume (R\$)         | Clusters ativos ($L_k^* > 0$) | R1 binding | R2 binding             | R5 binding |
| :------------ | -------------------: | --------------------: | :---------------------------: | :--------: | :--------------------- | :--------: |
| `base`        |       30.121.656,30  |       613.482.709,59  | 7 (D1–D7)                     | sim        | D2, D3, D4, D5, D6     | D1         |
| `conservador` |                0,00  |                 0,00  | 0                             | sim (triv.)| —                      | todos      |
| `agressivo`   |       34.838.679,47  |       689.677.042,81  | 10 (D1–D10)                   | não        | todos                  | nenhum     |
| `drift`       |       26.648.874,61  |       613.482.709,59  | 7 (D1–D7)                     | sim        | D2, D3, D4, D5, D6     | D1         |

**Cenário `base` — referência.** $Z^* = \text{R\$ 30{,}12 M}$ em 22 meses, volume R\$ 613 M, 7 clusters ativos (D1–D7), D8–D10 zerados. R1 binding em 32 % (a PD ponderada da carteira otimizada coincide com o teto), R2 binding para D2–D6 (a alavancagem $m_k \cdot CP_k$ é o gargalo desses decis), R5 binding apenas em D1 (o cluster mais rentável é capeado em 30 % da exposição total). O resultado reproduz a solução de referência da Seção 4 da modelagem, validando a equivalência entre o Simplex implementado neste projeto e o `scipy.optimize.linprog` (HiGHS) usado na sensibilidade.

**Cenário `conservador` — restrições saturadas.** Com `pd_fin_max = 0{,}25` e `alpha_conc = 0{,}15`, o problema fica numericamente infactível para qualquer volume positivo: $\alpha = 0{,}15$ exige pelo menos 7 clusters com exposições equilibradas para que nenhum ultrapasse 15 % do total, mas o teto de PD em 25 % só pode ser atendido com peso forte em D1 (PD 15,6 %), o que viola R5. O solver retorna $L_k = 0$ para todos os clusters, o ótimo factível. A leitura gerencial é direta: política conservadora desta magnitude inviabiliza o produto pré-aprovado nessa carteira, sinalizando ao comitê de risco onde os parâmetros precisam ser negociados.

**Cenário `agressivo` — todos os decis ativos.** Com `pd_fin_max = 0{,}40`, `alpha_conc = 0{,}50` e `LGD = 0{,}70`, R1 deixa de ser binding (folga R\$ 32,9 M no LHS linearizado, PD ponderada resultante de 35,2 %) e R5 sai do gargalo. O solver satura R2 em **todos** os 10 clusters (cada $L_k^* = m_k \cdot CP_k$), e o LGD menor reduz a perda esperada por cliente: $Z^* = \text{R\$ 34{,}84 M}$ (+15,7 % vs `base`) com volume R\$ 689,7 M. Esse é o teto técnico da carteira sob R2 e R3 isoladamente, e é coerente com o "volume potencial máximo de R\$ 689 M" descrito na Seção 1.5 da modelagem para o caso em que apenas R2 está ativa.

**Cenário `drift` — degradação da calibração.** Multiplicar $\gamma_d$ por 1,25 simula uma piora generalizada da calibração do scoring (a fração de PD anual que se materializa como over30mob3 sobe 25 %). A estrutura da base ótima é preservada (mesmos 7 clusters ativos, mesmos binding de R1, R2 e R5), e o impacto fica concentrado no valor da FO: $Z^*$ cai de 30,12 M para 26,65 M (–11,5 %), mantendo o mesmo volume R\$ 613 M. A leitura é a esperada para drift no horizonte de uso: o portfólio ótimo continua o mesmo porque a calibração afeta proporcionalmente todos os clusters, e a recomposição só seria necessária se $\gamma_d$ se movesse de forma heterogênea entre decis.

**Observação operacional.** Em todos os quatro cenários, `simplex.py` é o mesmo arquivo e não importa nenhuma biblioteca de otimização — a variação de resultados decorre exclusivamente do JSON de parâmetros, comprovando o desacoplamento entre algoritmo (`simplex.py`) e modelo (`main.py` + `parametros_*.json`). A reprodução do $Z^*$ de referência de 30,12 M no cenário base, com a mesma estrutura de binding observada na Seção 4 da modelagem, confirma o alinhamento 1-para-1 entre código e modelagem matemática.

## Conclusões

O algoritmo Simplex foi implementado do zero, sem uso de bibliotecas de otimização, e validado em quatro frentes: (i) problema clássico com solução analítica conhecida; (ii) detecção de problema ilimitado; (iii) detecção de múltiplas soluções; e (iv) o LP completo do Banco Pan resolvido em quatro cenários paramétricos sobre a base real. O resultado de referência $Z^* = \text{R\$ 30{,}12 M}$ no cenário base reproduz integralmente a solução obtida no `scipy.optimize.linprog` (HiGHS) usada na análise de sensibilidade, validando o alinhamento entre código e modelagem matemática (Seções 1.5, 1.5.1 e 1.6 de [`modelagem_matematica.md`](modelagem_matematica.md)).

Próximos passos identificados:

- Habilitar R6 (volume mínimo) como restrição linear adicional quando o parceiro estipular um $V^{min}$ operacional.
- Implementar R4 (teto de inadimplência física) no pipeline de pós-otimização, conforme detalhado na Seção 1.7 da modelagem.
- Expandir o número de clusters para um esquema híbrido decil + intra-decil (por faixa de `score_credito_cross`), atingindo $K \geq 100$ conforme requisito do parceiro para a entrega final.
