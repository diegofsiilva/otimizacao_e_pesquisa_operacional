# Testes de Usabilidade

## 1. Introdução

Os testes de usabilidade têm como objetivo validar se os usuários conseguem utilizar o Sistema de Crédito Banco PAN de forma eficiente, intuitiva e compatível com suas necessidades de negócio.

A avaliação foi planejada para reproduzir atividades reais realizadas por analistas e gestores de crédito durante o processo de geração de limites pré-aprovados. Os testes permitem identificar dificuldades de navegação, problemas de compreensão da interface e oportunidades de melhoria na experiência do usuário.

### Objetivos dos Testes

* Validar a facilidade de navegação da aplicação;
* Verificar a compreensão dos parâmetros de configuração do modelo;
* Avaliar a clareza dos resultados gerados pela otimização;
* Identificar dificuldades na execução das tarefas principais;
* Coletar feedback qualitativo dos participantes;
* Levantar oportunidades de melhoria para futuras versões do sistema.

---

## 2. Participantes

Os testes serão realizados com, no mínimo, 10 participantes compatíveis com as personas identificadas durante as etapas de UX e entendimento de negócio.

### Perfis dos Participantes

| Perfil                                                       | Quantidade Mínima |
| ------------------------------------------------------------ | ----------------- |
| Analista de Crédito                                          | 6                 |
| Gestor/Supervisor de Crédito                                 | 2                 |
| Profissional com experiência em análise de dados financeiros | 2                 |

### Consentimento dos Participantes

Os termos de consentimento assinados pelos participantes encontram-se armazenados em pasta específica no Google Drive da equipe, conforme orientação da disciplina.

**Link da pasta de consentimentos:**

---

## 3. Ambiente de Teste

Os testes serão conduzidos individualmente em ambiente controlado.

### Configuração

* Aplicação executada localmente;
* Navegador Google Chrome;
* Base de dados de demonstração fornecida pela equipe;
* Sessão moderada por um membro da equipe;
* Duração média entre 30 e 45 minutos por participante.

---

## 4. Cenário de Negócio

O participante assume o papel de um Analista de Crédito do Banco PAN.

Uma nova safra de clientes foi recebida e precisa ser processada para gerar limites de crédito otimizados. O participante deverá utilizar a aplicação para realizar todas as etapas do processo, desde o carregamento da base até a análise dos resultados e exportação dos dados.

---

## 5. Tarefas Avaliadas

### Tarefa 1 – Localizar uma Consulta Existente

**Objetivo:** Encontrar uma consulta previamente executada.

**Critérios de Sucesso:**

* Localiza a consulta em até 2 minutos;
* Utiliza filtros ou busca corretamente;
* Compreende os status apresentados.

**Funcionalidades Avaliadas:**

* Tela Clientes;
* Busca de consultas;
* Filtros;
* Histórico.

---

### Tarefa 2 – Criar uma Nova Consulta

**Objetivo:** Realizar o upload de uma nova base de clientes.

**Critérios de Sucesso:**

* Seleciona corretamente um arquivo `.parquet`;
* Inicia a consulta sem auxílio;
* Compreende as mensagens exibidas pelo sistema.

**Funcionalidades Avaliadas:**

* Upload de arquivo;
* Criação de consulta;
* Validação de formato.

---

### Tarefa 3 – Configurar os Parâmetros do Modelo

**Objetivo:** Revisar e ajustar os parâmetros da otimização.

**Parâmetros Avaliados:**

* Taxa de Interchange (`t`);
* Loss Given Default (`LGD`);
* Utilização Esperada (`u_bar`);
* Limite Máximo (`L_max`);
* Horizonte Temporal (`T`).

**Critérios de Sucesso:**

* Localiza a configuração;
* Compreende a finalidade geral dos parâmetros;
* Salva as alterações corretamente.

**Funcionalidades Avaliadas:**

* Modal de Configuração;
* Validações de entrada;
* Salvamento de parâmetros.

---

### Tarefa 4 – Acompanhar o Processamento

**Objetivo:** Monitorar a execução da otimização.

**Critérios de Sucesso:**

* Entende que o sistema está processando;
* Consegue identificar o status atual;
* Reconhece quando o processamento foi concluído.

**Funcionalidades Avaliadas:**

* Barra de progresso;
* Indicadores de status;
* Atualizações automáticas.

---

### Tarefa 5 – Interpretar os Resultados

**Objetivo:** Avaliar os resultados gerados pelo algoritmo.

**Critérios de Sucesso:**

* Identifica os limites gerados para cada cluster;
* Compreende o valor ótimo obtido;
* Interpreta corretamente os gráficos e indicadores.

**Funcionalidades Avaliadas:**

* Tela de Resultados;
* Tabelas;
* Gráficos;
* Indicadores da otimização.

---

### Tarefa 6 – Exportar os Resultados

**Objetivo:** Baixar os resultados gerados para compartilhamento.

**Critérios de Sucesso:**

* Localiza o botão de exportação;
* Conclui o download sem auxílio;
* Confirma que o arquivo foi gerado corretamente.

**Funcionalidades Avaliadas:**

* Exportação CSV;
* Download dos resultados.

---

### Tarefa 7 – Consultar Indicadores Operacionais

**Objetivo:** Utilizar o Cockpit para analisar o desempenho das execuções.

**Critérios de Sucesso:**

* Localiza os indicadores principais;
* Compreende os KPIs apresentados;
* Identifica execuções recentes e seus status.

**Funcionalidades Avaliadas:**

* Cockpit;
* KPIs operacionais;
* Histórico de consultas.

---

## 6. Roteiro do Teste de Usabilidade

### Instruções ao Participante

Obrigado por participar deste teste.

Estamos avaliando a aplicação, e não o participante. Não existem respostas certas ou erradas.

Durante o teste, pedimos que você verbalize seus pensamentos, dúvidas e percepções sempre que possível.

---

### Etapa 1 – Exploração Inicial

**Tarefa:**

"Observe a aplicação e descreva o que você acredita que ela faz."

**Registrar:**

* Primeira impressão;
* Clareza da navegação;
* Comentários espontâneos.

---

### Etapa 2 – Localização de Consulta

**Tarefa:**

"Encontre uma consulta já realizada anteriormente."

**Registrar:**

* Tempo gasto;
* Número de cliques;
* Dificuldades encontradas;
* Comentários do participante.

---

### Etapa 3 – Nova Consulta

**Tarefa:**

"Você recebeu uma nova base de clientes. Faça o upload e inicie uma nova análise."

**Registrar:**

* Dificuldades durante o upload;
* Entendimento das mensagens;
* Erros cometidos.

---

### Etapa 4 – Configuração do Modelo

**Tarefa:**

"Revise os parâmetros disponíveis antes da execução."

**Perguntas ao participante:**

* O que você acredita que cada parâmetro representa?
* Alguma informação está faltando?
* Algum campo gerou dúvida?

**Registrar:**

* Dúvidas levantadas;
* Necessidade de auxílio;
* Comentários espontâneos.

---

### Etapa 5 – Acompanhamento da Execução

**Tarefa:**

"Acompanhe o processamento até sua conclusão."

**Registrar:**

* Clareza dos status;
* Entendimento do progresso;
* Percepção sobre o tempo de espera.

---

### Etapa 6 – Interpretação dos Resultados

**Tarefa:**

"Analise os resultados e explique o que você apresentaria para um gestor."

**Perguntas:**

* Quais clusters receberam maiores limites?
* O resultado parece confiável?
* O que os gráficos indicam?

**Registrar:**

* Acertos de interpretação;
* Dificuldades encontradas;
* Comentários espontâneos.

---

### Etapa 7 – Exportação

**Tarefa:**

"Exporte os resultados para compartilhamento."

**Registrar:**

* Facilidade de localização;
* Tempo necessário;
* Sucesso da operação.

---

### Etapa 8 – Análise do Cockpit

**Tarefa:**

"Utilize o Cockpit para entender o histórico e os indicadores da operação."

**Registrar:**

* Interpretação dos KPIs;
* Clareza das métricas;
* Sugestões de melhoria.

---

## 7. Registro dos Resultados

Os resultados detalhados dos testes, incluindo participantes, ocorrências identificadas, severidade dos problemas, estimativas de correção e priorização das melhorias, serão registrados na planilha de tabulação da equipe.

**Link da planilha de resultados:**

> INSERIR LINK DA PLANILHA

---

## 8. Reflexões e Melhorias Identificadas

Após a conclusão dos testes, esta seção será preenchida com:

* Principais dificuldades observadas;
* Funcionalidades bem avaliadas;
* Problemas recorrentes;
* Melhorias priorizadas;
* Evidências de validação da solução junto aos usuários.

As melhorias serão classificadas segundo:

* Gravidade;
* Impacto para o usuário;
* Esforço de implementação;
* Prioridade de execução.
