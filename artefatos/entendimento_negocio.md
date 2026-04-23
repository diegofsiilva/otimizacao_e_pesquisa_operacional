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

## Referências

[1] PROJECT MANAGEMENT INSTITUTE. *A Guide to the Project Management Body of Knowledge (PMBOK® Guide)*. 7. ed. Newtown Square: Project Management Institute, 2021.

[2] BRASIL. Conselho Monetário Nacional. Resolução CMN nº 4.557, de 23 de fevereiro de 2017. Dispõe sobre a estrutura de gerenciamento de riscos e a estrutura de gerenciamento de capital em instituições financeiras. Brasília: Banco Central do Brasil, 2017. Disponível em: https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Resolução%20CMN&numero=4557. Acesso em: abr. 2026.

[3] BRASIL. Conselho Monetário Nacional. Resolução CMN nº 4.966, de 25 de novembro de 2021. Dispõe sobre os conceitos e os critérios contábeis aplicáveis a instrumentos financeiros e sobre a mensuração das provisões para perdas esperadas associadas ao risco de crédito. Brasília: Banco Central do Brasil, 2021. Disponível em: https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Resolução%20CMN&numero=4966. Acesso em: abr. 2026.