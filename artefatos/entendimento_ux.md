# Entendimento da Experiência do Usuário

---

## 1. Personas

Para este projeto, as _personas_ foram definidas com base nas áreas que efetivamente **utilizarão e sustentarão a solução**, a partir das reuniões com o parceiro.

 O usuário principal é o time de **Estratégia de Crédito**, responsável por **configurar parâmetros e restrições**, **avaliar cenários** e **decidir quais políticas de limites serão implementadas**. Como usuário secundário, considera-se o **time de Data Science**, que atua no **desenvolvimento e manutenção da solução**, além de **garantir a qualidade técnica dos resultados** e apoiar a **integração com os motores internos**.

Assim, as duas _personas_ buscam **refletir a dinâmica real do trabalho**: o time de Data Science viabiliza e valida tecnicamente, enquanto o time de Estratégia de Crédito interpreta os resultados, ajusta restrições e define a política a ser aplicada.

O detalhamento das _personas_ definidas pode ser encontrado a seguir: 

### Persona 1 — Rodinei Filho (Estratégia de Crédito)

<div align = center>
  <sub>FIGURA 1 - Persona do Time de Estratégia de Crédito </sub><br>
  <br>
  <img src="assets/Rodinei-Credito.png" 
  alt="Rodinei Filho"><br>
  <sup>Fonte: Material produzido pelos autores</sup>
</div>
  <br>

### Persona 2 — Larissa Paiva (Data Science)

<div align = center>
  <sub>FIGURA 2 - Persona do Time de Data Science </sub><br>
  <br>
  <img src="assets/Larissa-Dados.png" 
  alt="Larissa Paiva"><br>
  <sup>Fonte: Material produzido pelos autores</sup>
  </div>
<br>

## Conclusões

As _personas_ defindias refletem os dois papéis essenciais para que a solução de otimização de limites seja construída, validada e adotada no processo de definição de políticas.

Com o mapeamento das dores, necessidades, objetivos e benefícios esperados de cada _persona_, os principais aspectos da solução também foram evidenciados. O sucesso do projeto depende tanto da **confiabilidade e reprodutibilidade técnica** (garantidas por Data Science) quanto da **clareza para a tomada de decisão** (necessária para Estratégia de Crédito), assegurando que o modelo não só funcione, mas seja utilizado como suporte real à definição de políticas.

## 2. User Stories (5 pontos)

Segundo Max Rehkopf, gerente de _Marketing_ de Produto na **_Atlassian_** (empresa multinacional de _software_), _User Stories_ se tratam de tarefas de desenvolvimento, composta por descrições concisas e focadas nos usuários. Para o projeto com o _Banco Pan_, as _User Stories_ são derivadas das duas _personas_ mapeadas: XXXX e YYYY. Cada história é desenvolvida levando em consideração as suas dores específicas e ganhos esperados, buscando uma maior robustez e alinhamento da solução. 

As _User Stories_ também buscam seguir o _framework_ INVEST. Ele visa garantir que as histórias criadas são independentes umas das outras, negociáveis (podem ser ajustadas futuramente), geram valor para os usuários, estimáveis, concisas e testáveis.

---

### US01 - Carregar base de dados

**Como** cientista de dados,  
**eu quero** carregar a base de dados do banco no formato parquet,  
**para** utilizar informações corretas e completas na segmentação e otimização de limites por cluster.

**Dores relacionadas:**

- Bases inconsistentes.
- Retrabalho técnico.
- Falta de padronização.

**Critérios de aceitação:**

- Aceita arquivos parquet contendo as 17 variáveis do TAPI.
- Carrega bases com até ~1,8 milhões de registros elegíveis.
- Exibe erro claro para arquivo corrompido ou colunas ausentes.
- Permite uso de base mock para testes.

---

### US02 - Ajustar clusterização

**Como** cientista de dados,  
**eu quero** configurar o número de clusters utilizados na segmentação,  
**para** testar diferentes cenários de agrupamento dos clientes.

**Dores relacionadas:**

- Segmentação ruim.
- Pouca flexibilidade.
- Ajustes manuais.

**Critérios de aceitação:**

- Permite definir número inteiro de clusters.
- Aceita mínimo de 100 clusters.
- Exibe erro para valores inválidos.
- Executa clusterização com base mock e base real.

---

### US03 - Configurar metas de produção

**Como** analista de estratégia de crédito,  
**eu quero** configurar metas de clientes aprovados e volume total de limite,  
**para** alinhar a otimização aos objetivos do negócio.

**Dores relacionadas:**

- Falta de controle.
- Metas desalinhadas.
- Dependência técnica.

**Critérios de aceitação:**

- Permite definir meta de clientes aprovados.
- Permite definir meta de volume financeiro.
- Bloqueia valores fora das faixas válidas.
- Salva metas sem executar solver.

---

### US04 - Gerar limite por cluster

**Como** analista de estratégia de crédito,  
**eu quero** gerar limites sugeridos para cada cluster,  
**para** aplicar políticas segmentadas de crédito.

**Dores relacionadas:**

- Processo manual.
- Limites genéricos.
- Decisão lenta.

**Critérios de aceitação:**

- Retorna um limite para cada cluster ativo.
- Nenhum limite é inferior a R$200.
- Todos os limites finais são múltiplos de R$50.
- Exibe clusters sem solução viável.

---

### US05 - Consultar restrições ativas

**Como** analista de estratégia de crédito,  
**eu quero** consultar quais restrições do modelo impactaram cada cluster,  
**para** justificar decisões e facilitar auditorias.

**Dores relacionadas:**

- Falta de clareza.
- Baixa confiança.
- Dificuldade de justificar.

**Critérios de aceitação:**

- Exibe restrições aplicadas por cluster.
- Mostra identificador do cluster e limite sugerido.
- Permite busca por cluster.
- Retorna até 10.000 registros em até 3 segundos.

---

### US06 - Visualizar distribuição dos limites

**Como** analista de estratégia de crédito,  
**eu quero** visualizar a distribuição dos limites por cluster,  
**para** analisar os resultados e apoiar decisões.

**Dores relacionadas:**

- Outputs técnicos.
- Pouca visão geral.
- Insegurança na decisão.

**Critérios de aceitação:**

- Exibe média, mediana, mínimo e máximo por cluster.
- Permite visualização em tabela ou gráfico.
- Permite ordenar resultados.
- Funciona com dataset mock.

---

### US07 - Exportar resultados

**Como** cientista de dados,  
**eu quero** exportar os resultados finais da otimização,  
**para** integrar a saída com outros sistemas internos.

**Dores relacionadas:**

- Retrabalho manual.
- Compartilhamento difícil.
- Integração lenta.

**Critérios de aceitação:**

- Exporta arquivo CSV ou objeto Python.
- Contém identificador do cluster, limite atribuído e métricas principais.
- Funciona a partir de arquivo de resultados existente.
- Exibe mensagem de sucesso ou erro.

---

---

## 3. Jornada do Usuário (Opcional — vale 2 pontos extras)

Esta seção apresenta a jornada dos principais usuários envolvidos no processo de definição de limites de crédito: o analista de Política de Crédito e a cientista de dados. 
O objetivo é evidenciar como cada perfil interage com o modelo de otimização, destacando suas ações, percepções e principais desafios ao longo do processo. A partir dessa análise, são identificadas oportunidades de melhoria que orientam o desenvolvimento da solução proposta.


### Persona 1 — Rodinei Filho (Política de Crédito)

**Persona:** Rodinei Filho, analista de Política de Crédito do Banco PAN.  

**Cenário:** Definir e comunicar uma estratégia de concessão de limites pré-aprovados com base no modelo de otimização linear, equilibrando retorno esperado, risco de inadimplência e capacidade de pagamento dos correntistas.  

**Expectativa central:** Decisões seguras, simples, rastreáveis e orientadas por dados.



<div align = center>
  <sub>FIGURA 3 - Jornada de Usuário do Time de Política de Crédito </sub><br>
  <img src="assets/jornadaRodinei.jpg"><br>
  <sup>Fonte: Material produzido pelos autores</sup>
  </div>

---

### Persona 2 — Larissa Paiva (Data Science)

**Persona:** Larissa Paiva, cientista de dados responsável pelo desenvolvimento e manutenção do modelo de otimização de limites de crédito.  

**Cenário:** Desenvolver o modelo de otimização linear para definição de limites pré-aprovados, considerando função objetivo, restrições de negócio e integração com sistemas de produção do banco.  

**Expectativa central:** Clareza técnica, robustez matemática e confiança na tomada de decisão.


<div align = center>
  <sub>FIGURA 4 - Jornada de Usuário do Time de Data Science </sub><br>
  <img src="assets/jornadaLarissa.jpg"><br>
  <sup>Fonte: Material produzido pelos autores</sup>
</div>

---

### Conclusão 

A análise das jornadas evidencia a necessidade de maior integração entre áreas técnicas e de negócio, além de maior transparência e autonomia no uso do modelo. 
As oportunidades identificadas reforçam a importância de soluções que facilitem a interpretação dos resultados, a simulação de cenários e o monitoramento contínuo da estratégia, contribuindo para decisões mais seguras, ágeis e orientadas por dados.

---

## Fontes

(ARRUMAR REFERENCIAS ANTES DA ENTREGA)


2. [Template Jornada do Usuário (Miro)](https://miro.com/app/board/uXjVOi3EFh4=/?share_link_id=503534748467)
3. *[Dados do parceiro — TAPI, bases M1/M2/M3]*
4. *[Referências adicionais]*

BONILHA, D. Como escrever as melhores User Stories com INVEST - Blog Adaptworks. Disponível em: <https://blog.adapt.works/como-escrever-as-melhores-user-stories-com-invest>. Acesso em: 27 abr. 2026. 

REHKOPF, Max. Histórias de usuários | Exemplos e template. Disponível em: <https://www.atlassian.com/br/agile/project-management/user-stories>.  Acesso em: 27 abr. 2026.

5. [What are Personas- IxDF](https://www.interaction-design.org/literature/topics/personas)
6. [Personas Make Users Memorable - NN/Group](https://www.nngroup.com/articles/persona/)
