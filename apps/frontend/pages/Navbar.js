// pages/Navbar.js
// Navbar fixa full-width, colada no topo. Altura fixa 56px. Sem border-radius.
// Gradiente PAN original (Azul PAN #07B2FD → Azul Royal #005AEA, 90deg).
// Link ativo em branco com texto azul PAN. Logo navega para o Cockpit.

var Navbar = function (props) {
  var page = props.page;
  var setPage = props.setPage;
  var onConfig = props.onConfig;

  var links = [
    {
      key: "dashboard",
      label: "Cockpit",
      icon: (
        <svg
          width="15"
          height="15"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth="2"
        >
          <rect x="3" y="3" width="7" height="7" />
          <rect x="14" y="3" width="7" height="7" />
          <rect x="3" y="14" width="7" height="7" />
          <rect x="14" y="14" width="7" height="7" />
        </svg>
      ),
    },
    {
      key: "gerar",
      label: "Gerar Limites",
      icon: (
        <svg
          width="15"
          height="15"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth="2"
        >
          <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
          <polyline points="17 8 12 3 7 8" />
          <line x1="12" y1="3" x2="12" y2="15" />
        </svg>
      ),
    },
    {
      key: "resultados",
      label: "Resultados",
      icon: (
        <svg
          width="15"
          height="15"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth="2"
        >
          <polyline points="22 7 13.5 15.5 8.5 10.5 2 17" />
          <polyline points="16 7 22 7 22 13" />
        </svg>
      ),
    },
    {
      key: "clientes",
      label: "Clientes",
      icon: (
        <svg
          width="15"
          height="15"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth="2"
        >
          <circle cx="11" cy="11" r="8" />
          <path d="m21 21-4.35-4.35" />
        </svg>
      ),
    },
    {
      key: "config",
      label: "Configurações",
      isConfig: true,
      icon: (
        <svg
          width="15"
          height="15"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth="2"
        >
          <path d="M12 15a3 3 0 100-6 3 3 0 000 6z" />
          <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z" />
        </svg>
      ),
    },
  ];

  return (
    <header
      style={{
        background: "linear-gradient(90deg, #07B2FD 0%, #005AEA 100%)",
        borderRadius: 0,
      }}
      className="fixed top-0 left-0 w-full z-40 flex items-center h-14 px-8 shadow-xl border-b border-white/10"
    >
      {/* Logo - clicável, navega para o Cockpit */}
      <div
        className="flex items-center gap-2.5 mr-6 flex-shrink-0 cursor-pointer"
        onClick={function () {
          setPage("dashboard");
        }}
      >
        <img
          src="assets/Logo_PAN.jpg"
          alt="Banco PAN"
          className="h-8 w-auto object-contain flex-shrink-0"
        />
        <div>
          <div className="text-sm font-bold text-white leading-tight">
            Banco PAN
          </div>
          <div className="text-[10px] text-white/70 leading-tight">
            Otimizador de Limites
          </div>
        </div>
      </div>

      <div className="w-px h-5 bg-white/30 mr-5 flex-shrink-0" />

      {/* Links */}
      <nav className="flex items-center gap-1">
        {links.map(function (l) {
          var active = page === l.key;
          return (
            <button
              key={l.key}
              onClick={function () {
                l.isConfig ? onConfig() : setPage(l.key);
              }}
              style={{ borderRadius: 0 }}
              className={[
                "flex items-center gap-2 px-3.5 py-2 text-sm font-medium transition-colors",
                active
                  ? "bg-white text-[#005AEA] shadow-sm font-semibold"
                  : "text-white/90 hover:bg-white/15",
              ].join(" ")}
            >
              {l.icon}
              {l.label}
            </button>
          );
        })}
      </nav>
    </header>
  );
};
