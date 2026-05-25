// pages/Resultados.js
// Deps globals: CLUSTER_LIMITES, STATUS_PIE, EVOLUCAO, SCORE_DIST, SOLVER_COMPARISON, fmt, fmtZ

/* ── Gráfico de barras SVG ───────────────────────────────────── */
var BarChartSVG = function(props) {
  var data = props.data;
  var w = 420; var h = 180; var pad = { top: 10, right: 10, bottom: 28, left: 44 };
  var cw = w - pad.left - pad.right;
  var ch = h - pad.top - pad.bottom;
  var max = Math.max.apply(null, data.map(function(d){ return d.value; })) || 1;
  var bw = Math.floor(cw / data.length * 0.55);

  return (
    <svg viewBox={'0 0 ' + w + ' ' + h} width="100%" style={{ overflow: 'visible' }}>
      {[0, 0.25, 0.5, 0.75, 1].map(function(f) {
        var y = pad.top + ch * (1 - f);
        return (
          <g key={f}>
            <line x1={pad.left} x2={pad.left + cw} y1={y} y2={y} stroke="#e2e8f0" strokeWidth="1" />
            <text x={pad.left - 4} y={y + 4} textAnchor="end" fontSize="9" fill="#94a3b8">
              {f === 0 ? '0' : (max * f >= 1000 ? 'R$' + (max * f / 1000).toFixed(0) + 'k' : 'R$' + Math.round(max * f))}
            </text>
          </g>
        );
      })}
      {data.map(function(d, i) {
        var x = pad.left + (cw / data.length) * i + (cw / data.length - bw) / 2;
        var bh = ch * (d.value / max);
        var y = pad.top + ch - bh;
        return (
          <g key={d.label}>
            <rect x={x} y={y} width={bw} height={bh} rx="0" fill="#102C26" />
            <text x={x + bw / 2} y={h - pad.bottom + 14} textAnchor="middle" fontSize="9" fill="#64748b">{d.label}</text>
          </g>
        );
      })}
    </svg>
  );
};

/* ── Gráfico de linha SVG ────────────────────────────────────── */
var LineChartSVG = function(props) {
  var data = props.data;
  var w = 420; var h = 160; var pad = { top: 10, right: 10, bottom: 24, left: 40 };
  var cw = w - pad.left - pad.right;
  var ch = h - pad.top - pad.bottom;
  var max = Math.max.apply(null, data.map(function(d){ return d.value; })) * 1.1 || 1;
  var pts = data.map(function(d, i) {
    var x = pad.left + (cw / (data.length - 1)) * i;
    var y = pad.top + ch - (ch * d.value / max);
    return [x, y];
  });
  var polyline = pts.map(function(p){ return p[0] + ',' + p[1]; }).join(' ');
  var area = 'M' + pts[0][0] + ',' + pts[0][1] +
    pts.slice(1).map(function(p){ return ' L' + p[0] + ',' + p[1]; }).join('') +
    ' L' + pts[pts.length-1][0] + ',' + (pad.top + ch) +
    ' L' + pts[0][0] + ',' + (pad.top + ch) + ' Z';

  return (
    <svg viewBox={'0 0 ' + w + ' ' + h} width="100%" style={{ overflow: 'visible' }}>
      {[0, 0.5, 1].map(function(f) {
        var y = pad.top + ch * (1 - f);
        return (
          <g key={f}>
            <line x1={pad.left} x2={pad.left + cw} y1={y} y2={y} stroke="#e2e8f0" strokeWidth="1" />
            <text x={pad.left - 4} y={y + 4} textAnchor="end" fontSize="9" fill="#94a3b8">R${(max * f).toFixed(1)}M</text>
          </g>
        );
      })}
      <path d={area} fill="#102C26" fillOpacity="0.1" />
      <polyline points={polyline} fill="none" stroke="#22c55e" strokeWidth="2.5" strokeLinejoin="round" />
      {pts.map(function(p, i) {
        return <circle key={i} cx={p[0]} cy={p[1]} r="4" fill="#22c55e" />;
      })}
      {data.map(function(d, i) {
        var x = pad.left + (cw / (data.length - 1)) * i;
        return <text key={i} x={x} y={h - pad.bottom + 14} textAnchor="middle" fontSize="9" fill="#64748b">{d.label}</text>;
      })}
    </svg>
  );
};

/* ── Gráfico de área SVG ─────────────────────────────────────── */
var AreaChartSVG = function(props) {
  var data = props.data;
  var w = 420; var h = 160; var pad = { top: 10, right: 10, bottom: 24, left: 36 };
  var cw = w - pad.left - pad.right;
  var ch = h - pad.top - pad.bottom;
  var max = Math.max.apply(null, data.map(function(d){ return d.value; })) * 1.1 || 1;
  var pts = data.map(function(d, i) {
    var x = pad.left + (cw / (data.length - 1)) * i;
    var y = pad.top + ch - (ch * d.value / max);
    return [x, y];
  });
  var area = 'M' + pts[0][0] + ',' + pts[0][1] +
    pts.slice(1).map(function(p){ return ' L' + p[0] + ',' + p[1]; }).join('') +
    ' L' + pts[pts.length-1][0] + ',' + (pad.top + ch) +
    ' L' + pts[0][0] + ',' + (pad.top + ch) + ' Z';
  var polyline = pts.map(function(p){ return p[0] + ',' + p[1]; }).join(' ');

  return (
    <svg viewBox={'0 0 ' + w + ' ' + h} width="100%" style={{ overflow: 'visible' }}>
      {[0, 0.5, 1].map(function(f) {
        var y = pad.top + ch * (1 - f);
        return <line key={f} x1={pad.left} x2={pad.left + cw} y1={y} y2={y} stroke="#e2e8f0" strokeWidth="1" />;
      })}
      <path d={area} fill="#102C26" fillOpacity="0.15" />
      <polyline points={polyline} fill="none" stroke="#102C26" strokeWidth="2.5" strokeLinejoin="round" />
      {data.map(function(d, i) {
        var x = pad.left + (cw / (data.length - 1)) * i;
        return <text key={i} x={x} y={h - pad.bottom + 14} textAnchor="middle" fontSize="9" fill="#64748b">{d.label}</text>;
      })}
    </svg>
  );
};

/* ── Donut SVG ───────────────────────────────────────────────── */
var DonutChart = function(props) {
  var data = props.data;
  var r = 60; var ri = 38; var cx = 80; var cy = 80;
  var total = data.reduce(function(s, d){ return s + d.value; }, 0);
  var slices = []; var angle = -90;
  data.forEach(function(d) {
    var sweep = (d.value / total) * 360;
    var a1 = angle * Math.PI / 180;
    var a2 = (angle + sweep) * Math.PI / 180;
    var x1 = cx + r * Math.cos(a1); var y1 = cy + r * Math.sin(a1);
    var x2 = cx + r * Math.cos(a2); var y2 = cy + r * Math.sin(a2);
    var xi1 = cx + ri * Math.cos(a1); var yi1 = cy + ri * Math.sin(a1);
    var xi2 = cx + ri * Math.cos(a2); var yi2 = cy + ri * Math.sin(a2);
    var large = sweep > 180 ? 1 : 0;
    slices.push({
      path: 'M'+x1+','+y1+' A'+r+','+r+' 0 '+large+',1 '+x2+','+y2+' L'+xi2+','+yi2+' A'+ri+','+ri+' 0 '+large+',0 '+xi1+','+yi1+' Z',
      color: d.color
    });
    angle += sweep;
  });

  return (
    <svg viewBox="0 0 160 160" width="160" height="160">
      {slices.map(function(s, i){ return <path key={i} d={s.path} fill={s.color} />; })}
    </svg>
  );
};

/* ── Resultados ──────────────────────────────────────────────── */
var Resultados = function(props) {
  var hasData = props.hasData;
  var setPage = props.setPage;

  if (!hasData) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-xl font-bold text-slate-800">Resultados da Simulação</h1>
          <p className="mt-1 text-xs text-slate-500">Nenhuma simulação executada</p>
          <div className="mt-1 h-0.5 w-10 bg-[#102C26]" />
        </div>
        <div className="bg-[#F7E7CE] border border-slate-200 shadow-sm flex flex-col items-center justify-center py-20 px-6 text-center gap-5">
          <div className="w-14 h-14 bg-[#D4EDE8] flex items-center justify-center">
            <svg width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="#102C26" strokeWidth="1.5">
              <polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>
            </svg>
          </div>
          <div>
            <p className="text-sm font-semibold text-slate-800 mb-1">Nenhuma simulação executada</p>
            <p className="text-xs text-slate-500 max-w-xs">Carregue uma base e execute o Simplex em <strong>Gerar Limites</strong> para visualizar os resultados aqui.</p>
          </div>
          <button onClick={function(){ if (setPage) setPage('gerar'); }}
            className="flex items-center gap-2 px-5 py-2.5 text-sm font-semibold bg-[#102C26] text-white hover:bg-[#1a4a3f] transition-colors shadow-sm">
            <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5"><polygon points="5 3 19 12 5 21 5 3"/></svg>
            Ir para Gerar Limites
          </button>
        </div>
      </div>
    );
  }

  function exportarLimites() {
    var sc = SOLVER_COMPARISON;
    var header = ['Cluster', 'Simplex (R$)', 'PuLP/CBC (R$)', 'Match'];
    var rows = sc.simplex.clusters.map(function(cs, i) {
      var cp = sc.pulp.clusters[i];
      var match = cs.limite === cp.limite ? 'Sim' : 'Não';
      return [cs.id, cs.limite || 0, cp.limite || 0, match];
    });
    var csv = [header].concat(rows).map(function(r){ return r.join(';'); }).join('\n');
    var blob = new Blob(['﻿' + csv], { type: 'text/csv;charset=utf-8;' });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a'); a.href = url; a.download = 'limites_clusters.csv';
    document.body.appendChild(a); a.click();
    document.body.removeChild(a); URL.revokeObjectURL(url);
  }

  var KPIs = [
    { label: 'Total de Clusters',     value: '10',       sub: '↑ 2 novos clusters',      highlight: false },
    { label: 'Limite Total Aprovado', value: 'R$ 15,7M', sub: '↑ 8.5% vs mês anterior',  highlight: true  },
    { label: 'Clientes Ativos',       value: '1.247',    sub: '↑ 12 novos este mês',      highlight: false },
    { label: 'Taxa de Aprovação',     value: '87.5%',    sub: '↑ 2.3% vs ano anterior',   highlight: false },
  ];

  var sc = SOLVER_COMPARISON;

  var barData  = CLUSTER_LIMITES.map(function(d){ return { label: d.name, value: d.limite }; });
  var lineData = EVOLUCAO.map(function(d){ return { label: d.mes, value: d.valor }; });
  var areaData = SCORE_DIST.map(function(d){ return { label: d.score, value: d.n }; });

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-800">Resultados da Simulação</h1>
          <p className="mt-1 text-xs text-slate-500">Output do algoritmo Simplex · simulação executada em Jun/2024</p>
          <div className="mt-1 h-0.5 w-10 bg-[#102C26]" />
        </div>
        <button onClick={exportarLimites}
          className="flex items-center gap-2 px-4 py-2 text-sm font-semibold border border-slate-200 bg-[#F7E7CE] text-slate-600 hover:bg-slate-50 transition-colors shadow-sm">
          <svg width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
          Exportar CSV
        </button>
      </div>

      {/* Banner */}
      <div className="flex items-center gap-3 px-4 py-3 bg-[#E8F4F1] border border-[#3D7A6B] text-sm text-[#102C26]">
        <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2" className="flex-shrink-0"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        <span>Indicadores da última execução do Simplex. Para nova simulação, acesse <strong>Gerar Limites</strong>.</span>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-4 gap-4">
        {KPIs.map(function(k) {
          return (
            <div key={k.label} className={' border shadow-sm p-5 ' + (k.highlight ? 'border-[#3D7A6B] bg-[#E8F4F1]' : 'bg-[#F7E7CE] border-slate-200')}>
              <div className="text-xs font-medium text-slate-500 mb-2">{k.label}</div>
              <div className={'text-2xl font-bold mb-1 ' + (k.highlight ? 'text-[#102C26]' : 'text-slate-800')}>{k.value}</div>
              <div className="text-xs text-slate-500">{k.sub}</div>
            </div>
          );
        })}
      </div>

      {/* Gráficos linha 1 */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-[#F7E7CE] border border-slate-200 shadow-sm p-5">
          <div className="text-sm font-semibold text-slate-800 mb-4">Limites por Cluster</div>
          <BarChartSVG data={barData} />
        </div>

        <div className="bg-[#F7E7CE] border border-slate-200 shadow-sm p-5">
          <div className="text-sm font-semibold text-slate-800 mb-4">Distribuição por Status</div>
          <div className="flex items-center gap-6">
            <DonutChart data={STATUS_PIE} />
            <div className="space-y-2 flex-1">
              {STATUS_PIE.map(function(d) {
                return (
                  <div key={d.name} className="flex items-center gap-2 text-sm">
                    <div className="w-2.5 h-2.5 flex-shrink-0" style={{ background: d.color }} />
                    <span className="font-medium text-slate-700 flex-1">{d.name}</span>
                    <span className="text-slate-500">{d.value}%</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Comparação Simplex vs PuLP */}
      <div className="bg-[#F7E7CE] border border-slate-200 shadow-sm p-5">
        <div className="mb-1 text-sm font-semibold text-slate-800">Comparação de Solvers: Simplex vs PuLP</div>
        <div className="text-xs text-slate-400 mb-5">Validação da solução ótima com biblioteca externa (PuLP / CBC)</div>

        <div className="grid grid-cols-2 gap-3 mb-5">
          {[sc.simplex, sc.pulp].map(function(s) {
            return (
              <div key={s.label} className="border border-slate-200 bg-slate-50 p-4">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-semibold text-slate-600">{s.label}</span>
                  <span className="inline-flex items-center px-2 py-0.5 text-[11px] font-medium bg-green-50 text-green-700 border border-green-200">{s.status}</span>
                </div>
                <div className="text-2xl font-bold text-slate-800 mb-1">{fmtZ(s.z)}</div>
                <div className="text-xs text-slate-500">Valor objetivo (z)</div>
                <div className="text-xs text-slate-500 mt-1">Tempo: <span className="font-medium text-slate-700">{s.tempo_ms} ms</span></div>
              </div>
            );
          })}
        </div>

        {/* Tabela comparativa por cluster */}
        <div className="overflow-x-auto border border-slate-200">
          <table className="w-full text-xs">
            <thead>
              <tr className="bg-[#102C26]">
                {['Cluster', 'Simplex (R$)', 'PuLP / CBC (R$)', 'Match'].map(function(h) {
                  return <th key={h} className="px-3 py-2.5 text-left font-semibold text-[#F7E7CE] uppercase tracking-wide whitespace-nowrap">{h}</th>;
                })}
              </tr>
            </thead>
            <tbody>
              {sc.simplex.clusters.map(function(cs, i) {
                var cp = sc.pulp.clusters[i];
                var match = cs.limite === cp.limite;
                return (
                  <tr key={cs.id} className={'border-t border-slate-100 ' + (i % 2 === 0 ? '' : 'bg-slate-50/50')}>
                    <td className="px-3 py-2 font-mono font-semibold text-[#102C26]">{cs.id}</td>
                    <td className="px-3 py-2 text-slate-700">{cs.limite ? fmt(cs.limite) : '—'}</td>
                    <td className="px-3 py-2 text-slate-700">{cp.limite ? fmt(cp.limite) : '—'}</td>
                    <td className="px-3 py-2">
                      {match ? (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 text-[11px] font-medium bg-green-50 text-green-700 border border-green-200">
                          <svg width="10" height="10" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="3"><polyline points="20 6 9 17 4 12"/></svg>
                          Idêntico
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 text-[11px] font-medium bg-amber-50 text-amber-700 border border-amber-200">
                          <svg width="10" height="10" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="3"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                          Diverge
                        </span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        <div className="mt-3 text-xs text-slate-500">
          Δz = <span className="font-semibold text-slate-700">{(sc.delta_z_pct * 100).toFixed(4)}%</span> · PD financeiro atual: <span className="font-semibold text-slate-700">{(sc.pd_fin_atual * 100).toFixed(2)}%</span>
        </div>
      </div>

      {/* Gráficos linha 2 */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-[#F7E7CE] border border-slate-200 shadow-sm p-5">
          <div className="text-sm font-semibold text-slate-800 mb-4">Evolução do Limite Total (R$ M)</div>
          <LineChartSVG data={lineData} />
        </div>

        <div className="bg-[#F7E7CE] border border-slate-200 shadow-sm p-5">
          <div className="text-sm font-semibold text-slate-800 mb-4">Distribuição de Score</div>
          <AreaChartSVG data={areaData} />
        </div>
      </div>
    </div>
  );
};
