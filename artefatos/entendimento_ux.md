# Entendimento da Experiência do Usuário

> **Guia de uso deste template:**
>
> - Trechos em _itálico entre colchetes_ `[...]` são instruções — substituir pelo conteúdo do grupo
> - Blocos `> TAPI`, `> PARA NOTA 10` e `> NÃO FAZER` são lembretes internos — **remover antes de entregar**
>
> **Feedback do módulo passado (UX, nota 7,5 — nota mais baixa do grupo):**
>
> - **Não** explicar "o que é persona" — o professor considera desnecessário. Ir direto.
> - **Dores = consequências**, não atividades. "Faz cálculo manual" é atividade; "sente pressão por erro que pode custar milhões" é dor.
> - **"Como a solução ajuda"** deve ser explícito e concreto — não confundir com "desejos" ou "cenários de interação"
> - **Necessidades = outcomes**, não features. "Eliminar achismo" > "ter dashboard"
> - **User Stories: SMALL é o mais cobrado.** Se tem "e" no meio, são duas US.
> - **Critérios de aceite testáveis** — sem termos vagos ("parâmetros definidos", "funciona corretamente", "condições críticas")
> - **Não incluir funcionalidades fora do escopo** — se o TAPI não prevê, a persona não pode precisar disso

---

## 1. Personas (5 pontos)

_Identificar os **usuários reais** da solução. Criar **2-3 personas** com perfis distintos._

> **TAPI — quem são os usuários:**
>
> | Área                                                     | Papel no projeto                                                                                                                                                                | Tipo de usuário                    |
> | :------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :--------------------------------- |
> | **Time de Políticas de Crédito (Estratégia de Crédito)** | **Usuário final da solução.** Configura parâmetros, avalia cenários, decide qual política de limites implementar. É quem o TAPI chama de "usuário da solução".                  | **Persona primária**               |
> | **Time de Data Science (Crédito)**                       | Desenvolve e mantém a solução. Integra com motores internos. Valida resultados técnicos. Líderes deste time (Eduardo Schneider, Mateus Gonzalez) são os avaliadores do projeto. | **Persona primária ou secundária** |
> | **Time de TI**                                           | Implementação prática, integração com motores de precificação. Não usa diretamente, mas viabiliza a solução.                                                                    | **Stakeholder (não persona)**      |
> | **Time de Dados e Segurança da Informação**              | Governança de dados, compliance. Não usa diretamente.                                                                                                                           | **Stakeholder (não persona)**      |
>
> **Sugestão de personas (validar com parceiro):**
>
> 1. **Analista/Gerente de Estratégia de Crédito** — quem efetivamente usa a solução no dia a dia para definir políticas de limites. Persona principal.
> 2. **Cientista de Dados da área de Crédito** — quem integra, calibra e mantém o modelo. Persona técnica.
> 3. (Opcional) **Gestor executivo / Líder de risco** — quem avalia resultados e toma decisão final. Persona secundária — cuidado para não atribuir funcionalidades que não existem.

> **PARA NOTA 10:**
>
> - Validar personas com o parceiro no kickoff: "quem efetivamente usaria essa solução?"
> - Cada persona deve ter conexão **direta** com a solução — se não interage com o sistema, não é persona
> - O TAPI diz que o uso é "conjunto entre Data Science e Estratégia de Crédito" — ambos os times devem estar representados
>
> **NÃO FAZER (feedback M5):**
>
> - ~~"Segundo Cooper (2004), persona é uma representação fictícia..."~~ — ir direto
> - ~~Incluir "monitoramento em tempo real" ou funcionalidades não previstas no TAPI~~
> - ~~Ganhos ligados à alta gestão e não ao usuário principal~~ — professor cobrou isso explicitamente
> - ~~Usar "desejos" ou "cenários de interação" no lugar de "como a solução ajuda"~~

---

### Persona 1 — [Nome] (Estratégia de Crédito)

_Esta é a persona **principal** — o TAPI diz que "o time de políticas de crédito será o usuário final da solução"._

|                 |                                                                         |
| :-------------- | :---------------------------------------------------------------------- |
| **Nome**        | _[Nome fictício realista]_                                              |
| **Idade**       | _[Ex: 32-42 anos]_                                                      |
| **Cargo**       | _[Ex: Analista/Gerente de Estratégia de Crédito]_                       |
| **Formação**    | _[Ex: Economia, Engenharia, Estatística + MBA/especialização em risco]_ |
| **Localização** | _[São Paulo, SP — sede do Pan/BTG]_                                     |
| **Experiência** | _[Anos no mercado, tempo no Pan]_                                       |

> **Contexto do TAPI para esta persona:**
>
> - Define políticas de limites pré-aprovados de cartão de crédito
> - Trabalha em conjunto com Data Science — recebe outputs do modelo e decide o que implementar
> - Avalia cenários de concessão (conservador/moderado/agressivo)
> - Precisa justificar decisões para comitê de crédito e auditoria
> - Monitora inadimplência física e financeira da carteira
> - Lida com o trade-off entre área comercial (quer mais volume) e área de risco (quer menos inadimplência)

**Background profissional:**

_[1-2 parágrafos. Descrever o dia a dia, como se relaciona com o problema de limites, por que usaria a solução.]_

**Dores:**

> **Lembrete:** Dores são **consequências emocionais, operacionais ou profissionais** — não atividades.
>
> - ❌ "Faz calibragem manual em planilhas" → atividade
> - ✅ "Sente pressão constante por cada decisão de limite, sabendo que um erro de calibração pode gerar milhões em provisão e colocar seu cargo em risco" → dor

_Sugestões de dores para esta persona (adaptar/reescrever):_

- _Pressão por reduzir inadimplência sem sacrificar receita — sensação de "escolher qual problema criar"_
- _Incapacidade de defender decisões com argumentos quantitativos no comitê de crédito — depende de intuição_
- _Sobrecarga ao equilibrar manualmente múltiplas variáveis (PD, capacidade, score, segmento) em planilhas_
- _Tensão com a área comercial: sem ferramenta objetiva, a discussão sobre limites vira disputa política_
- _Risco reputacional: como responsável pela política, qualquer aumento de inadimplência recai sobre essa pessoa_

- _[Dor 1]_
- _[Dor 2]_
- _[Dor 3]_
- _[Dor 4]_

**Como a solução ajuda [Nome]:**

> **Lembrete:** Ser concreto. Conectar cada item a uma dor acima.
>
> - ❌ "A solução melhora a eficiência" → vago
> - ✅ "Substitui intuição por decisão matematicamente fundamentada, permitindo defender escolhas com dados no comitê" → concreto

_Sugestões (adaptar):_

- _O modelo define limites otimizados respeitando simultaneamente inadimplência física, financeira e capacidade de pagamento — elimina o "escolher qual problema criar"_
- _Cenários configuráveis (alterar tetos de inadimplência, metas de produção) e execução em minutos — substitui semanas de calibragem manual_
- _Cada limite é rastreável à função objetivo e restrições ativas — defensável em comitê e auditoria_
- _O trade-off comercial vs. risco é formalizado na função objetivo — linguagem comum baseada em dado_

- _[Como alivia Dor 1]_
- _[Como alivia Dor 2]_
- _[...]_

**Necessidades (como outcomes):**

> **Lembrete:** Outcomes, não features.
>
> - ❌ "Ter um dashboard de cenários" → feature
> - ✅ "Eliminar a incerteza sobre o impacto financeiro de cada decisão de limite" → outcome

- _[Necessidade 1]_
- _[Necessidade 2]_
- _[Necessidade 3]_

---

### Persona 2 — [Nome] (Data Science)

_O TAPI diz que o time de Data Science "é responsável pelo desenvolvimento de tais soluções na instituição". São eles que integram o modelo aos motores internos do banco._

|                 |                                                        |
| :-------------- | :----------------------------------------------------- |
| **Nome**        | _[Nome]_                                               |
| **Idade**       | _[Ex: 27-35 anos]_                                     |
| **Cargo**       | _[Ex: Cientista de Dados Sênior — Crédito]_            |
| **Formação**    | _[Ex: Ciência da Computação, Estatística, Engenharia]_ |
| **Localização** | _[São Paulo, SP]_                                      |
| **Experiência** | _[Experiência em DS, tempo no Pan]_                    |

> **Contexto do TAPI para esta persona:**
>
> - Mantém os modelos de scoring que geram `score_interno` e `pd_produto`
> - Integra outputs do modelo de otimização aos motores de crédito do banco
> - O TAPI pede output preferencialmente em **Python** — esta persona é quem lida com isso
> - Os líderes técnicos (Mateus Gonzalez) e executivos (Eduardo Schneider, Felipe Rubim) desta área avaliam o projeto
> - Avalia o modelo comparando rentabilidade entre `limite_ofertado` e limite sugerido

**Background profissional:**

_[Descrição]_

**Dores:**

_Sugestões de dores (adaptar):_

- _Frustração de que os modelos de ML (scoring) geram PD precisa, mas a tradução para limite é feita por regras simplistas — trabalho técnico subaproveitado_
- _Conflito com compliance sobre explicabilidade: modelos sofisticados são rejeitados por serem "caixa preta"_
- _Pressão por mostrar impacto financeiro mensurável do trabalho de Data Science_
- _Dificuldade de integrar soluções novas aos motores de crédito legados do banco_

- _[Dor 1]_
- _[Dor 2]_
- _[Dor 3]_

**Como a solução ajuda [Nome]:**

_Sugestões (adaptar):_

- _Usa diretamente os outputs existentes (`pd_produto`, `score_propensao_contrato`) como inputs — dá uso real à infra de ML_
- _Otimização linear é interpretável por construção — elimina conflito com compliance_
- _Output em Python para integração direta com motores internos_
- _Calcula impacto financeiro (receita esperada vs. perda) diretamente — métrica apresentável_

- _[...]_

**Necessidades (como outcomes):**

- _[...]_

---

### Persona 3 (secundária) — [Nome]

_Opcional. Pode ser um gestor executivo, analista de produtos, ou outro perfil. Marcar como "secundária" se interage menos._

> **CUIDADO (feedback M5):** Ganhos NÃO devem ser da alta gestão — devem ser do **usuário direto**. Se incluir um gestor executivo, as dores/ganhos devem ser **dele como usuário** (ex: avaliar resultados do modelo), não como beneficiário indireto (ex: "o banco lucra mais").

|                 |     |
| :-------------- | :-- |
| **Nome**        |     |
| **Idade**       |     |
| **Cargo**       |     |
| **Formação**    |     |
| **Localização** |     |
| **Experiência** |     |

**Background profissional:**

_[Descrição]_

**Dores:**

- _[...]_

**Como a solução ajuda [Nome]:**

- _[...]_

**Necessidades (como outcomes):**

- _[...]_

---

## 2. User Stories (5 pontos)

_Mínimo **5 User Stories**. Formato: "como [quem], eu quero [o que], para [por que]". Cada US conectada a uma persona e dor._

> **INVEST — o professor cobra fortemente (feedback M5):**
>
> | Critério        | O que significa                                 | Erro comum neste projeto                                                        |
> | :-------------- | :---------------------------------------------- | :------------------------------------------------------------------------------ |
> | **I**ndependent | Cada US testável isoladamente                   | ~~US de visualização que depende de importação estar pronta — usar dados mock~~ |
> | **N**egotiable  | O "como" é negociável, o "para que" não         | ~~Especificar "usar React" ou "API REST" na US~~                                |
> | **V**aluable    | Valor direto para o usuário                     | ~~"Como dev, eu quero refatorar"~~                                              |
> | **E**stimable   | Equipe consegue estimar esforço                 | ~~US gigante sem escopo claro~~                                                 |
> | **S**mall       | **UMA responsabilidade.** Se tem "e", são duas. | ~~"importar dados **e** rodar o modelo **e** ver resultados"~~                  |
> | **T**estable    | Critérios **sem ambiguidade**                   | ~~"funciona corretamente", "principais resultados", "parâmetros definidos"~~    |

> **TAPI — funcionalidades que o MVP deve ter:**
>
> - Seleção ótima e atribuição de limites de cartão por cliente ou cluster (≥100 clusters)
> - Formulação teórica (função objetivo + restrições)
> - Restrições configuráveis: inadimplência física e financeira, capacidade de pagamento com alavancagem diferenciada, limite mínimo R$200, múltiplos de R$50, metas de produção
> - Comparação com política atual (`limite_ofertado`)
> - Output em Python
> - Descrição técnica dos algoritmos e métodos
>
> **TAPI — o que NÃO está no escopo:**
>
> - ~~Ajuste de modelos de score de crédito~~ — scores são fornecidos prontos
> - ~~Programação não-linear ou estocástica~~
> - ~~Dashboard web sofisticado~~ — o TAPI não pede interface gráfica, pede software Python
> - ~~Monitoramento em tempo real~~
> - ~~Integração direta com sistemas do banco~~ — o TAPI pede output Python para integração posterior

> **Sugestões de User Stories alinhadas ao TAPI:**
>
> _Agrupadas por persona — escolher, adaptar e detalhar critérios de aceite:_
>
> **Para a persona de Estratégia de Crédito:**
>
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
>
> - Carregar base de dados do parceiro (parquet com as 17 variáveis do TAPI)
> - Executar clusterização com número configurável de clusters (≥100)
> - Executar o solver de otimização e obter limites ótimos por cluster
> - Exportar resultados em formato Python/CSV para integração com motores internos
> - Validar que os limites respeitam R$200 mínimo e são múltiplos de R$50
> - Rodar backtesting contra safras históricas (M1, M2, M3)
>
> **Atenção:** Cada item acima é uma US potencial. **Não** juntar vários em uma só.

---

### US1 — _[Título curto]_

**Como** _[Persona]_, **eu quero** _[ação única e específica]_, **para** _[benefício conectado a uma dor]_.

**Critérios de Aceitação:**

- _[Critério 1 — mensurável, sem ambiguidade. Ex: "aceita valores entre 0,0 e 15,0"]_
- _[Critério 2 — com valores numéricos. Ex: "executa em ≤ 5 minutos para ≥ 100 clusters"]_
- _[Critério 3 — verificável. Ex: "nenhum limite gerado é inferior a R$ 200"]_

> **Dicas para critérios testáveis neste projeto:**
>
> - ~~"O modelo respeita as restrições"~~ → "Nenhum limite gerado viola: (a) teto de inadimplência física, (b) teto financeiro, (c) capacidade × multiplicador, (d) R$ 200 mínimo, (e) múltiplo de R$ 50"
> - ~~"Exibe os resultados"~~ → "Exibe: receita esperada total (R$), inadimplência física projetada (%), inadimplência financeira projetada (%), quantidade de clientes aprovados, volume total de limite"
> - ~~"Funciona para a base"~~ → "Processa a base M1 (~1,8M elegíveis) em ≤ X minutos com ≥ 100 clusters"
> - ~~"Compara com o atual"~~ → "Para os ~117K clientes com `limite_ofertado` não nulo, exibe: diferença média de limite (R$), variação de rentabilidade esperada (%), variação de inadimplência projetada (pp)"

---

### US2 — _[Título]_

**Como** _[Persona]_, **eu quero** _[ação]_, **para** _[benefício]_.

**Critérios de Aceitação:**

- _[...]_

---

### US3 — _[Título]_

**Como** _[Persona]_, **eu quero** _[ação]_, **para** _[benefício]_.

**Critérios de Aceitação:**

- _[...]_

---

### US4 — _[Título]_

**Como** _[Persona]_, **eu quero** _[ação]_, **para** _[benefício]_.

**Critérios de Aceitação:**

- _[...]_

---

### US5 — _[Título]_

**Como** _[Persona]_, **eu quero** _[ação]_, **para** _[benefício]_.

**Critérios de Aceitação:**

- _[...]_

---

_[Adicionar mais US — recomendação: 7-9 US pequenas e focadas. Melhor ter mais US pequenas do que poucas grandes.]_

---

## 3. Jornada do Usuário (Opcional — vale 2 pontos extras)

_Mapear o percurso de **uma persona específica** (a primária) usando a solução._

> **PARA NOTA MÁXIMA:**
>
> - Conectar a uma persona específica
> - Cada etapa deve corresponder a uma ou mais User Stories
> - Incluir pensamentos e sentimentos realistas
> - Identificar oportunidades de melhoria

> **Sugestão de jornada para a persona de Estratégia de Crédito:**
>
> | Etapa                                                                       | Correspondência com US      |
> | :-------------------------------------------------------------------------- | :-------------------------- |
> | 1. Receber dados processados do time de DS                                  | US de carregamento de dados |
> | 2. Configurar parâmetros (tetos de inadimplência, alavancagem, metas)       | US de configuração          |
> | 3. Executar otimização                                                      | US de execução              |
> | 4. Analisar resultados agregados (receita, inadimplência física/financeira) | US de visualização          |
> | 5. Comparar com política atual (`limite_ofertado`)                          | US de comparação            |
> | 6. Investigar clusters específicos (quais restrições foram ativas)          | US de explicabilidade       |
> | 7. Ajustar parâmetros e re-executar (cenário alternativo)                   | US de cenários              |
> | 8. Exportar resultado final para apresentar no comitê                       | US de exportação            |

| Etapa | Ação          | Pensamento      | Sentimento        | Oportunidade       |
| :---- | :------------ | :-------------- | :---------------- | :----------------- |
| _[1]_ | _[O que faz]_ | _[O que pensa]_ | _[Como se sente]_ | _[O que melhorar]_ |
| _[2]_ |               |                 |                   |                    |
| _[3]_ |               |                 |                   |                    |
| _[4]_ |               |                 |                   |                    |
| _[5]_ |               |                 |                   |                    |
| _[6]_ |               |                 |                   |                    |

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
3. _[Dados do parceiro — TAPI, bases M1/M2/M3]_
4. _[Referências adicionais]_
