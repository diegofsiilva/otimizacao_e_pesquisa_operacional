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

[Descreva os dados utilizados, as ferramentas, os algoritmos e a metodologia adotada para resolver o problema.]

### 2.1 [Subseção — ex.: Dados]

[Descrição dos dados de entrada, fontes, volume e variáveis relevantes.]

### 2.2 [Subseção — ex.: Pré-processamento]

[Etapas de limpeza, transformação e preparação dos dados.]

### 2.3 [Subseção — ex.: Modelagem]

[Descrição do modelo matemático, variáveis de decisão, função objetivo e restrições.]

### 2.4 [Subseção — ex.: Algoritmo]

[Descrição do algoritmo implementado e suas etapas.]

### 2.5 [Subseção — ex.: Ferramentas e Tecnologias]

[Linguagens, bibliotecas e ambientes utilizados.]

---
> 💡 **Sugestão de "ir além" — Materiais e Métodos**
>
> Adicione um diagrama de fluxo do pipeline completo (pré-processamento → clusterização → resolução do LP → pós-otimização). Pode ser feito em Mermaid, draw.io ou mesmo uma figura exportada. Artigos técnicos reais sempre incluem esse tipo de figura porque facilita a reprodutibilidade e deixa o leitor entender o método sem precisar ler todo o texto. É um dos elementos mais valorizados por revisores.
---

## 3. TRABALHOS RELACIONADOS

Esta seção apresenta e analisa os trabalhos identificados na revisão de literatura, posicionando-os em relação ao problema proposto. A busca sistemática descrita em 3.1 resultou na seleção de três estudos que cobrem os dois componentes técnicos centrais do projeto — programação linear aplicada a decisões de crédito e clusterização para identificação de risco financeiro —, analisados individualmente nas seções 3.2 a 3.4, comparados sistematicamente em 3.5 e sintetizados em termos de lacuna em 3.6.

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

Após a etapa de triagem, foram selecionados três trabalhos para análise comparativa. O critério de seleção priorizou cobertura dos componentes técnicos centrais do projeto: programação linear aplicada a decisões de crédito (AL-MUSBAHU et al., 2025; KWAPONG, 2013) e clusterização para identificação de risco financeiro (LI; TAO; LI, 2022). Um trabalho adicional identificado na busca — Scarpel e Milioni (2002) — aborda a integração entre modelagem preditiva e otimização prescritiva em decisões de crédito, o que o aproxima conceitualmente do pipeline adotado neste projeto. Contudo, sua formulação emprega Programação Inteira sobre uma variável de decisão binária aplicada a crédito corporativo, contexto e natureza de decisão suficientemente distintos para que uma análise comparativa direta fosse de profundidade limitada. Por essa razão, o trabalho é referenciado como validação metodológica do paradigma de duas etapas na seção de lacuna identificada, sem integrar o conjunto de análises comparativas detalhadas.

Ressalta-se que esta revisão de literatura constitui uma base inicial, compatível com a fase de desenvolvimento em que o projeto se encontra. O conjunto de três trabalhos foi escolhido por oferecer uma fundação sólida para cada componente técnico do modelo, sem pretensão de exaustividade. Trabalhos adicionais poderão ser incorporados em versões futuras do artigo à medida que o escopo da análise for ampliado.

---

### 3.2 Application of Linear Programming for Optimal Net Revenue on Bank Loan — AL-MUSBAHU et al. (2025)

**Resumo do trabalho:** 

O trabalho aborda a aplicação da Programação Linear no contexto de otimizar a receita total no quesito de empréstimos bancários. A otimização de portfólios se trata de um pilar importante no setor de finanças e da Teoria de Investimentos, tendo implicações tanto para investidores quanto gestores, que precisam alocar recursos para múltiplas categorias de ativos (AL-MUSBAHU et al., 2025). Embora publicado em um periódico de circulação recente, o trabalho foi selecionado por ser o estudo mais atual identificado que aplica programação linear diretamente a portfólios de empréstimos bancários com dados reais de 2025, tornando-o relevante para a validação da abordagem adotada neste projeto.

Dessa forma, a Programação Linear apresenta-se como uma maneira para otimizar a alocação de empréstimos bancários em diferentes áreas (como empréstimos de crédito e para o financiamento de carros, por exemplo), considerando que as relações entre as variáveis mantenham-se lineares. Por esse caminho, uma função matemática linear pode ser mapeada, levando em consideração as relações da concessão de risco-retorno, segundo Konno e Yamazaki (1991, *apud* AL-MUSBAHU et al., 2025).

Com informações de Janeiro de 2025, coletadas do **Access Bank**, localizado na região Ogun, na Nigéria, o modelo definido leva em consideração informações reais relacionadas a taxas e parâmetros para a modelagem, como juros e risco. Assim, o programa foi capaz de retornar uma alocação ótima para um caso de teste, seguindo todas as restrições mapeadas para o cenário (como o fato de que 45% dos empréstimos totais precisavam ser destinados para o financiamento de carros e empréstimos para organizações) (AL-MUSBAHU et al., 2025).

No caso de teste, era desejado alocar ₦300.000.000. A alocação ótima mapeou que 20% do valor deveria ser destinado para o financiamento de residências, 50% para cartões de crédito e 30% para empréstimos para organizações, trazendo um retorno anual de ₦24.615.000. Categorias como empréstimos pessoais receberam uma alocação de zero, demonstrando como, em comparação com outras categorias, elas mostram-se como opções menos lucrativas para o banco (AL-MUSBAHU et al., 2025).

**Pontos positivos:**

O artigo aborda pontos importantes que estão diretamente relacionados com o contexto do trabalho elaborado. O principal deles é em relação à metodologia utilizada para a resolução do problema de alocação de empréstimos. Tanto o artigo de Al-Musbahu (2025) quanto neste trabalho empregam da Programação Linear, que se trata de uma técnica matemática de otimização, que busca determinar o melhor resultado possível (tanto de maximização quanto de minimização).

O artigo, além de mapear a função-objetivo, também traz as restrições do problema, aspecto extremamente importante para o funcionamento da solução. Um ponto explicitado é sobre a influência dessas restrições no resultado. Por exemplo, uma restrição pode exigir percentuais mínimos para certos tipos de empréstimos (como no caso de teste apresentado na introdução), forçando a inclusão de categorias que, quando analisadas por um escopo individual, não se apresentam como ideais (tendo um retorno financeiro menor). Com isso, o trabalho destaca que a solução ótima do modelo abordado por esse artigo não deve contemplar apenas o resultado das taxas de retorno, mas sim levar em consideração as regras de negócio específicas. Aspectos como a taxa de inadimplência permitem a abordagem de cenários mais realistas e completos para a solução.  

Por outro lado, um aspecto que ambos também tratam é da aplicação direta da Programação Linear para problemas do mundo financeiro. Apesar de não abordarem o mesmo tema diretamente (empréstimos X limite de crédito), tanto o artigo de Al-Musbahu (2025) quanto este trabalho buscam trazer a computação e utilização de algoritmos para ambientes financeiros especializados. Como forma de validação, os dois empregam dados reais de instituições financeiras, trabalhando sobre informações condizentes com os cenários existentes, trazendo uma maior confiabilidade para os resultados encontrados.

**Pontos negativos / limitações:** 

Conforme mencionado anteriormente, uma limitação do trabalho de Al-Musbahu (2025) em relação a este projeto está no nível de análise adotado: apesar de ambos estarem no ambiente financeiro, o artigo trabalha com alocação entre categorias de empréstimos, enquanto aqui o foco é a definição de limite de crédito. Essa diferença afeta não apenas o objetivo da formulação, mas também os parâmetros considerados, o que reduz a comparabilidade direta entre os dois modelos.

Outro ponto a considerar é a amostragem de dados. O artigo de Al-Musbahu utiliza informações de uma única instituição/filial em um recorte temporal específico, o que pode limitar a robustez do modelo e a generalização dos resultados, já que os parâmetros de juros, risco e restrições refletem um contexto particular.


**Diferença em relação ao nosso problema:** 

A divergência central está na variável de decisão e na granularidade operacional. Enquanto o artigo de Al-Musbahu (2025) investiga a definição ótima de alocação entre categorias de empréstimos bancários, o presente trabalho trata da oferta de limite de crédito para clientes, organizada por clusters/perfis.

Além disso, o artigo comparado opera com um conjunto menor de variáveis agregadas por tipo de empréstimo (por exemplo, taxa de juros e inadimplência por categoria), ao passo que este trabalho utiliza um número maior de variáveis e parâmetros por cluster de clientes, incluindo aspectos como capacidade de pagamento e propensão à contratação. Essa diferença também aparece na base de dados: o artigo trabalha com uma amostra mais limitada, enquanto este projeto considera um volume maior de clientes, aumentando a complexidade do modelo e da definição da solução ótima.

---

### 3.3 Application of Linear Programming to Optimal Credit Portfolio: The Case of Akuapem Rural Bank Ltd. — KWAPONG (2013)

**Resumo do trabalho:** Kwapong (2013) formula e resolve um modelo de programação linear para maximizar o retorno líquido da carteira de crédito do Akuapem Rural Bank Ltd., banco rural de Gana com portfólio total de GH¢ 15 milhões. O banco opera com cinco modalidades de empréstimo (Indústria Artesanal, Transporte, Agricultura, Salário e Microfinanças), cada uma com taxa de juros e probabilidade de inadimplência distintas: o empréstimo de Transporte, por exemplo, opera a 32% com 5% de inadimplência, enquanto o Salário apresenta 30% de taxa e apenas 1% de inadimplência. A função objetivo maximiza a receita líquida de cada modalidade, descontando a perda esperada por inadimplência, formulada como $Z = \sum_j I_j(1 - P_j)x_j$. O modelo é resolvido sob quatro restrições principais: teto total de fundos, alocação mínima de 40% para Salário e Microfinanças, mínimo de 60% para os demais segmentos e teto de inadimplência agregada de 3% (KWAPONG, 2013).

Para testar a robustez da solução, o autor analisa sete cenários variando o número de restrições e as taxas de juros. No cenário base, a solução ótima aloca GH¢ 7 milhões a Transporte, GH¢ 2 milhões a Agricultura e GH¢ 6 milhões a Salário, com retorno de GH¢ 4,48 milhões, descartando Indústria Artesanal e Microfinanças por baixa atratividade líquida. O trabalho conclui que há relação positiva entre risco e retorno e que o aumento das taxas de juros melhora o resultado, desde que o risco seja controlado (KWAPONG, 2013). Apesar de publicado em 2013, trata-se do antecedente metodológico mais próximo identificado na literatura para a função objetivo adotada neste projeto, razão pela qual foi incluído na análise comparativa.

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

### 3.5 Tabela Comparativa dos Trabalhos Analisados

Examinados individualmente nas seções anteriores, os três trabalhos revelam padrões que se tornam mais nítidos numa comparação direta. A tabela a seguir sistematiza as dimensões mais relevantes para esse confronto, com ênfase em dois eixos que a análise anterior colocou em evidência: o nível em que a decisão é tomada, distinguindo portfólio agregado de cluster de clientes; e o papel que a segmentação ocupa no pipeline de cada trabalho, como produto final ou como etapa de entrada para uma decisão operacional.

A distribuição dos trabalhos nesses dois eixos é reveladora. Al-Musbahu et al. (2025) e Kwapong (2013) empregam programação linear sobre categorias de crédito predefinidas pelo banco, sem qualquer etapa de segmentação baseada em dados. Li, Tao e Li (2022) seguem o caminho inverso: demonstram que dados financeiros conseguem separar perfis de risco com objetividade, mas encerram o trabalho nessa etapa, sem traduzir os grupos em nenhuma decisão operacional. O presente trabalho parte da combinação das duas abordagens.

| Dimensão | AL-MUSBAHU et al. (2025) | KWAPONG (2013) | LI; TAO; LI (2022) | Este trabalho |
|---|---|---|---|---|
| **Problema central** | Alocação ótima de portfólio de empréstimos bancários | Maximização de receita líquida de portfólio de crédito rural | Identificação de empresas de alto risco financeiro | Otimização de limites de crédito pré-aprovados por cluster de clientes |
| **Técnica principal** | Programação Linear | Programação Linear + análise de sensibilidade (7 cenários) | K-Means em dois níveis + PCA | CART + Programação Linear (Simplex / HiGHS) |
| **Nível de análise** | Portfólio agregado por tipo de produto | Portfólio agregado por modalidade | Grupo de empresas (sem decisão operacional) | Cluster de clientes individuais (~800 grupos) |
| **Segmentação dos tomadores** | Ausente — categorias predefinidas institucionalmente | Ausente — modalidades predefinidas institucionalmente | Endógena via K-Means — **produto final** do pipeline | Endógena via CART — **etapa intermediária** do pipeline |
| **Variável de decisão** | Volume alocado por tipo de empréstimo (R$) | Volume alocado por modalidade de crédito (R$) | Não há | Limite contínuo $L_k \in \mathbb{R}^+$ por cluster |
| **Controle de risco** | Taxa de inadimplência por categoria de empréstimo | Teto de PD agregada (3%) + PD por modalidade | Concentração de eventos ST no cluster de risco | PD financeira ponderada (R1), alavancagem diferenciada por score (R2), concentração por cluster (R5) |
| **Domínio de aplicação** | Empréstimos bancários — Nigéria | Crédito rural — Gana | Risco corporativo — China | Cartão de crédito PF — Brasil (~1,8M elegíveis/safra) |

A tabela confirma uma observação que emerge das análises anteriores: o trabalho que mais se aproxima estruturalmente deste é Kwapong (2013), não pelo contexto geográfico nem pela escala, mas pela forma da função objetivo. A expressão utilizada por Kwapong,

$$Z = \sum_j I_j(1 - P_j)x_j$$

corresponde diretamente ao coeficiente adotado aqui:

$$c_k = \pi_k \cdot (T\bar{u}t - PD_k \cdot \gamma_{d(k)} \cdot \text{LGD})$$

Nos dois casos, o retorno por unidade alocada é calculado como a diferença entre a receita esperada e a perda esperada por inadimplência. A distinção está no nível de operação: Kwapong (2013) resolve o problema para cinco modalidades predefinidas pelo banco; este trabalho resolve para aproximadamente 800 clusters derivados dos próprios dados via CART.

Já a contribuição de Li, Tao e Li (2022) é de outra natureza: o artigo não propõe uma formulação de otimização, mas demonstra que variáveis financeiras conseguem separar perfis de risco com objetividade, o que sustenta a premissa da Etapa 1 do pipeline proposto. O que essa leitura implica em termos de lacuna de pesquisa é o tema da seção seguinte.

---

### 3.6 Lacuna Identificada

A comparação sistematizada na seção anterior permite precisar três dimensões de lacuna relevantes para o presente projeto.

A primeira diz respeito à granularidade da variável de decisão. Kwapong (2013) e Al-Musbahu et al. (2025) formulam problemas de programação linear sobre categorias de empréstimo predefinidas, tratando todos os tomadores de um mesmo segmento como homogêneos. Nenhum dos dois realiza segmentação baseada em dados: as categorias são definidas institucionalmente, não derivadas do comportamento observado da base. Essa homogeneidade limita a capacidade do modelo de capturar a variação real entre perfis de clientes e de calibrar limites proporcionais a cada tomador.

A segunda lacuna está na desconexão entre segmentação e decisão. Li, Tao e Li (2022) demonstram que variáveis financeiras permitem separar perfis de risco de forma objetiva e reprodutível, mas encerram o trabalho nessa etapa: os grupos identificados não alimentam nenhuma decisão operacional. A clusterização é o produto final, não uma entrada para um problema de otimização.

A terceira lacuna está na ausência de um pipeline que integre as duas etapas em decisões de crédito ao consumidor em escala real. Scarpel e Milioni (2002) avançam nessa direção ao combinar um modelo Logit com Programação Inteira para decisões de concessão de crédito no contexto brasileiro, validando o paradigma de estimar e depois otimizar. Trata-se de uma referência metodologicamente consolidada que, apesar de sua data de publicação, representa o único trabalho identificado que integra modelagem preditiva e otimização prescritiva em concessão de crédito no contexto brasileiro. O trabalho, contudo, trata a concessão como uma decisão binária sobre crédito corporativo, sem atribuição contínua de limite a pessoas físicas em escala de portfólio. Por essa razão, optou-se por não incluí-lo nas análises comparativas detalhadas: o contexto e a natureza da variável de decisão diferem o suficiente para que uma comparação direta fosse de profundidade limitada. O trabalho é referenciado, ainda assim, como validação metodológica do pipeline adotado.

Reconhece-se que a abordagem proposta tem limitações próprias: a qualidade da otimização depende da estabilidade dos clusters gerados, e o modelo requer revalidação periódica conforme o comportamento de crédito da base evolui, aspectos que ficam fora do escopo deste trabalho e apontam para direções de pesquisa futura. O presente trabalho busca endereçar as três dimensões identificadas ao propor um pipeline que combina segmentação via CART com otimização contínua de limite via programação linear, aplicado a um portfólio de crédito ao consumidor em escala real.

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

*Nota: os links disponibilizados nas referências direcionam para a página do artigo na base de origem. O acesso ao texto completo pode exigir clicar em botão de visualização ou download de PDF disponível na própria página.*

AL-MUSBAHU, Abdulrahim; TETE, Ahmed Rufai; MANYISA, Yisa Emmanuel; MOHAMMED, Jibrin. Application of Linear Programming for Optimal Net Revenue on Bank Loan. **Kontagora Journal of Mathematics**, v. 1, n. 1, p. 214-230, 2025. DOI: 10.5281/zenodo.17401383.

KWAPONG, Samuel Darkwa. Application of Linear Programming to Optimal Credit Portfolio: The Case of Akuapem Rural Bank Ltd. 2013. Dissertação (MSc in Industrial Mathematics) — Kwame Nkrumah University of Science and Technology, Institute of Distance Learning, Kumasi, 2013. Disponível em: <https://ir.knust.edu.gh/handle/123456789/5841>. Acesso em: 20 maio 2026.

LI, Bingxiang; TAO, Rui; LI, Meng. Identification of Enterprise Financial Risk Based on Clustering Algorithm. **Computational Intelligence and Neuroscience**, v. 2022, art. 1086945, 2022. DOI: 10.1155/2022/1086945.

SCARPEL, R. A.; MILIONI, A. Z. Utilização conjunta de modelagem econométrica e otimização em decisões de concessão de crédito. **Pesquisa Operacional**, v. 22, n. 1, p. 61-72, 2002. DOI: 10.1590/S0101-74382002000100004.