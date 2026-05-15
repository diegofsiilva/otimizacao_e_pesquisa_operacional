# Documentação do Protótipo - Modelo de Otimização Linear para Limites de Cartão de Crédito

## 1. Visão Geral

Este projeto desenvolve um Modelo de Otimização Linear para a definição de limites pré-aprovados de cartão de crédito no Banco Pan / BTG Pactual. A iniciativa visa superar as limitações das abordagens empíricas tradicionais, implementando um algoritmo de pesquisa operacional que atua como motor de decisão automatizado. O sistema equilibra o retorno esperado e o risco de inadimplência, processando variáveis simultâneas como perfil do cliente, probabilidade de inadimplência e capacidade de pagamento para calcular o limite ideal a ser ofertado a cada correntista. Os resultados são disponibilizados em linguagem Python, permitindo integração direta aos motores internos de crédito do banco. A interface prototipada serve como uma ferramenta de apoio para cientistas de dados e analistas de estratégia de crédito, permitindo o carregamento de bases, a configuração de parâmetros e metas, a geração de limites segmentados por cluster e a visualização detalhada dos resultados.

## 2. Estrutura da Interface


A interface do Modelo de Otimização Linear foi projetada com foco na clareza, organização e coerência visual, buscando proporcionar uma experiência de usuário intuitiva. A navegação principal é composta por um menu superior que inclui as seções **Dashboard**, **Gerar Limites** e **Resultados**, permitindo um acesso rápido às funcionalidades essenciais da solução. O padrão visual adota uma paleta de cores neutras com destaques em azul e verde para elementos interativos e indicadores de sucesso, respectivamente, mantendo a consistência em todas as telas. A tipografia e a iconografia foram selecionadas para garantir legibilidade e reconhecimento imediato das ações e informações.

## 3. Rascunhos Iniciais


Os Rascunhos iniciais representam a fase de baixa fidelidade do projeto, onde as estruturas básicas das telas foram definidas. Eles serviram como base para o desenvolvimento do protótipo de alta fidelidade, garantindo a coesão entre o planejamento e a implementação visual.


### Rascunho da Home (Dashboard)


![Rascunho da Home](/artefatos/assets/ux/rascunho_home.png)

Este rascunho ilustra a disposição inicial dos elementos na tela principal, focando na apresentação de um resumo de dados e uma tabela de clientes.

### Rascunho de Carregamento de Dados


![Rascunho de Carregamento de Base](/artefatos/assets/ux/rascunho_carregar.png)


Representa a estrutura para a funcionalidade de upload de arquivos, com uma área dedicada para o carregamento da base de dados e uma pré-visualização em formato de tabela.

### Rascunho de Configurações


![Rascunho de Configurações](/artefatos/assets/ux/rascunho_config.png)


Detalha a organização dos parâmetros editáveis e não editáveis, com campos claros para a inserção e visualização de configurações do modelo.

## 4. Protótipo Interativo


O protótipo interativo do Modelo de Otimização Linear visa demonstrar a funcionalidade e a experiência de usuário das principais interações.

* [Protótipo interativo do Figma](https://www.figma.com/design/OC2gQQXzaZVLYfvDv4ixnr/Devedores?node-id=62-2&t=ft6Y4FQXwoefHD2f-1)


#### Objetivos do Protótipo


O protótipo foi desenvolvido para:


*   Validar os fluxos de usabilidade para carregamento de dados, configuração de parâmetros e visualização de resultados.
*   Apresentar a interface de usuário em alta fidelidade, permitindo a avaliação da estética e da organização visual.
*   Simular as interações chave do modelo, como upload de arquivos, edição de configurações e navegação entre dashboards e relatórios.

## 5. Fluxos de Usabilidade


Os fluxos de usabilidade foram definidos com base nas User Stories fornecidas, garantindo que as interações do usuário sejam intuitivas e eficientes para alcançar os objetivos de negócio.


### Fluxo 1 — Carregar Base de Dados e Gerar Limites


**User Stories Relacionadas:**
*   **US01 - Carregar base de dados:** Como cientista de dados, eu quero carregar a base de dados do banco no formato parquet, para utilizar informações corretas e completas na segmentação e otimização de limites por cluster.
*   **US04 - Gerar limite por cluster:** Como analista de estratégia de crédito, eu quero gerar limites sugeridos para cada cluster, para aplicar políticas segmentadas de crédito.


**Passos:**
1.  O usuário navega para a seção "Gerar Limites".
2.  Na tela de "Carregar Base & Gerar Limites", o usuário arrasta e solta um arquivo (ou clica para selecionar) no formato CSV ou XLSX (simulando o parquet).
3.  Após o upload, a interface exibe o nome do arquivo carregado e um resumo dos "Limites Gerados por Cluster", incluindo o total de clusters, quantos possuem solução viável e quantos não.
4.  Uma tabela detalha o "Cluster ID", o "Limite Sugerido" e o "Status" (Solução Viável ou Sem Solução) para cada cluster.


**Telas Envolvidas:**
*   `Gerar limite.png` (Tela inicial de upload)
*   `Visualizar a geração de limites.png` (Tela após o upload e geração dos limites)


**Resultado Esperado:**
O usuário consegue carregar uma base de dados e visualizar os limites de crédito sugeridos para cada cluster, com indicação clara de quais clusters possuem uma solução viável de limite.


### Fluxo 2 — Configurar Parâmetros e Metas


**User Stories Relacionadas:**
*   **US02 - Ajustar clusterização:** Como cientista de dados, eu quero configurar o número de clusters utilizados na segmentação, para testar diferentes cenários de agrupamento dos clientes.
*   **US03 - Configurar metas de produção:** Como analista de estratégia de crédito, eu quero configurar metas de clientes aprovados e volume total de limite, para alinhar a otimização aos objetivos do negócio.


**Passos:**
1.  O usuário acessa a tela de "Configurações" (disponível através de um ícone de engrenagem ou menu).
2.  Na tela de configurações, o usuário visualiza e edita os "Parâmetros Editáveis", como "Taxa de Interchange", "Loss Given Default", "Utilização esperada do Limite" e "Teto máximo de Limite".
3.  Ao clicar no ícone de edição, um modal ou área de edição é apresentada, permitindo ajustar o valor do parâmetro (ex: usando um slider para a Taxa de Interchange).
4.  O usuário salva as alterações ou as cancela.


**Telas Envolvidas:**
*   `tela-config.png` (Tela de configurações)
*   `config-edicao.png` (Modal/área de edição de parâmetro)


**Resultado Esperado:**
O usuário consegue ajustar os parâmetros do modelo de clusterização e definir as metas de produção, impactando diretamente a otimização dos limites de crédito.


### Fluxo 3 — Visualizar e Exportar Resultados


**User Stories Relacionadas:**
*   **US06 - Visualizar distribuição dos limites:** Como analista de estratégia de crédito, eu quero visualizar a distribuição dos limites por cluster, para analisar os resultados e apoiar decisões.
*   **US07 - Exportar resultados:** Como cientista de dados, eu quero exportar os resultados finais da otimização, para integrar a saída com outros sistemas internos.


**Passos:**
1.  O usuário navega para a seção "Resultados".
2.  Na tela "Visualizar Resultados", o usuário encontra um dashboard com KPIs como "Total de Clusters", "Limite Total Aprovado", "Clientes Ativos" e "Taxa de Aprovação".
3.  Gráficos visuais, como "Limites por Cluster", "Distribuição por Status", "Evolução Temporal de Limites" e "Distribuição por Faixa de Score", são apresentados para uma análise aprofundada.
4.  Na tela do Dashboard (Home), o usuário pode utilizar o botão "Exportar" para gerar um arquivo com os resultados finais da otimização.


**Telas Envolvidas:**
*   `resultados.png` (Tela de visualização de resultados)
*   `home.png` (Tela do Dashboard com opção de exportar)


**Resultado Esperado:**
O usuário consegue analisar a distribuição e evolução dos limites de crédito através de visualizações gráficas e exportar os dados otimizados para uso em outros sistemas.


