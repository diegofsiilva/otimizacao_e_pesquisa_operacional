# Entendimento do Negócio

> **Status:** Rascunho pré-TAPI. Seções preenchidas com base em dados públicos do Banco Pan e na descrição do projeto. Trechos com `[PREENCHER]` precisam do TAPI. Trechos com `[VALIDAR]` devem ser confirmados com o parceiro.
>
> **Dependências com outros artefatos:**
> - `[APÓS UX]` = preencher quando as personas estiverem prontas
> - `[APÓS MODELAGEM]` = preencher quando a formulação matemática estiver pronta
> - `[APÓS TAPI]` = preencher quando o TAPI for recebido

---

## 1. Matriz de Avaliação de Valor — Oceano Azul (Peso 2,5)

### 1.1 Quem está sendo comparado

*O roteiro da Profa. Natália pede comparar **abordagens**, não bancos concorrentes. Ex: prática tradicional, solução baseada em regras, solução do grupo.*

A análise compara três **abordagens de definição de limites de crédito pré-aprovados**:

| Abordagem | Descrição |
|:---|:---|
| **Prática tradicional (comitê/regras de mesa)** | Decisão baseada em experiência dos analistas, regras internas informais e revisão periódica por comitê de crédito. Comum em bancos médios e na operação histórica do Pan para produtos não-colateralizados. |
| **Solução baseada em scoring + regras fixas** | Modelos de credit scoring (regressão logística, gradient boosting) geram um score por cliente, mapeado a limites pré-definidos por tabela (ex: score 700-750 → R\$ 3.000). Padrão atual de mercado. O Pan já usa IA em 100% das decisões de crédito ([Consumidor Moderno](https://consumidormoderno.com.br/inteligencia-artificial-banco-pan/)). |
| **Solução do grupo (otimização matemática)** | Modelo de otimização que maximiza retorno esperado sujeito a restrições de risco (NPL máximo), capacidade de pagamento e regras de negócio, definindo o limite ótimo por cliente ou cluster. `[APÓS MODELAGEM: detalhar o tipo — LP, MIP, etc.]` |

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
- **Aderência à capacidade (5 / 5 / 9):** Tradicional considera renda qualitativamente. Scoring usa renda como input, mas o limite final vem de tabela. A solução modela capacidade como restrição hard. Os dados mostram a variável `capacidade_pagamento` disponível (mediana R\$ 550, max R\$ 25.000).
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

- **Concessão padronizada sem segmentação:** a tabela fixa (score → limite) trata todos de um mesmo score como iguais. Os dados mostram que clientes com o mesmo `score_interno` podem ter `capacidade_pagamento` entre R\$ 0 e R\$ 25.000 — são perfis completamente diferentes. A solução elimina essa padronização.
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
| **Baixo (2)** | 5-20% | Impacto menor, contornável sem replanejar |
| **Médio (3)** | 20-50% | Impacto moderado, exige ação corretiva |
| **Alto (4)** | 50-75% | Impacto significativo no escopo, prazo ou resultado |
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
- **Altos (8-14):** Riscos 2, 5, 6, 7, 8 e 12 são significativos mas mais controláveis com ações de mitigação.

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

## 4. Análise Financeira do Projeto

O Banco Pan opera uma carteira de crédito total de R\$ 57,8 bi [[1]](#ref-1), concentrada em veículos (~57\%) e consignado (~36\%). O cartão de crédito representa ~5\% da carteira (~a seção de ineR\$ 2,9 bi em 3T25) [[1]](#ref-1)[[2]](#ref-2), sendo o produto de **maior risco** do portfólio. O NPL >90 dias atingiu 8,3% em Q2 2025 [[1]](#ref-1)[[3]](#ref-3), o que indica tendência de alta e pressiona a provisão para perdas (PCLD), que chegou a R\$ 2,33 bi em 2024, equivalente a **~4,5× o lucro líquido IFRS** do mesmo ano (R\$ 528 mi) [[11]](#ref-11)[[12]](#ref-12). Em janeiro de 2026, o Pan foi incorporado ao BTG Pactual [[12]](#ref-12).

Esse contexto evidencia que qualquer melhoria marginal na qualidade da concessão de crédito tem impacto amplificado na linha final do resultado do banco, o que torna indispensável avaliar se o investimento em uma solução de otimização de limites se justifica economicamente. Esta seção apresenta essa análise financeira, considerando um horizonte de **1 ano**, por meio do cálculo do ROI (*Return on Investment*) com premissas justificadas: estimamos o investimento necessário para implementar a solução em produção, os custos operacionais recorrentes e o benefício esperado sobre a carteira de cartões. Como o parceiro não disponibilizou um orçamento fechado para o projeto [[13]](#ref-13), os valores abaixo são **estimativas baseadas em premissas justificadas e fontes públicas**; quando uma estimativa é assumida pelo grupo, isso é explicitado.

### 4.1 Premissas declaradas

As estimativas de custo e benefício apresentadas a seguir dependem de um conjunto de premissas sobre a operação do parceiro, o modelo de receita do cartão e o impacto esperado da solução. Declará-las explicitamente permite ao leitor avaliar a robustez dos resultados e identificar quais pontos precisam ser validados com dados reais. Cada premissa é acompanhada de uma classificação de **Confiança**: **Alta** = dado público verificável; **Média** = estimativa com fonte indireta ou média de mercado; **Baixa** = premissa do grupo sem benchmark específico para o Pan.

#### A. Operação do parceiro

| # | Premissa | Valor | Conf. | Fonte / Justificativa |
|:---:|:---|:---|:---:|:---|
| A1 | Carteira de cartão de crédito | ~R\$ 2,9 bi | Média | [[1]](#ref-1)[[2]](#ref-2). ~5% da carteira total. |
| A2 | NPL >90 dias (carteira total) | 8,3% | Alta | [[1]](#ref-1)[[3]](#ref-3) |
| A3 | Taxa de recuperação (crédito sem garantia) | 30% | Média | [[4]](#ref-4). Média do sistema bancário. |
| A4 | Perda líquida anual (carteira de cartões) | ~R\$ 168 mi | Média | Derivada: A1 × A2 × (1 − A3) = R\$ 2,9 bi × 8,3% × 70% |

#### B. Modelo de receita (conforme TAPI)

| # | Premissa | Valor | Conf. | Fonte / Justificativa |
|:---:|:---|:---|:---:|:---|
| B1 | Receita do cartão = interchange a taxa fixa | Sim | Alta | [[13]](#ref-13), p. 4 (para manter linearidade do modelo) |
| B2 | Taxa de interchange do emissor | ~1,6% | Média | Média ponderada do mercado brasileiro [[5]](#ref-5)[[6]](#ref-6). Faixa: 1,5-1,7%. |
| B3 | Utilização média do limite | ~30% | Média | Benchmark [[6]](#ref-6) para cartões sem garantia em perfil renda baixa |
| B4 | Receita anual de interchange (baseline) | ~R\$ 167 mi | - | Derivada: A1 × B3 × B2 × 12 = R\$ 2,9 bi × 30% × 1,6% × 12 |

#### C. Benefício esperado do modelo

| # | Premissa | Valor | Conf. | Fonte / Justificativa |
|:---:|:---|:---|:---:|:---|
| C1 | Melhoria esperada pelo modelo sobre o resultado econômico combinado | 1,0% (cenário base) | Baixa | [[7]](#ref-7) e [[8]](#ref-8) reportam ganhos de 1-5% em carteiras já geridas por scoring. Adotamos o **piso da faixa** como cenário base, por ser a estimativa mais defensável na ausência de backtesting com dados do parceiro. |

#### D. Custos de implementação

| # | Premissa | Valor | Conf. | Fonte / Justificativa |
|:---:|:---|:---|:---:|:---|
| D1 | Cientista de dados sênior (líder técnico) | R\$ 30.000/mês (com encargos CLT ~35%) | Média | [[9]](#ref-9)[[10]](#ref-10). Faixa: R\$ 18.000-30.000/mês. |
| D2 | Cientista de dados pleno | R\$ 17.500/mês (com encargos) | Média | [[9]](#ref-9). Faixa: R\$ 10.000-18.000/mês. |
| D3 | Engenheiro de dados pleno | R\$ 20.000/mês (com encargos) | Média | [[9]](#ref-9). Faixa: R\$ 12.000-20.000/mês. |
| D4 | Tech Lead / Gerente de Projeto | R\$ 38.000/mês (com encargos) | Média | [[9]](#ref-9). Faixa: R\$ 22.000-38.000/mês. |

### 4.2 Investimento inicial

Para fins desta análise, o investimento inicial reflete o custo de implementação da solução em ambiente produtivo do Banco Pan, organizado por fase do ciclo de vida de um projeto de analytics em crédito.

O time técnico core (cientista sênior (D1), cientista pleno (D2) e engenheiro de dados (D3)) custa R\$ 67.500/mês e atua nas três primeiras fases. Sobre esse custo-base incidem a infraestrutura de desenvolvimento (R\$ 5.000/mês) e a gestão de projeto (D4 a ~18% de dedicação, ~R\$ 6.800/mês), totalizando ~R\$ 79.300/mês de custo recorrente. Custos específicos de cada fase (validação independente, integração, conformidade) são adicionados conforme detalhado abaixo.

| Fase | Escopo | Duração | Derivação | Custo (R\$) |
|:---|:---|:---:|:---|---:|
| **1. Desenvolvimento e modelagem** | Formulação matemática, implementação do solver, análise exploratória, definição de clusters | 3 meses | Custo recorrente × 3 meses (R\$ 79,3k × 3) | 238.000 |
| **2. Backtesting e validação** | Testes com safras históricas (M1-M3), análise de sensibilidade, validação independente pelo time de risco do banco | 1 mês | Custo recorrente × 1 mês (R\$ 79,3k) + validação independente pelo time de risco do banco (~300h de analista sênior, ~R\$ 60k) | 139.000 |
| **3. Integração e homologação** | Conexão ao motor de crédito existente do Pan, construção dos pipelines de dados, deploy em ambiente segregado | 2 meses | Custo recorrente × 2 meses (R\$ 79,3k × 2) + especialistas de integração do banco (~4 semanas, ~R\$ 24k) | 183.000 |
| **4. Conformidade regulatória** | Revisão de compliance e proteção de dados, controles de acesso à base sigilosa, documentação de modelo, aprovação em comitê de crédito | Paralelo às Fases 2-3 (meses 4-6), ~0,5 FTE | Dedicação parcial de profissional de compliance/governança ao longo de 3 meses | 65.000 |
| **Investimento inicial total** | | **~6 meses** | | **R\$ 625.000** |

### 4.3 Custos operacionais anuais

Após a entrada em produção, o modelo requer manutenção contínua para manter performance e aderência regulatória.

| Item | Anual (R\$) | Premissa |
|:---|---:|:---|
| Infraestrutura de produção (cloud) | 120.000 | D7: R\$ 10.000/mês |
| Monitoramento do modelo (cientista de dados pleno, 30% dedicação) | 63.000 | D2: R\$ 17.500 × 30% |
| Ajustes periódicos (recalibração trimestral, ~40h/ciclo) | 30.000 | D1: R\$ 30.000 ÷ 160h × 40h × 4 ciclos |
| Suporte analítico e reportes ao comitê de crédito (~20h/mês) | 26.000 | D2: R\$ 17.500 ÷ 160h × 20h × 12 |
| **Total custos anuais** | **R\$ 239.000** | |


### 4.4 Benefícios econômicos estimados

O benefício vem da **redistribuição mais eficiente dos limites de crédito**: clientes de baixo risco recebem limites mais aderentes ao seu perfil (aumentando utilização e receita de interchange), enquanto clientes de alto risco têm limites reduzidos (diminuindo perdas por inadimplência). Trata-se de uma **única ação de otimização** que gera impacto simultâneo nos dois lados (receita e risco) da função objetivo definida pelo TAPI [[13]](#ref-13).

Por essa razão, tratamos o benefício como uma **melhoria única sobre o resultado econômico combinado** da carteira, e não como duas melhorias independentes somadas. O baseline econômico combinado é:

$$
\text{Baseline combinado} = \text{Receita de interchange (B4)} + \text{Perda evitável (A4)} = R\$\ 167\ mi + R\$\ 168\ mi = R\$\ 335\ mi
$$

Aplicando a premissa C1 (melhoria de 1,0% no cenário base, **piso da faixa** reportada na literatura):

$$
\text{Ganho anual} = R\$\ 335\ mi \times 1,0\% = R\$\ 3.350.000
$$

Esse ganho se materializa como uma combinação de mais receita de interchange (clientes bons usando mais o cartão) e menos perda por inadimplência (clientes arriscados com limites menores). A proporção exata entre os dois depende de como o modelo redistribui os limites — o que só será conhecido após o backtesting.

> **Nota metodológica:** ao somar receita de interchange e perda evitada no mesmo baseline, tratamos as duas componentes como economicamente equivalentes. Na prática, R\$ 1 de perda evitada vai integralmente para a linha do lucro, enquanto R\$ 1 de receita bruta de interchange ainda carrega custos associados (taxa da bandeira, processamento, fraude). O efeito líquido no lucro não é perfeitamente simétrico. Optamos por manter a simplificação em primeira ordem porque (i) não dispomos das taxas internas do Pan para decompor o interchange líquido e (ii) o impacto dessa assimetria é marginal frente à incerteza já capturada na análise de sensibilidade (seção 4.5).

> **Sensibilidade à premissa A3 (taxa de recuperação):** se a recuperação real for 20% em vez de 30%, a perda líquida (A4) sobe de R\$ 168 mi para R\$ 193 mi, e o baseline combinado vai de R\$ 335 mi para R\$ 360 mi. No cenário base (C1 = 1,0%), o ganho anual passaria de R\$ 3,35 mi para R\$ 3,60 mi, uma variação de ~7% que não altera a conclusão de viabilidade. Diferentemente de C1, a taxa de recuperação pode ser verificada com dados públicos do BCB [[4]](#ref-4) ou obtida diretamente com o parceiro.

### 4.5 Cálculo do ROI


$$
ROI = \frac{\text{Benefício líquido}}{\text{Investimento inicial}} \times 100
$$

Onde:

$$
\text{Benefício líquido} = \text{Ganhos estimados (1 ano)} - \text{Custos operacionais anuais}
$$

#### Cenário base (passo a passo)

**Passo 1 - Investimento inicial:** R\$ 625.000 (seção 4.2)

**Passo 2 - Custos operacionais anuais:** R\$ 239.000 (seção 4.3)

**Passo 3 - Ganhos estimados (1 ano):** R\$ 3.350.000 (seção 4.4, C1 = 1,0%)

**Passo 4 - Benefício líquido:**

$$
\text{Benefício líquido} = R\$\ 3.350.000 - R\$\ 239.000 = R\$\ 3.111.000
$$

**Passo 5 - ROI:**

$$
ROI = \frac{R\$\ 3.111.000}{R\$\ 625.000} \times 100 \approx \textbf{497,8\%}
$$

#### Análise de sensibilidade - cenários para C1

A premissa C1 é o principal driver de incerteza da análise (confiança Baixa). Para avaliar a robustez do resultado, recalculamos o ROI em quatro cenários que cobrem a faixa de 0,5% a 3,0%:

| Cenário | C1 (melhoria) | Ganho anual | Custos anuais | Benefício líquido | **ROI** |
|:---|:---:|---:|---:|---:|---:|
| Pessimista | 0,5% | R\$ 1,675 mi | R\$ 239 mil | R\$ 1,436 mi | **229,8%** |
| **Base** | **1,0%** | **R\$ 3,350 mi** | **R\$ 239 mil** | **R\$ 3,111 mi** | **497,8%** |
| Moderado | 2,0% | R\$ 6,700 mi | R\$ 239 mil | R\$ 6,461 mi | **1.033,8%** |
| Otimista | 3,0% | R\$ 10,050 mi | R\$ 239 mil | R\$ 9,811 mi | **1.569,8%** |

Mesmo no cenário pessimista (C1 = 0,5%), o ROI de ~230% indica retorno significativamente superior ao investimento, o projeto se pagaria em menos de 6 meses de operação.

### 4.6 Interpretação do resultado

**Viabilidade financeira.** O ROI base de **~498%** indica que o projeto é financeiramente viável: o ganho gerado em um ano supera em ~5× o valor investido. O investimento de R\$ 625 mil equivale a apenas **0,07\% do lucro ajustado** anual do Pan (~R\$ 855 mi em 2024 [[1]](#ref-1)), o que caracteriza um projeto de baixo risco financeiro para o banco. Pelo lado do ganho, os R\$ 3,35 mi anuais no cenário base representam **~0,4% do lucro ajustado**, ou seja, o projeto não é apenas viável, é materialmente relevante para o resultado do banco.

**Por que o ROI é dessa magnitude.** ROIs de três dígitos são comuns em projetos de analytics aplicados a grandes carteiras de crédito, porque o investimento em modelagem (centenas de milhares de reais) atua sobre uma base de ativos de bilhões. No caso do Pan, uma melhoria de 1% sobre o baseline combinado de R\$ 335 mi gera R\$ 3,35 mi, valor que supera em ~5× o investimento. O mesmo efeito de alavancagem é reportado na literatura: Trench *et al.* [[8]](#ref-8) documentam ROIs de magnitude semelhante em otimização de limites de cartão de crédito em grandes bancos americanos. Mesmo que, na prática, o modelo capture apenas metade do benefício teórico previsto (C1 efetivo de 0,5%), o ROI permaneceria acima de 200% (cenário pessimista na tabela de sensibilidade), o que reforça a robustez da conclusão de viabilidade.

**Ponto de equilíbrio (break-even).** Para que o ROI seja zero, o ganho anual precisaria cobrir apenas o investimento mais os custos operacionais: R\$ 625 mil + R\$ 239 mil = R\$ 864 mil. Sobre o baseline combinado de R\$ 335 mi, isso equivale a uma melhoria de apenas **~0,26%**, um patamar muito abaixo dos 1-5% reportados na literatura [[7]](#ref-7)[[8]](#ref-8). A solução se paga mesmo que capture apenas uma fração mínima do potencial de otimização.

**Benefício operacional para o usuário.** Além do ganho financeiro, a solução gera valor operacional direto para o analista de crédito e o time de estratégia (conforme detalhado no Canvas, seção 3). Estimativa preliminar: cada ciclo de revisão manual de política de limites consome ~40-60 horas de analista sênior (levantamento de dados, simulação de cenários, validação com comitê). Com a solução automatizando a geração de cenários, estimamos redução de ~50% desse tempo, equivalente a ~20-30 horas/ciclo. Em 4 ciclos anuais (recalibração trimestral), isso representa ~80-120 horas/ano de analista sênior, ou **~R\$ 15.000-22.500/ano** (a custo D1). O valor é modesto frente ao ROI financeiro, mas representa um ganho tangível de produtividade para o time de crédito.

#### Limitações da análise

- **Premissa C1 não validada com dados do parceiro.** A melhoria de 1,0% (cenário base) é extraída da literatura acadêmica, não de backtesting com dados do Banco Pan. O ROI real só será conhecido após a implementação do modelo com dados históricos das safras M1-M3. Por essa razão, adotamos o piso da faixa reportada (1%) como cenário base, e não o ponto médio.

- **Custos dependem da infraestrutura interna do banco.** Os valores estimados para integração (Fase 3) e conformidade (Fase 4) pressupõem que o Pan já dispõe de motor de crédito e processos de governança estruturados. Se a infraestrutura for menos madura, esses custos podem ser significativamente maiores.

- **Investimento 100% amortizado no primeiro ano.** O ROI apresentado trata o investimento de R\$ 625 mil como integralmente consumido no Ano 1, o que é uma simplificação didática aceita pelo roteiro. Em uma análise corporativa real, esse investimento seria amortizado ao longo do ciclo de vida do modelo (tipicamente 3 anos, compatível com o ciclo de revisão e recalibração de modelos de risco em bancos regulados). Nesse caso, o custo anualizado do investimento seria ~R\$ 208 mil/ano (R\$ 625k ÷ 3), e o ROI do Ano 1 seria calculado contra essa parcela em vez do total, resultando em ROI ainda mais alto. A conclusão de viabilidade, portanto, não é afetada pela simplificação; ao contrário, a abordagem adotada é a mais conservadora possível.

----

## Referências da análise financeira

> <a id="ref-1"></a>[[1]](#ref-1) BANCO PAN. **Relações com Investidores - Demonstrações financeiras e resultados trimestrais (2T25 e 3T25)**. São Paulo, 2025. Disponível em: https://ri.bancopan.com.br/. Acesso em: 20 abr. 2026.
>
> <a id="ref-2"></a>[[2]](#ref-2) ADVFN. Banco Pan reporta R\$ 209 milhões de lucro líquido e expansão de crédito sustenta BPAN4. *ADVFN Brasil*, nov. 2025. Disponível em: https://br.advfn.com/jornal/2025/11/banco-pan-reporta-r-209-milhoes-de-lucro-liquido-e-expansao-de-credito-sustenta-bpan4. Acesso em: 20 abr. 2026.
>
> <a id="ref-3"></a>[[3]](#ref-3) ADVFN. Banco Pan registra queda de 9% no lucro do 2T25 com aumento da inadimplência. *ADVFN Brasil*, ago. 2025. Disponível em: https://br.advfn.com/jornal/2025/08/banco-pan-registra-queda-de-9-no-lucro-do-2t25-com-aumento-da-inadimplencia. Acesso em: 20 abr. 2026.
>
> <a id="ref-4"></a>[[4]](#ref-4) BANCO CENTRAL DO BRASIL. **Relatório de Estabilidade Financeira**, 2º semestre de 2024. Brasília: BCB, 2024. Disponível em: https://www.bcb.gov.br/publicacoes/ref. Acesso em: 20 abr. 2026.
>
> <a id="ref-5"></a>[[5]](#ref-5) BANCO CENTRAL DO BRASIL. **Arranjos de pagamento - Taxas de intercâmbio**. Brasília: BCB, [s.d.]. Disponível em: https://www.bcb.gov.br/estabilidadefinanceira/pagamentosarranjos. Acesso em: 20 abr. 2026.
>
> <a id="ref-6"></a>[[6]](#ref-6) ASSOCIAÇÃO BRASILEIRA DAS EMPRESAS DE CARTÕES DE CRÉDITO E SERVIÇOS (ABECS). **Indicadores de mercado**. São Paulo: ABECS, 2024. Disponível em: https://www.abecs.org.br/indicadores-de-mercado. Acesso em: 20 abr. 2026.
>
> <a id="ref-7"></a>[[7]](#ref-7) THOMAS, L. C. **Consumer Credit Models: Pricing, Profit and Portfolios**. Oxford: Oxford University Press, 2009.
>
> <a id="ref-8"></a>[[8]](#ref-8) TRENCH, M. S. *et al.* Managing credit lines and prices for Bank One credit cards. **Interfaces**, v. 33, n. 5, p. 4-21, 2003.
>
> <a id="ref-9"></a>[[9]](#ref-9) GLASSDOOR BRASIL. **Pesquisa salarial - Cientista de dados, Engenheiro de dados, Tech Lead**. 2025. Disponível em: https://www.glassdoor.com.br/. Acesso em: 20 abr. 2026.
>
> <a id="ref-10"></a>[[10]](#ref-10) ROBERT HALF. **Guia Salarial 2025**. São Paulo: Robert Half, 2025. Disponível em: https://www.roberthalf.com.br/guia-salarial. Acesso em: 20 abr. 2026.
>
> <a id="ref-11"></a>[[11]](#ref-11) COMISSÃO DE VALORES MOBILIÁRIOS (CVM). **Sistema RAD - DFP e ITR Banco Pan S.A.** Disponível em: https://www.rad.cvm.gov.br/. Acesso em: 20 abr. 2026.
>
> <a id="ref-12"></a>[[12]](#ref-12) NORD INVESTIMENTOS. Banco Pan (BPAN4) - Resultados 4T24. 2025. Disponível em: https://www.nordinvestimentos.com.br/blog/banco-pan-bpan4-resultados-4t24/. Acesso em: 20 abr. 2026.
>
> <a id="ref-13"></a>[[13]](#ref-13) BANCO PAN; INTELI. **TAPI - Termo de Abertura do Projeto Integrador: Otimização de limites pré-aprovados de cartão de crédito**. São Paulo, 2026.



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

1. [Banco Pan - Relações com Investidores](https://ri.bancopan.com.br/)
2. [Banco Pan - Resultados 2T25 (Nord Investimentos)](https://www.nordinvestimentos.com.br/blog/banco-pan-bpan4-resultados-2t25/)
3. [Banco Pan - IA em decisões de crédito (Consumidor Moderno)](https://consumidormoderno.com.br/inteligencia-artificial-banco-pan/)
4. [LGPD - Lei 13.709/2018](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm)
5. [Glassdoor - Salários Brasil 2025](https://www.glassdoor.com.br/Salarios)
6. [AWS Pricing - EC2](https://aws.amazon.com/ec2/pricing/)
7. [Strategyzer - Value Proposition Canvas](https://www.strategyzer.com/library/the-value-proposition-canvas)
