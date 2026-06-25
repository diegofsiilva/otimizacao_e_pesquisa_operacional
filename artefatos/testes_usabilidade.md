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

## 7. Registro dos Resultados
 
Os resultados detalhados dos testes, incluindo participantes, ocorrências identificadas, severidade dos problemas, estimativas de correção e priorização das melhorias, foram registrados na planilha de tabulação da equipe.
 
**Link da planilha de resultados:** [https://docs.google.com/spreadsheets/d/1IxDAuojgarxuJwVwt3IJXnsd-jvfqeaGgoswVQHKZEE/edit?gid=0#gid=0](https://docs.google.com/spreadsheets/d/1OcvbRqZd_wAdPkaLY5pUgVpFc1TuJq7nZ97pXq-oThE/edit?gid=0#gid=0
)
 
---
 
### Contribuição dos Testes para o Projeto
 
Os testes de usabilidade foram fundamentais para validar se o Sistema de Crédito Banco PAN atende às necessidades reais dos seus usuários em um contexto próximo ao de produção. Ao colocar analistas e gestores de crédito diretamente em contato com a aplicação, foi possível observar comportamentos, dúvidas e percepções que não surgiriam em revisões internas da equipe de desenvolvimento.
 
A principal contribuição dos testes foi revelar a distância entre o modelo mental dos usuários e a lógica de navegação adotada pelo sistema. Em vários momentos, participantes demonstraram expectativas diferentes sobre como as funcionalidades deveriam estar organizadas — por exemplo, a confusão recorrente entre as seções "Clientes" e "Gerar Limites", ou a dificuldade em distinguir as responsabilidades das telas de Resultados e Cockpit. Esse tipo de achado só se torna visível quando o sistema é testado com usuários reais.
 
Além disso, os testes confirmaram que o fluxo principal da aplicação — da criação da consulta até a exportação dos resultados — é executável sem grandes bloqueios, o que representa uma validação importante do núcleo funcional da solução.
 
---
 
### O Que Era Esperado
 
Antes da realização dos testes, a equipe esperava que:
 
* Os usuários conseguissem completar as tarefas principais sem auxílio, dado que o fluxo foi projetado para ser linear e progressivo;
* Possíveis dificuldades estivessem concentradas na interpretação dos parâmetros do modelo (por envolverem conceitos técnicos como LGD e Interchange) e na leitura dos gráficos de resultado;
* A nomenclatura das telas pudesse gerar alguma ambiguidade, especialmente para usuários com menor familiaridade com o processo de otimização de crédito;
* O Cockpit pudesse ser percebido como redundante ou de difícil interpretação sem contexto prévio.
De modo geral, as expectativas se confirmaram: o fluxo principal mostrou-se funcional e acessível, mas os pontos de atrito previstos — nomenclatura, interpretação técnica e distinção entre telas — de fato se manifestaram durante os testes, oferecendo insumos concretos para melhorias.
 
---
 
### Resultados por Etapa
 
#### Etapa 1 – Exploração Inicial
 
**O que era esperado:** Que os participantes conseguissem identificar o propósito geral da aplicação com base na interface, sem instruções detalhadas.
 
**O que foi observado:** A maioria dos participantes compreendeu que se tratava de um sistema de análise de crédito, mas o significado e a distinção entre as seções "Clientes" e "Gerar Limites" não foi imediatamente claro. Um participante relatou que esperaria primeiro carregar os clientes e só depois gerar limites — sugerindo que a nomenclatura induz a um modelo mental de dois passos independentes, quando na prática o fluxo é integrado. A sugestão de renomear para algo como "Carregar e Gerar" foi registrada como oportunidade de melhoria.
 
---
 
#### Etapa 2 – Localização de Consulta
 
**O que era esperado:** Que os participantes localizassem uma consulta previamente executada utilizando a tela de histórico ou filtros disponíveis, em até 2 minutos.
 
**O que foi observado:** A maior parte dos participantes conseguiu localizar consultas anteriores sem grande dificuldade. O principal atrito registrado foi a dúvida inicial sobre em qual seção do sistema as consultas ficavam armazenadas — alguns participantes navegaram para a seção "Clientes" antes de encontrar o caminho correto. Após a primeira interação, o fluxo foi considerado compreensível.
 
---
 
#### Etapa 3 – Criação de Nova Consulta e Upload
 
**O que era esperado:** Que os usuários realizassem o upload de um arquivo `.parquet` e iniciassem a otimização sem auxílio, compreendendo as mensagens exibidas pelo sistema.
 
**O que foi observado:** Todos os participantes concluíram a tarefa com sucesso. A área de upload por arrastar e soltar foi identificada rapidamente. Dois pontos de melhoria foram levantados de forma recorrente: a ausência de documentação resumida sobre as colunas obrigatórias do arquivo próxima à área de upload, e a falta de visibilidade dos parâmetros do modelo antes do início da execução. O redirecionamento automático para a tela de resultados após a conclusão foi bem avaliado pela maioria.
 
---
 
#### Etapa 4 – Configuração dos Parâmetros do Modelo
 
**O que era esperado:** Que os participantes localizassem o modal de configuração, compreendessem a finalidade geral dos parâmetros e salvassem as alterações corretamente.
 
**O que foi observado:** Esta etapa concentrou o maior volume de dúvidas conceituais. Parâmetros como LGD (Loss Given Default), Taxa de Interchange e Utilização Esperada geraram questionamentos mesmo entre participantes com experiência em análise de dados financeiros. A ausência de descrições ou tooltips explicativos para cada campo foi apontada como lacuna relevante. Os participantes conseguiram salvar os parâmetros, mas frequentemente sem plena compreensão do impacto de cada valor configurado.
 
---
 
#### Etapa 5 – Acompanhamento da Execução
 
**O que era esperado:** Que os participantes identificassem o status do processamento em tempo real e reconhecessem a conclusão da execução sem ambiguidade.
 
**O que foi observado:** O acompanhamento do processamento foi bem compreendido. Os indicadores de status e a barra de progresso foram considerados informativos. Não houve registros de confusão sobre o estado atual da execução. O feedback automático ao término foi bem avaliado, com participantes relatando que o sistema comunicou a conclusão de forma clara.
 
---
 
#### Etapa 6 – Interpretação dos Resultados
 
**O que era esperado:** Que os participantes identificassem os limites gerados por cluster, compreendessem os indicadores apresentados e fossem capazes de comunicar os resultados a um gestor.
 
**O que foi observado:** Esta foi a etapa com maior variação de desempenho entre os participantes. Alguns conseguiram interpretar rapidamente os indicadores e os limites por cluster, enquanto outros precisaram navegar entre Resultados e Cockpit para montar uma visão completa — evidenciando sobreposição de informações entre as duas telas. Um participante apontou que alguns gráficos têm caráter excessivamente técnico para perfis menos analíticos. Houve também um relato de que os números apresentados pareceram inconsistentes, levantando a hipótese de problema na base de dados de demonstração. A sugestão de posicionar parâmetros e premissas da execução em área mais visível foi recorrente.
 
---
 
#### Etapa 7 – Exportação dos Resultados
 
**O que era esperado:** Que os participantes localizassem o botão de exportação, realizassem o download sem auxílio e confirmassem que o arquivo gerado era o esperado.
 
**O que foi observado:** A exportação foi a tarefa com maior taxa de sucesso e menor atrito. Todos os participantes concluíram a operação sem dificuldades relevantes. O único ponto de atenção foi a dúvida de um participante sobre a diferença entre "exportar clientes" e "exportar resultados da otimização", sugerindo que a nomenclatura dos botões de exportação poderia ser mais descritiva.
 
---
 
#### Etapa 8 – Análise do Cockpit
 
**O que era esperado:** Que os participantes acessassem o Cockpit, compreendessem os KPIs apresentados e identificassem execuções recentes com seus respectivos status.
 
**O que foi observado:** O acesso ao Cockpit foi realizado sem dificuldades por todos os participantes. Os indicadores da parte superior foram considerados úteis para uma visão rápida. No entanto, dois problemas recorrentes foram identificados: a falta de descrições adicionais para alguns campos técnicos, e a ausência de indicadores como o total de limite ofertado e comparações entre execuções distintas. Um participante questionou a presença de informações relacionadas ao fluxo interno da pipeline na tela, sugerindo que esses dados sejam mantidos apenas para uso técnico e removidos da interface operacional. A distinção de responsabilidades entre a tela de Resultados e o Cockpit também foi apontada como ponto de confusão recorrente.

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
