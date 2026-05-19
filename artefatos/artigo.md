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

A busca foi conduzida nas bases ScienceDirect, SciELO, arXiv.org, IEEE Xplore e Google Scholar. As consultas foram realizadas em português e inglês, combinando termos de domínio como *cartão de crédito*, *concessão de crédito*, *credit limit* e *credit line management* com termos metodológicos como *programação linear*, *programação inteira mista* e *decision optimization*. As principais queries utilizadas foram:

| # | Query |
|---|---|
| 1 | `"credit limit optimization" AND "linear programming" AND "bank"` |
| 2 | `"credit card line assignment" AND "optimization" AND "portfolio"` |
| 3 | `"credit risk" AND "credit limit optimization"` |
| 4 | `"credit line assignment" AND "customer segmentation"` |
| 5 | `"otimização de limite de crédito" AND "cartão de crédito"` |
| 6 | `"gestão de linha de crédito" AND "modelos contínuos"` |

As queries foram adaptadas e aplicadas às bases listadas, respeitando as particularidades de indexação de cada uma.

**Critérios de inclusão:** aderência ao problema de definição, ajuste ou otimização de decisões de crédito; tratamento explícito de otimização, modelagem prescritiva ou formulação matemática aplicável ao contexto financeiro; publicação nos últimos cinco anos, preferencialmente. Trabalhos fora desse recorte temático, mas relevantes como base metodológica para a formulação do modelo, também foram considerados quando contribuíam diretamente para a estrutura de otimização adotada.

**Critérios de exclusão:** materiais sem densidade técnica; textos promocionais ou instrucionais voltados ao consumidor final; referências sem conexão com modelagem analítica ou otimização de política de crédito.

Após a etapa de triagem, foram selecionados quatro trabalhos para análise comparativa. Três deles são recentes e tratam de gestão de limites de crédito, otimização matemática e decisões financeiras orientadas por risco e retorno. Um quarto trabalho, mais antigo, foi incluído por sua relevância metodológica consolidada na integração entre modelagem estatística e otimização aplicada à concessão de crédito.

---

### 3.2 Application of Linear Programming for Optimal Net Revenue on Bank Loan

**Resumo do trabalho:** [Descreva o problema que o trabalho aborda, a metodologia utilizada e os principais resultados obtidos. Use citação indireta (AL-MUSBAHU et al., 2025).]

**Pontos positivos:** [O que o trabalho faz bem e que é relevante para o nosso contexto.]

**Pontos negativos / limitações:** [Limitações metodológicas, de dados ou de escopo identificadas no trabalho.]

**Diferença em relação ao nosso problema:** [Explique de forma clara por que o problema tratado neste trabalho **não é idêntico** ao nosso: diferenças no objetivo (ex.: minimização de custo vs. maximização de retorno), no tipo de dado (ex.: crédito corporativo vs. crédito ao consumidor), na técnica (ex.: heurística vs. PL exata) ou no contexto de aplicação. Este campo é especialmente importante para justificar a pertinência da busca sem que o trabalho resolva exatamente o mesmo problema.]

**Referência ABNT:**

> AL-MUSBAHU, Abdulrahim; TETE, Ahmed Rufai; MANYISA, Yisa Emmanuel; MOHAMMED, Jibrin. Application of linear programming for optimal net revenue on bank loan. **Kontagora Journal of Mathematics**, v. 1, n. 1, p. 214–230, 2025. DOI: 10.5281/zenodo.17401383.

---

### 3.3 Turbinando a gestão de limites de crédito com analíticos avançados

**Resumo do trabalho:** [Descreva o problema que o trabalho aborda, a metodologia utilizada e os principais resultados obtidos. Use citação indireta (IT FORUM, [s.d.]).]

**Pontos positivos:** [O que o trabalho faz bem e que é relevante para o nosso contexto.]

**Pontos negativos / limitações:** [Limitações metodológicas, de dados ou de escopo identificadas no trabalho.]

**Diferença em relação ao nosso problema:** [Explique de forma clara por que o problema tratado neste trabalho **não é idêntico** ao nosso.]

**Referência ABNT:**

> IT FORUM. Turbinando a gestão de limites de crédito com analíticos avançados. **IT Forum**, [s.d.]. Disponível em: https://itforum.com.br/noticias/gestao-limites-redito-analiticos-avancados/. Acesso em: 19 maio 2026.

---

### 3.4 Otimização matemática: o grande trunfo para geração de retorno financeiro para as empresas

**Resumo do trabalho:** [Descreva o problema que o trabalho aborda, a metodologia utilizada e os principais resultados obtidos. Use citação indireta (FERNANDES, 2021).]

**Pontos positivos:** [O que o trabalho faz bem e que é relevante para o nosso contexto.]

**Pontos negativos / limitações:** [Limitações metodológicas, de dados ou de escopo identificadas no trabalho.]

**Diferença em relação ao nosso problema:** [Explique de forma clara por que o problema tratado neste trabalho **não é idêntico** ao nosso.]

**Referência ABNT:**

> FERNANDES, Marcelo. Otimização matemática: o grande trunfo para geração de retorno financeiro para as empresas. **TI Inside Online**, 19 fev. 2021. Disponível em: https://tiinside.com.br/19/02/2021/otimizacao-matematica-o-grande-trunfo-para-geracao-de-retorno-financeiro-para-as-empresas/. Acesso em: 19 maio 2026.

---

### 3.5 Utilização conjunta de modelagem econométrica e otimização em decisões de concessão de crédito *(referência clássica)*

**Resumo do trabalho:** [Descreva o problema que o trabalho aborda, a metodologia utilizada e os principais resultados obtidos. Use citação indireta (SCARPEL; MILIONI, 2002). Justifique brevemente a inclusão de um trabalho fora do recorte temporal dos últimos cinco anos.]

**Pontos positivos:** [O que o trabalho faz bem e que é relevante para o nosso contexto.]

**Pontos negativos / limitações:** [Limitações metodológicas, de dados ou de escopo identificadas no trabalho.]

**Diferença em relação ao nosso problema:** [Explique de forma clara por que o problema tratado neste trabalho **não é idêntico** ao nosso.]

**Referência ABNT:**

> SCARPEL, R. A.; MILIONI, A. Z. Utilização conjunta de modelagem econométrica e otimização em decisões de concessão de crédito. **Pesquisa Operacional**, v. 22, n. 1, p. 61–72, 2002. Disponível em: https://www.scielo.br/j/pope/a/3DkFSwbgRxdtDDG6MSPBDLM/. Acesso em: 19 maio 2026.

---

---
> 💡 **Sugestão de "ir além" — Trabalhos Relacionados**
>
> Ao final da seção, após a tabela comparativa, adicione um parágrafo de **lacuna identificada** (*research gap*): explique o que nenhum dos trabalhos encontrados resolve e que este projeto se propõe a resolver. Algo como: "Observa-se que nenhum dos trabalhos revisados combina simultaneamente X, Y e Z no contexto de W — lacuna que este trabalho busca preencher." Isso é padrão em artigos de conferência e periódico, e deixa o leitor com clareza sobre a contribuição original do trabalho.

### 3.6 Tabela Comparativa

| Dimensão | AL-MUSBAHU et al. (2025) | IT FORUM ([s.d.]) | FERNANDES (2021) | SCARPEL; MILIONI (2002) | Este trabalho |
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

AL-MUSBAHU, Abdulrahim; TETE, Ahmed Rufai; MANYISA, Yisa Emmanuel; MOHAMMED, Jibrin. Application of linear programming for optimal net revenue on bank loan. **Kontagora Journal of Mathematics**, v. 1, n. 1, p. 214–230, 2025. DOI: 10.5281/zenodo.17401383.

FERNANDES, Marcelo. Otimização matemática: o grande trunfo para geração de retorno financeiro para as empresas. **TI Inside Online**, 19 fev. 2021. Disponível em: https://tiinside.com.br/19/02/2021/otimizacao-matematica-o-grande-trunfo-para-geracao-de-retorno-financeiro-para-as-empresas/. Acesso em: 19 maio 2026.

IT FORUM. Turbinando a gestão de limites de crédito com analíticos avançados. **IT Forum**, [s.d.]. Disponível em: https://itforum.com.br/noticias/gestao-limites-redito-analiticos-avancados/. Acesso em: 19 maio 2026.

SCARPEL, R. A.; MILIONI, A. Z. Utilização conjunta de modelagem econométrica e otimização em decisões de concessão de crédito. **Pesquisa Operacional**, v. 22, n. 1, p. 61–72, 2002. Disponível em: https://www.scielo.br/j/pope/a/3DkFSwbgRxdtDDG6MSPBDLM/. Acesso em: 19 maio 2026.
