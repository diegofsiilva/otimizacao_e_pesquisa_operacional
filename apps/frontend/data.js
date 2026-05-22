// ─────────────────────────────────────────
//  data.js  –  dados globais + helpers de UI
//  Carregado como type="text/babel" antes das páginas.
//  Usa `var` para que cada símbolo vire global (window.X).
// ─────────────────────────────────────────

/* ── Dados ── */
var CLIENTS = [
  { id:'CLI-001', score:850, status:'Ativo',      limite:5000,  cadastro:'14/01/2024' },
  { id:'CLI-002', score:720, status:'Ativo',      limite:3500,  cadastro:'19/02/2024' },
  { id:'CLI-003', score:620, status:'Em Análise', limite:null,  cadastro:'09/03/2024' },
  { id:'CLI-004', score:910, status:'Ativo',      limite:12500, cadastro:'04/11/2023' },
  { id:'CLI-005', score:780, status:'Ativo',      limite:8000,  cadastro:'27/01/2024' },
  { id:'CLI-006', score:450, status:'Inativo',    limite:null,  cadastro:'11/08/2023' },
  { id:'CLI-007', score:950, status:'Ativo',      limite:15000, cadastro:'29/09/2023' },
  { id:'CLI-008', score:680, status:'Ativo',      limite:4200,  cadastro:'13/02/2024' },
];

var CLUSTER_LIMITES = [
  { name:'CLU-001', limite:4000  },
  { name:'CLU-002', limite:3500  },
  { name:'CLU-003', limite:2000  },
  { name:'CLU-004', limite:12000 },
  { name:'CLU-005', limite:8000  },
  { name:'CLU-006', limite:1500  },
  { name:'CLU-007', limite:15500 },
];

var STATUS_PIE = [
  { name:'Ativo',      value:84, color:'#22c55e' },
  { name:'Em Análise', value:6,  color:'#eab308' },
  { name:'Inativo',    value:10, color:'#ef4444' },
];

var EVOLUCAO = [
  { mes:'Jan', valor:8.0  },
  { mes:'Fev', valor:8.5  },
  { mes:'Mar', valor:10.0 },
  { mes:'Abr', valor:11.5 },
  { mes:'Mai', valor:12.0 },
  { mes:'Jun', valor:13.5 },
  { mes:'Jul', valor:15.7 },
];

var SCORE_DIST = [
  { score:300, n:50  }, { score:400, n:180 }, { score:500, n:420 },
  { score:600, n:730 }, { score:700, n:1150}, { score:800, n:950 },
  { score:900, n:600 }, { score:1000,n:180 },
];

var PARAMS_EDITAVEIS = [
  { key:'t',     label:'Taxa de interchange',           value:0.0115, min:0, max:0.05,  step:0.0001 },
  { key:'LGD',   label:'Loss Given Default',            value:0.6,    min:0, max:1,     step:0.01   },
  { key:'u_bar', label:'Utilização esperada do Limite', value:0.75,   min:0, max:1,     step:0.01   },
  { key:'L_max', label:'Teto máximo de Limite',         value:25000,  min:0, max:50000, step:500    },
];

var PARAMS_NAO_EDITAVEIS = [
  { label:'Taxa de interchange', value:'0.0115' },
  { label:'Taxa de interchange', value:'0.0115' },
  { label:'Taxa de interchange', value:'0.0115' },
  { label:'Taxa de interchange', value:'0.0115' },
];

var CLUSTERS_UPLOAD = [
  { id:'CLU-001', limite:1500,  status:'viavel' },
  { id:'CLU-002', limite:5000,  status:'viavel' },
  { id:'CLU-003', limite:null,  status:'sem'    },
  { id:'CLU-004', limite:200,   status:'viavel' },
  { id:'CLU-005', limite:12500, status:'viavel' },
];

/* ── Helpers de formatação ── */
var fmt = function(v) {
  if (v == null) return '—';
  return 'R$ ' + v.toLocaleString('pt-BR');
};

/* ── Componentes de UI reutilizáveis ── */
var StatusBadge = function({ status }) {
  var cls = status === 'Ativo' ? 'badge-ativo'
          : status === 'Em Análise' ? 'badge-analise'
          : 'badge-inativo';
  return <span className={'badge ' + cls}>{status}</span>;
};

var ScoreBar = function({ score }) {
  var pct = Math.round((score / 1000) * 100);
  return (
    <div className="score-cell">
      <div className="score-bar-track">
        <div className="score-bar-fill" style={{ width: pct + '%' }} />
      </div>
      <span className="score-val">{score}</span>
    </div>
  );
};

var DotsMenu = function() {
  return (
    <button style={{ background:'none', border:'none', cursor:'pointer', color:'#94a3b8', fontSize:18 }}>
      ⋮
    </button>
  );
};

var TooltipLimite = function({ active, payload, label }) {
  if (active && payload && payload.length) {
    return (
      <div style={{ background:'#fff', border:'1px solid #e2e8f0', borderRadius:8, padding:'8px 12px', fontSize:12 }}>
        <p style={{ fontWeight:600, marginBottom:2 }}>{label}</p>
        <p style={{ color:'#0ea5e9' }}>
          R$ {payload[0].value.toLocaleString('pt-BR')}k
        </p>
      </div>
    );
  }
  return null;
};
