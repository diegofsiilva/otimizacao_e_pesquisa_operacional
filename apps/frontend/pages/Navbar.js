// pages/Navbar.js

var Navbar = function(props) {
  var page = props.page;
  var setPage = props.setPage;
  var onConfig = props.onConfig;

  var s1 = React.useState(false); var scrolled = s1[0]; var setScrolled = s1[1];

  React.useEffect(function() {
    function onScroll() { setScrolled(window.scrollY > 40); }
    window.addEventListener('scroll', onScroll);
    return function() { window.removeEventListener('scroll', onScroll); };
  }, []);

  var links = [
    {
      key: 'dashboard', label: 'Dashboard',
      icon: <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>
    },
    {
      key: 'gerar', label: 'Gerar Limites',
      icon: <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
    },
    {
      key: 'resultados', label: 'Resultados',
      icon: <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>
    },
    {
      key: 'config', label: 'Configurações', isConfig: true,
      icon: <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path d="M12 15a3 3 0 100-6 3 3 0 000 6z"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"/></svg>
    },
  ];

  return (
    <header style={{ transition: 'top .35s ease, width .35s ease, padding .35s ease, box-shadow .35s ease, border-radius .35s ease' }}
      className={[
        'fixed left-1/2 -translate-x-1/2 z-40 bg-[#102C26] border border-[#1e4a3f] flex items-center',
        scrolled
          ? 'top-3 w-[calc(100%-4rem)] max-w-7xl px-6 h-12 shadow-xl '
          : 'top-5 w-[calc(100%-4rem)] max-w-7xl px-8 h-16 shadow-lg '
      ].join(' ')}>

      {/* Logo */}
      <div className="flex items-center gap-2.5 mr-6 flex-shrink-0" style={{ transition: 'gap .35s ease' }}>
        <img src="assets/Logo_PAN.jpg" alt="Banco PAN"
          style={{ transition: 'height .35s ease' }}
          className={['w-auto object-contain flex-shrink-0', scrolled ? 'h-6' : 'h-8'].join(' ')} />
        <div style={{ transition: 'opacity .35s ease', opacity: scrolled ? 0.85 : 1 }}>
          <div className={['font-bold text-[#F7E7CE] leading-tight', scrolled ? 'text-xs' : 'text-sm'].join(' ')}
            style={{ transition: 'font-size .35s ease' }}>Banco PAN</div>
          {!scrolled && <div className="text-[10px] text-[#F7E7CE]/60 leading-tight">Otimizador de Limites</div>}
        </div>
      </div>

      {/* Divisor */}
      <div className="w-px h-5 bg-[#F7E7CE]/20 mr-5 flex-shrink-0" />

      {/* Links */}
      <nav className="flex items-center gap-1">
        {links.map(function(l) {
          var active = page === l.key;
          return (
            <button key={l.key} onClick={function() { l.isConfig ? onConfig() : setPage(l.key); }}
              className={[
                'flex items-center gap-2  font-medium transition-colors',
                scrolled ? 'px-3 py-1.5 text-xs' : 'px-3.5 py-2 text-sm',
                active ? 'bg-[#F7E7CE] text-[#102C26] shadow-sm' : 'text-[#F7E7CE]/80 hover:bg-[#1e4a3f]'
              ].join(' ')}>
              {l.icon}{l.label}
            </button>
          );
        })}
      </nav>
    </header>
  );
};
