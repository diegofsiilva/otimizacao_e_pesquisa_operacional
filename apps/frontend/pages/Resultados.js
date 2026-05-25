// pages/Resultados.js
// Deps globals: CLUSTER_LIMITES, STATUS_PIE, EVOLUCAO, SCORE_DIST, SOLVER_COMPARISON, fmt, fmtZ

var Resultados = function() {
  var RC = Recharts;

  var TooltipLimite = function(props) {
    if (!props.active || !props.payload || !props.payload.length) return null;
    return (
      <div className="bg-white border border-slate-200 rounded-lg shadow-lg px-3 py-2 text-xs">
        <p className="font-semibold text-slate-700">{props.payload[0].payload.name}</p>
        <p className="text-sky-600">Limite: {fmt(props.payload[0].value)}</p>
      </div>
    );
  };

  var KPIs = [
    { label: 'Total de Clusters',     value: '10',       sub: '↑ 2 novos clusters',        highlight: false },
    { label: 'Limite Total Aprovado', value: 'R$ 15,7M', sub: '↑ 8.5% vs mês anterior',   highlight: true  },
    { label: 'Clientes Ativos',       value: '1.247',    sub: '↑ 12 novos este mês',       highlight: false },
    { label: 'Taxa de Aprovação',     value: '87.5%',    sub: '↑ 2.3% vs ano anterior',    highlight: false },
  ];

  var sc = SOLVER_COMPARISON;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-slate-800">Visualizar Resultados</h1>
        <div className="mt-1 h-0.5 w-10 bg-sky-500 rounded-full" />
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-4 gap-4">
        {KPIs.map(function(k) {
          return (
            <div key={k.label} className={'bg-white rounded-xl border shadow-sm p-5 ' + (k.highlight ? 'border-sky-300 bg-sky-50' : 'border-slate-200')}>
              <div className="text-xs font-medium text-slate-500 mb-2">{k.label}</div>
              <div className={'text-2xl font-bold mb-1 ' + (k.highlight ? 'text-sky-600' : 'text-slate-800')}>{k.value}</div>
              <div className="text-xs text-slate-500">{k.sub}</div>
            </div>
          );
        })}
      </div>

      {/* Gráficos linha 1 */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
          <div className="text-sm font-semibold text-slate-800 mb-4">Limites por Cluster</div>
          <RC.ResponsiveContainer width="100%" height={220}>
            <RC.BarChart data={CLUSTER_LIMITES} margin={{ top:4, right:8, left:0, bottom:4 }}>
              <RC.CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
              <RC.XAxis dataKey="name" tick={{ fontSize:11, fill:'#64748b' }} axisLine={false} tickLine={false} />
              <RC.YAxis tickFormatter={function(v){ return v >= 1000 ? 'R$' + (v/1000).toFixed(0) + 'k' : 'R$' + v; }}
                tick={{ fontSize:11, fill:'#64748b' }} axisLine={false} tickLine={false} />
              <RC.Tooltip content={<TooltipLimite />} cursor={{ fill:'#f0f9ff' }} />
              <RC.Bar dataKey="limite" fill="#38bdf8" radius={[4,4,0,0]} maxBarSize={48} />
            </RC.BarChart>
          </RC.ResponsiveContainer>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
          <div className="text-sm font-semibold text-slate-800 mb-4">Distribuição por Status</div>
          <div className="flex items-center gap-6">
            <RC.ResponsiveContainer width={180} height={180}>
              <RC.PieChart>
                <RC.Pie data={STATUS_PIE} cx="50%" cy="50%" innerRadius={52} outerRadius={80}
                  startAngle={90} endAngle={-270} dataKey="value" strokeWidth={2}>
                  {STATUS_PIE.map(function(d, i) { return <RC.Cell key={i} fill={d.color} />; })}
                </RC.Pie>
                <RC.Tooltip formatter={function(v){ return [v + '%', '']; }} />
              </RC.PieChart>
            </RC.ResponsiveContainer>
            <div className="space-y-2 flex-1">
              {STATUS_PIE.map(function(d) {
                return (
                  <div key={d.name} className="flex items-center gap-2 text-sm">
                    <div className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ background: d.color }} />
                    <span className="font-medium text-slate-700 flex-1">{d.name}</span>
                    <span className="text-slate-500">{d.value}%</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* ── Comparação Simplex vs PuLP ──────────────────────────── */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
        <div className="mb-1 text-sm font-semibold text-slate-800">Comparação de Solvers: Simplex vs PuLP</div>
        <div className="text-xs text-slate-400 mb-5">Validação da solução ótima com biblioteca externa (PuLP / CBC)</div>

        {/* Cards lado a lado */}
        <div className="grid grid-cols-2 gap-3 mb-4">
          {[sc.simplex, sc.pulp].map(function(s) {
            return (
              <div key={s.label} className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-semibold text-slate-600">{s.label}</span>
                  <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium bg-green-50 text-green-700 border border-green-200">{s.status}</span>
                </div>
                <div className="text-2xl font-bold text-slate-800 mb-1">{fmtZ(s.z)}</div>
                <div className="text-xs text-slate-500">Valor objetivo (z)</div>
                <div className="text-xs text-slate-500 mt-1">Tempo: <span className="font-medium text-slate-700">{s.tempo_ms} ms</span></div>
              </div>
            );
          })}
        </div>

        {/* Delta */}
        <div className="rounded-xl bg-green-50 border border-green-200 px-4 py-3 flex items-center justify-between mb-4">
          <div>
            <div className="text-xs font-semibold text-green-700">Diferença entre solvers (Δz)</div>
            <div className="text-xs text-green-600 mt-0.5">Ambos convergem para a mesma solução ótima</div>
          </div>
          <div className="text-2xl font-bold text-green-600">{sc.delta_z_pct.toFixed(2)}%</div>
        </div>

        {/* Tabela cluster-a-cluster */}
        <div className="text-xs font-semibold text-slate-600 mb-2">Limites por cluster</div>
        <div className="rounded-lg overflow-hidden border border-slate-200">
          <table className="w-full text-xs">
            <thead className="bg-slate-100">
              <tr>
                {['Cluster','Simplex','PuLP','Match'].map(function(h) {
                  return <th key={h} className={'px-3 py-2 font-semibold text-slate-600 ' + (h === 'Match' ? 'text-center' : 'text-left')}>{h}</th>;
                })}
              </tr>
            </thead>
            <tbody>
              {sc.simplex.clusters.map(function(row, i) {
                var pulpRow = sc.pulp.clusters[i];
                var match = row.limite === pulpRow.limite;
                return (
                  <tr key={row.id} className="border-t border-slate-100 hover:bg-slate-50">
                    <td className="px-3 py-2 font-medium text-slate-700">{row.id}</td>
                    <td className="px-3 py-2 text-slate-700">{row.limite > 0 ? fmt(row.limite) : '—'}</td>
                    <td className="px-3 py-2 text-slate-700">{pulpRow.limite > 0 ? fmt(pulpRow.limite) : '—'}</td>
                    <td className="px-3 py-2 text-center">
                      {match
                        ? <span className="text-green-600 font-bold text-sm">✓</span>
                        : <span className="text-red-500 font-bold text-sm">✗</span>}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        <div className="flex items-center gap-2 text-xs text-slate-500 border-t border-slate-100 pt-3 mt-3">
          <span>PD financeiro atual:</span>
          <span className="font-semibold text-slate-700">{(sc.pd_fin_atual * 100).toFixed(2)}%</span>
        </div>
      </div>

      {/* Gráficos linha 2 */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
          <div className="text-sm font-semibold text-slate-800 mb-4">Evolução Temporal de Limites</div>
          <RC.ResponsiveContainer width="100%" height={190}>
            <RC.LineChart data={EVOLUCAO} margin={{ top:4, right:8, left:0, bottom:4 }}>
              <RC.CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
              <RC.XAxis dataKey="mes" tick={{ fontSize:11, fill:'#64748b' }} axisLine={false} tickLine={false} />
              <RC.YAxis tickFormatter={function(v){ return 'R$' + v + 'M'; }}
                tick={{ fontSize:10, fill:'#64748b' }} axisLine={false} tickLine={false} width={44} />
              <RC.Tooltip formatter={function(v){ return ['R$ ' + v + 'M', 'Total']; }} />
              <RC.Line type="monotone" dataKey="valor" stroke="#22c55e" strokeWidth={2.5}
                dot={{ fill:'#22c55e', r:4, strokeWidth:0 }} activeDot={{ r:6 }} />
            </RC.LineChart>
          </RC.ResponsiveContainer>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
          <div className="text-sm font-semibold text-slate-800 mb-4">Distribuição por Faixa de Score</div>
          <RC.ResponsiveContainer width="100%" height={190}>
            <RC.AreaChart data={SCORE_DIST} margin={{ top:4, right:8, left:0, bottom:4 }}>
              <defs>
                <linearGradient id="scoreGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor="#38bdf8" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#38bdf8" stopOpacity={0.05} />
                </linearGradient>
              </defs>
              <RC.CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
              <RC.XAxis dataKey="score" tick={{ fontSize:10, fill:'#64748b' }} axisLine={false} tickLine={false} />
              <RC.YAxis tick={{ fontSize:11, fill:'#64748b' }} axisLine={false} tickLine={false} />
              <RC.Tooltip />
              <RC.Area type="monotone" dataKey="n" stroke="#0ea5e9" strokeWidth={2.5} fill="url(#scoreGrad)" />
            </RC.AreaChart>
          </RC.ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
