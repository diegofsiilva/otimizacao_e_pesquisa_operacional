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
| **Solução baseada em scoring + regras fixas** | Modelos de credit scoring (regressão logística, gradient boosting) geram um score por cliente, mapeado a limites pré-definidos por tabela (ex: score 700–750 → R$ 3.000). Padrão atual de mercado. O Pan já usa IA em 100% das decisões de crédito ([Consumidor Moderno](https://consumidormoderno.com.br/inteligencia-artificial-banco-pan/)). |
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

### Matriz de Risco

A gestão de riscos é um pilar fundamental para o desenvolvimento estruturado de qualquer projeto que envolva modelagem quantitativa aplicada a decisões financeiras. Segundo o Project Management Body of Knowledge [1], esse processo permite antecipar incertezas capazes de comprometer o andamento, a qualidade ou a adoção da solução proposta, estabelecendo planos de resposta antes que as ameaças se materializem. No contexto específico de instituições financeiras, o tema ganha uma camada adicional de importância: a Resolução CMN nº 4.557/2017 [2] exige que bancos mantenham estrutura formal de gerenciamento de riscos integrada à sua estratégia de negócio, o que torna qualquer nova ferramenta de decisão de crédito — como a proposta neste projeto — sujeita aos princípios de gestão prudencial. Este mapeamento, portanto, não é apenas um exercício acadêmico, mas um requisito para que a solução seja adotável no ambiente real do Banco PAN.

## Visualização da Matriz de Risco

A matriz a seguir posiciona visualmente cada evento segundo dois eixos: probabilidade de ocorrência e magnitude do impacto. No lado das ameaças, a distribuição revela que os riscos mais críticos não são de natureza algorítmica, mas semântica — concentrados na tradução correta da realidade de negócio para a formulação matemática, na qualidade dos dados disponíveis e na aderência regulatória da solução. No lado das oportunidades, destacam-se condições estruturalmente favoráveis ao projeto que, se capturadas de forma deliberada, elevam a credibilidade e a adotabilidade da entrega final.

Os riscos foram selecionados de forma a cobrir as sete dimensões sugeridas pelo roteiro: técnicos, operacionais, de negócio, de dados, de implementação, de governança e de interpretação econômica. O objetivo desta seção é definir ações claras para evitar ou mitigar esses eventos, garantindo que a entrega final seja não apenas funcional, mas adotável no ambiente real do parceiro.

![Matriz de Riscos e Oportunidades](assets/riscosg04.jpg)

## Tabela de Ameaças

| ID | Descrição | Justificativa | Plano de Mitigação |
|----|-----------|---|---|
| A01 | Função objetivo desalinhada com o apetite de risco real do PAN | Formulação incorreta produz soluções tecnicamente ótimas mas economicamente inadequadas, comprometendo toda a proposta. | Validar em Sprint Reviews com representantes do parceiro. Documentar trade-offs e submetê-los a revisão formal. |
| A02 | Insuficiência ou baixa qualidade dos dados para calibração | Total dependência de terceiros para dados sensíveis. Dados inadequados invalidam qualquer conclusão quantitativa. | Acordar "mínimo viável de dados" no Sprint 1. Preparar bases sintéticas como backup e validar qualidade dos dados reais assim que recebidos. |
| A03 | Viés amostral e uso inadequado de variáveis | Dados restritos a clientes já aprovados induzem o modelo a replicar vieses da política atual em vez de otimizá-la. | Validar variáveis com especialistas do PAN. Aplicar reponderação para corrigir survivorship bias e testar robustez com subconjuntos distintos. |
| A04 | Premissas de modelagem não documentadas ou injustificadas | Simplificações sem registro tornam o modelo uma caixa-preta impossível de auditar ou ajustar. | Manter "caderno de hipóteses" com todas as premissas. Realizar análise de sensibilidade e validar premissas-chave com o parceiro. |
| A05 | Expansão excessiva do escopo | Tentação de incorporar múltiplos segmentos e variáveis impede entrega funcional no prazo letivo. | Definir MVP rígido no Sprint 1. Congelar escopo por sprint e renegociar adições formalmente via comitê interno. |
| A06 | Dificuldade de implementação no ambiente do parceiro | Restrições de infraestrutura, latência ou sistemas legados podem inviabilizar a adoção real da solução. | Mapear requisitos de infraestrutura no Sprint 1. Adotar arquitetura modular com stack simples e dependências claras. |
| A07 | Baixa explicabilidade e defensabilidade em comitê | Ausência de documentação das restrições ativas compromete a defesa em comitê de crédito ou auditoria. | Gerar relatório de restrições ativas por decisão. Construir dashboard de transparência rastreando cada limite até a função objetivo. |
| A08 | Calibragem incorreta dos limites recomendados | Limites excessivos amplificam risco e inadimplência; limites conservadores demais reduzem conversão e receita. Na dúvida, errar para o lado conservador é preferível enquanto o modelo amadurece. | Backtesting contra safras históricas, hard caps por faixa de PD e comparação sistemática contra a política atual como baseline. |
| A09 | Não-aderência ao framework regulatório (CMN nº 4.966/2021) | Não incorporar perda esperada (PD × exposição) conforme a resolução vigente torna a solução inadotável no ambiente real do PAN. | Mapear exigências regulatórias no Sprint 1 e estruturar restrições do modelo com lógica aderente. Validar com o parceiro. |
| A10 | Descasamento entre inadimplência física e financeira | Otimizar apenas uma métrica pode violar a outra — ex.: limites altos a poucos clientes arriscados estouram a inadimplência financeira mesmo respeitando a física. | Implementar ambas como restrições independentes no modelo. Monitorar as duas métricas nos relatórios de backtesting. |
| A11 | Modelo ignora propensão à conversão dos clientes | Desconsiderar que parte dos clientes não converterá superestima o retorno esperado e torna a alocação de capital ineficiente. | Incorporar score de propensão à conversão na função objetivo ou como variável de segmentação. |

## Tabela de Oportunidades

| ID | Descrição | Justificativa | Plano de Potencialização |
|----|-----------|---|---|
| O01 | Alinhamento com a Resolução CMN nº 4.966/2021 e Basel | Incorporar o framework de perda esperada (PD × LGD × EAD) desde o início transforma uma exigência regulatória em diferencial competitivo da solução. | Estudar a resolução no Sprint 1 e estruturar restrições com nomenclatura aderente. Explicitar a conformidade no artefato final. |
| O02 | Acesso a dados reais de safras históricas do PAN | Dados históricos com inadimplência observada permitem calibração realista, inatingível com dados sintéticos. | Negociar acesso via TAPI no Sprint 1. Estruturar dicionário de dados com performance observada e validar qualidade nas primeiras duas semanas. |
| O03 | Feedback contínuo do parceiro em Sprint Reviews | Checkpoints quinzenais permitem validar decisões cedo, evitando retrabalho custoso. Oportunidade de alta frequência e baixo custo de captura. | Preparar pautas objetivas e levar protótipos a cada review. Registrar decisões, pendências e responsáveis após cada encontro. |
| O04 | Benchmark com literatura consolidada de CLO | Literatura madura em Credit Limit Optimization evita reinvenção e ancora decisões de modelagem em práticas de mercado. | Revisão bibliográfica antes de fechar a função objetivo. Citar referências no artefato para fortalecer credibilidade junto ao parceiro. |
| O05 | Aprendizado prático em risco de crédito como capital humano | Exposição a problema real de quantitative finance gera portfólio diferenciado para os membros, sem impacto direto na entrega. | Registrar aprendizados internamente e conectar ao conteúdo acadêmico de econometria, otimização e risco de crédito. |

## Conclusão

A análise conjunta das ameaças e oportunidades mapeadas revela uma característica estrutural deste projeto: seu maior desafio não é técnico, mas de aderência — entre o modelo matemático e a realidade de negócio do Banco PAN, entre as premissas assumidas e os dados disponíveis, e entre a solução entregue e o arcabouço regulatório vigente.

Do lado das ameaças, quatro concentrações exigem atenção prioritária. O eixo de interpretação econômica — função objetivo (A01), premissas de modelagem (A04) e explicabilidade (A07) — indica que a principal fragilidade do projeto é a tradução correta da estratégia de risco-retorno do banco para linguagem matemática. Os riscos de dados e implementação (A02, A03, A06) são estruturalmente dependentes do parceiro, exigindo negociação clara desde o Sprint 1. A calibragem do modelo (A08) carrega assimetria relevante: errar para o lado conservador é preferível enquanto o modelo amadurece, pois limites excessivos têm impacto catastrófico e de difícil reversão. Por fim, os riscos regulatórios e de dupla métrica de inadimplência (A09, A10, A11) representam requisitos formais cujo não-atendimento tornaria a solução inadotável independentemente de qualquer mérito técnico.

Do lado das oportunidades, o projeto dispõe de quatro alavancas de alto potencial: ancoragem regulatória desde o início (O01), acesso a dados reais com performance observada (O02), validação contínua com o parceiro em Sprint Reviews (O03) e benchmark com literatura consolidada de Credit Limit Optimization (O04). Nenhuma dessas condições se realizará automaticamente — todas exigem ação deliberada e disciplinada a partir das primeiras semanas de desenvolvimento.

Em síntese, o sucesso da entrega depende menos da sofisticação algorítmica e mais da disciplina de processo: validar premissas com o parceiro, documentar decisões de modelagem, respeitar o escopo definido e capturar ativamente as condições favoráveis identificadas. Projetos de otimização aplicada em ambientes bancários regulados são, antes de tudo, exercícios de rigor metodológico e comunicação estruturada — e é nessa dimensão que este mapeamento orienta as prioridades da equipe.

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

1. [Banco Pan - Relações com Investidores](https://ri.bancopan.com.br/)
2. [Banco Pan - Resultados 2T25 (Nord Investimentos)](https://www.nordinvestimentos.com.br/blog/banco-pan-bpan4-resultados-2t25/)
3. [Banco Pan - IA em decisões de crédito (Consumidor Moderno)](https://consumidormoderno.com.br/inteligencia-artificial-banco-pan/)
4. [LGPD - Lei 13.709/2018](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm)
5. [Glassdoor - Salários Brasil 2025](https://www.glassdoor.com.br/Salarios)
6. [AWS Pricing - EC2](https://aws.amazon.com/ec2/pricing/)
7. [Strategyzer - Value Proposition Canvas](https://www.strategyzer.com/library/the-value-proposition-canvas)

## referências matriz de risco:

[1] PROJECT MANAGEMENT INSTITUTE. *A Guide to the Project Management Body of Knowledge (PMBOK® Guide)*. 7. ed. Newtown Square: Project Management Institute, 2021.

[2] BRASIL. Conselho Monetário Nacional. Resolução CMN nº 4.557, de 23 de fevereiro de 2017. Dispõe sobre a estrutura de gerenciamento de riscos e a estrutura de gerenciamento de capital em instituições financeiras. Brasília: Banco Central do Brasil, 2017. Disponível em: https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Resolução%20CMN&numero=4557. Acesso em: abr. 2026.

[3] BRASIL. Conselho Monetário Nacional. Resolução CMN nº 4.966, de 25 de novembro de 2021. Dispõe sobre os conceitos e os critérios contábeis aplicáveis a instrumentos financeiros e sobre a mensuração das provisões para perdas esperadas associadas ao risco de crédito. Brasília: Banco Central do Brasil, 2021. Disponível em: https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Resolução%20CMN&numero=4966. Acesso em: abr. 2026.

