// pages/Navbar.js

var Navbar = function(props) {
  var page = props.page;
  var setPage = props.setPage;
  var onConfig = props.onConfig;

  var links = [
    {
      key: 'dashboard', label: 'Dashboard',
      icon: <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>
    },
    {
      key: 'gerar', label: 'Gerar Limites',
      icon: <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
    },
    {
      key: 'resultados', label: 'Resultados',
      icon: <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>
    },
  ];

  return (
    <aside className="fixed left-0 top-0 bottom-0 w-56 bg-[#F0EEE4] border-r border-slate-200 flex flex-col z-40 shadow-sm">
      <div className="px-5 py-5 border-b border-slate-100">
        <div className="flex items-center gap-2.5">
          <img src="assets/Logo_PAN.jpg" alt="Banco PAN" className="h-8 w-auto rounded-lg object-contain flex-shrink-0" />
          <div>
            <div className="text-sm font-bold text-slate-800 leading-tight">Banco PAN</div>
            <div className="text-[10px] text-slate-400 leading-tight">Otimizador de Limites</div>
          </div>
        </div>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1">
        {links.map(function(l) {
          var active = page === l.key;
          return (
            <button key={l.key} onClick={function() { setPage(l.key); }}
              className={['w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors text-left',
                active ? 'bg-sky-500 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-100'].join(' ')}>
              {l.icon}{l.label}
            </button>
          );
        })}
      </nav>

      <div className="px-3 py-4 border-t border-slate-100">
        <button onClick={onConfig}
          className="w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-sm font-medium text-slate-600 hover:bg-slate-100 transition-colors">
          <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
            <path d="M12 15a3 3 0 100-6 3 3 0 000 6z"/>
            <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"/>
          </svg>
          Configurações
        </button>
      </div>
    </aside>
  );
};
