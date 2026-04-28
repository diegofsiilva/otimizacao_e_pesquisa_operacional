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

Nesta seção, apresentamos a análise financeira preliminar da solução de otimização de limites pré-aprovados de cartão de crédito, considerando um horizonte de **1 ano**. O objetivo é demonstrar a viabilidade econômica da proposta por meio do cálculo do ROI (*Return on Investment*), com premissas justificadas.

O TAPI não apresenta orçamento fechado do parceiro. Os valores abaixo são **estimativas baseadas em premissas justificadas e fontes públicas**. Quando uma estimativa é assumida pelo grupo, isso é explicitado.

> **Nota sobre simplificações didáticas.** Para fins didáticos, esta análise adota três simplificações que, em um estudo de viabilidade corporativo, seriam tratadas de forma mais granular: (i) o CAPEX é amortizado integralmente no Ano 1, sem distribuição plurianual; (ii) assume-se LGD = 100% (perda total em caso de inadimplência), dispensando estimativa de taxa de recuperação além da já declarada em A3; e (iii) não se aplica taxa de desconto (WACC) ao fluxo de caixa do período, dado o horizonte de apenas 12 meses. Essas escolhas tornam o modelo mais transparente na leitura do resultado, sem comprometer a validade da conclusão qualitativa.

---

### 4.1 Contexto financeiro do Banco Pan

O Banco Pan opera uma carteira de crédito total de R\$ 57,8 bi (RI Q2 2025), concentrada em veículos (~57%) e consignado (~36%). O cartão de crédito representa ~5% da carteira (~R\$ 2,9 bi em 3T25), sendo o produto de **maior risco** do portfólio. O NPL >90 dias atingiu 8,3% em Q2 2025 — tendência de alta que pressiona a provisão para perdas (PCLD), que chegou a R\$ 2,33 bi em 2024, equivalente a **~4,5× o lucro líquido IFRS** do mesmo ano (R\$ 528 mi). Esse dado é relevante porque mostra que qualquer melhoria marginal na qualidade da concessão de crédito tem impacto amplificado na linha final do resultado do banco. Em janeiro de 2026, o Pan foi incorporado ao BTG Pactual (Fontes: DFP/ITR depositadas na CVM; RI Banco Pan; Nord Investimentos; ADVFN).

---

### 4.2 Premissas declaradas

Toda estimativa repousa em premissas. A coluna **Confiança** indica o grau de certeza: **Alta** = dado público verificável; **Média** = estimativa com fonte indireta ou média de mercado; **Baixa** = premissa do grupo sem benchmark específico para o Pan.

#### A. Operação do parceiro

| # | Premissa | Valor | Conf. | Fonte / Justificativa |
|:---:|:---|:---|:---:|:---|
| A1 | Carteira de cartão de crédito | ~R\$ 2,9 bi | Média | RI Banco Pan, 3T25. ~5% da carteira total. |
| A2 | NPL >90 dias (carteira total) | 8,3% | Alta | RI Banco Pan, Q2 2025 |
| A3 | Taxa de recuperação (crédito sem garantia) | 30% | Média | BCB — Rel. Estab. Financeira, 2024. Média do sistema bancário. |
| A4 | Perda líquida anual (carteira de cartões) | ~R\$ 168 mi | Média | Derivada: A1 × A2 × (1 − A3) = R\$ 2,9 bi × 8,3% × 70% |

#### B. Modelo de receita (conforme TAPI)

| # | Premissa | Valor | Conf. | Fonte / Justificativa |
|:---:|:---|:---|:---:|:---|
| B1 | Receita do cartão = interchange a taxa fixa | Sim | Alta | TAPI, p. 4 (para manter linearidade do modelo) |
| B2 | Taxa de interchange do emissor | ~1,6% | Média | Média ponderada do mercado brasileiro (ABECS/BCB, 2024). Faixa: 1,5–1,7%. |
| B3 | Utilização média do limite | ~30% | Média | Benchmark ABECS para cartões sem garantia em perfil renda baixa |
| B4 | Receita anual de interchange (baseline) | ~R\$ 167 mi | — | Derivada: A1 × B3 × B2 × 12 = R\$ 2,9 bi × 30% × 1,6% × 12 |

#### C. Benefício esperado do modelo

| # | Premissa | Valor | Conf. | Fonte / Justificativa |
|:---:|:---|:---|:---:|:---|
| C1 | Melhoria esperada pelo modelo sobre o resultado econômico combinado | 1,0% (cenário base) | Baixa | Thomas (2009) e Trench et al. (2003) reportam ganhos de 1–5% em carteiras já geridas por scoring. Adotamos o **piso da faixa** como cenário base, por ser a estimativa mais defensável na ausência de backtesting com dados do parceiro. |
| C2 | Percentual de captura dos benefícios no Ano 1 | 25% (cenário base) | Baixa | Premissa conservadora que incorpora rampagem lenta da adoção interna, ciclo de validação com a área de crédito, atrasos de integração com sistemas legados e resistência organizacional à mudança de processo. Em projetos de otimização de carteira, o primeiro ano raramente captura mais de 30% do benefício potencial. |

#### D. Custos de implementação

| # | Premissa | Valor | Conf. | Fonte / Justificativa |
|:---:|:---|:---|:---:|:---|
| D1 | Cientista de dados sênior (líder técnico) | R\$ 30.000/mês (com encargos CLT ~35%) | Média | Glassdoor/Robert Half, 2025. Faixa: R\$ 18.000–30.000/mês. |
| D2 | Cientista de dados pleno | R\$ 17.500/mês (com encargos) | Média | Glassdoor, 2025. Faixa: R\$ 10.000–18.000/mês. |
| D3 | Engenheiro de dados pleno | R\$ 20.000/mês (com encargos) | Média | Glassdoor, 2025. Faixa: R\$ 12.000–20.000/mês. |
| D4 | Tech Lead / Gerente de Projeto | R\$ 38.000/mês (com encargos) | Média | Glassdoor, 2025. Faixa: R\$ 22.000–38.000/mês. |
| D5 | Prazo total de desenvolvimento + integração | 6 meses | Média | Estimativa do grupo |
| D6 | Infraestrutura cloud (dev/staging) | R\$ 5.000/mês | Média | Pricing AWS/Azure para workloads analíticos |
| D7 | Infraestrutura de produção (cloud enterprise) | R\$ 10.000/mês | Média | Pricing AWS/Azure com SLA bancário |

---

### 4.3 Investimento inicial

O investimento estima o custo que o **Banco Pan** incorreria para implementar a solução em produção — não o custo do projeto acadêmico do Inteli. A estimativa está organizada por **fase do projeto**, refletindo o ciclo de vida de uma solução de analytics em crédito.

| Fase | Escopo | Duração | Custo (R\$) |
|:---|:---|:---:|---:|
| **1. Desenvolvimento e modelagem** | Formulação matemática, implementação do solver, análise exploratória, definição de clusters | 3 meses | 230.000 |
| **2. Backtesting e validação** | Testes com safras históricas (M1–M3), análise de sensibilidade, validação independente pelo time de risco do banco | 1 mês | 130.000 |
| **3. Integração e homologação** | Conexão ao motor de crédito existente do Pan, construção dos pipelines de dados, deploy em ambiente segregado | 2 meses | 200.000 |
| **4. Conformidade regulatória** | Revisão de compliance e proteção de dados, controles de acesso à base sigilosa, documentação de modelo, aprovação em comitê de crédito | Paralelo às Fases 2–3 (meses 4–6), ~0,5 FTE | 65.000 |
| **Investimento inicial total** | | **~6 meses** | **R\$ 625.000** |

**Composição dos custos por fase:**

O time técnico core (D1 + D2 + D3) custa ~R\$ 67.500/mês. Ao longo dos 6 meses de desenvolvimento, esse time responde por ~R\$ 405.000 do investimento total. Os R\$ 220.000 restantes se distribuem em:

- Infraestrutura de desenvolvimento (D6): R\$ 5.000/mês × 6 = R\$ 30.000
- Gestão de projeto (D4, dedicação parcial ~18%): R\$ 38.000 × 18% × 6 = ~R\$ 41.000
- Validação independente pelo time de risco do banco (~300h de analista sênior): ~R\$ 60.000 (embutido na Fase 2)
- Integração com motor de crédito (especialistas do banco, ~4 semanas): ~R\$ 24.000 (embutido na Fase 3)
- Conformidade e governança (Fase 4 — revisão de compliance, controle de acesso, model card, aprovação em comitê): R\$ 65.000

Total detalhado: R\$ 405k + R\$ 30k + R\$ 41k + R\$ 60k + R\$ 24k + R\$ 65k = **R\$ 625.000**.

---

### 4.4 Custos operacionais anuais

Após a entrada em produção, o modelo requer manutenção contínua para manter performance e aderência regulatória.

| Item | Anual (R\$) | Premissa |
|:---|---:|:---|
| Infraestrutura de produção (cloud) | 120.000 | D7: R\$ 10.000/mês |
| Monitoramento do modelo (cientista de dados pleno, 30% dedicação) | 63.000 | D2: R\$ 17.500 × 30% |
| Ajustes periódicos (recalibração trimestral, ~40h/ciclo) | 30.000 | D1: R\$ 30.000 ÷ 160h × 40h × 4 ciclos |
| Suporte analítico e reportes ao comitê de crédito (~20h/mês) | 26.000 | D2: R\$ 17.500 ÷ 160h × 20h × 12 |
| **Total custos anuais** | **R\$ 239.000** | |

---

### 4.5 Benefícios econômicos estimados

O benefício vem da **redistribuição mais eficiente dos limites de crédito**: clientes de baixo risco recebem limites mais aderentes ao seu perfil (aumentando utilização e receita de interchange), enquanto clientes de alto risco têm limites reduzidos (diminuindo perdas por inadimplência). Trata-se de uma **única ação de otimização** que gera impacto simultâneo nos dois lados — receita e risco — da função objetivo definida pelo TAPI.

Por essa razão, tratamos o benefício como uma **melhoria única sobre o resultado econômico combinado** da carteira, e não como duas melhorias independentes somadas. O baseline econômico combinado é:

$$
\text{Baseline combinado} = \text{Receita de interchange (B4)} + \text{Perda evitável (A4)} = R\$\ 167\ mi + R\$\ 168\ mi = R\$\ 335\ mi
$$

Aplicando a premissa C1 (melhoria de 1,0% no cenário base — **piso da faixa** reportada na literatura):

$$
\text{Ganho potencial (regime permanente)} = R\$\ 335\ mi \times 1,0\% = R\$\ 3.350.000
$$

Esse ganho se materializa como uma combinação de mais receita de interchange (clientes bons usando mais o cartão) e menos perda por inadimplência (clientes arriscados com limites menores). A proporção exata entre os dois depende de como o modelo redistribui os limites — o que só será conhecido após o backtesting.

> **O ganho já é líquido de perdas por inadimplência.** É importante notar que o baseline combinado inclui, em sua composição, a perda líquida anual por inadimplência da carteira de cartões (A4 = R\$ 168 mi, já descontada a taxa de recuperação de 30%). A melhoria de 1% (C1) incide sobre esse baseline que já incorpora o custo da inadimplência — ou seja, o ganho estimado de R\$ 3,35 mi representa o saldo **líquido** entre receita incremental gerada e perdas evitadas, não apenas um aumento bruto de receita. Não há, portanto, necessidade de subtrair perdas por inadimplência em etapa posterior do cálculo: elas já estão contabilizadas na construção do baseline. Os benchmarks da literatura (Thomas, 2009; Trench et al., 2003) que fundamentam a premissa C1 também reportam ganhos líquidos, reforçando a consistência metodológica.

Contudo, o primeiro ano de operação não captura a totalidade do benefício potencial. A rampagem da adoção interna (integração com motor de crédito, validação pelo comitê, treinamento do time de estratégia) limita a captura efetiva. Aplicando a premissa C2 (captura de 25% no Ano 1):

$$
\text{Ganho efetivo no Ano 1} = R\$\ 3.350.000 \times 25\% = R\$\ 837.500
$$

> **Nota metodológica:** ao somar receita de interchange e perda evitada no mesmo baseline, tratamos as duas componentes como economicamente equivalentes. Na prática, R\$ 1 de perda evitada vai integralmente para a linha do lucro, enquanto R\$ 1 de receita bruta de interchange ainda carrega custos associados (taxa da bandeira, processamento, fraude). O efeito líquido no lucro não é perfeitamente simétrico. Optamos por manter a simplificação em primeira ordem porque (i) não dispomos das taxas internas do Pan para decompor o interchange líquido e (ii) o impacto dessa assimetria é marginal frente à incerteza já capturada na análise de sensibilidade (seção 4.6).

> **Sensibilidade à premissa A3 (taxa de recuperação):** se a recuperação real for 20% em vez de 30%, a perda líquida (A4) sobe de R\$ 168 mi para R\$ 193 mi, e o baseline combinado vai de R\$ 335 mi para R\$ 360 mi. No cenário base (C1 = 1,0%), o ganho anual passaria de R\$ 3,35 mi para R\$ 3,60 mi — uma variação de ~7% que não altera a conclusão de viabilidade. Diferentemente de C1, a taxa de recuperação pode ser verificada com dados públicos do BCB ou obtida diretamente com o parceiro.

---

### 4.6 Cálculo do ROI

$$
ROI = \frac{\text{Benefício líquido}}{\text{Investimento inicial}} \times 100
$$

Onde:

$$
\text{Benefício líquido} = \text{Ganhos estimados (1 ano)} - \text{Custos operacionais anuais}
$$

#### Cenário base — passo a passo

**Passo 1 — Investimento inicial:** R\$ 625.000 (seção 4.3)

**Passo 2 — Custos operacionais anuais:** R\$ 239.000 (seção 4.4)

**Passo 3 — Ganhos efetivos no Ano 1:** R\$ 837.500 (seção 4.5, C1 = 1,0%, C2 = 25%)

**Passo 4 — Benefício líquido:**

$$
\text{Benefício líquido} = R\$\ 837.500 - R\$\ 239.000 = R\$\ 598.500
$$

**Passo 5 — ROI:**

$$
ROI = \frac{R\$\ 598.500}{R\$\ 625.000} \times 100 \approx \textbf{95,8\%}
$$

**Passo 6 — Payback:**

$$
\text{Payback} = \frac{R\$\ 625.000}{R\$\ 598.500 / 12} \approx \textbf{12{,}5\ meses}
$$

#### Análise de sensibilidade — cenários para C1 e C2

As premissas C1 (melhoria) e C2 (captura no Ano 1) são os principais drivers de incerteza da análise (ambas com confiança Baixa). Para avaliar a robustez do resultado, recalculamos o ROI em três cenários que variam ambos os parâmetros simultaneamente:

| Cenário | C1 (melhoria) | C2 (captura Y1) | Ganho efetivo Y1 | Custos anuais | Benefício líquido | **ROI** | **Payback** |
|:---|:---:|:---:|---:|---:|---:|---:|---:|
| Pessimista | 0,5% | 15% | R\$ 251 mil | R\$ 239 mil | R\$ 12 mil | **2%** | **não paga em 1 ano** |
| **Base** | **1,0%** | **25%** | **R\$ 838 mil** | **R\$ 239 mil** | **R\$ 599 mil** | **96%** | **12,5 meses** |
| Otimista | 2,0% | 40% | R\$ 2.680 mil | R\$ 239 mil | R\$ 2.441 mil | **391%** | **3,1 meses** |

No cenário pessimista (C1 = 0,5%, captura de apenas 15%), o projeto gera valor marginalmente positivo mas não se paga no horizonte de 1 ano — exigindo justificativa estratégica complementar (ganhos regulatórios, maturidade analítica) para aprovação em comitê. No cenário base, o ROI de ~96% indica que o projeto praticamente se paga no primeiro ano, com payback de ~12,5 meses.

---

### 4.7 Interpretação dos resultados

**Viabilidade financeira.** O ROI base de **~96%** indica que o projeto é financeiramente viável: o ganho gerado no primeiro ano praticamente recupera o investimento total. O investimento de R\$ 625 mil equivale a apenas **0,07% do lucro ajustado** anual do Pan (~R\$ 855 mi em 2024, RI Banco Pan) — é um projeto de baixo risco financeiro para o banco. Pelo lado do ganho, os R\$ 599 mil de benefício líquido no cenário base representam **~0,07% do lucro ajustado** — um impacto marginal mas positivo para um projeto de otimização mono-produto. A modéstia do número é esperada e desejável: trata-se de uma calibragem cirúrgica em um produto específico, não de uma transformação estrutural da carteira.

**Por que o ROI não é mais alto.** Embora a literatura reporte ROIs de três dígitos em projetos de analytics aplicados a grandes carteiras de crédito (Trench et al., 2003), esses valores se referem a regime permanente, após plena integração da solução ao processo decisório do banco. No Ano 1, a captura de apenas 25% do benefício potencial (premissa C2) reflete a realidade de rampagem: integração com motor de crédito, validação pelo comitê, treinamento do time de estratégia e resistência organizacional. Em regime permanente (captura plena), o ROI anualizado seria significativamente mais alto — mas seria desonesto apresentá-lo como resultado do Ano 1.

**Ponto de equilíbrio (break-even).** Para que o benefício líquido seja zero no Ano 1, o ganho efetivo precisaria cobrir apenas os custos operacionais: R\$ 239 mil. Sobre o ganho potencial de R\$ 3,35 mi (regime permanente), isso equivale a uma captura de apenas **~7%** — um patamar muito baixo que só se materializaria em cenário de adoção quase nula da solução.

**Benefício operacional para o usuário.** Além do ganho financeiro, a solução gera valor operacional direto para o analista de crédito e o time de estratégia (conforme detalhado no Canvas, seção 3). Estimativa preliminar: cada ciclo de revisão manual de política de limites consome ~40–60 horas de analista sênior (levantamento de dados, simulação de cenários, validação com comitê). Com a solução automatizando a geração de cenários, estimamos redução de ~50% desse tempo — equivalente a ~20–30 horas/ciclo. Em 4 ciclos anuais (recalibração trimestral), isso representa ~80–120 horas/ano de analista sênior, ou **~R\$ 15.000–22.500/ano** (a custo D1). Esse benefício não foi monetizado no cálculo do ROI para manter a análise conservadora.

#### Limitações da análise

- **Premissa C1 não validada com dados do parceiro.** A melhoria de 1,0% (cenário base) é extraída da literatura acadêmica, não de backtesting com dados do Banco Pan. O ROI real só será conhecido após a implementação do modelo com dados históricos das safras M1–M3. Por essa razão, adotamos o piso da faixa reportada (1%) como cenário base, e não o ponto médio.

- **Custos dependem da infraestrutura interna do banco.** Os valores estimados para integração (Fase 3) e conformidade (Fase 4) pressupõem que o Pan já dispõe de motor de crédito e processos de governança estruturados. Se a infraestrutura for menos madura, esses custos podem ser significativamente maiores.

- **Investimento 100% amortizado no primeiro ano.** Para fins didáticos, o ROI apresentado trata o investimento de R\$ 625 mil como integralmente consumido no Ano 1. Em uma análise corporativa real, esse investimento seria amortizado ao longo do ciclo de vida do modelo — tipicamente 3 anos, compatível com o ciclo de revisão e recalibração de modelos de risco em bancos regulados. Nesse caso, o custo anualizado do investimento seria ~R\$ 208 mil/ano (R\$ 625k ÷ 3), e o ROI do Ano 1 seria calculado contra essa parcela em vez do total, resultando em ROI mais alto. A conclusão de viabilidade, portanto, não é afetada pela simplificação — ao contrário, a abordagem adotada é a mais conservadora possível.

- **Captura de 25% no Ano 1 é premissa do grupo.** A taxa de captura (C2) é a segunda maior fonte de incerteza da análise, após C1. O valor de 25% reflete a experiência típica de projetos de analytics em bancos (rampagem lenta, resistência organizacional), mas pode ser otimista ou pessimista dependendo da maturidade da infraestrutura de crédito do Pan.

---

## Referências da análise financeira

> ASSOCIAÇÃO BRASILEIRA DAS EMPRESAS DE CARTÕES DE CRÉDITO E SERVIÇOS (ABECS). **Indicadores de mercado**. São Paulo: ABECS, 2023–2024. Disponível em: https://www.abecs.org.br/indicadores-de-mercado. Acesso em: 20 abr. 2026.
>
> ADVFN. Banco Pan reporta R\$ 209 milhões de lucro líquido e expansão de crédito sustenta BPAN4. *ADVFN Brasil*, nov. 2025. Disponível em: https://br.advfn.com/jornal/2025/11/banco-pan-reporta-r-209-milhoes-de-lucro-liquido-e-expansao-de-credito-sustenta-bpan4. Acesso em: 20 abr. 2026.
>
> ADVFN. Banco Pan registra queda de 9% no lucro do 2T25 com aumento da inadimplência. *ADVFN Brasil*, ago. 2025. Disponível em: https://br.advfn.com/jornal/2025/08/banco-pan-registra-queda-de-9-no-lucro-do-2t25-com-aumento-da-inadimplencia. Acesso em: 20 abr. 2026.
>
> BANCO CENTRAL DO BRASIL. **Relatório de Estabilidade Financeira**, 2º semestre de 2024. Brasília: BCB, 2024. Disponível em: https://www.bcb.gov.br/publicacoes/ref. Acesso em: 20 abr. 2026.
>
> BANCO CENTRAL DO BRASIL. **Arranjos de pagamento — Taxas de intercâmbio**. Brasília: BCB, [s.d.]. Disponível em: https://www.bcb.gov.br/estabilidadefinanceira/pagamentosarranjos. Acesso em: 20 abr. 2026.
>
> BANCO PAN. **Relações com Investidores — Demonstrações financeiras e resultados trimestrais (2T25 e 3T25)**. São Paulo, 2025. Disponível em: https://ri.bancopan.com.br/. Acesso em: 20 abr. 2026.
>
> BANCO PAN; INTELI. **TAPI — Termo de Abertura do Projeto Integrador: Otimização de limites pré-aprovados de cartão de crédito**. São Paulo, 2026.
>
> COMISSÃO DE VALORES MOBILIÁRIOS (CVM). **Sistema RAD — DFP e ITR Banco Pan S.A.** Disponível em: https://www.rad.cvm.gov.br/. Acesso em: 20 abr. 2026.
>
> GLASSDOOR BRASIL. **Pesquisa salarial — Cientista de dados, Engenheiro de dados, Tech Lead**. 2025. Disponível em: https://www.glassdoor.com.br/. Acesso em: 20 abr. 2026.
>
> NORD INVESTIMENTOS. Banco Pan (BPAN4) — Resultados 4T24. 2025. Disponível em: https://www.nordinvestimentos.com.br/blog/banco-pan-bpan4-resultados-4t24/. Acesso em: 20 abr. 2026.
>
> ROBERT HALF. **Guia Salarial 2025**. São Paulo: Robert Half, 2025. Disponível em: https://www.roberthalf.com.br/guia-salarial. Acesso em: 20 abr. 2026.
>
> THOMAS, L. C. **Consumer Credit Models: Pricing, Profit and Portfolios**. Oxford: Oxford University Press, 2009.
>
> TRENCH, M. S. *et al.* Managing credit lines and prices for Bank One credit cards. **Interfaces**, v. 33, n. 5, p. 4–21, 2003.



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
