# Entendimento do Negócio

> **Status:** Rascunho pré-TAPI. Seções preenchidas com base em dados públicos do Banco Pan e na descrição do projeto. Trechos com `[PREENCHER]` precisam do TAPI. Trechos com `[VALIDAR]` devem ser confirmados com o parceiro.
>
> **Dependências com outros artefatos:**
> - `[APÓS UX]` = preencher quando as personas estiverem prontas
> - `[APÓS MODELAGEM]` = preencher quando a formulação matemática estiver pronta
> - `[APÓS TAPI]` = preencher quando o TAPI for recebido

---

## 1. Matriz de Avaliação de Valor - Oceano Azul (Peso 2,5)

&emsp; A Estratégia do Oceano Azul, desenvolvida por W. Chan Kim e Renée Mauborgne [1], parte da premissa de que o crescimento competitivo mais relevante não vem da disputa por participação em mercados saturados (oceanos vermelhos), mas da criação de espaços de mercado inexplorados onde a concorrência torna-se irrelevante. Para operacionalizar essa lógica, os autores propõem a Matriz de Avaliação de Valor (Strategy Canvas), ferramenta que permite mapear visualmente como diferentes soluções se posicionam em relação a um conjunto de atributos relevantes para o cliente, revelando eixos de diferenciação.
No contexto deste projeto, a aplicação da matriz serve a dois propósitos complementares: primeiro, mapear o posicionamento relativo da solução proposta frente às alternativas hoje disponíveis no mercado brasileiro para definição de limites pré-aprovados de crédito; segundo, identificar onde a proposta gera valor diferenciado o suficiente para justificar sua adoção pelo Banco PAN em um setor no qual a concorrência por clientes de cartão é intensa. A análise se organiza em torno de oito atributos estratégicos selecionados pela equipe e comparados entre três abordagens representativas do espectro competitivo.a

### 1.1 Abordagens Comparadas

A comparação envolve três abordagens distintas que representam o espectro real de soluções adotadas no mercado para definição de limites de crédito pré-aprovado. A escolha deliberada desse trio — em vez de comparar apenas prática tradicional versus solução proposta — permite mostrar que a diferenciação da proposta não se resume a "ser mais moderna", mas a ocupar um ponto ótimo entre sofisticação analítica e transparência.

**Abordagem A** — Prática tradicional do setor. Corresponde ao modelo dominante em instituições financeiras brasileiras de médio porte: definição de limites a partir de regras fixas por faixa de score de crédito, complementadas por calibragem manual de parâmetros realizada empiricamente pelo time de estratégia de crédito. A decisão costuma ser operacionalmente escalável, mas pouco granular e metodologicamente opaca.

**Abordagem B** — Modelos de Machine Learning Black-Box. Corresponde a abordagens mais sofisticadas adotadas por fintechs e bancos digitais, tipicamente baseadas em modelos de aprendizado supervisionado (XGBoost, redes neurais) que preveem diretamente o "limite ótimo" a partir de features do cliente. Essa abordagem é consistente com práticas internacionais consolidadas em Credit Limit Optimization [2], mas apresenta limitações estruturais em explicabilidade e em incorporação de restrições agregadas de carteira.
Nota: o TAPI descreve a prática atual do Banco PAN como scoring + regras fixas (mais próxima da Abordagem A), não como ML black-box. A inclusão da Abordagem B como comparador serve para demonstrar que a solução proposta não perde em sofisticação frente ao estado da arte em modelagem preditiva, ao mesmo tempo em que supera essa alternativa em rastreabilidade e controle.

**Abordagem C** - Nossa Solução (Otimização Matemática). Corresponde à proposta do grupo: um modelo de otimização linear que determina limites pré-aprovados por cliente ou cluster (mínimo 100 clusters), maximizando o retorno esperado da carteira — definido a partir da receita de interchange a taxa fixa, conforme orientação do TAPI — sujeito a restrições explícitas de apetite de risco (tetos de inadimplência física e financeira), capacidade de pagamento individual com alavancagem diferenciada por perfil de risco, metas de produção configuráveis e regras operacionais (limite mínimo de R\$200, discretização em múltiplos de R\$50). A solução é complementarmente informada pelo arcabouço de perda esperada da Resolução CMN nº 4.966/2021 [3] — contribuição analítica do grupo, não requisito formal do parceiro — e articula sofisticação matemática com rastreabilidade da decisão.

### 1.2 Os 8 atributos

*O roteiro pede exatamente **8 atributos relevantes para o cliente e/ou parceiro**, com justificativa de cada um para o problema do Banco Pan.*

> **NÃO FAZER (roteiro):**
> - ~~Atributos genéricos como "qualidade" ou "eficiência" sem explicar~~
> - ~~Confundir atributo do cliente com característica técnica sem relação com valor percebido~~

| # | Atributo | Por que é relevante para o Banco Pan |
|:---:|:---|:---|
| 1 | **Precisão na definição do limite** | O Pan tem NPL >90d em 8,3% (Q2 2025) — limites mal calibrados são uma das causas diretas. Definir o limite certo reduz inadimplência e aumenta utilização. |
| 2 | **Controle de risco da carteira** | Com NPL crescente há 12 meses, controlar o risco agregado da carteira (não apenas individual) é prioridade. |
| 3 | **Aderência à capacidade de pagamento** | O projeto exige que limites respeitem capacidade de pagamento do cliente — é critério-chave. `[VALIDAR: confirmar peso deste critério com parceiro]` |
| 4 | **Personalização por perfil de cliente** | O Pan tem 32,1M de clientes com perfis diversos. Tratá-los de forma homogênea por faixa de score gera sub ou sobre-concessão. |
| 5 | **Rapidez da decisão** | Crédito pré-aprovado exige decisão em tempo quase real para não perder o momento de conversão. |
| 6 | **Transparência/explicabilidade** | LGPD Art. 20 exige explicabilidade de decisões automatizadas. Áreas internas (risco, compliance) também precisam entender a lógica. |
| 7 | **Escalabilidade** | Os dados mostram ~14,5M de clientes na base e ~12,7M elegíveis. A solução precisa funcionar nessa escala. |
| 8 | **Governança da decisão** | Bacen e compliance exigem rastreabilidade e controle sobre os parâmetros que definem limites. |

### 1.3 Matriz de avaliação

*Justificar **cada nota** na seção seguinte. Não preencher a matriz sem justificativa.*

| Atributo | Tradicional | Scoring + Regras | Solução do Grupo |
|:---|:---:|:---:|:---:|
| Precisão na definição do limite | 4 | 6 | 9 |
| Controle de risco da carteira | 5 | 6 | 9 |
| Aderência à capacidade de pagamento | 5 | 5 | 9 |
| Personalização por perfil de cliente | 3 | 5 | 9 |
| Rapidez da decisão | 3 | 8 | 8 |
| Transparência/explicabilidade | 7 | 4 | 8 |
| Escalabilidade | 2 | 8 | 7 |
| Governança da decisão | 6 | 5 | 8 |

> `[VALIDAR]` As notas da coluna "Scoring + Regras" refletem o estado atual do Pan. Confirmar com o parceiro no kickoff se os scores internos correspondem à realidade operacional.

**Justificativa das notas:**

- **Precisão (4 / 6 / 9):** A abordagem tradicional usa julgamento humano, sujeito a viés. Scoring + regras melhora com dados, mas o mapeamento score→limite por tabela ignora variáveis como utilização esperada. A solução do grupo otimiza considerando múltiplas variáveis simultaneamente. `[APÓS MODELAGEM: especificar quais variáveis]`
- **Controle de risco (5 / 6 / 9):** Tradicional é reativa (revisão periódica). Scoring define limites por faixa individual, mas não controla o NPL agregado. A solução inclui restrição explícita de NPL máximo — controle agregado.
- **Aderência à capacidade (5 / 5 / 9):** Tradicional considera renda qualitativamente. Scoring usa renda como input, mas o limite final vem de tabela. A solução modela capacidade como restrição hard. Os dados mostram a variável `capacidade_pagamento` disponível (mediana R$ 550, max R$ 25.000).
- **Personalização (3 / 5 / 9):** Tradicional usa grandes segmentos informais. Scoring tipicamente 5-10 faixas. A solução pode definir limite por cliente individual ou por cluster refinado.
- **Rapidez (3 / 8 / 8):** Tradicional depende de analista humano. Scoring e otimização são automatizados. A solução do grupo recebe 8 (não 9) porque o tempo de solver pode ser maior que lookup de tabela, mas ainda near-real-time.
- **Transparência (7 / 4 / 8):** Tradicional é transparente (o analista explica), mas subjetiva. Scoring com ML pode ser black-box. A solução de otimização gera decisões rastreáveis — cada limite resulta de restrições explícitas.
- **Escalabilidade (2 / 8 / 7):** Tradicional não escala. Scoring escala muito bem (tabela). A solução exige solver, que escala mas com custo computacional crescente — por isso 7 e não 9. `[APÓS MODELAGEM: estimar tempo de solver para 14,5M clientes]`
- **Governança (6 / 5 / 8):** Tradicional tem governança via comitê, mas informal. Scoring tem modelo documentado, mas tradução score→limite é ad hoc. A solução explicita todas as restrições — auditável e versionável.

### 1.4 As quatro ações

> **NÃO FAZER (roteiro):** ~~Descrever o conceito de Oceano Azul sem aplicá-lo ao projeto~~

**Reduzir**

- **Subjetividade da decisão:** a prática tradicional depende do julgamento do analista. A solução reduz isso ao tornar a decisão resultado de otimização com parâmetros explícitos.
- **Exposição desnecessária ao risco:** modelos de scoring + regras fixas podem conceder limites elevados a clientes que "passam" no score mas têm baixa capacidade. Os dados mostram `delta_capacidade_pagamento` negativo para parte da base — indicando piora na capacidade. A solução usa `capacidade_pagamento` como restrição direta.

**Eliminar**

- **Concessão padronizada sem segmentação:** a tabela fixa (score → limite) trata todos de um mesmo score como iguais. Os dados mostram que clientes com o mesmo `score_interno` podem ter `capacidade_pagamento` entre R$ 0 e R$ 25.000 — são perfis completamente diferentes. A solução elimina essa padronização.
- **Decisões empíricas sem critério formal:** decisões "para esse perfil costumamos dar X" são eliminadas pela lógica estruturada de otimização.

**Aumentar**

- **Assertividade da oferta:** limites mais aderentes ao perfil aumentam probabilidade de ativação. Os dados mostram que dos ~117K que receberam oferta, apenas ~6.500 contrataram (5,6%) e ~5.700 ativaram. Limites inadequados ao perfil podem estar contribuindo para essa baixa conversão.
- **Controle de risco da carteira:** a solução eleva o nível de controle ao tratar o NPL máximo como restrição do modelo, não como consequência observada ex post.
- **Uso de dados na decisão:** a otimização consome mais variáveis simultaneamente do que uma tabela de regras (PD, capacidade, renda, score de propensão, etc.). Os dados disponíveis incluem pelo menos 10 variáveis de input relevantes.

**Criar**

- **Lógica estruturada de otimização:** nenhuma das abordagens atuais **otimiza** — elas classificam e mapeiam. A solução busca o **melhor limite possível** dado as restrições. `[APÓS MODELAGEM: referenciar a função objetivo aqui]`
- **Balanceamento simultâneo entre risco e retorno:** hoje o trade-off é resolvido informalmente. A solução formaliza na função objetivo. `[APÓS MODELAGEM: mencionar λ ou ponderação explícita]`
- **Explicitação das restrições de negócio:** restrições como NPL máximo, budget, limite mínimo/máximo saem do "conhecimento tácito" e entram como parâmetros configuráveis do modelo.

---

## 2. Matriz de Risco (Peso 2,5)

### 2.1 Critérios de classificação

*O roteiro pede explicar os critérios usados para classificar impacto e probabilidade.*

| Nível | Probabilidade | Impacto |
|:---:|:---|:---|
| **Muito Baixo (1)** | < 5% de chance | Efeito negligenciável |
| **Baixo (2)** | 5–20% | Impacto menor, contornável sem replanejar |
| **Médio (3)** | 20–50% | Impacto moderado, exige ação corretiva |
| **Alto (4)** | 50–75% | Impacto significativo no escopo, prazo ou resultado |
| **Muito Alto (5)** | > 75% | Impacto crítico — pode inviabilizar o projeto |

### 2.2 Riscos identificados

*O roteiro pede **pelo menos 10 riscos** com: descrição, **causa provável**, impacto esperado, probabilidade, **posição na matriz** e **justificativa da classificação**.*

> **NÃO FAZER (roteiro):**
> - ~~Listar riscos genéricos como "o projeto pode dar errado"~~
> - ~~Citar riscos sem relação com a solução do grupo~~
> - ~~Não justificar a posição do risco na matriz~~
> - ~~Confundir risco do projeto com limitação natural do problema~~
>
> **NÃO FAZER (feedback M5):**
> - ~~Classificar como "baixo impacto" riscos que podem afetar a credibilidade do modelo~~ — calibrar com cuidado

| # | Risco | Causa provável | Impacto esperado | Prob. | Imp. | Posição |
|:---:|:---|:---|:---|:---:|:---:|:---:|
| 1 | Concessão de limites excessivamente altos para clientes arriscados | Calibração inadequada da função objetivo (peso excessivo em receita vs risco) | Aumento de inadimplência, impacto direto em provisão | 3 | 5 | **Crítico** |
| 2 | Concessão de limites muito baixos, reduzindo atratividade | Restrições de risco excessivamente conservadoras | Perda de competitividade, redução de ativação, churn | 3 | 4 | **Alto** |
| 3 | Formulação do modelo sem aderência ao negócio | Falta de entendimento do TAPI ou ausência de validação com parceiro | Solução tecnicamente correta mas irrelevante para o Pan | 3 | 5 | **Crítico** |
| 4 | Uso inadequado das variáveis disponíveis | Dados sem dicionário claro; variáveis correlacionadas; inclusão de variáveis sensíveis como proxy (CEP → raça) | Modelo enviesado ou com baixo poder preditivo; risco LGPD | 4 | 4 | **Crítico** |
| 5 | Simplificações que prejudicam a interpretação econômica | Uso de proxies inadequadas sem justificar; linearização de relações não-lineares | Resultados matematicamente válidos mas economicamente sem sentido | 3 | 4 | **Alto** |
| 6 | Descumprimento de restrições de risco da carteira | Restrições não formalizadas no modelo ou com valores incorretos | Carteira resultante viola políticas internas ou exigências regulatórias | 2 | 5 | **Alto** |
| 7 | Dificuldade de implementação prática no ambiente do parceiro | Stack tecnológico incompatível; dados em formato indisponível | Solução não pode ser integrada — valor apenas teórico | 3 | 4 | **Alto** |
| 8 | Baixa explicabilidade da solução | Modelo complexo demais; documentação insuficiente dos parâmetros | Compliance/auditoria recusa a solução; descumprimento LGPD Art. 20 | 3 | 4 | **Alto** |
| 9 | Qualidade insuficiente dos dados fornecidos | Missing values, outliers, período não representativo, viés de seleção | "Garbage in, garbage out" — modelo gera decisões ruins | 4 | 4 | **Crítico** |
| 10 | Dependência excessiva de premissas não justificadas | Falta de dados reais para calibrar parâmetros (LGD, utilização); valores arbitrários | Resultados são artefato das premissas, sem validade prática | 4 | 4 | **Crítico** |
| 11 | Viés de seleção nos dados de inadimplência | `over30mob3` só existe para os ~5K que ativaram (0,03% da base) — não observamos os demais | Modelo treinado com subconjunto não representativo da população | 4 | 4 | **Crítico** |
| 12 | Atrasos no time devido ao prazo curto da sprint | Sprint 1 com poucos dias de dev efetivo | Entregas incompletas ou com qualidade inferior | 4 | 3 | **Alto** |

> **Nota sobre o Risco 11:** Este risco foi identificado diretamente dos dados (`base_ref_M1_v2.parquet`). Dos 14,5M de clientes, apenas ~5K têm `over30mob3` preenchido. Isso é um viés de seleção clássico em crédito ("reject inference") — não sabemos como os clientes que não receberam oferta se comportariam.

### 2.3 Justificativa do posicionamento

*O roteiro pede justificativa do posicionamento de cada risco.*

**Posição = Probabilidade × Impacto:**
- **Críticos (≥ 15):** Riscos 4, 9, 10 e 11 têm probabilidade alta (4) porque o grupo ainda não recebeu o TAPI nem analisou os dados em profundidade — são riscos inerentes ao estágio atual. Riscos 1 e 3 têm impacto muito alto (5) porque comprometem a razão de existir da solução.
- **Altos (8–14):** Riscos 2, 5, 6, 7, 8 e 12 são significativos mas mais controláveis com ações de mitigação.

### 2.4 Análise dos riscos mais críticos

*O roteiro pede análise dos riscos mais críticos.*

**Riscos 1 e 2 (limites altos/baixos demais)** são faces opostas do mesmo problema: calibração inadequada do trade-off receita × risco. Ambos dependem da correta formulação da função objetivo (Risco 3). Se a formulação errar, ambos se materializam automaticamente.

**Riscos 4, 9, 10 e 11 (dados e premissas)** formam uma cadeia: dados com problemas (9) + viés de seleção (11) → premissas inadequadas (10) → uso errado de variáveis (4). A mitigação mais efetiva é uma EDA rigorosa e documentação explícita de toda premissa.

`[APÓS TAPI: recalibrar probabilidades e impactos com informações reais do parceiro]`

### 2.5 Representação visual da matriz

*Inserir a imagem da matriz 5×5 com os riscos posicionados. Fazer em Figma, Canva ou Miro.*

![Matriz de Risco](assets/matriz_risco.png)

`[PREENCHER: criar imagem da matriz 5×5 e inserir aqui]`

---

## 3. Canvas da Proposta de Valor (Peso 2,5)

### 3.1 Segmento de cliente

*O roteiro diz que o "cliente" pode ser analisado em dois níveis e que o grupo deve **deixar claro qual nível está analisando** e, **idealmente, reconhecer os dois**.*

Neste projeto, o "cliente" opera em dois níveis:

- **Cliente direto da solução**: times internos do Banco Pan que utilizarão o modelo — áreas de **crédito, estratégia de crédito e Data Science**. São eles que configuram parâmetros, executam cenários e implementam os limites resultantes. `[APÓS UX: referenciar as personas criadas — ex: "Persona Renata (gestora de risco)"]`
- **Cliente final impactado**: **correntistas do Banco Pan elegíveis à concessão de cartão de crédito pré-aprovado**. Não interagem diretamente com o modelo, mas são afetados pelo resultado (limites mais ou menos aderentes ao perfil). Os dados mostram ~14,5M de clientes na base, dos quais ~12,7M passam nos filtros de elegibilidade.

A análise foca no **cliente direto** (times internos), pois são os usuários efetivos da solução.

`[APÓS TAPI: confirmar quais áreas do banco utilizarão a solução]`

### 3.2 Perfil do Cliente (lado direito do Canvas)

**Tarefas do cliente:**
- Definir e revisar políticas de limites pré-aprovados de crédito
- Equilibrar receita da carteira com controle de inadimplência
- Reportar e justificar indicadores de risco (NPL, provisão) à diretoria
- Atender exigências de explicabilidade (LGPD Art. 20) e capital regulatório

**Dores:**

> **NÃO FAZER (feedback M5 da profa. de UX — mesma professora):**
> - ~~Ganhos ligados à alta gestão e não ao usuário principal~~
> - Isso vale também aqui no Canvas de negócios

- Pressão constante por reduzir NPL crescente (8,3% e subindo) sem sacrificar receita — a sensação de estar "escolhendo qual problema criar"
- Sobrecarga cognitiva ao revisar políticas que envolvem dezenas de variáveis simultâneas, sem ferramenta que integre todas
- Risco reputacional pessoal quando decisões de limite resultam em inadimplência acima do esperado
- Falta de base objetiva para defender decisões em reuniões com produto e comercial — "intuição" não convence stakeholders que querem mais receita

`[APÓS UX: cruzar com as dores das personas — garantir coerência]`

**Ganhos esperados:**

> **ATENÇÃO (feedback M5):** Ganhos devem ser **do usuário direto**, não da alta gestão. Ganhos como "aumento de lucro do banco" ou "valor para o acionista" NÃO entram aqui.

- Sentir segurança ao defender decisões de limite com argumentação matemática, não opinião
- Poder simular cenários (conservador/moderado/agressivo) antes de implementar
- Reduzir tempo gasto em análises manuais e debates subjetivos
- Ter rastreabilidade das decisões para auditorias e compliance

### 3.3 Mapa de Valor (lado esquerdo do Canvas)

**Produtos e serviços:**

*O roteiro pede: "o que exatamente o grupo está propondo?"*

- Modelo de otimização matemática que define limites pré-aprovados por cliente ou cluster, respeitando restrições de risco e negócio `[APÓS MODELAGEM: especificar tipo — LP, MIP, etc.]`
- Interface para configurar parâmetros (NPL máximo, budget, limite min/max) e executar cenários `[APÓS UX: alinhar com User Stories]`
- Módulo de explicabilidade (quais variáveis mais influenciaram cada decisão de limite)

**Aliviadores de dor:**

*Como a solução reduz ou elimina os problemas identificados?*

- Substitui intuição por base matemática — elimina o "operar no escuro"
- NPL máximo como restrição do modelo — ataca diretamente a pressão pelo NPL, que simplesmente não é violado
- Cenários pré-configurados permitem comparar resultados sem refazer análises manuais
- Decisões rastreáveis e documentáveis — em caso de auditoria, a lógica é reproduzível

**Criadores de ganho:**

*Como a solução gera benefícios concretos e relevantes?*

- Simulação what-if rápida: testar "o que acontece se eu reduzir o NPL máximo de 8% para 7%?" leva minutos
- Argumentação objetiva: fornece dados concretos para reuniões entre áreas
- Para o cliente final: limites mais aderentes à capacidade de pagamento — reduz tanto sub-concessão quanto sobre-concessão

### 3.4 Figura do Canvas

> **ATENÇÃO (roteiro):** *"Lembre-se de colocar a figura"*

![Canvas Proposta de Valor](assets/canvas_proposta_valor.png)

`[PREENCHER: criar imagem do Canvas (template Strategyzer) em Figma, Miro ou Canva e inserir aqui]`

> **NÃO FAZER (roteiro):**
> - ~~Tratar o canvas como texto genérico de empreendedorismo~~
> - ~~Não delimitar quem é o cliente~~
> - ~~Listar dores e ganhos sem conectá-los ao projeto~~
> - ~~Descrever apenas a ferramenta técnica, sem explicar o valor gerado~~

---

## 4. Análise Financeira do Projeto (Peso 2,5)

*O roteiro pede análise para **horizonte de 1 ano** com **premissas justificadas**. "O mais importante é mostrar lógica econômica, coerência de premissas e capacidade de estimar o ROI."*

> **ATENÇÃO (roteiro):** O TAPI não apresenta orçamento fechado. O grupo deve trabalhar com **premissas justificadas**, não com números inventados. Quando uma estimativa for assumida, explicitar no texto.

### 4.1 Premissas declaradas

| # | Premissa | Valor | Fonte / Justificativa |
|:---:|:---|:---|:---|
| P1 | Carteira de crédito do Pan | R$ 57,8 bi | RI Banco Pan, Q2 2025 |
| P2 | NPL >90 dias | 8,3% | RI Banco Pan, Q2 2025 |
| P3 | Perda estimada associada ao NPL | ~R$ 4,8 bi/ano | P1 × P2 (simplificação — assume perda = carteira × NPL, sem considerar recuperação) |
| P4 | Salário/hora dev júnior | R$ 23,17/h | Glassdoor Brasil, média 2025 |
| P5 | Salário/hora tech lead | R$ 79,55/h | Glassdoor Brasil, média 2025 |
| P6 | Carga horária do projeto | ~100h por pessoa | 10 semanas × 10h/semana |
| P7 | Infraestrutura cloud | AWS EC2 t3.medium | Pricing público AWS, sa-east-1 |
| P8 | Redução de NPL pelo modelo | 0,1pp a 0,5pp | **Premissa assumida** — literatura reporta melhorias nessa faixa para modelos de otimização de crédito. `[APÓS TAPI: validar com parceiro]` |

### 4.2 Investimento inicial

| Item | Detalhamento | Total (R$) |
|:---|:---|---:|
| Equipe de desenvolvimento (7 devs júnior) | 7 × 100h × R$ 23,17/h (P4, P6) | 16.219 |
| Orientação técnica (1 tech lead) | 1 × 100h × R$ 79,55/h (P5, P6) | 7.955 |
| Testes e validação | Incluso nas horas de dev | — |
| Equipamentos (notebooks) | 7 × R$ 4.200 (amortização do período) | 29.400 |
| **Subtotal investimento inicial** | | **53.574** |

### 4.3 Custos operacionais anuais

| Item | Mensal (R$) | Anual (R$) |
|:---|---:|---:|
| Infraestrutura cloud (EC2 t3.medium) | 160 | 1.920 |
| Banco de dados (Supabase Pro) | 130 | 1.560 |
| Armazenamento (S3, 50GB) | 6 | 72 |
| Manutenção e monitoramento | Equipe interna do banco | — |
| **Subtotal operacional** | **296** | **3.552** |

**Investimento total Ano 1:** R$ 53.574 + R$ 3.552 = **R$ 57.126**

> **Nota:** Esses custos refletem o projeto acadêmico. Uma implementação em produção envolveria custos adicionais significativos (integração com sistemas, equipe dedicada de MLOps, infra de produção). Não incluídos por falta de informação do parceiro. `[APÓS TAPI: recalcular se houver dados de investimento real]`

### 4.4 Benefícios econômicos estimados

*Os benefícios são **economias por redução de perdas com inadimplência**, não receitas novas.*

> **NÃO FAZER (roteiro):** ~~Confundir receita com economia~~

Base de cálculo: perda anual estimada de ~R$ 4,8 bi (P3).

| Cenário | Redução de NPL (P8) | Economia anual | Tipo |
|:---|:---:|---:|:---|
| Conservador | 0,1 pp | R$ 57,8 mi | Economia (redução de provisão) |
| Moderado | 0,3 pp | R$ 173,4 mi | Economia |
| Otimista | 0,5 pp | R$ 289,0 mi | Economia |

*Além da redução de perdas, a otimização pode gerar aumento de receita por melhor utilização dos limites (clientes bons recebem limites mais altos). Não quantificado por falta de dados de utilização.*

### 4.5 Cálculo do ROI

*O roteiro pede a fórmula e o cálculo.*

$$
ROI = \frac{\text{Ganhos estimados} - \text{Custos do projeto}}{\text{Investimento total}} \times 100
$$

**Cenário conservador:**

$$
ROI = \frac{R\$\ 57.800.000 - R\$\ 57.126}{R\$\ 57.126} \times 100 \approx 101.080\%
$$

### 4.6 Interpretação do resultado

*O roteiro pede interpretação, não apenas o número.*

O ROI calculado é extraordinariamente alto (~101.000%). Isso **não é um erro** — reflete uma característica estrutural: o investimento é muito baixo (projeto acadêmico, ~R$ 57 mil) enquanto o benefício potencial é muito alto (redução de perdas em carteira de R$ 57,8 bi). Esse tipo de ROI é comum em projetos de otimização aplicados a grandes carteiras financeiras.

**Limitações importantes:**

1. **Os custos refletem apenas o projeto acadêmico.** Uma implementação real exigiria investimento ordens de grandeza maior (equipe, infra enterprise, integração, compliance) — o que reduziria o ROI substancialmente, embora provavelmente se mantivesse positivo.
2. **A premissa de redução de NPL (P8) é assumida.** O ROI real depende da efetividade do modelo, que só será conhecida após backtesting com dados reais.
3. **Não foram considerados** custos de oportunidade, riscos de implementação, nem tempo de maturação do modelo.

> **NÃO FAZER (roteiro):**
> - ~~Apresentar números sem explicar de onde vieram~~ — todas as premissas estão na tabela 4.1
> - ~~Fazer conta sem premissas~~ — cada número tem fonte
> - ~~Produzir análise apenas descritiva, sem cálculo~~ — ROI calculado acima

`[APÓS TAPI: recalcular com custos reais de implementação e metas de NPL do parceiro]`

---

## Checklist pré-entrega

**Oceano Azul:**
- [x] Explicação de quem está sendo comparado (3 abordagens)
- [x] Definição dos 8 atributos com justificativa para o Pan
- [x] Notas atribuídas com justificativa para cada uma
- [x] 4 ações (Reduzir, Eliminar, Aumentar, Criar) aplicadas ao projeto
- [ ] `[APÓS MODELAGEM]` Detalhar tipo de modelo na abordagem do grupo
- [ ] `[APÓS TAPI]` Validar notas do Pan atual com parceiro

**Riscos:**
- [x] Pelo menos 10 riscos apresentados (temos 12)
- [x] Critérios de classificação de impacto e probabilidade
- [x] Cada risco tem: descrição, causa provável, impacto, prob, posição, justificativa
- [x] Análise dos riscos mais críticos
- [ ] `[PREENCHER]` Imagem da matriz 5×5

**Canvas:**
- [x] Dois níveis de cliente identificados (direto + final)
- [x] Dores do cliente direto
- [x] Ganhos do cliente direto (do usuário, não da alta gestão)
- [x] Produtos e serviços da solução
- [x] Aliviadores de dor conectados às dores
- [x] Criadores de ganho
- [ ] `[PREENCHER]` Figura do Canvas (template Strategyzer)
- [ ] `[APÓS UX]` Cruzar com personas

**Financeira:**
- [x] Premissas claramente declaradas com fonte
- [x] Separação entre investimento, custo operacional e benefício
- [x] Distinção entre receita e economia
- [x] Cálculo do ROI com fórmula
- [x] Interpretação do resultado com limitações
- [ ] `[APÓS TAPI]` Recalcular com dados reais

---

## Fontes

[1] KIM, W. Chan; MAUBORGNE, Renée. A Estratégia do Oceano Azul: Como Criar Novos Mercados e Tornar a Concorrência Irrelevante. Rio de Janeiro: Sextante, 2005.
[2] EXPERIAN. Balancing Growth and Risk with Credit Limit Optimization. Experian Insights, 2024. Disponível em: https://www.experian.com/blogs/insights/credit-limit-optimization/. Acesso em: [data].
[3] BRASIL. Conselho Monetário Nacional. Resolução CMN nº 4.966, de 25 de novembro de 2021. Dispõe sobre os conceitos e os critérios contábeis aplicáveis a instrumentos financeiros e sobre a mensuração das provisões para perdas esperadas associadas ao risco de crédito. Brasília: Banco Central do Brasil, 2021. Disponível em: https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Resolução%20CMN&numero=4966. Acesso em: [data].
