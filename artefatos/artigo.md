# [Título do Artigo]

**[Nome Autor 1], [Nome Autor 2], [Nome Autor 3], ...**

[Instituição], [Cidade], [Estado], [País]

[email@instituicao.edu.br]

---

## RESUMO

*(A ser entregue na Sprint 4.)*

**Palavras-chave:** palavra1, palavra2, palavra3.

---

## 1. INTRODUÇÃO

[Parágrafo 1 — Contextualização do problema: descreva o cenário em que o problema está inserido.]

[Parágrafo 2 — Relevância do problema: explique por que o tema é importante, usando dados, estatísticas ou referências que justifiquem o interesse.]

[Parágrafo 3 — Objetivo do trabalho: apresente claramente o que este trabalho se propõe a fazer.]

[Parágrafo 4 — Justificativa: explique a motivação com base no contexto do projeto, sem mencionar explicitamente o nome da empresa parceira.]

---
> 💡 **Sugestão de "ir além" — Introdução**
>
> Inclua um dado quantitativo real e citado do contexto brasileiro logo no segundo parágrafo — por exemplo, a taxa de inadimplência de cartão de crédito divulgada pelo Banco Central do Brasil (disponível em dadosabertos.bcb.gov.br). Isso ancora o problema em escala real e demonstra que a motivação não é hipotética. Artigos publicados em conferências e periódicos da área quase sempre abrem com um dado desse tipo antes de apresentar o objetivo.
---

## 2. MATERIAIS E MÉTODOS

Esta seção descreve o _pipeline_ metodologico adotado no estudo, desde a caracterização dos dados de entrada até a definição do modelo de otimização e sua resolução. O fluxo seguido inclui a preparação e transformação dos dados, a segmentação dos clientes em perfis homogêneos, a formulação do problema de programação linear e a implementação do algoritmo de solução. Por fim, são detalhadas as ferramentas e tecnologias utilizadas para garantir a reprodutibilidade do processo.

### 2.1 Dados utilizados

Os dados foram fornecidos pelo **Banco Pan** em três tabelas correspondentes a safras temporais (M1, M2, e M3), contendo clientes correntistas com variáveis de perfil, risco capacidade de pagamento e comportamento. A base total tem cerca de 15 milhões de clientes por safra, das quais uma fração é elegível ao produto e segue para a etapa de otimização. A Tabela 1 resume as variáveis utilizadas diretamente no modelo e seu papel na formulação; as demais colunas são usadas apenas para controle a análises descritivas. As restrições e o papel na função associadas a essas variáveis são detalhadas na Seção 2.3.

**Tabela 1 — Variáveis fornecidas pelo parceiro (estatísticas da safra M1)**

| Variável                     | Descrição                                     | Estatísticas (M1)                                                  | Papel no modelo |
|:-----------------------------|:----------------------------------------------|:-------------------------------------------------------------------|:---------------|
| `token`                      | Identificador anônimo por safra               | 0 a 14.569.141                                                     | Chave de identificação |
| `safra_ref_uso`              | Safra de referência                           | M1, M2, M3                                                         | Permite backtesting entre safras |
| `score_interno`              | Score de crédito interno                      | min=54, med=292, max=975                                           | Não usado diretamente; gera `pd_produto` |
| `pd_produto`                 | Probabilidade de default no produto           | min=0,025, med=0,71, max=0,946                                     | Parâmetro de risco na função objetivo e na restrição R1 |
| `score_generico_1`           | Score de bureau (bureau 1)                    | min=49, med=409, max=995. Nulls: 0,1%                              | Variável de segmentação para clusterização |
| `score_generico_2`           | Score de bureau (bureau 2)                    | min=1, med=713, max=942. Nulls: <0,01%                             | Variável de segmentação para clusterização |
| `capacidade_pagamento`       | Estimativa interna de capacidade de pagamento | min=0, med=548, max=25.000. Nulls: 0,3% M1; 42,2% M2; 43,5% M3     | Restrição R2 (alavancagem) |
| `delta_capacidade_pagamento` | Capacidade deduzida dos saldos a vencer       | min=−25.000, med=55, max=25.000. Nulls: idem                       | Variante conservadora (apoio à análise) |
| `renda_estimada`             | Estimativa interna de renda                   | min=1.275, med=1.908, max=17.950. Nulls: 0,3%                      | Proxy para R2 quando `capacidade_pagamento` é nula |
| `fx_idade`                   | Faixa etária                                  | 9 faixas: 21–30 (35,5%), 31–40 (31,1%), 41–50 (18,8%)              | Segmentação e análise de resultados |
| `flag_filtros`               | Indicador de perfil restrito                  | 0 = elegível (1,84M), 1 = restrito (12,73M)                        | Filtro de elegibilidade |
| `score_propensao_contrato`   | Score de propensão à conversão                | min=3, med=315, max=846                                            | Parâmetro de conversão na função objetivo |
| `score_credito_cross`        | Score de crédito multiproduto                 | min=103, med=706, max=954                                          | Define a faixa de alavancagem do cluster (mₖ) |
| `limite_ofertado`            | Limite ofertado na política atual             | min=200, med=806, max=20.000. 99,2% null                           | Baseline para backtesting |
| `flag_contrato`              | Indicadora de contratação (1 = contratou)     | 6.506 (0,04%)                                                      | Backtesting (conversão) |
| `flag_ativacao`              | Indicadora de ativação (1 = ativou)           | 5.704 (87,7% dos que contrataram)                                  | Backtesting (ativação) |
| `over30mob3`                 | Atraso >30 dias nas 3 primeiras parcelas      | 4.966 válidos, 377 eventos (7,6%). 99,97% null                     | Inadimplência observada (viés de seleção) |

Além das variáveis das três safras, alguns parâmetros necessários à formulação do modelo foram informados diretamente pelo parceiro (por exemplo, taxa de _interchange_, LGD e horizonte de receita). Esses valores são tratados como constantes na formulação e são apresentados explicitamente na seção 2.3, junto com a função objetivo e as restrições.

### 2.2 Pré-processamento

[Etapas de limpeza, transformação e preparação dos dados.]

### 2.3 Modelagem matemática

Esta seção apresenta a formulação matemática do problema de definição de limites de crédito pré-aprovados. Dado um conjunto de clientes elegíveis, agrupados por $K$ _clusters_ relativamente homogêneos, busca-se determinar o limite $L_k$ a ser ofertado a cada cluster $k$ de modo a maximizar o retorno líquido esperado da carteira. Opta-se por uma formulação de Programação Linear (LP) por sua interpretabilidade em larga escala, uma vez que a decisão deve ser tomada simultaneamente para múltiplos perfis de clientes, além de ser um requisito mapeado pelo parceiro. 

Para preservar a linearidade do modelo, grandezas de risco e comportamento (como probabilidade de inadimplência ($PD_k$), propensão à contratação ($\pi$_k) e parâmetros operacionais do produto) são tratadas como parâmetros estimados na etapa de pré-processamento, enquanto os limites $L_k$ constituem as variáveis de decisão. A função objetivo considera a receita esperada de _interchange_ descontada da perda esperada por inadimplência, e as restrições incorporam políticas prudenciais e operacionais, como teto de risco agregado, alavancagem em relação à capacidade  d epagamento e limites máximos por oferta.

A Tabela 2 resume os principais parâmetros utilizados na formulação, incluindo grandezas estimadas a partir dos dados (por exemplo, $PD_k$, $\pi_k$, $CP_k$) e constantes operacionais fornecidas pelo parceiro (por exemplo, taxa de _interchange_ $t$, horizonte de receita $T$ e $\mathrm{LGD}$). Esses parâmetros são calculados na etapa de pré-processamento e, em seguida, tratados como constantes no problema de otimização, garantindo que a função objetivo e as restrições permaneçam lineares nas variáveis de decisão $L_k$.

**Tabela 2 — Parâmetros do modelo de otimização**

| Símbolo | Descrição | Unidade / Domínio | Como é obtido (no pipeline) | Fonte |
|---|---|---|---|---|
| $K$ | Número de clusters de clientes elegíveis | inteiro, $K \ge 100$ | Definido na etapa de clusterização | Pré-processamento |
| $k$ | Índice do cluster | $k \in \{1,\dots,K\}$ | — | — |
| $n_k$ | Número de clientes no cluster $k$ | inteiro positivo | Contagem de observações no cluster | Dados + clusterização |
| $PD_k$ | Probabilidade de default representativa do cluster $k$ | $[0,1]$ | Média de `pd_produto` dentro do cluster $k$ | Dados (scoring interno) |
| $\pi_k$ | Propensão à contratação (normalizada) do cluster $k$ | $[0,1]$ | Normaliza `score_propensao_contrato` via min–max e tira média no cluster | Dados + normalização |
| $CP_k$ | Capacidade de pagamento representativa do cluster $k$ | R\$ | Percentil 5 de `capacidade_pagamento` no cluster; quando nulo, proxy via `renda_estimada \times 0{,}30` | Dados + regra de proxy |
| $m_k$ | Multiplicador de alavancagem permitido no cluster $k$ | ex.: $[0{,}20,\,0{,}45]$ | Mapeado por faixas do `score_credito_cross` (médio do cluster) | Política/heurística calibrada |
| $t$ | Taxa de interchange mensal | adimensional | Constante | Parceiro / premissa |
| $T$ | Horizonte de receita considerado | meses | Constante (ex.: $T=22$) | Parceiro / premissa |
| $\bar{u}$ | Utilização média esperada do limite | $[0,1]$ | Constante (ex.: $\bar{u}=0{,}75$) | Parceiro / premissa |
| $\mathrm{LGD}$ | Loss Given Default | $[0,1]$ | Constante (ex.: $\mathrm{LGD}=0{,}80$) | Parceiro / premissa |
| $d(k)$ | Decil associado ao $PD_k$ (para calibração) | $\{1,\dots,10\}$ | Identifica o decil onde o $PD_k$ cai | Pré-processamento |
| $\gamma_d$ | Fator de calibração da PD no decil $d$ | $>0$ | Razão empírica (ex.: baseada em `over30mob3` vs `pd_produto`) por decil | Estimado em análise histórica |
| $PD_k^{cal}$ | PD calibrada do cluster $k$ | $[0,1]$ | $PD_k^{cal} = PD_k \cdot \gamma_{d(k)}$ | Derivado |
| $\overline{PD}_{fin}^{atual}$ | Teto de risco financeiro da carteira (ponderado por exposição) | $[0,1]$ | Definido como benchmark/limite de política | Parceiro / política |
| $L^{max}$ | Limite máximo permitido por oferta | R\$ | Constante (ex.: $25.000$) | Política operacional |
| $\alpha$  | Concentração máxima de exposição em um único cluster | $[0,1]$ | Constante (ex.: 5%) para as restrições | Política/prudencial |
| $V^{min}$  | Piso de produção (volume total de limite ofertado) | R\$ | Constante para as restrições | Meta comercial |


#### Função objetivo

O objetivo do modelo é maximizar o retorno líquido esperado da carteira no horizonte $T$, definido como a diferença entre (i) a receita esperada de _interchange_ gerada pelo uso do cartão e (ii) a perda esperada por inadimplência, ambas condicionadas à contratação do produto. Considerando a modelagem por _clusters_, em que todos os $n_k$ clientes do cluster $k$ recebem o mesmo limite $L_k$, a função objetivo é dada por:

$$
\max \sum_{k=1}^{K} n_k \cdot
\left[
\underbrace{\pi_k \cdot T \cdot \bar{u} \cdot t \cdot L_k}_{\text{Receita esperada em }T\text{ meses}}
\;-\;
\underbrace{\pi_k \cdot PD_k^{cal} \cdot \mathrm{LGD} \cdot L_k}_{\text{Perda esperada por inadimplência}}
\right].
$$

No primeiro termo, $\pi_k$ representa a probabilidade de contratação (ou propensão à conversão) do cluster $k$; $\bar{u}$ é a fração média esperada do limite efetivamente utilizada; $t$ é a taxa de _interchange_ aplicada sobre o volume transacionado; e $T$ acumula a receita ao longo do horizonte considerado. Assim, $T\cdot\bar{u}\cdot t\cdot L_k$ aproxima a receita total de _interchange_ por cliente (condicional ao cliente utilizar o produto), enquanto o fator $\pi_k$ pondera essa receita pela chance de contratação.

No segundo termo, $PD_k^{cal}$ é a probabilidade calibrada de inadimplência associada ao cluster $k$ (obtida a partir do $PD_k$ e do fator $\gamma_{d(k)}$, quando aplicável), e $\mathrm{LGD}$ é a perda dada a inadimplência. A expressão $PD_k^{cal}\cdot \mathrm{LGD}\cdot L_k$ representa a perda esperada por cliente, e novamente é ponderada por $\pi_k$, refletindo que a perda só se materializa no subconjunto que efetivamente contrata o produto.

Agrupando os termos constantes, pode-se reescrever a função objetivo como:

$$
\max \sum_{k=1}^{K} n_k \cdot c_k \cdot L_k,
\quad \text{onde}\quad
c_k = \pi_k\cdot\left(T\cdot \bar{u}\cdot t - PD_k^{cal}\cdot \mathrm{LGD}\right).
$$

O coeficiente $c_k$ pode ser interpretado como o retorno líquido marginal esperado por unidade monetária de limite ofertado ao cluster $k$. Como todos os fatores em $c_k$ são parâmetros, a função objetivo é linear em $L_k$, caracterizando um problema de Programação Linear (LP).

### 2.4 Implementação do algoritmo

[Descrição do algoritmo implementado e suas etapas.]

### 2.5 Ferramentas e Tecnologias

[Linguagens, bibliotecas e ambientes utilizados.]

---
> 💡 **Sugestão de "ir além" — Materiais e Métodos**
>
> Adicione um diagrama de fluxo do pipeline completo (pré-processamento → clusterização → resolução do LP → pós-otimização). Pode ser feito em Mermaid, draw.io ou mesmo uma figura exportada. Artigos técnicos reais sempre incluem esse tipo de figura porque facilita a reprodutibilidade e deixa o leitor entender o método sem precisar ler todo o texto. É um dos elementos mais valorizados por revisores.
---

## 3. TRABALHOS RELACIONADOS

### 3.1 Protocolo de Busca e Seleção

A busca foi conduzida nas bases SciELO, Google Scholar, BDTD/NDLTD, Scopus/Web of Science, Dimensions e BASE. As consultas foram realizadas em português e inglês, combinando termos de domínio como *credit portfolio*, *credit limit* e *bank loan* com termos metodológicos como *linear programming*, *simplex*, *optimization*, *clustering* e *risk identification*. ScienceDirect, IEEE Xplore e arXiv.org também foram consultados, mas não retornaram resultados aderentes aos critérios de inclusão definidos. As queries são documentadas em inglês para fins de padronização e reprodutibilidade; buscas equivalentes foram realizadas em português nas bases que suportam indexação no idioma. As principais queries utilizadas foram:

| # | Query |
|---|---|
| 1 | `"credit limit optimization" AND "linear programming" AND "bank"` |
| 2 | `"optimal credit portfolio" AND "linear programming"` |
| 3 | `"credit portfolio" AND "linear programming" AND "risk"` |
| 4 | `"loan allocation" AND "linear programming" AND "financial institution"` |
| 5 | `"linear programming" AND "bank loan" AND "optimal revenue"` |
| 6 | `"credit line assignment" AND "customer segmentation"` |
| 7 | `"enterprise financial risk" AND "clustering algorithm"` |
| 8 | `"clustering" AND "financial risk" AND "bank"` |
| 9 | `"credit risk" AND "cluster analysis" AND "bank"` |

As queries foram adaptadas e aplicadas às bases listadas, respeitando as particularidades de indexação de cada uma.

**Critérios de inclusão:** aderência ao problema de definição, ajuste ou otimização de decisões de crédito; tratamento explícito de otimização, modelagem prescritiva ou formulação matemática aplicável ao contexto financeiro; e contribuição para a discussão de risco, retorno e alocação de crédito em instituições financeiras. Foram priorizadas publicações dos últimos cinco anos, preferencialmente. Trabalhos fora desse recorte temporal ou temático estrito também foram considerados quando apresentavam relevância metodológica consolidada e contribuição direta para a formulação do modelo adotado.

**Critérios de exclusão:** materiais sem densidade técnica; textos promocionais ou instrucionais voltados ao consumidor final; referências sem conexão com modelagem analítica, otimização ou apoio quantitativo à decisão de crédito; e trabalhos cujo foco principal não permitisse estabelecer relação com o problema de alocação, aprovação ou gestão de crédito.

Após a etapa de triagem, foram selecionados quatro trabalhos para análise comparativa. Três deles foram escolhidos por sua aderência aos temas de otimização de portfólio de crédito via programação linear e identificação de risco financeiro via clusterização. Um quarto trabalho, mais antigo, foi incluído por sua relevância metodológica consolidada na integração entre modelagem econométrica e otimização aplicada à concessão de crédito.

---

### 3.2 Application of Linear Programming for Optimal Net Revenue on Bank Loan — AL-MUSBAHU et al. (2025)

**Resumo do trabalho:** 

O trabalho aborda a aplicação da Programação Linear no contexto de otimizar a receita total no quesito de empréstimos bancários. A otimização de portfólios se trata de um pilar importante no setor de finanças e da Teoria de Investimentos, tendo implicações tanto para investidores quanto gestores, que precisam alocar recursos para múltiplas categorias de ativos (AL-MUSBAHU et al., 2025).

Dessa forma, a Programação Linear apresenta-se como uma maneira para otimizar a alocação de empréstimos bancários em diferentes áreas (como empréstimos de crédito e para o financiamento de carros, por exemplo), considerando que as relações entre as variáveis mantenham-se lineares. Por esse caminho, uma função matemática linear pode ser mapeada, levando em consideração as relações da concessão de risco-retorno, segundo Konno e Yamazaki (1991, *apud* AL-MUSBAHU et al., 2025).

Com informações de Janeiro de 2025, coletadas do **Access Bank**, localizado na região Ogun, na Nigéria, o modelo definido leva em consideração informações reais relacionadas a taxas e parâmetros para a modelagem, como juros e risco. Assim, o programa foi capaz de retornar uma alocação ótima para um caso de teste, seguindo todas as restrições mapeadas para o cenário (como o fato de que 45% dos empréstimos totais precisavam ser destinados para o financiamento de carros e empréstimos para organizações.) (AL-MUSBAHU et al., 2025).

No caso de teste, era desejado alocar ₦300.000.000. A alocação ótima mapeou que 20% do valor deveria ser destinado para o financiamento de residências, 50% para cartões de crédito e 30% para empréstimos para organizações, trazendo um retorno anual de ₦24.615.000 Categorias como empréstimos pessoais receberam uma alocação de zero, demonstrando como, em comparação com outras categorias, elas mostram-se como opções menos lucrativas para o banco (AL-MUSBAHU et al., 2025).

**Pontos positivos:**

O artigo aborda pontos importantes que estão diretamente relacionados com o contexto do trabalho elaborado. O principal deles é em relação a metodologia utilizada para a resolução do problema de alocação de empréstimos. Tanto o artigo de Al-Musbahu (2025) quanto neste trabalho empregam da Programação Linear, que se trata de uma técnica matemática de otimização, que busca determinar o melhor resultado possível (tanto de maximização ou minimização).

O artigo, além de mapear a função-objetivo, também traz as restrições do problema, aspecto extremamente importante para o funcionamento da solução. Um ponto explicitado é sobre a influência dessas restrições no resultado. Por exemplo, uma restrição pode exigir percentuais mínimos para certos tipos de empréstimos (como no caso de teste apresentado na introdução), forçando a inclusão de categorias que, quando analisadas por um escopo individual, não se apresentam como ideais (tendo um retorno financeiro menor). Com isso, o trabalho destaca que a solução ótima do modelo abordado por esse artigo não deve contemplar apenas o resultado das taxas de retorno, mas sim levar em consideração as regras de negócio específicas. Aspectos como a taxa de inadimplência permitem a abordagem de cenários mais realistas e completos para a solução.  

Por outro lado, um aspecto que ambos também tratam é da aplicação direta da Progamação Linear para problemas do mundo financeiro. Apesar de não abordarem o mesmo tema diretamente (empréstimos X limites de crédito), tanto o artigo de Al-Musbahu (2025) quanto este trabalho buscam trazer a computação e utilização de algoritmos para ambientes financeiros especializados. Como forma de validação, os dois empregam dados reais de instituições financeiras, trabalhando sobre informações condinzentes com os cenários existentes, trazendo uma maior confiabilidade para os resultados encontrados.

**Pontos negativos / limitações:** 

Conforme mencionado anteriormente, um aspecto que pode ser considerado negativo no trabalho de Al-Musbahu (2025) em relação a este trabalho se trata do tema proposto. Apesar de ambos estarem localizados no ambiente financeiro, eles abordam categorias essencialmente diferentes, que são a oferta de empréstimos e definição de limites de crédito. 

Essa divergência não está limitada a apenas o objetivo da função matemática, mas também nos parâmetros que são levados em consideração. A função utilizada no presente trabalho aborda variáveis que não estão presentes no artigo de Al-Mushabu (2025) e vice-versa, fator que pode limitar a comparação direta entre os dois casos.

Outro ponto que deve ser levado em consideração é em relação a amostragem de dados. O artigo de Al-Musbahu leva em consideração as informações coletadas por apenas uma filial do banco durante um único período, fator que pode limitar a robustez de seu modelo e da definição das variáveis do modelo, afetando o resultado direto da função matemática.


**Diferença em relação ao nosso problema:** 

 O principal ponto de divergência entre ambos os trabalhos se trata do tema abordado. Enquanto o artigo de Al-Musbahu (2025) investiga a definição ótima de categorias para empréstimos bancários, o tema do presente artigo é sobre a oferta de limite de créditos para clientes de um banco. 

 Apesar de tratarem de categorias diferentes, isso não significa que o trabalho de Al-Musbahu (2025) não é útil para o contexto atual. Ele traz uma perspectiva valiosa em relação a modelagem matemática do problema, e de quais maneiras as restrições definidas podem afetar no contexto da solução.

 Outro ponto de destaque em relação às divergências está no escopo. O artigo de Al-Musbahu tem um escopo menor do que este trabalho. O modelo do artigo comparado utiliza um conjunto menor de variáveis, agregadas por tipo de empréstimo (taxa de juros e de inadimplência), enquanto o presente trabalho opera com um número maior de variáveis e parâmetros por cluster de clientes, como a capacidade de pagamento e propensão à contratação. 

 Esse aspecto também está presente na base de dados. O artigo de Al-Musbahu trabalha com uma amostra limitada, enquanto este trabalho considera um volume maior de dados, contendo milhões de clientes, assim ampliando a complexidade do modelo e definição da solução ótima.
 
 De forma geral, o trabalho de Al-Mushabu apresenta-se como uma base sólida inicial para o mapeamento da solução desse artigo. O artigo traz conceitos-chave que também serão abordados, porém diferenciando-se o suficiente para evitar que este trabalho se torne redundante.

---

### 3.3 Application of Linear Programming to Optimal Credit Portfolio: The Case of Akuapem Rural Bank Ltd. — KWAPONG (2013)

**Resumo do trabalho:** Kwapong (2013) formula e resolve um modelo de programação linear para maximizar o retorno líquido da carteira de crédito do Akuapem Rural Bank Ltd., banco rural de Gana com portfólio total de GH¢ 15 milhões. O banco opera com cinco modalidades de empréstimo (Indústria Artesanal, Transporte, Agricultura, Salário e Microfinanças), cada uma com taxa de juros e probabilidade de inadimplência distintas: o empréstimo de Transporte, por exemplo, opera a 32% com 5% de inadimplência, enquanto o Salário apresenta 30% de taxa e apenas 1% de inadimplência. A função objetivo maximiza a receita líquida de cada modalidade, descontando a perda esperada por inadimplência, formulada como $Z = \sum_j I_j(1 - P_j)x_j$. O modelo é resolvido sob quatro restrições principais: teto total de fundos, alocação mínima de 40% para Salário e Microfinanças, mínimo de 60% para os demais segmentos e teto de inadimplência agregada de 3% (KWAPONG, 2013).

Para testar a robustez da solução, o autor analisa sete cenários variando o número de restrições e as taxas de juros. No cenário base, a solução ótima aloca GH¢ 7 milhões a Transporte, GH¢ 2 milhões a Agricultura e GH¢ 6 milhões a Salário, com retorno de GH¢ 4,48 milhões, descartando Indústria Artesanal e Microfinanças por baixa atratividade líquida. O trabalho conclui que há relação positiva entre risco e retorno e que o aumento das taxas de juros melhora o resultado, desde que o risco seja controlado (KWAPONG, 2013).

**Pontos positivos:** A estrutura da função objetivo de Kwapong (2013) guarda relação estrutural direta com o presente trabalho: ambas maximizam a receita líquida descontando a perda esperada por inadimplência, com a forma $Z = \sum_j I_j(1 - P_j)x_j$ mapeando explicitamente o trade-off risco-retorno de cada categoria de crédito. Essa equivalência valida que a programação linear é um instrumento adequado para problemas de portfólio de crédito com controle simultâneo de risco. Vale destacar também a análise de sensibilidade conduzida nos sete cenários: ao variar o número de restrições e as taxas de juros, o autor identifica quais restrições são de fato limitantes por meio dos preços duais, como o valor negativo de -0,013 associado à restrição de alocação setorial, que sinaliza um efeito desfavorável sobre o retorno. Essa prática de análise de sensibilidade é metodologicamente sólida e diretamente replicável no pipeline do presente projeto.

**Pontos negativos / limitações:** A principal limitação do trabalho é tratar todos os tomadores dentro de uma mesma categoria como homogêneos. Ao definir apenas uma taxa de juros e uma probabilidade de inadimplência por modalidade, o modelo ignora a variação de perfil entre clientes de um mesmo segmento. Na prática, dois clientes de Salário com capacidade de pagamento muito diferente recebem o mesmo tratamento na formulação, o que reduz a precisão da estimativa de retorno. Outra limitação é a ausência de variável de decisão por cliente: a formulação define quanto alocar em cada categoria, não quanto conceder a cada indivíduo. Esse design é adequado para o problema de Kwapong (2013), mas não resolve diretamente problemas onde o limite individual é a variável central.

**Diferença em relação ao nosso problema:** A diferença fundamental está no nível de análise. Kwapong (2013) trabalha com cinco categorias de empréstimo, cada uma tratada como uma variável única no modelo LP. O presente trabalho opera no nível do cliente individual, agrupado por perfil via CART, com a programação linear sendo aplicada para definir o limite de crédito de cada cluster. Enquanto Kwapong (2013) responde "quanto alocar para Transporte versus Salário", o presente projeto responde "qual limite conceder ao cliente do cluster X dado seu perfil de risco e capacidade de pagamento". A segmentação em Kwapong (2013) é predefinida e fixa (modalidades institucionais do banco), enquanto aqui ela é endógena ao modelo, determinada pelos dados via CART.

De forma geral, Kwapong (2013) é o antecedente mais próximo do presente trabalho em termos de formulação matemática, confirmando que a estrutura LP com função objetivo de receita líquida ajustada por risco é aplicável ao crédito bancário. A diferença principal está na granularidade: o salto do nível de portfólio para o nível de cliente segmentado é o que este projeto propõe acrescentar.

---

### 3.4 Identification of Enterprise Financial Risk Based on Clustering Algorithm — LI; TAO; LI (2022)

**Resumo do trabalho:** O trabalho aborda a identificação de risco financeiro em empresas listadas na China, com o objetivo de selecionar um conjunto pequeno de empresas de alto risco que concentre uma proporção elevada de companhias que viriam a receber tratamento especial (ST – "special treatment") nos anos seguintes (LI; TAO; LI, 2022). A metodologia parte de 27 indicadores financeiros alternativos, dos quais são selecionadas 4 variáveis financeiras finais: razão de ativos tangíveis, razão de caixa sobre ativos, razão de endividamento de curto prazo e razão de endividamento de longo prazo. Os autores aplicam PCA para reduzir essas 4 variáveis a 2 dimensões e, em seguida, utilizam o algoritmo K-means (com K = 3 na primeira etapa e K = 4 na segunda etapa, aplicando K-means novamente apenas no cluster com mais empresas ST) para formar grupos e identificar o cluster de alto risco (LI; TAO; LI, 2022). O resultado principal mostra que o cluster de alto risco representa apenas 9% da amostra, mas concentra cerca de 36% das novas empresas ST já no ano corrente, proporção que aumenta ao estender o horizonte para 5 anos. Os autores concluem que o K-means, mesmo selecionando um grupo pequeno, é eficaz para filtrar empresas que merecem atenção cuidadosa de investidores (LI; TAO; LI, 2022).

**Pontos positivos:** Li, Tao e Li (2022) mostram que dados financeiros conseguem separar perfis de risco de forma objetiva, sem depender de regras empíricas. Isso reforça uma premissa central do nosso projeto: que é possível agrupar clientes em perfis homogêneos a partir de dados antes de tomar uma decisão de crédito. A contribuição conceitual vale mesmo que o algoritmo de segmentação seja diferente, pois o artigo valida a ideia de que reduzir heterogeneidade é uma etapa legítima e necessária antes da decisão final. Também é relevante que o trabalho trate a segmentação como parte estrutural da solução, não como um pré-processamento acessório, o que conversa diretamente com a forma como usamos o CART no nosso pipeline.

**Pontos negativos / limitações:** O artigo identifica grupos de risco, mas não transforma essa informação em uma decisão operacional. Não há função objetivo, não há restrições de negócio e não há valor atribuído a cada grupo: a clusterização é o produto final. Para o nosso problema, isso é uma limitação relevante, pois precisamos ir além da segmentação e definir qual limite conceder a cada perfil. Outra limitação é que a escolha das variáveis finais (4 de 27) e a configuração do K-means em dois níveis introduzem decisões metodológicas que o artigo não generaliza, o que reduz a replicabilidade direta da abordagem.

**Diferença em relação ao nosso problema:** O artigo resolve um problema de classificação: dado um conjunto de empresas, identificar quais têm maior risco. Nosso problema é de otimização: dado um conjunto de grupos de clientes, definir qual limite maximiza o retorno líquido respeitando restrições de inadimplência, capacidade de pagamento e teto por cliente. Além disso, o contexto é fundamentalmente diferente, pois o artigo trabalha com empresas listadas em bolsa, enquanto o nosso projeto lida com pessoas físicas titulares de cartão de crédito. No nosso pipeline, a segmentação via CART é uma etapa intermediária que viabiliza a otimização; no artigo, ela é o fim em si mesma.

De forma geral, Li, Tao e Li (2022) contribuem como referência para a etapa de segmentação do nosso projeto, validando conceitualmente o uso de agrupamento baseado em dados para apoiar decisões de crédito. O trabalho se diferencia o suficiente do nosso para evitar redundância, justamente por não abordar a etapa de otimização que é central neste artigo.

---

### 3.5 Utilização conjunta de modelagem econométrica e otimização em decisões de concessão de crédito — SCARPEL; MILIONI (2002) *(referência clássica)*

**Resumo do trabalho:** [Descreva o problema que o trabalho aborda, a metodologia utilizada e os principais resultados obtidos. Use citação indireta (SCARPEL; MILIONI, 2002). Justifique brevemente a inclusão de um trabalho fora do recorte temporal dos últimos cinco anos.]

**Pontos positivos:** [O que o trabalho faz bem e que é relevante para o nosso contexto.]

**Pontos negativos / limitações:** [Limitações metodológicas, de dados ou de escopo identificadas no trabalho.]

**Diferença em relação ao nosso problema:** [Explique de forma clara por que o problema tratado neste trabalho **não é idêntico** ao nosso.]

**Referência ABNT:**

> SCARPEL, R. A.; MILIONI, A. Z. Utilização conjunta de modelagem econométrica e otimização em decisões de concessão de crédito. **Pesquisa Operacional**, v. 22, n. 1, p. 61-72, 2002. DOI: 10.1590/S0101-74382002000100004. Disponível em: <https://www.scielo.br/j/pope/a/3DkFSwbgRxdtDDG6MSPBDLM/>. Acesso em: 20 maio 2026.

---

---
> 💡 **Sugestão de "ir além" — Trabalhos Relacionados**
>
> Ao final da seção, após a tabela comparativa, adicione um parágrafo de **lacuna identificada** (*research gap*): explique o que nenhum dos trabalhos encontrados resolve e que este projeto se propõe a resolver. Algo como: "Observa-se que nenhum dos trabalhos revisados combina simultaneamente X, Y e Z no contexto de W — lacuna que este trabalho busca preencher." Isso é padrão em artigos de conferência e periódico, e deixa o leitor com clareza sobre a contribuição original do trabalho.

### 3.6 Tabela Comparativa

| Dimensão | AL-MUSBAHU et al. (2025) | KWAPONG (2013) | LI; TAO; LI (2022) | SCARPEL; MILIONI (2002) | Este trabalho |
|---|---|---|---|---|---|
| Problema central | | | | | |
| Técnica de otimização | | | | | |
| Uso de clusterização | | | | | |
| Variável de decisão | | | | | |
| Controle de risco | | | | | |
| Domínio de aplicação | | | | | |
| Similaridade com nosso problema | | | | | — |

---

## 4. RESULTADOS

*(A ser entregue na Sprint 4.)*

---

## 5. ANÁLISE E DISCUSSÃO

*(A ser entregue na Sprint 4.)*

---

## 6. CONCLUSÃO

*(A ser entregue na Sprint 4.)*

---

## REFERÊNCIAS BIBLIOGRÁFICAS

AL-MUSBAHU, Abdulrahim; TETE, Ahmed Rufai; MANYISA, Yisa Emmanuel; MOHAMMED, Jibrin. Application of Linear Programming for Optimal Net Revenue on Bank Loan. **Kontagora Journal of Mathematics**, v. 1, n. 1, p. 214-230, 2025. DOI: 10.5281/zenodo.17401383.
// https://fuekjournals.org/index.php/KJM/article/view/166

KWAPONG, Samuel Darkwa. Application of Linear Programming to Optimal Credit Portfolio: The Case of Akuapem Rural Bank Ltd. 2013. Dissertação (MSc in Industrial Mathematics) — Kwame Nkrumah University of Science and Technology, Institute of Distance Learning, Kumasi, 2013. Disponível em: <https://ir.knust.edu.gh/handle/123456789/5841>. Acesso em: 20 maio 2026.
// https://ir.knust.edu.gh/items/ffdc0243-2ecc-4937-8aa1-6a752e613d93

LI, Bingxiang; TAO, Rui; LI, Meng. Identification of Enterprise Financial Risk Based on Clustering Algorithm. **Computational Intelligence and Neuroscience**, v. 2022, art. 1086945, 2022. DOI: 10.1155/2022/1086945.
// https://www.researchgate.net/publication/359925373_Identification_of_Enterprise_Financial_Risk_Based_on_Clustering_Algorithm

SCARPEL, R. A.; MILIONI, A. Z. Utilização conjunta de modelagem econométrica e otimização em decisões de concessão de crédito. **Pesquisa Operacional**, v. 22, n. 1, p. 61-72, 2002. DOI: 10.1590/S0101-74382002000100004. Disponível em: <https://www.scielo.br/j/pope/a/3DkFSwbgRxdtDDG6MSPBDLM/>. Acesso em: 20 maio 2026.
// https://www.scielo.br/j/pope/a/3DkFSwbgRxdtDDG6MSPBDLM/