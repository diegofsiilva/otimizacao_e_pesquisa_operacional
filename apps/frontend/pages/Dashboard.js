// pages/Dashboard.js  –  Deps globals: CLIENTS, fmt

var ScoreBar = function(props) {
  var score = props.score;
  var pct = Math.round((score / 1000) * 100);
  var color = score >= 750 ? '#22c55e' : score >= 550 ? '#fbbf24' : '#f87171';
  return (
    <div className="flex items-center gap-2">
      <div className="w-20 h-1.5 bg-slate-200 rounded-full overflow-hidden">
        <div style={{ width: pct + '%', background: color }} className="h-full rounded-full" />
      </div>
      <span className="text-xs font-medium text-slate-600">{score}</span>
    </div>
  );
};

var StatusBadge = function(props) {
  var s = props.status;
  var cls = s === 'Ativo'
    ? 'bg-green-50 text-green-700 border border-green-200'
    : s === 'Pendente'
    ? 'bg-amber-50 text-amber-700 border border-amber-200'
    : 'bg-red-50 text-red-600 border border-red-200';
  return <span className={'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ' + cls}>{s}</span>;
};

var DotsMenu = function() {
  return (
    <button className="p-1 rounded hover:bg-slate-100 text-slate-400">
      <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
        <circle cx="12" cy="5" r="1" fill="currentColor"/><circle cx="12" cy="12" r="1" fill="currentColor"/><circle cx="12" cy="19" r="1" fill="currentColor"/>
      </svg>
    </button>
  );
};

var KPI_CARDS = [
  { label: 'Total de Clientes',  value: '1.247',          sub: '+12 desde o último mês', subColor: 'text-green-500',  iconBg: 'bg-sky-100',   iconColor: '#0ea5e9',
    icon: <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75"/></svg> },
  { label: 'Clusters Ativos',    value: '10',             sub: 'Sem alterações',          subColor: 'text-slate-500',  iconBg: 'bg-sky-100',   iconColor: '#0ea5e9',
    icon: <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><rect x="2" y="17" width="20" height="4" rx="1"/><rect x="2" y="11" width="20" height="4" rx="1"/><rect x="2" y="5" width="20" height="4" rx="1"/></svg> },
  { label: 'Limite Total',       value: 'R$ 15.750.000',  sub: '+5.2% último mês',        subColor: 'text-green-500',  iconBg: 'bg-green-100', iconColor: '#22c55e',
    icon: <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg> },
  { label: 'Taxa de Aprovação',  value: '87.5%',          sub: '+2.3% último ano',        subColor: 'text-green-500',  iconBg: 'bg-amber-100', iconColor: '#f59e0b',
    icon: <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg> },
];

var Dashboard = function() {
  var s1 = React.useState(''); var search = s1[0]; var setSearch = s1[1];
  var s2 = React.useState(1);  var page   = s2[0]; var setPage   = s2[1];

  var filtered = CLIENTS.filter(function(c) {
    return c.id.toLowerCase().indexOf(search.toLowerCase()) !== -1;
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-slate-800">Dashboard</h1>
        <div className="mt-1 h-0.5 w-10 bg-sky-500 rounded-full" />
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-4 gap-4">
        {KPI_CARDS.map(function(k) {
          return (
            <div key={k.label} className="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-medium text-slate-500">{k.label}</span>
                <div className={'w-9 h-9 rounded-lg flex items-center justify-center ' + k.iconBg} style={{ color: k.iconColor }}>
                  {k.icon}
                </div>
              </div>
              <div className="text-2xl font-bold text-slate-800 mb-1">{k.value}</div>
              <div className={'text-xs font-medium ' + k.subColor}>{k.sub}</div>
            </div>
          );
        })}
      </div>

      {/* Lista de clientes */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100">
          <div className="flex items-center gap-2 text-sm font-semibold text-slate-700">
            <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="#94a3b8" strokeWidth="2"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/></svg>
            Lista de Clientes
          </div>
          <div className="flex items-center gap-2">
            {[
              { label: 'Importar', icon: <svg width="12" height="12" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>, primary: false },
              { label: 'Exportar', icon: <svg width="12" height="12" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>, primary: false },
              { label: 'Adicionar', icon: <svg width="12" height="12" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>, primary: true },
            ].map(function(b) {
              return (
                <button key={b.label}
                  className={'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors '
                    + (b.primary ? 'bg-sky-500 text-white border-sky-500 hover:bg-sky-600' : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50')}>
                  {b.icon}{b.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Search */}
        <div className="flex items-center gap-2 px-5 py-3">
          <div className="relative flex-1">
            <svg className="absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400" width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
            <input className="w-full pl-8 pr-3 py-1.5 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-sky-400 focus:ring-1 focus:ring-sky-400"
              placeholder="Buscar cliente..." value={search} onChange={function(e) { setSearch(e.target.value); }} />
          </div>
          <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border border-slate-200 bg-white text-slate-600 hover:bg-slate-50">
            <svg width="12" height="12" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>
            Filtrar
          </button>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-y border-slate-100 bg-slate-50">
                {['Cluster','Score','Status','Limite','Cadastro','Ações'].map(function(h) {
                  return <th key={h} className="px-4 py-2.5 text-left text-[11px] font-semibold text-slate-500 uppercase tracking-wide">{h}</th>;
                })}
              </tr>
            </thead>
            <tbody>
              {filtered.map(function(c) {
                return (
                  <tr key={c.id} className="border-b border-slate-50 hover:bg-slate-50 transition-colors">
                    <td className="px-4 py-3 text-sm font-medium text-slate-800">{c.id}</td>
                    <td className="px-4 py-3"><ScoreBar score={c.score} /></td>
                    <td className="px-4 py-3"><StatusBadge status={c.status} /></td>
                    <td className="px-4 py-3 text-sm font-medium text-slate-700">{c.limite ? fmt(c.limite) : '—'}</td>
                    <td className="px-4 py-3 text-sm text-slate-500">{c.cadastro}</td>
                    <td className="px-4 py-3"><DotsMenu /></td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="flex items-center justify-between px-5 py-3 border-t border-slate-100">
          <span className="text-xs text-slate-500">Mostrando 1–{filtered.length} de {filtered.length}</span>
          <div className="flex items-center gap-1">
            <button className="px-3 h-7 rounded text-xs text-slate-500 hover:bg-slate-100">Anterior</button>
            {[1,2,3].map(function(n) {
              return (
                <button key={n} onClick={function() { setPage(n); }}
                  className={'w-7 h-7 rounded text-xs font-medium transition-colors ' + (page === n ? 'bg-sky-500 text-white' : 'text-slate-600 hover:bg-slate-100')}>
                  {n}
                </button>
              );
            })}
            <button className="px-3 h-7 rounded text-xs text-slate-500 hover:bg-slate-100">Próximo</button>
          </div>
        </div>
      </div>
    </div>
  );
};
