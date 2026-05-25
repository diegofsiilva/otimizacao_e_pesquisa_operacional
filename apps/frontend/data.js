// ─────────────────────────────────────────
//  data.js  –  dados globais + helpers de UI
//  Carregado como <script src> antes dos pages.
//  Usa `var` para expor tudo em window.
// ─────────────────────────────────────────

/* ── Clientes (Dashboard) ─────────────────────────────────── */
var CLIENTS = [
  { id: 'CLI-001', score: 850, status: 'Ativo',    limite: 5000,  cadastro: '14/01/2024' },
  { id: 'CLI-002', score: 620, status: 'Pendente', limite: null,  cadastro: '02/02/2024' },
  { id: 'CLI-003', score: 780, status: 'Ativo',    limite: 3200,  cadastro: '19/01/2024' },
  { id: 'CLI-004', score: 430, status: 'Inativo',  limite: null,  cadastro: '05/03/2024' },
  { id: 'CLI-005', score: 910, status: 'Ativo',    limite: 8500,  cadastro: '22/01/2024' },
  { id: 'CLI-006', score: 540, status: 'Pendente', limite: null,  cadastro: '11/03/2024' },
  { id: 'CLI-007', score: 720, status: 'Ativo',    limite: 2800,  cadastro: '28/02/2024' },
  { id: 'CLI-008', score: 680, status: 'Ativo',    limite: 4100,  cadastro: '07/03/2024' },
];

/* ── Gráficos – Resultados ────────────────────────────────── */
var CLUSTER_LIMITES = [
  { name: 'CLU-1', limite: 250   },
  { name: 'CLU-2', limite: 0     },
  { name: 'CLU-3', limite: 0     },
  { name: 'CLU-4', limite: 0     },
  { name: 'CLU-5', limite: 18500 },
  { name: 'CLU-6', limite: 1600  },
  { name: 'CLU-7', limite: 0     },
];

var STATUS_PIE = [
  { name: 'Ativo',    value: 84, color: '#22c55e' },
  { name: 'Inativo',  value:  6, color: '#f87171' },
  { name: 'Pendente', value: 10, color: '#fbbf24' },
];

var EVOLUCAO = [
  { mes: 'Jan', valor: 8.0  },
  { mes: 'Fev', valor: 9.2  },
  { mes: 'Mar', valor: 10.1 },
  { mes: 'Abr', valor: 11.4 },
  { mes: 'Mai', valor: 13.0 },
  { mes: 'Jun', valor: 15.7 },
];

var SCORE_DIST = [
  { score: '300-400', n: 50  },
  { score: '400-500', n: 120 },
  { score: '500-600', n: 280 },
  { score: '600-700', n: 410 },
  { score: '700-800', n: 260 },
  { score: '800-900', n: 100 },
  { score: '900+',    n:  27 },
];

/* ── Comparação Simplex vs PuLP (resultados reais) ──────────── */
var SOLVER_COMPARISON = {
  simplex: {
    label: 'Simplex (próprio)',
    z: 81240312.34,
    status: 'Ótimo',
    tempo_ms: 142,
    clusters: [
      { id: 'CLU-1', limite: 250   },
      { id: 'CLU-2', limite: 0     },
      { id: 'CLU-3', limite: 0     },
      { id: 'CLU-4', limite: 0     },
      { id: 'CLU-5', limite: 18500 },
      { id: 'CLU-6', limite: 1600  },
      { id: 'CLU-7', limite: 0     },
    ],
  },
  pulp: {
    label: 'PuLP / CBC',
    z: 81240312.70,
    status: 'Ótimo',
    tempo_ms: 310,
    clusters: [
      { id: 'CLU-1', limite: 250   },
      { id: 'CLU-2', limite: 0     },
      { id: 'CLU-3', limite: 0     },
      { id: 'CLU-4', limite: 0     },
      { id: 'CLU-5', limite: 18500 },
      { id: 'CLU-6', limite: 1600  },
      { id: 'CLU-7', limite: 0     },
    ],
  },
  delta_z_pct: 0.0,
  pd_fin_atual: 0.1375,
};

/* ── Parâmetros configuráveis ─────────────────────────────── */
var PARAMS_EDITAVEIS = [
  { key: 't',     label: 'Taxa de interchange',      value: 0.0115, min: 0,    max: 0.05,   step: 0.0001 },
  { key: 'pd',    label: 'Probabilidade de Default', value: 0.05,   min: 0,    max: 0.3,    step: 0.001  },
  { key: 'L_max', label: 'Limite máximo (R$)',       value: 50000,  min: 1000, max: 200000, step: 1000   },
];

var PARAMS_NAO_EDITAVEIS = [
  { label: 'Custo de capital (Ke)',    value: '14,25%' },
  { label: 'Custo de funding (Kd)',    value: '11,50%' },
  { label: 'Taxa de recuperação (RR)', value: '30%'    },
  { label: 'Exposição padrão (EAD)',   value: 'Limite' },
  { label: 'LGD',                      value: '70%'    },
  { label: 'PD financeiro atual',      value: '13,75%' },
];

/* ── Clusters upload (GerarLimites) ──────────────────────── */
var CLUSTERS_UPLOAD = [
  { id: 'CLU-001', limite: 1500,  status: 'viavel' },
  { id: 'CLU-002', limite: 3200,  status: 'viavel' },
  { id: 'CLU-003', limite: null,  status: 'sem'    },
  { id: 'CLU-004', limite: 800,   status: 'viavel' },
  { id: 'CLU-005', limite: null,  status: 'sem'    },
  { id: 'CLU-006', limite: 5000,  status: 'viavel' },
  { id: 'CLU-007', limite: 2100,  status: 'viavel' },
  { id: 'CLU-008', limite: null,  status: 'sem'    },
  { id: 'CLU-009', limite: 4400,  status: 'viavel' },
  { id: 'CLU-010', limite: 900,   status: 'viavel' },
];

/* ── Helpers ─────────────────────────────────────────────── */
var fmt = function(v) {
  return 'R$ ' + Number(v).toLocaleString('pt-BR');
};

var fmtZ = function(v) {
  return 'R$ ' + Number(v).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
};
