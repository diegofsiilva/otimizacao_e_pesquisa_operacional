// ─────────────────────────────────────────
//  pages/Navbar.js  –  barra de navegação superior
// ─────────────────────────────────────────

var Navbar = function({ page, setPage }) {
  var links = [
    { id:'dashboard',  label:'Dashboard',     icon:'home'    },
    { id:'gerar',      label:'Gerar Limites',  icon:'grid'    },
    { id:'resultados', label:'Resultados',     icon:'chart'   },
  ];

  function NavIcon({ type }) {
    if (type === 'home') return (
      <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/>
        <polyline points="9 22 9 12 15 12 15 22"/>
      </svg>
    );
    if (type === 'grid') return (
      <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="3" width="18" height="18" rx="2"/>
        <line x1="3" y1="9" x2="21" y2="9"/>
        <line x1="9" y1="21" x2="9" y2="9"/>
      </svg>
    );
    return (
      <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <line x1="18" y1="20" x2="18" y2="10"/>
        <line x1="12" y1="20" x2="12" y2="4"/>
        <line x1="6"  y1="20" x2="6"  y2="14"/>
      </svg>
    );
  }

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <div className="navbar-logo">
          <svg width="18" height="18" fill="none" viewBox="0 0 24 24">
            <polyline points="22 7 13.5 15.5 8.5 10.5 2 17" stroke="#fff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
            <polyline points="16 7 22 7 22 13"              stroke="#fff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </div>
        Sistema de Crédito
      </div>

      <div className="navbar-nav">
        {links.map(function(l) {
          return (
            <button
              key={l.id}
              className={'nav-link' + (page === l.id ? ' active' : '')}
              onClick={function() { setPage(l.id); }}
            >
              <NavIcon type={l.icon} />
              {l.label}
            </button>
          );
        })}
      </div>
    </nav>
  );
};
