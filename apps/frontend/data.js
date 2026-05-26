// data.js -- dados globais e helpers de UI
// Usa var para expor tudo em window antes dos componentes de página.

// Clientes (Dashboard)
var CLIENTS = [
  {
    id: "CLI-001",
    score: 850,
    status: "Ativo",
    limite: 5000,
    cadastro: "14/01/2024",
  },
  {
    id: "CLI-002",
    score: 620,
    status: "Pendente",
    limite: null,
    cadastro: "02/02/2024",
  },
  {
    id: "CLI-003",
    score: 780,
    status: "Ativo",
    limite: 3200,
    cadastro: "19/01/2024",
  },
  {
    id: "CLI-004",
    score: 430,
    status: "Inativo",
    limite: null,
    cadastro: "05/03/2024",
  },
  {
    id: "CLI-005",
    score: 910,
    status: "Ativo",
    limite: 8500,
    cadastro: "22/01/2024",
  },
  {
    id: "CLI-006",
    score: 540,
    status: "Pendente",
    limite: null,
    cadastro: "11/03/2024",
  },
  {
    id: "CLI-007",
    score: 720,
    status: "Ativo",
    limite: 2800,
    cadastro: "28/02/2024",
  },
  {
    id: "CLI-008",
    score: 680,
    status: "Ativo",
    limite: 4100,
    cadastro: "07/03/2024",
  },
];

// Limites por cluster para o gráfico de barras
var CLUSTER_LIMITES = [
  { name: "CLU-1", limite: 250 },
  { name: "CLU-2", limite: 0 },
  { name: "CLU-3", limite: 0 },
  { name: "CLU-4", limite: 0 },
  { name: "CLU-5", limite: 18500 },
  { name: "CLU-6", limite: 1600 },
  { name: "CLU-7", limite: 0 },
];

// Distribuição de status para o gráfico de setor (donut)
// Cores da paleta terciária PAN conforme brandbook
var STATUS_PIE = [
  { name: "Ativo", value: 84, color: "#67DE98" },
  { name: "Inativo", value: 6, color: "#FF5D5C" },
  { name: "Pendente", value: 10, color: "#FAE95D" },
];

// Série temporal de limites aprovados para o gráfico de linha
var EVOLUCAO = [
  { mes: "Jan", valor: 8.0 },
  { mes: "Fev", valor: 9.2 },
  { mes: "Mar", valor: 10.1 },
  { mes: "Abr", valor: 11.4 },
  { mes: "Mai", valor: 13.0 },
  { mes: "Jun", valor: 15.7 },
];

// Histograma de distribuição de scores
var SCORE_DIST = [
  { score: "300-400", n: 50 },
  { score: "400-500", n: 120 },
  { score: "500-600", n: 280 },
  { score: "600-700", n: 410 },
  { score: "700-800", n: 260 },
  { score: "800-900", n: 100 },
  { score: "900+", n: 27 },
];

// Comparação entre o solver próprio (Simplex) e o PuLP/CBC
var SOLVER_COMPARISON = {
  simplex: {
    label: "Simplex (próprio)",
    z: 81240312.34,
    status: "Ótimo",
    tempo_ms: 142,
    clusters: [
      { id: "CLU-1", limite: 250 },
      { id: "CLU-2", limite: 0 },
      { id: "CLU-3", limite: 0 },
      { id: "CLU-4", limite: 0 },
      { id: "CLU-5", limite: 18500 },
      { id: "CLU-6", limite: 1600 },
      { id: "CLU-7", limite: 0 },
    ],
  },
  pulp: {
    label: "PuLP / CBC",
    z: 81240312.7,
    status: "Ótimo",
    tempo_ms: 310,
    clusters: [
      { id: "CLU-1", limite: 250 },
      { id: "CLU-2", limite: 0 },
      { id: "CLU-3", limite: 0 },
      { id: "CLU-4", limite: 0 },
      { id: "CLU-5", limite: 18500 },
      { id: "CLU-6", limite: 1600 },
      { id: "CLU-7", limite: 0 },
    ],
  },
  delta_z_pct: 0.0,
  pd_fin_atual: 0.1375,
};

// Parâmetros que o usuário pode ajustar no modal de configurações
var PARAMS_EDITAVEIS = [
  {
    key: "t",
    label: "Taxa de interchange",
    value: 0.0175,
    min: 0.3,
    max: 1.0,
    step: 0.01,
  },
  {
    key: "LGD",
    label: "Loss Given Default (LGD)",
    value: 0.6,
    min: 0.3,
    max: 1.0,
    step: 0.01,
  },
  {
    key: "u_bar",
    label: "Utilização esperada do limite",
    value: 0.75,
    min: 0.3,
    max: 1.0,
    step: 0.01,
  },
  {
    key: "L_max",
    label: "Limite máximo (R$)",
    value: 25000,
    min: 10000,
    max: 50000,
    step: 500,
  },
];

// Parâmetros fixos exibidos no modal (somente leitura)
var PARAMS_NAO_EDITAVEIS = [
  { label: "Custo de capital (Ke)", value: "14,25%" },
  { label: "Custo de funding (Kd)", value: "11,50%" },
  { label: "Taxa de recuperação (RR)", value: "30%" },
  { label: "Exposição padrão (EAD)", value: "Limite" },
  { label: "LGD", value: "70%" },
  { label: "PD financeiro atual", value: "13,75%" },
];

// Resultado simulado após upload de CSV (GerarLimites)
var CLUSTERS_UPLOAD = [
  { id: "CLU-001", limite: 1500, status: "viavel" },
  { id: "CLU-002", limite: 3200, status: "viavel" },
  { id: "CLU-003", limite: null, status: "sem" },
  { id: "CLU-004", limite: 800, status: "viavel" },
  { id: "CLU-005", limite: null, status: "sem" },
  { id: "CLU-006", limite: 5000, status: "viavel" },
  { id: "CLU-007", limite: 2100, status: "viavel" },
  { id: "CLU-008", limite: null, status: "sem" },
  { id: "CLU-009", limite: 4400, status: "viavel" },
  { id: "CLU-010", limite: 900, status: "viavel" },
];

// Formata valor monetário simples
var fmt = function (v) {
  return "R$ " + Number(v).toLocaleString("pt-BR");
};

// Formata valor monetário com duas casas decimais
var fmtZ = function (v) {
  return (
    "R$ " +
    Number(v).toLocaleString("pt-BR", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })
  );
};
