# Entendimento da Experiência do Usuário

> **Guia de uso deste template:**
> - Trechos em *itálico entre colchetes* `[...]` são instruções — substituir pelo conteúdo do grupo
> - Blocos `> TAPI`, `> PARA NOTA 10` e `> NÃO FAZER` são lembretes internos — **remover antes de entregar**
>
> **Feedback do módulo passado (UX, nota 7,5 — nota mais baixa do grupo):**
> - **Não** explicar "o que é persona" — o professor considera desnecessário. Ir direto.
> - **Dores = consequências**, não atividades. "Faz cálculo manual" é atividade; "sente pressão por erro que pode custar milhões" é dor.
> - **"Como a solução ajuda"** deve ser explícito e concreto — não confundir com "desejos" ou "cenários de interação"
> - **Necessidades = outcomes**, não features. "Eliminar achismo" > "ter dashboard"
> - **User Stories: SMALL é o mais cobrado.** Se tem "e" no meio, são duas US.
> - **Critérios de aceite testáveis** — sem termos vagos ("parâmetros definidos", "funciona corretamente", "condições críticas")
> - **Não incluir funcionalidades fora do escopo** — se o TAPI não prevê, a persona não pode precisar disso

---
<br>

## 1. Personas

Personas são representações fictícias de usuários reais, criadas com base em dados, comportamentos e necessidades observadas. Elas ajudam equipes a entender melhor quem são os usuários de um produto, orientando decisões de design, tecnologia e negócio, alinhando todos os times. Também, elas auxiliam na criação de soluções centradas no usuário, o que priorizar funcionalidades de mais impacto e melhora a experiência e usabilidade do sistema.


> **Quem são os usuários:**
>
> | Área | Papel no projeto | Tipo de usuário |
> |:---|:---|:---|
> | **Time de Políticas de Crédito (Estratégia de Crédito)** | **Usuário final da solução.** Configura parâmetros, avalia cenários, decide qual política de limites implementar. É quem o TAPI chama de "usuário da solução". | **Persona primária** |
> | **Time de Data Science (Crédito)** | Desenvolve e mantém a solução. Integra com motores internos. Valida resultados técnicos. Líderes deste time (Eduardo Schneider, Mateus Gonzalez) são os avaliadores do projeto. | **Persona secundária** |

### Persona 1 — Rodinei Filho (Estratégia de Crédito)

<div align = center>
  <sub>FIGURA x - Persona do Time de  Políticas de Crédito </sub><br>
  <img src= "../assets/Rodinei-Credito.png" 
  alt="Rodinei Filho"><br>
  <sup>Fonte: Material produzido pelos autores</sup>
  </div>
  <br>

  Para aprofundar a compreensão do usuário final da solução, foram detalhados os principais objetivos, dores e necessidades do analista de política de crédito no contexto do projeto. Esse detalhamento permite entender como as decisões estratégicas são tomadas e quais desafios estão envolvidos no equilíbrio entre risco e rentabilidade. A partir dessa análise, é possível orientar o desenvolvimento de uma solução mais intuitiva, transparente e alinhada às demandas do negócio.

**Objetivos**
- Definir políticas de limite que maximizem retorno sem aumentar inadimplência da carteira
- Garantir que as decisões estejam alinhadas com metas do banco (crescimento, risco, volume)
- Conseguir justificar decisões para liderança com base em dados
- Reduzir decisões manuais e subjetivas, tornando o processo mais consistente
- Ajustar rapidamente estratégias conforme mudanças no mercado ou performance

**Dores**
- Recebe outputs do modelo sem clareza de “por que” aquele limite foi sugerido
- Dificuldade de traduzir métricas técnicas (ex: probabilidade de inadimplência) em decisão prática
- Sensação de perda de controle quando o modelo parece “decidir sozinho”
- Processo atual pode ser manual ou pouco padronizado
- Pressão constante para equilibrar risco vs crescimento (trade-off difícil)
- Dificuldade em prever impacto de mudanças antes de aplicá-las (falta de simulação)
- Dependência do time de Data Science para ajustes simples

**Necessidades**
- Interface visual clara que traduza o modelo em informação de negócio
- Explicabilidade: entender quais variáveis impactaram o limite sugerido
- Ferramenta de simulação (ex: “e se eu aumentar o limite médio?”)
- Controle sobre restrições (ex: risco máximo, capacidade de pagamento)
- Visão agregada da carteira (risco, retorno, volume)
- Comparação entre cenário atual vs cenário sugerido
- Agilidade para testar e implementar mudanças

### Persona 2 — Larissa Paiva (Data Science)

<div align = center>
  <sub>FIGURA x - Persona do Time de Data Science </sub><br>
  <img src= "../assets/Larissa-Dados.png" 
  alt="Larissa Paiva"><br>
  <sup>Fonte: Material produzido pelos autores</sup>
  </div>
<br>

**Objetivos**
- Construir um modelo de otimização que maximize retorno ajustado ao risco
- Garantir que o modelo respeite todas as restrições de negócio
- Fazer com que o modelo seja utilizado na prática (não só tecnicamente correto)
- Reduzir necessidade de ajustes manuais após entrega
- Monitorar performance e identificar quando o modelo precisa ser recalibrado

**Dores**
- Regras de negócio nem sempre são claras ou formalizadas
- Mudanças frequentes de política geram retrabalho no modelo
- Dificuldade de explicar decisões complexas para stakeholders não técnicos
- Falta de feedback estruturado do time de política
- Output do modelo pode não ser interpretado corretamente
- Tempo gasto ajustando pequenas regras que poderiam ser parametrizadas
- Dificuldade em validar impacto real do modelo após implementação

**Necessidades**
- Estrutura clara de restrições (formalizadas e parametrizáveis)
- Ferramenta para testar diferentes configurações do modelo
- Visibilidade de como o modelo está sendo usado pela política
- Métricas claras de avaliação (retorno, risco, inadimplência)
- Integração com sistemas internos (motor de crédito)
- Padronização de inputs e outputs
-Redução de dependência de ajustes manuais

## Considerações Finais

As personas mostram claramente a relação entre os dois principais perfis do sistema:

- **Larissa (Data Science)** → foca na construção e qualidade do modelo  
- **Rodinei (Política de Crédito)** → foca na decisão e estratégia  

A solução proposta deve garantir transparência, usabilidade e alinhamento entre técnica e negócio. Isso é essencial para que o modelo não apenas funcione bem, mas também seja confiável e utilizado na prática.

## 2. User Stories (5 pontos)

*Mínimo **5 User Stories**. Formato: "como [quem], eu quero [o que], para [por que]". Cada US conectada a uma persona e dor.*

> **INVEST — o professor cobra fortemente (feedback M5):**
>
> | Critério | O que significa | Erro comum neste projeto |
> |:---|:---|:---|
> | **I**ndependent | Cada US testável isoladamente | ~~US de visualização que depende de importação estar pronta — usar dados mock~~ |
> | **N**egotiable | O "como" é negociável, o "para que" não | ~~Especificar "usar React" ou "API REST" na US~~ |
> | **V**aluable | Valor direto para o usuário | ~~"Como dev, eu quero refatorar"~~ |
> | **E**stimable | Equipe consegue estimar esforço | ~~US gigante sem escopo claro~~ |
> | **S**mall | **UMA responsabilidade.** Se tem "e", são duas. | ~~"importar dados **e** rodar o modelo **e** ver resultados"~~ |
> | **T**estable | Critérios **sem ambiguidade** | ~~"funciona corretamente", "principais resultados", "parâmetros definidos"~~ |

> **TAPI — funcionalidades que o MVP deve ter:**
> - Seleção ótima e atribuição de limites de cartão por cliente ou cluster (≥100 clusters)
> - Formulação teórica (função objetivo + restrições)
> - Restrições configuráveis: inadimplência física e financeira, capacidade de pagamento com alavancagem diferenciada, limite mínimo R$200, múltiplos de R$50, metas de produção
> - Comparação com política atual (`limite_ofertado`)
> - Output em Python
> - Descrição técnica dos algoritmos e métodos
>
> **TAPI — o que NÃO está no escopo:**
> - ~~Ajuste de modelos de score de crédito~~ — scores são fornecidos prontos
> - ~~Programação não-linear ou estocástica~~
> - ~~Dashboard web sofisticado~~ — o TAPI não pede interface gráfica, pede software Python
> - ~~Monitoramento em tempo real~~
> - ~~Integração direta com sistemas do banco~~ — o TAPI pede output Python para integração posterior

> **Sugestões de User Stories alinhadas ao TAPI:**
>
> *Agrupadas por persona — escolher, adaptar e detalhar critérios de aceite:*
>
> **Para a persona de Estratégia de Crédito:**
> - Configurar teto de inadimplência física (média simples de PD ≤ valor atual)
> - Configurar teto de inadimplência financeira (média ponderada de PD por limite ≤ valor atual)
> - Configurar multiplicadores de alavancagem por faixa de risco
> - Configurar metas de produção (quantidade de clientes aprovados, volume de limite)
> - Visualizar distribuição dos limites otimizados por cluster/faixa de risco
> - Comparar limites otimizados vs. `limite_ofertado` (política atual) em termos de rentabilidade
> - Consultar quais restrições foram ativas para um dado cluster (explicabilidade/auditoria)
> - Executar cenários alternativos (ex: "e se o teto de inadimplência fosse 1pp menor?")
>
> **Para a persona de Data Science:**
> - Carregar base de dados do parceiro (parquet com as 17 variáveis do TAPI)
> - Executar clusterização com número configurável de clusters (≥100)
> - Executar o solver de otimização e obter limites ótimos por cluster
> - Exportar resultados em formato Python/CSV para integração com motores internos
> - Validar que os limites respeitam R$200 mínimo e são múltiplos de R$50
> - Rodar backtesting contra safras históricas (M1, M2, M3)
>
> **Atenção:** Cada item acima é uma US potencial. **Não** juntar vários em uma só.

---

### US1 — *[Título curto]*

**Como** *[Persona]*, **eu quero** *[ação única e específica]*, **para** *[benefício conectado a uma dor]*.

**Critérios de Aceitação:**
- *[Critério 1 — mensurável, sem ambiguidade. Ex: "aceita valores entre 0,0 e 15,0"]*
- *[Critério 2 — com valores numéricos. Ex: "executa em ≤ 5 minutos para ≥ 100 clusters"]*
- *[Critério 3 — verificável. Ex: "nenhum limite gerado é inferior a R$ 200"]*

> **Dicas para critérios testáveis neste projeto:**
> - ~~"O modelo respeita as restrições"~~ → "Nenhum limite gerado viola: (a) teto de inadimplência física, (b) teto financeiro, (c) capacidade × multiplicador, (d) R$ 200 mínimo, (e) múltiplo de R$ 50"
> - ~~"Exibe os resultados"~~ → "Exibe: receita esperada total (R$), inadimplência física projetada (%), inadimplência financeira projetada (%), quantidade de clientes aprovados, volume total de limite"
> - ~~"Funciona para a base"~~ → "Processa a base M1 (~1,8M elegíveis) em ≤ X minutos com ≥ 100 clusters"
> - ~~"Compara com o atual"~~ → "Para os ~117K clientes com `limite_ofertado` não nulo, exibe: diferença média de limite (R$), variação de rentabilidade esperada (%), variação de inadimplência projetada (pp)"

---

### US2 — *[Título]*

**Como** *[Persona]*, **eu quero** *[ação]*, **para** *[benefício]*.

**Critérios de Aceitação:**
- *[...]*

---

### US3 — *[Título]*

**Como** *[Persona]*, **eu quero** *[ação]*, **para** *[benefício]*.

**Critérios de Aceitação:**
- *[...]*

---

### US4 — *[Título]*

**Como** *[Persona]*, **eu quero** *[ação]*, **para** *[benefício]*.

**Critérios de Aceitação:**
- *[...]*

---

### US5 — *[Título]*

**Como** *[Persona]*, **eu quero** *[ação]*, **para** *[benefício]*.

**Critérios de Aceitação:**
- *[...]*

---

*[Adicionar mais US — recomendação: 7-9 US pequenas e focadas. Melhor ter mais US pequenas do que poucas grandes.]*

---

## 3. Jornada do Usuário (Opcional — vale 2 pontos extras)


### Persona 1 — Rodinei Filho (Política de Crédito)

**Persona:** Rodinei Filho, analista de Política de Crédito do Banco PAN.  

**Cenário:** Definir e comunicar uma estratégia de concessão de limites pré-aprovados com base no modelo de otimização linear, equilibrando retorno esperado, risco de inadimplência e capacidade de pagamento dos correntistas.  

**Expectativa central:** Decisões seguras, simples, rastreáveis e orientadas por dados.

<img src="/assets/jornadaRodinei.jpg">

#### Mapa da Jornada

| Etapa | Ação | Pensamento | Sentimento | Oportunidade |
|:---|:---|:---|:---|:---|
| **1. Receber análise** | Acessa o sistema e visualiza a distribuição dos limites sugeridos pelo modelo, junto às métricas de risco e retorno da carteira. Consulta o contexto da recomendação para entender o que o modelo está propondo. | *"O que o modelo está sugerindo? Faz sentido com o que eu já sei da carteira?"* | Curioso, levemente desconfiante — precisa entender a lógica por trás dos números antes de confiar. | Exibir junto ao output um resumo da função objetivo e das restrições ativas, para que a recomendação venha acompanhada de seu racional matemático desde o primeiro contato. **US relacionada: US06** |
| **2. Interpretar outputs** | Avalia o impacto dos limites sugeridos sobre a inadimplência física e financeira. Analisa o retorno esperado da estratégia e compara os resultados com as metas de negócio vigentes. | *"Qual o impacto em risco e retorno? Estou dentro das restrições que o banco exige?"* | Analítico e pressionado — precisa traduzir números técnicos em decisão defensável para a gestão. | Disponibilizar uma visão comparativa direta entre o output do modelo e as metas, com destaque automático para restrições próximas do limite. **US relacionada: US06** |
| **3. Simular cenários** | Ajusta metas de produção (volume de clientes aprovados e volume financeiro de limite ofertado) e testa o impacto das mudanças nos resultados. Compara cenários alternativos para identificar o melhor equilíbrio. | *"Posso melhorar esse equilíbrio? O que acontece se eu relaxar a meta de inadimplência em 0,5 ponto?"* | Engajado e investigativo — sente que tem controle sobre a política, mas anseia por um retorno de simulação mais rápido. | Oferecer um simulador de cenários baseado diretamente na função objetivo, sem dependência do time de Data Science para cada rodada. **US relacionada: US03** |
| **4. Decidir estratégia** | Consulta as restrições ativas que impactam cada decisão (capacidade de pagamento, alavancagem, PDD), valida a aderência às políticas de crédito vigentes e define a estratégia final de concessão. | *"Qual decisão maximiza o resultado com segurança? Consigo justificar essa escolha em comitê?"* | Cauteloso e responsável — o peso da decisão é real, pois erros afetam a carteira e os correntistas. | Gerar templates de decisão com as restrições utilizadas explicitadas, facilitando a documentação e a defesa da estratégia em auditorias e comitês. **US relacionada: US04** |
| **5. Comunicar e revisar** | Exporta os resultados e os compartilha com as áreas envolvidas (gestão, engenharia, produto). Acompanha o desempenho da carteira ao longo do tempo e ajusta a estratégia conforme os resultados observados. | *"Funcionou ou preciso ajustar? O modelo continua válido para o cenário atual?"* | Reflexivo e responsável pelo ciclo completo — busca evidências de que a política entregou o que prometia. | Criar um dashboard com impacto esperado versus realizado (retorno, inadimplência, volume concedido), com alertas automáticos quando o desempenho divergir das premissas do modelo. **US relacionada: US07** |

#### Oportunidades Consolidadas

A jornada de Rodinei expõe três tensões recorrentes que moldam as oportunidades de design da solução. A primeira é a tensão entre sofisticação do modelo e interpretabilidade operacional: cada fase exige que ele consiga traduzir outputs matemáticos em decisões justificáveis, sem mediação constante do time de Data Science. A segunda é a tensão entre agilidade e rigor: simular cenários hoje depende de ciclos longos de reprocessamento, o que limita a exploração de alternativas antes da decisão. A terceira é a tensão entre decisão pontual e governança contínua: Rodinei precisa não apenas decidir bem, mas documentar e monitorar a política ao longo do tempo.

Essas tensões convergem para cinco oportunidades estruturais: (1) simulador de cenários autônomo baseado na função objetivo; (2) visualização clara do impacto em inadimplência física e financeira; (3) templates de decisão com restrições explícitas; (4) dashboard de acompanhamento de retorno, risco e volume; e (5) sandbox para testar políticas respeitando o motor de crédito e as restrições regulatórias do banco.

#### Responsabilidades do Rodinei

A jornada de Rodinei só se sustenta se cada área cumpre seu papel de forma coordenada. A Política de Crédito define e mantém as regras de negócio — risco, alavancagem e capacidade de pagamento. O próprio Rodinei documenta as decisões com base na função objetivo e nas restrições utilizadas em cada rodada. O time de Data Science entrega os outputs interpretáveis, especialmente as variáveis de risco e retorno esperado por cluster. O Produto constrói a interface de simulação e decisão. Engenharia e TI implementam o pipeline de integração e monitoramento em produção. A Gestão, por fim, define as metas de inadimplência, rentabilidade e volume que balizam a função objetivo.

---

### Persona 2 — Larissa Paiva (Data Science)

**Persona:** Larissa Paiva, cientista de dados responsável pelo desenvolvimento e manutenção do modelo de otimização de limites de crédito.  

**Cenário:** Desenvolver o modelo de otimização linear para definição de limites pré-aprovados, considerando função objetivo, restrições de negócio e integração com sistemas de produção do banco.  

**Expectativa central:** Clareza técnica, robustez matemática e confiança na tomada de decisão.

<img src="/assets/jornadaLarissa.jpg">

#### Mapa da Jornada

| Etapa | Ação | Pensamento | Sentimento | Oportunidade |
|:---|:---|:---|:---|:---|
| **1. Receber a demanda** | Carrega e valida a base de dados no formato adequado. Analisa as variáveis de risco, renda e capacidade de pagamento disponíveis. Entende os objetivos de negócio e as restrições iniciais fornecidas pela Política de Crédito. | *"Qual o problema e quais as restrições? O que o negócio quer maximizar e o que não pode ser violado?"* | Investigativa e meticulosa — qualquer ambiguidade na demanda se propaga como erro no modelo. | Criar um canal estruturado e versionado entre negócio e Data Science para formalização da função objetivo e das restrições, evitando retrabalho por interpretações divergentes. **US relacionada: US01** |
| **2. Desenvolver o modelo** | Configura a segmentação de clientes (clusterização), define metas de produção e restrições formais do modelo, e estrutura a otimização com função objetivo e conjunto de restrições explícitas. | *"Como otimizar isso matematicamente? A formulação que escolhi é válida e resolve o problema real?"* | Concentrada e tecnicamente exigente consigo mesma — sente responsabilidade pela robustez da solução que vai orientar decisões de crédito reais. | Disponibilizar um ambiente de versionamento de regras e premissas para evitar inconsistências entre o modelo em desenvolvimento e a política em vigor. **US relacionadas: US02, US03** |
| **3. Validar resultados** | Garante que os limites gerados respeitam o mínimo de R$ 200 e os múltiplos de R$ 50. Testa a consistência da solução com dados históricos e avalia o impacto projetado em risco e rentabilidade da carteira. | *"O resultado é melhor que o atual? Consigo provar que o modelo não viola nenhuma restrição operacional?"* | Rigorosa e crítica — a comparação com a baseline histórica é o momento de maior tensão técnica da jornada. | Fornecer uma ferramenta de simulação que permita testar o modelo contra cenários históricos antes de qualquer exposição em produção. **US relacionada: US05** |
| **4. Comunicar ao negócio** | Apresenta a distribuição dos limites por cluster de risco, exibe métricas agregadas (média, mínimo, máximo por segmento) e explica os trade-offs entre risco e retorno de forma acessível para a área de Política de Crédito. | *"Como explicar isso para o negócio? Consigo traduzir PD e EL em linguagem que o Rodinei consiga usar em comitê?"* | Mediadora entre dois mundos — sente a responsabilidade de não deixar que a sofisticação técnica se torne um obstáculo para a adoção da solução. | Padronizar a tradução de métricas técnicas para métricas de negócio (por exemplo, PD expressa como impacto financeiro esperado), reduzindo o esforço de comunicação a cada ciclo. **US relacionada: US06** |
| **5. Monitorar produção** | Exporta os resultados para integração com sistemas internos, acompanha a performance do modelo em produção e ajusta parâmetros conforme mudanças de cenário macroeconômico ou de comportamento da carteira. | *"O modelo continua performando bem? Houve deriva nos dados que exige recalibração?"* | Vigilante e comprometida com a longevidade da solução — sabe que um modelo bem construído pode degradar se não for monitorado continuamente. | Implementar monitoramento contínuo de inadimplência e retorno da carteira com alertas automáticos de deriva, integrando o ciclo de revisão ao calendário de gestão do banco. **US relacionada: US07** |

#### Oportunidades Consolidadas

A jornada de Larissa revela um desafio que começa antes do modelo: a ausência de um protocolo estruturado para receber e formalizar a demanda do negócio. Quando a função objetivo e as restrições chegam de forma ambígua ou verbal, o retrabalho técnico é inevitável. Ao longo do desenvolvimento, a maior fragilidade está na falta de versionamento das premissas — qualquer alteração na política de crédito pode invalidar silenciosamente um modelo já treinado. Na validação, a ausência de um ambiente de simulação pré-produção força Larissa a depender de análises manuais em dados históricos, o que consome tempo e aumenta o risco de erros não detectados.

As oportunidades se organizam em torno de cinco eixos: (1) canal estruturado com o negócio para definição e versionamento da função objetivo e restrições; (2) ferramenta de simulação para testar cenários antes da produção; (3) monitoramento contínuo de inadimplência e retorno com alertas de deriva; (4) padronização da tradução de métricas técnicas para linguagem de negócio; e (5) alinhamento dos ciclos de revisão do modelo ao calendário de gestão da carteira.

#### Responsabilidades da Larissa

O sucesso da jornada de Larissa depende de uma divisão de responsabilidades clara entre quatro frentes. O time de Data Science, liderado por Larissa, desenvolve o modelo de otimização linear com função objetivo e restrições formalizadas. A Política de Crédito fornece as regras de negócio e valida as restrições que o modelo deve respeitar. O Produto disponibiliza a ferramenta de simulação e visualização dos resultados. Engenharia e TI implementam o pipeline de integração e o monitoramento em produção. A Gestão, por fim, alinha os ciclos de revisão do modelo com base na performance da carteira, fechando o ciclo entre decisão técnica e estratégia de negócio.

---

## Checklist pré-entrega

**Personas:**
- [ ] Nenhuma explicação conceitual ("o que é persona")
- [ ] Personas correspondem aos **usuários reais** da solução (Estratégia de Crédito + Data Science, conforme TAPI)
- [ ] Dores são **consequências emocionais/operacionais**, não atividades
- [ ] "Como a solução ajuda" é **concreto** e conectado às dores
- [ ] Necessidades são **outcomes**, não features
- [ ] Nenhuma funcionalidade fora do escopo (TAPI não pede dashboard web, monitoramento real-time, integração direta)
- [ ] Ganhos são do **usuário direto**, não da alta gestão (feedback M5)

**User Stories:**
- [ ] Mínimo 5 US, formato "como [quem], eu quero [o que], para [por que]"
- [ ] Cada US tem **uma única responsabilidade** (SMALL — se tem "e", quebrar)
- [ ] Cada US é **independente** (testável isoladamente, sem depender de outra)
- [ ] Critérios de aceite **inline** (junto da US, não em seção separada)
- [ ] Critérios **testáveis** — sem termos vagos ("parâmetros definidos", "funciona corretamente")
- [ ] Critérios com **valores numéricos** quando aplicável (tempo, quantidade, limites)
- [ ] US conectadas a personas e dores específicas
- [ ] Nenhuma US referencia funcionalidade fora do escopo do TAPI

**Alinhamento TAPI:**
- [ ] Mencionado que o output é Python (não webapp)
- [ ] Mencionado que a solução é usada em conjunto por DS e Estratégia de Crédito
- [ ] Restrições do TAPI aparecem nas US: inadimplência física/financeira, alavancagem diferenciada, R$200 mínimo, múltiplos R$50, metas de produção
- [ ] Backtesting contra `limite_ofertado` presente em alguma US
- [ ] Dados do TAPI (17 variáveis, parquet, ~1,8M elegíveis) refletidos nas US de carregamento

---

## Fontes

1. [Princípio INVEST - Adapt Works](https://blog.adapt.works/como-escrever-as-melhores-user-stories-com-invest/)
2. [Template Jornada do Usuário (Miro)](https://miro.com/app/board/uXjVOi3EFh4=/?share_link_id=503534748467)
3. *[Dados do parceiro — TAPI, bases M1/M2/M3]*
4. *[Referências adicionais]*
5. [What are Personas- IxDF](https://www.interaction-design.org/literature/topics/personas)
6. [Personas Make Users Memorable - NN/Group](https://www.nngroup.com/articles/persona/)
