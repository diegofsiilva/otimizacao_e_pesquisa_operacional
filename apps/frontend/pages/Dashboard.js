// ─────────────────────────────────────────
//  pages/Dashboard.js  –  tela principal
//  Depende de: data.js (CLIENTS, fmt, StatusBadge, ScoreBar, DotsMenu)
// ─────────────────────────────────────────

var Dashboard = function() {
  var useState = React.useState;
  var search = useState('')[0];
  var setSearch = useState('')[1];

  // re-declare properly
  var _s = React.useState('');
  var searchVal = _s[0];
  var setSearchVal = _s[1];

  var _p = React.useState(1);
  var currentPage = _p[0];
  var setCurrentPage = _p[1];

  var filtered = CLIENTS.filter(function(c) {
    return c.id.toLowerCase().includes(searchVal.toLowerCase());
  });

  return (
    <div className="page">
      <h1 className="page-title">Dashboard</h1>
      <div className="page-title-underline" />

      {/* KPI Cards */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-card-header">
            <span className="kpi-label">Total de Clientes</span>
            <div className="kpi-icon" style={{ background:'#e0f2fe' }}>
              <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="#0ea5e9" strokeWidth="2">
                <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/>
                <circle cx="9" cy="7" r="4"/>
                <path d="M23 21v-2a4 4 0 00-3-3.87"/>
                <path d="M16 3.13a4 4 0 010 7.75"/>
              </svg>
            </div>
          </div>
          <div className="kpi-value">1.247</div>
          <div className="kpi-sub">+12 desde o último mês</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-card-header">
            <span className="kpi-label">Clusters Ativos</span>
            <div className="kpi-icon" style={{ background:'#e0f2fe' }}>
              <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="#0ea5e9" strokeWidth="2">
                <rect x="2" y="17" width="20" height="4" rx="1"/>
                <rect x="2" y="11" width="20" height="4" rx="1"/>
                <rect x="2" y="5"  width="20" height="4" rx="1"/>
              </svg>
            </div>
          </div>
          <div className="kpi-value">10</div>
          <div className="kpi-sub neutral">Sem alterações</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-card-header">
            <span className="kpi-label">Limite Total</span>
            <div className="kpi-icon" style={{ background:'#dcfce7' }}>
              <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="#22c55e" strokeWidth="2">
                <line x1="12" y1="1" x2="12" y2="23"/>
                <path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/>
              </svg>
            </div>
          </div>
          <div className="kpi-value" style={{ fontSize:22 }}>R$ 15.750.000</div>
          <div className="kpi-sub">+5.2% último mês</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-card-header">
            <span className="kpi-label">Taxa de Aprovação</span>
            <div className="kpi-icon" style={{ background:'#fef3c7' }}>
              <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="#f59e0b" strokeWidth="2">
                <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/>
                <polyline points="17 6 23 6 23 12"/>
              </svg>
            </div>
          </div>
          <div className="kpi-value">87.5%</div>
          <div className="kpi-sub">+2.3% último ano</div>
        </div>
      </div>

      {/* Lista de Clientes */}
      <div className="section-card">
        <div className="list-header">
          <div className="list-header-left">
            <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="#64748b" strokeWidth="2">
              <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
            </svg>
            Lista de Clientes
          </div>
          <div className="list-header-right">
            <button className="btn">
              <svg width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
                <polyline points="17 8 12 3 7 8"/>
                <line x1="12" y1="3" x2="12" y2="15"/>
              </svg>
              Importar
            </button>
            <button className="btn">
              <svg width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
                <polyline points="7 10 12 15 17 10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
              </svg>
              Exportar
            </button>
            <button className="btn btn-primary">
              <svg width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
                <line x1="12" y1="5" x2="12" y2="19"/>
                <line x1="5"  y1="12" x2="19" y2="12"/>
              </svg>
              Adicionar
            </button>
          </div>
        </div>

        <div className="search-row">
          <input
            className="search-input"
            placeholder="Buscar cliente..."
            value={searchVal}
            onChange={function(e) { setSearchVal(e.target.value); }}
          />
          <button className="btn">
            <svg width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
              <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>
            </svg>
            Filtrar
          </button>
        </div>

        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Cluster</th>
                <th>Score</th>
                <th>Status</th>
                <th>Limite</th>
                <th>Cadastro</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(function(c) {
                return (
                  <tr key={c.id}>
                    <td style={{ fontWeight:500 }}>{c.id}</td>
                    <td><ScoreBar score={c.score} /></td>
                    <td><StatusBadge status={c.status} /></td>
                    <td style={{ fontWeight:500 }}>{c.limite ? fmt(c.limite) : '—'}</td>
                    <td style={{ color:'#64748b' }}>{c.cadastro}</td>
                    <td><DotsMenu /></td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        <div className="pagination">
          <span className="pagination-info">Mostrando 1-8 de 8</span>
          <div className="pagination-btns">
            <button className="page-btn page-btn-text">Anterior</button>
            {[1, 2, 3].map(function(n) {
              return (
                <button
                  key={n}
                  className={'page-btn' + (currentPage === n ? ' active' : '')}
                  onClick={function() { setCurrentPage(n); }}
                >
                  {n}
                </button>
              );
            })}
            <button className="page-btn page-btn-text">Próximo</button>
          </div>
        </div>
      </div>
    </div>
  );
};
