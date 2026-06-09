// data.js -- helpers de formatação e metadados de UI.
// Dados de negócio (clusters, clientes, consultas) vêm da API via api.js.

// -------------------------------------------------------------------------
// Formatação monetária
// -------------------------------------------------------------------------

// Formata um número inteiro como moeda brasileira sem casas decimais.
// Ex: 4500 → "R$ 4.500"
var fmt = function (v) {
  return "R$ " + Number(v).toLocaleString("pt-BR");
};

// Formata um número como moeda brasileira com duas casas decimais.
// Ex: 34182456.78 → "R$ 34.182.456,78"
var fmtZ = function (v) {
  return (
    "R$ " +
    Number(v).toLocaleString("pt-BR", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })
  );
};

// -------------------------------------------------------------------------
// Metadados de UI - parâmetros editáveis do modelo
//
// Os *valores* reais vêm sempre de GET /api/config.
// Estes metadados definem apenas como o formulário se comporta:
// label em português, limites e passo do slider.
// O campo `value` aqui é somente o fallback exibido antes da API responder.
// -------------------------------------------------------------------------

var PARAMS_EDITAVEIS = [
  {
    key: "t",
    label: "Taxa de interchange",
    value: 0.0175,
    min: 0.005,
    max: 0.05,
    step: 0.0005,
  },
  {
    key: "LGD",
    label: "Loss Given Default (LGD)",
    value: 0.8,
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
    label: "Limite máximo por cluster (R$)",
    value: 25000,
    min: 5000,
    max: 50000,
    step: 500,
  },
  {
    key: "T",
    label: "Horizonte de uso do limite (meses)",
    value: 15,
    min: 6,
    max: 60,
    step: 1,
  },
];

// -------------------------------------------------------------------------
// Metadados de UI - parâmetros exibidos como somente leitura no ConfigModal
// -------------------------------------------------------------------------

var PARAMS_NAO_EDITAVEIS = [
  { label: "Custo de capital (Ke)", value: "14,25%" },
  { label: "Custo de funding (Kd)", value: "11,50%" },
  { label: "Taxa de recuperação (RR)", value: "30%" },
  { label: "Exposição padrão (EAD)", value: "Limite" },
  { label: "PD financeiro atual", value: "13,75%" },
];
