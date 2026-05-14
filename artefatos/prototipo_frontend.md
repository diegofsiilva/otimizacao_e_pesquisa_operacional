# Documentação do Protótipo — Sistema de Otimização de Limites de Crédito

# 1. Visão Geral da Solução

O presente protótipo foi desenvolvido com o objetivo de representar visualmente a solução proposta para o processo de definição de limites pré-aprovados de crédito do Banco PAN. A proposta busca transformar um fluxo atualmente complexo, técnico e parcialmente manual em uma experiência mais estruturada, rastreável e orientada por dados.

A solução tem como foco principal apoiar o time de Estratégia de Crédito na análise e definição de políticas segmentadas de concessão de limites, utilizando técnicas de clusterização e otimização matemática. Além disso, o sistema também atende às necessidades do time de Data Science, responsável pela preparação dos dados, parametrização técnica e manutenção do modelo.

O protótipo foi construído considerando as User Stories mapeadas durante as etapas anteriores do projeto, bem como os problemas identificados nas personas e jornadas de usuário. Dessa forma, cada fluxo presente nas telas busca resolver dores reais relacionadas à falta de transparência, dificuldade de simulação de cenários, dependência técnica e baixa explicabilidade das decisões.

As telas foram organizadas de maneira sequencial e lógica, refletindo o fluxo operacional esperado dentro do contexto do banco:

1. Carregamento da base de dados;
2. Configuração dos parâmetros do modelo;
3. Execução da otimização;
4. Visualização e análise dos resultados.

O protótipo foi desenvolvido em média fidelidade, priorizando clareza visual, organização das informações e consistência entre os componentes da interface.

---

# 2. Estrutura Geral da Interface

A interface foi planejada para manter consistência visual e facilidade de navegação ao longo de todo o sistema. Todas as telas seguem o mesmo padrão estrutural, permitindo que o usuário compreenda rapidamente a organização do produto e consiga executar tarefas sem necessidade de treinamento complexo.

A navegação principal ocorre através de um menu lateral representado pelo ícone “hambúrguer”, localizado no canto superior esquerdo. Esse padrão foi escolhido por ser amplamente reconhecido em aplicações modernas e permitir expansão futura do sistema sem comprometer o espaço útil da interface.

Além disso, todas as telas apresentam:
- título principal da funcionalidade;
- divisão visual clara entre seções;
- alinhamento consistente dos componentes;
- tipografia padronizada;
- uso de cartões e tabelas para organização dos dados;
- acesso rápido às configurações pelo ícone inferior.

A identidade visual minimalista foi adotada para priorizar legibilidade e interpretação rápida dos dados, aspecto importante considerando o contexto corporativo e analítico da solução.

---

# 3. Wireframe — Carregar Base de Dados


## 3.1 Objetivo da Tela

A tela de carregamento de base de dados representa o primeiro passo operacional da solução. Seu principal objetivo é permitir que o usuário importe a base de clientes elegíveis utilizada no processo de clusterização e otimização dos limites de crédito.

Essa funcionalidade está diretamente relacionada à User Story US01 — “Carregar base de dados”, cujo foco é garantir que o modelo utilize informações corretas, padronizadas e completas.

O principal usuário dessa funcionalidade é o time de Data Science, responsável pela preparação e validação técnica das informações utilizadas no modelo.

<div align="center">Figura 1: Tela Carregar Base de Dados</div>
<div align="center">
  <img src="assets/tela_Carregar_bade_de_dados.png">
</div>
<div align="center">Fonte: Material produzido pelos autores</div>

## 3.2 Estrutura da Tela

A interface foi dividida em duas áreas principais:
- área de upload;
- visualização da tabela carregada.

Essa separação foi pensada para tornar o processo mais intuitivo e permitir validação rápida dos dados após a importação.

---

## 3.3 Área de Upload

A área de upload ocupa posição de destaque na tela, permitindo que o usuário compreenda imediatamente a principal ação esperada naquele contexto.

O componente foi desenhado em formato de grande caixa central com ícone de upload, reforçando visualmente a ação de importação de arquivos.

### Objetivos da funcionalidade
- Receber o arquivo contendo os dados dos clientes;
- Validar a estrutura da base;
- Garantir compatibilidade com o modelo;
- Evitar erros de processamento posteriores.

### Regras de negócio previstas
- Aceitação apenas de arquivos `.parquet`;
- Verificação automática das colunas obrigatórias;
- Validação da integridade da estrutura;
- Tratamento de arquivos corrompidos;
- Exibição de mensagens de erro claras ao usuário.

Além disso, a funcionalidade foi projetada considerando grandes volumes de dados, já que a base operacional do banco pode conter aproximadamente 1,8 milhão de registros elegíveis.

---

## 3.4 Visualização da Tabela

Após o carregamento do arquivo, o sistema apresenta uma tabela contendo amostras da base importada.

Essa funcionalidade possui papel importante na experiência do usuário, pois reduz insegurança operacional e permite validação visual rápida antes da execução do modelo.

A tabela foi desenhada de maneira simplificada, priorizando:
- organização visual;
- leitura rápida;
- navegação eficiente.

Também foi adicionada paginação inferior para facilitar exploração de grandes conjuntos de dados sem comprometer desempenho ou poluição visual.

---

## 3.5 Fluxo de Usabilidade — Upload da Base

### User Story Relacionada
US01 — Carregar base de dados.

### Fluxo principal

```text
Usuário acessa a tela
        ↓
Seleciona arquivo parquet
        ↓
Sistema valida estrutura
        ↓
Sistema processa upload
        ↓
Tabela é exibida
```

Resultado esperado

A base fica disponível para utilização no processo de clusterização e otimização.

# 4. Wireframe — Configurações
## 4.1 Objetivo da Tela

A tela de configurações foi projetada para permitir parametrização do modelo matemático sem necessidade de alteração direta no código.

Seu principal objetivo é oferecer autonomia ao time de Estratégia de Crédito para testar cenários diferentes de negócio, simulando alterações nas restrições e metas utilizadas pela otimização.

Essa funcionalidade se relaciona principalmente às User Stories:

US02 — Ajustar clusterização;
US03 — Configurar metas de produção.

<div align="center">Figura 1: Tela de Configuração</div>
<div align="center">
  <img src="assets/tela_config.png">
</div>
<div align="center">Fonte: Material produzido pelos autores</div>

## 4.2 Organização da Tela

A interface foi dividida em dois grandes grupos:

parâmetros editáveis;
parâmetros não editáveis.

Essa divisão foi criada para separar informações operacionais das variáveis estruturais do modelo.

##4.3 Parâmetros Editáveis

Os parâmetros editáveis representam variáveis que podem ser alteradas conforme as necessidades estratégicas do negócio.

Cada item foi apresentado em formato de cartão individual contendo:

nome do parâmetro;
valor atual;
ícone de edição.

Esse formato melhora a identificação rápida das configurações e facilita futuras expansões do sistema.

## 4.4 Taxa de Interchange

Esse parâmetro representa a taxa de receita obtida nas transações realizadas com cartão.

Sua configuração impacta diretamente a função objetivo do modelo, influenciando:

rentabilidade;
receita esperada;
retorno financeiro da carteira.
## 4.5 Loss Given Default (LGD)

O LGD representa a perda esperada em caso de inadimplência.

Esse parâmetro possui impacto importante na avaliação de risco da carteira e é utilizado no balanceamento entre crescimento e segurança operacional.

Sua presença explícita na interface aumenta transparência e governança do modelo.

## 4.6 Utilização Esperada do Limite

Representa o percentual médio esperado de utilização do limite concedido.

Esse valor influencia diretamente:

receita projetada;
exposição financeira;
capacidade operacional da carteira.
## 4.7 Teto Máximo de Limite

Define o valor máximo permitido para os limites sugeridos pelo modelo.

Essa restrição existe para garantir aderência às políticas internas do banco e evitar exposição excessiva em determinados clusters.

## 4.8 Parâmetros Não Editáveis

Os parâmetros não editáveis foram incluídos com objetivo de ampliar transparência e rastreabilidade do sistema.

Mesmo não sendo alteráveis pela interface, sua exibição ajuda:

auditoria;
entendimento técnico;
interpretação das decisões;
governança do modelo.

## 4.9 Fluxo de Usabilidade — Configuração do Modelo
User Stories Relacionadas
US02;
US03.
Fluxo principal
Usuário acessa configurações
        ↓
Seleciona parâmetro
        ↓
Edita valor desejado
        ↓
Sistema valida informação
        ↓
Parâmetro é salvo
Resultado esperado

O modelo passa a utilizar os novos parâmetros definidos pelo usuário.

# 5. Wireframe — Visualizar Resultados
## 5.1 Objetivo da Tela

A tela de resultados representa o principal ponto de apoio à tomada de decisão dentro da solução.

Seu objetivo é apresentar os limites sugeridos pelo solver de otimização para cada cluster ativo, permitindo análise rápida dos resultados e identificação de possíveis inconsistências.

Essa funcionalidade se relaciona diretamente às User Stories:

US04 — Gerar limite por cluster;
US06 — Visualizar distribuição dos limites.

<div align="center">Figura 1: Tela Carregar Base de Dados</div>
<div align="center">
  <img src="assets/tela_resultados.png">
</div>
<div align="center">Fonte: Material produzido pelos autores</div>

## 5.2 Estrutura da Tela

A tela foi organizada em:

área informativa;
botão de execução;
tabela de resultados.

Essa organização busca orientar o usuário de maneira natural:

entender o funcionamento;
executar a otimização;
interpretar os resultados.
## 5.3 Área Informativa

O cartão superior possui papel explicativo e contextual.

Seu objetivo é reforçar:

regras de negócio;
restrições aplicadas;
funcionamento geral da geração de limites.

Essa abordagem contribui para:

redução de ambiguidades;
maior confiança na solução;
melhor experiência de uso.
## 5.4 Geração dos Limites

O botão “Gerar Limite” representa a principal ação da tela.

Ao ser acionado, o sistema executa:

processamento do modelo;
aplicação das restrições;
validação das regras;
cálculo dos limites finais.

O fluxo foi pensado para transmitir simplicidade operacional mesmo tratando de um processo matematicamente complexo.

## 5.5 Tabela de Resultados

A tabela apresenta:

identificador do cluster;
limite sugerido;
status da solução.

Os resultados foram organizados em formato tabular por serem mais adequados ao contexto analítico do sistema.

Além disso, a coluna de status melhora a explicabilidade do modelo, permitindo identificar clusters:

com solução viável;
sem solução possível.
5.6 Status das Soluções
Solução Viável

Indica que o solver encontrou um limite compatível com todas as restrições definidas.

Sem Solução

Indica que o conjunto de restrições impossibilitou geração válida para aquele cluster.

Essa distinção é importante para análise operacional e revisão das políticas aplicadas.

## 5.7 Fluxo de Usabilidade — Geração de Limites
User Stories Relacionadas
US04;
US06.
Fluxo principal
Usuário acessa resultados
        ↓
Clica em “Gerar Limite”
        ↓
Sistema executa otimização
        ↓
Resultados são processados
        ↓
Tabela é exibida
Resultado esperado

O usuário consegue analisar os limites sugeridos e tomar decisões estratégicas com apoio do modelo.

## 6. Relação entre Wireframes e User Stories
Wireframe	User Stories Relacionadas
Carregar Base de Dados	US01
Configurações	US02, US03
Visualizar Resultados	US04, US06
## 7. Considerações de UX

O desenvolvimento das telas buscou seguir princípios básicos de usabilidade e boas práticas de experiência do usuário.

Entre os principais aspectos considerados estão:

consistência visual;
clareza das ações;
organização hierárquica das informações;
feedback visual;
redução de complexidade;
facilidade de navegação.

Além disso, a solução evita violações graves das Heurísticas de Nielsen, especialmente:

visibilidade do status do sistema;
consistência e padrões;
reconhecimento em vez de memorização;
controle do usuário;
prevenção de erros.
8. Conclusão

Os wireframes e o protótipo desenvolvidos representam os principais fluxos operacionais da solução de otimização de limites de crédito proposta para o Banco PAN.

A interface foi construída buscando equilibrar:

simplicidade de uso;
clareza visual;
governança;
transparência;
apoio à tomada de decisão.

Os fluxos apresentados permitem compreender como o sistema poderá ser utilizado pelos times de Estratégia de Crédito e Data Science, demonstrando aderência às User Stories mapeadas e às necessidades identificadas durante o processo de levantamento de requisitos.