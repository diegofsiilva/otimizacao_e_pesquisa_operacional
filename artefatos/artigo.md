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

### 3.1 Protocolo de Busca e Seleção

A busca foi conduzida nas bases ScienceDirect, SciELO, arXiv.org, IEEE Xplore e Google Scholar. As consultas foram realizadas em português e inglês, combinando termos de domínio como *crédito bancário*, *cartão de crédito*, *concessão de crédito*, *credit limit*, *credit line management* e *credit portfolio* com termos metodológicos como *programação linear*, *programação inteira mista* e *decision optimization*. As principais queries utilizadas foram:

| # | Query |
|---|---|
| 1 | `"credit limit optimization" AND "linear programming" AND "bank"` |
| 2 | `"credit card line assignment" AND "optimization" AND "portfolio"` |
| 3 | `"credit risk" AND "credit limit optimization"` |
| 4 | `"credit line assignment" AND "customer segmentation"` |
| 5 | `"otimização de limite de crédito" AND "cartão de crédito"` |
| 6 | `"gestão de linha de crédito" AND "modelos contínuos"` |
| 7 | `"optimal credit portfolio" AND "linear programming"` |
| 8 | `"loan returns" AND "financial institution" AND "linear programming"` |
| 9 | `"clustering" AND "financial risk" AND "bank"` |

As queries foram adaptadas e aplicadas às bases listadas, respeitando as particularidades de indexação de cada uma.

**Critérios de inclusão:** aderência ao problema de definição, ajuste ou otimização de decisões de crédito; tratamento explícito de otimização, modelagem prescritiva ou formulação matemática aplicável ao contexto financeiro; e contribuição para a discussão de risco, retorno e alocação de crédito em instituições financeiras. Foram priorizadas publicações dos últimos cinco anos, preferencialmente. Trabalhos fora desse recorte temporal ou temático estrito também foram considerados quando apresentavam relevância metodológica consolidada e contribuição direta para a formulação do modelo adotado.

**Critérios de exclusão:** materiais sem densidade técnica; textos promocionais ou instrucionais voltados ao consumidor final; referências sem conexão com modelagem analítica, otimização ou apoio quantitativo à decisão de crédito; e trabalhos cujo foco principal não permitisse estabelecer relação com o problema de alocação, aprovação ou gestão de crédito.

Após a etapa de triagem, foram selecionados quatro trabalhos para análise comparativa. Três deles foram escolhidos por sua aderência aos temas de otimização de portfólio de crédito via programação linear e identificação de risco financeiro via clusterização. Um quarto trabalho, mais antigo, foi incluído por sua relevância metodológica consolidada na integração entre modelagem econométrica e otimização aplicada à concessão de crédito.

---

### 3.2 Application of Linear Programming for Optimal Net Revenue on Bank Loan — AL-MUSBAHU et al. (2025)

**Resumo do trabalho:** [Descreva o problema que o trabalho aborda, a metodologia utilizada e os principais resultados obtidos. Use citação indireta (AL-MUSBAHU et al., 2025).]

**Pontos positivos:** [O que o trabalho faz bem e que é relevante para o nosso contexto.]

**Pontos negativos / limitações:** [Limitações metodológicas, de dados ou de escopo identificadas no trabalho.]

**Diferença em relação ao nosso problema:** [Explique de forma clara por que o problema tratado neste trabalho **não é idêntico** ao nosso: diferenças no objetivo (ex.: minimização de custo vs. maximização de retorno), no tipo de dado (ex.: crédito corporativo vs. crédito ao consumidor), na técnica (ex.: heurística vs. PL exata) ou no contexto de aplicação. Este campo é especialmente importante para justificar a pertinência da busca sem que o trabalho resolva exatamente o mesmo problema.]

**Referência ABNT:**

> AL-MUSBAHU, Abdulrahim; TETE, Ahmed Rufai; MANYISA, Yisa Emmanuel; MOHAMMED, Jibrin. Application of linear programming for optimal net revenue on bank loan. **Kontagora Journal of Mathematics**, v. 1, n. 1, p. 214–230, 2025. DOI: 10.5281/zenodo.17401383.

---

### 3.3 Application of Linear Programming to Optimal Credit Portfolio: The Case of Akuapem Rural Bank Ltd. — KWAPONG (2013)

**Resumo do trabalho:** [Descreva o problema que o trabalho aborda, a metodologia utilizada e os principais resultados obtidos. Use citação indireta (KWAPONG, 2013).]

**Pontos positivos:** [O que o trabalho faz bem e que é relevante para o nosso contexto.]

**Pontos negativos / limitações:** [Limitações metodológicas, de dados ou de escopo identificadas no trabalho.]

**Diferença em relação ao nosso problema:** [Explique de forma clara por que o problema tratado neste trabalho **não é idêntico** ao nosso.]

**Referência ABNT:**

> KWAPONG, Samuel Darkwa. Application of Linear Programming to Optimal Credit Portfolio: The Case of Akuapem Rural Bank Ltd. 2013. Dissertação (MSc in Industrial Mathematics) — Kwame Nkrumah University of Science and Technology, Institute of Distance Learning, 2013. Disponível em: <https://ir.knust.edu.gh/handle/123456789/5841>. Acesso em: 20 maio 2026.

---

### 3.4 Identification of Enterprise Financial Risk Based on Clustering Algorithm — LI; TAO; LI (2022)

**Resumo do trabalho:** O trabalho aborda a identificação de risco financeiro em empresas listadas na China, com o objetivo de selecionar um conjunto pequeno de empresas de alto risco que concentre uma proporção elevada de companhias que viriam a receber tratamento especial (ST – "special treatment") nos anos seguintes (LI; TAO; LI, 2022). A metodologia parte de 27 indicadores financeiros alternativos, dos quais são selecionadas 4 variáveis financeiras finais: razão de ativos tangíveis, razão de caixa sobre ativos, razão de endividamento de curto prazo e razão de endividamento de longo prazo. Os autores aplicam PCA para reduzir essas 4 variáveis a 2 dimensões e, em seguida, utilizam o algoritmo K-means (com K = 3 na primeira etapa e K = 4 na segunda etapa, aplicando K-means novamente apenas no cluster com mais empresas ST) para formar grupos e identificar o cluster de alto risco (LI; TAO; LI, 2022). O resultado principal mostra que o cluster de alto risco representa apenas 9% da amostra, mas concentra cerca de 36% das novas empresas ST já no ano corrente, proporção que aumenta ao estender o horizonte para 5 anos. Os autores concluem que o K-means, mesmo selecionando um grupo pequeno, é eficaz para filtrar empresas que merecem atenção cuidadosa de investidores (LI; TAO; LI, 2022).

**Pontos positivos:** [O que o trabalho faz bem e que é relevante para o nosso contexto.]

**Pontos negativos / limitações:** [Limitações metodológicas, de dados ou de escopo identificadas no trabalho.]

**Diferença em relação ao nosso problema:** [Explique de forma clara por que o problema tratado neste trabalho **não é idêntico** ao nosso.]

**Referência ABNT:**

> LI, Bingxiang; TAO, Rui; LI, Meng. Identification of Enterprise Financial Risk Based on Clustering Algorithm. **Computational Intelligence and Neuroscience**, v. 2022, art. 1086945, 2022. DOI: 10.1155/2022/1086945.

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

KWAPONG, Samuel Darkwa. Application of Linear Programming to Optimal Credit Portfolio: The Case of Akuapem Rural Bank Ltd. 2013. Dissertação (MSc in Industrial Mathematics) — Kwame Nkrumah University of Science and Technology, Institute of Distance Learning, 2013.

LI, Bingxiang; TAO, Rui; LI, Meng. Identification of Enterprise Financial Risk Based on Clustering Algorithm. **Computational Intelligence and Neuroscience**, v. 2022, art. 1086945, 2022. DOI: 10.1155/2022/1086945.

SCARPEL, R. A.; MILIONI, A. Z. Utilização conjunta de modelagem econométrica e otimização em decisões de concessão de crédito. **Pesquisa Operacional**, v. 22, n. 1, p. 61-72, 2002. DOI: 10.1590/S0101-74382002000100004. Disponível em: <https://www.scielo.br/j/pope/a/3DkFSwbgRxdtDDG6MSPBDLM/>. Acesso em: 20 maio 2026.