// ─────────────────────────────────────────
//  pages/Resultados.js  –  gráficos e KPIs de resultado
//  Depende de: data.js (CLUSTER_LIMITES, STATUS_PIE, EVOLUCAO, SCORE_DIST, TooltipLimite)
//              Recharts (global window.Recharts)
// ─────────────────────────────────────────

var Resultados = function() {
  var R = Recharts;

  return (
    <div className="page">
      <h1 className="page-title">Visualizar Resultados</h1>
      <div className="page-title-underline" />

      {/* KPI Cards */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-card-header">
            <span className="kpi-label">Total de Clusters</span>
          </div>
          <div className="kpi-value">10</div>
          <div className="kpi-sub">↑ 2 novos clusters</div>
        </div>

        <div className="kpi-card highlight">
          <div className="kpi-card-header">
            <span className="kpi-label">Limite Total Aprovado</span>
          </div>
          <div className="kpi-value">R$ 15,7M</div>
          <div className="kpi-sub">↑ 8.5% vs mês anterior</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-card-header">
            <span className="kpi-label">Clientes Ativos</span>
          </div>
          <div className="kpi-value">1.247</div>
          <div className="kpi-sub">↑ 12 novos este mês</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-card-header">
            <span className="kpi-label">Taxa de Aprovação</span>
          </div>
          <div className="kpi-value">87.5%</div>
          <div className="kpi-sub">↑ 2.3% vs ano anterior</div>
        </div>
      </div>

      {/* Gráficos – linha 1 */}
      <div className="charts-grid">

        {/* Barras – Limites por Cluster */}
        <div className="section-card">
          <div className="section-title">Limites por Cluster</div>
          <R.ResponsiveContainer width="100%" height={240}>
            <R.BarChart
              data={CLUSTER_LIMITES}
              margin={{ top:4, right:8, left:0, bottom:4 }}
            >
              <R.CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
              <R.XAxis
                dataKey="name"
                tick={{ fontSize:11, fill:'#64748b' }}
                axisLine={false} tickLine={false}
              />
              <R.YAxis
                tickFormatter={function(v) { return 'R$ ' + v/1000 + 'k'; }}
                tick={{ fontSize:11, fill:'#64748b' }}
                axisLine={false} tickLine={false}
              />
              <R.Tooltip content={<TooltipLimite />} cursor={{ fill:'#f0f9ff' }} />
              <R.Bar dataKey="limite" fill="#38bdf8" radius={[4,4,0,0]} maxBarSize={48} />
            </R.BarChart>
          </R.ResponsiveContainer>
        </div>

        {/* Donut – Distribuição por Status */}
        <div className="section-card">
          <div className="section-title">Distribuição por Status</div>
          <div style={{ display:'flex', alignItems:'center', gap:24 }}>
            <R.ResponsiveContainer width={200} height={200}>
              <R.PieChart>
                <R.Pie
                  data={STATUS_PIE}
                  cx="50%" cy="50%"
                  innerRadius={55} outerRadius={85}
                  startAngle={90} endAngle={-270}
                  dataKey="value"
                  strokeWidth={2}
                >
                  {STATUS_PIE.map(function(d, i) {
                    return <R.Cell key={i} fill={d.color} />;
                  })}
                </R.Pie>
                <R.Tooltip formatter={function(v) { return v + '%'; }} />
              </R.PieChart>
            </R.ResponsiveContainer>

            <div className="donut-legend">
              {STATUS_PIE.map(function(d) {
                return (
                  <div key={d.name} className="donut-legend-item">
                    <div className="donut-dot" style={{ background: d.color }} />
                    <span style={{ color:'#0f172a', fontWeight:500 }}>{d.name}</span>
                    <span style={{ color:'#64748b', marginLeft:'auto', paddingLeft:12 }}>{d.value}%</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Gráficos – linha 2 */}
      <div className="charts-grid">

        {/* Linha – Evolução Temporal */}
        <div className="section-card">
          <div className="section-title">Evolução Temporal de Limites</div>
          <R.ResponsiveContainer width="100%" height={200}>
            <R.LineChart
              data={EVOLUCAO}
              margin={{ top:4, right:8, left:0, bottom:4 }}
            >
              <R.CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
              <R.XAxis
                dataKey="mes"
                tick={{ fontSize:11, fill:'#64748b' }}
                axisLine={false} tickLine={false}
              />
              <R.YAxis
                tickFormatter={function(v) { return 'R$\n' + v + 'M'; }}
                tick={{ fontSize:10, fill:'#64748b' }}
                axisLine={false} tickLine={false}
                width={48}
              />
              <R.Tooltip formatter={function(v) { return ['R$ ' + v + 'M', 'Total']; }} />
              <R.Line
                type="monotone"
                dataKey="valor"
                stroke="#22c55e"
                strokeWidth={2.5}
                dot={{ fill:'#22c55e', r:4, strokeWidth:0 }}
                activeDot={{ r:6 }}
              />
            </R.LineChart>
          </R.ResponsiveContainer>
        </div>

        {/* Área – Distribuição por Faixa de Score */}
        <div className="section-card">
          <div className="section-title">Distribuição por Faixa de Score</div>
          <R.ResponsiveContainer width="100%" height={200}>
            <R.AreaChart
              data={SCORE_DIST}
              margin={{ top:4, right:8, left:0, bottom:4 }}
            >
              <defs>
                <linearGradient id="scoreGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor="#38bdf8" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#38bdf8" stopOpacity={0.05} />
                </linearGradient>
              </defs>
              <R.CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
              <R.XAxis
                dataKey="score"
                tick={{ fontSize:11, fill:'#64748b' }}
                axisLine={false} tickLine={false}
              />
              <R.YAxis
                tick={{ fontSize:11, fill:'#64748b' }}
                axisLine={false} tickLine={false}
              />
              <R.Tooltip />
              <R.Area
                type="monotone"
                dataKey="n"
                stroke="#0ea5e9"
                strokeWidth={2.5}
                fill="url(#scoreGrad)"
              />
            </R.AreaChart>
          </R.ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
