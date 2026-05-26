// pages/Dashboard.js
// Deps globais: CLIENTS, fmt

// Barra de progresso proporcional ao score (0-1000)
// Cores semânticas da paleta terciária PAN: verde, amarelo, vermelho
var ScoreBar = function (props) {
  var score = props.score;
  var pct = Math.round((score / 1000) * 100);
  var color = score >= 750 ? "#67DE98" : score >= 550 ? "#FAE95D" : "#FF5D5C";
  return (
    <div className="flex items-center gap-2">
      <div className="w-20 h-1.5 bg-[#E8EFF7] overflow-hidden">
        <div
          style={{ width: pct + "%", background: color }}
          className="h-full"
        />
      </div>
      <span className="text-xs font-medium text-[#3B4049]">{score}</span>
    </div>
  );
};

// Badge de status com cores semânticas da paleta terciária PAN
var StatusBadge = function (props) {
  var s = props.status;
  var cls =
    s === "Ativo"
      ? "bg-[#67DE98]/20 text-[#2E6DA4] border border-[#67DE98]/60"
      : s === "Pendente"
        ? "bg-[#FAE95D]/30 text-[#3B4049] border border-[#FAE95D]/80"
        : "bg-[#FF5D5C]/20 text-[#DC2F37] border border-[#FF5D5C]/50";
  return (
    <span
      className={
        "inline-flex items-center px-2.5 py-0.5 text-xs font-semibold " +
        cls
      }
    >
      {s}
    </span>
  );
};

// Botão de ações da linha da tabela
var DotsMenu = function () {
  return (
    <button className="p-1 hover:bg-[#E2EAF4] text-[#9C9C9F] transition-colors">
      <svg
        width="15"
        height="15"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        strokeWidth="2"
      >
        <circle cx="12" cy="5" r="1" fill="currentColor" />
        <circle cx="12" cy="12" r="1" fill="currentColor" />
        <circle cx="12" cy="19" r="1" fill="currentColor" />
      </svg>
    </button>
  );
};

// KPI cards -- ícones em tons de azul PAN conforme brandbook
// 4o card usa amarelo terciário como toque pontual de destaque (10% terciário permitido)
var KPI_CARDS = [
  {
    label: "Total de Clientes",
    period: "na base carregada",
    value: "1.247",
    badge: "+12",
    trend: "up",
    iconBg: "#D6E8F5",
    iconColor: "#2E6DA4",
    icon: (
      <svg
        width="18"
        height="18"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        strokeWidth="2"
      >
        <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" />
        <circle cx="9" cy="7" r="4" />
        <path d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75" />
      </svg>
    ),
  },
  {
    label: "Clusters Identificados",
    period: "segmentação atual",
    value: "10",
    badge: "=",
    trend: "neutral",
    iconBg: "#D6E8F5",
    iconColor: "#1B3A5C",
    icon: (
      <svg
        width="18"
        height="18"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        strokeWidth="2"
      >
        <rect x="2" y="17" width="20" height="4" rx="0" />
        <rect x="2" y="11" width="20" height="4" rx="0" />
        <rect x="2" y="5" width="20" height="4" rx="0" />
      </svg>
    ),
  },
  {
    label: "Score Médio",
    period: "média da carteira",
    value: "682",
    badge: "+8",
    trend: "up",
    iconBg: "#D6E8F5",
    iconColor: "#0D1B2A",
    icon: (
      <svg
        width="18"
        height="18"
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
    label: "Clientes Elegíveis",
    period: "aptos à otimização",
    value: "1.089",
    badge: "87.3%",
    trend: "up",
    iconBg: "#FFFCE6",
    iconColor: "#3B4049",
    icon: (
      <svg
        width="18"
        height="18"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        strokeWidth="2"
      >
        <path d="M22 11.08V12a10 10 0 11-5.93-9.14" />
        <polyline points="22 4 12 14.01 9 11.01" />
      </svg>
    ),
  },
];

var Dashboard = function (props) {
  var setPage = props.setPage;
  var s1 = React.useState("");
  var search = s1[0];
  var setSearch = s1[1];
  var s2 = React.useState(1);
  var pageNum = s2[0];
  var setPageNum = s2[1];

  function exportarCSV() {
    var header = ["ID", "Score", "Status", "Limite", "Cadastro"];
    var rows = CLIENTS.map(function (c) {
      return [
        c.id,
        c.score,
        c.status,
        c.limite !== null ? c.limite : "",
        c.cadastro,
      ];
    });
    var csv = [header]
      .concat(rows)
      .map(function (r) {
        return r.join(";");
      })
      .join("\n");
    var blob = new Blob(["\uFEFF" + csv], { type: "text/csv;charset=utf-8;" });
    var url = URL.createObjectURL(blob);
    var a = document.createElement("a");
    a.href = url;
    a.download = "clientes.csv";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  var filtered = CLIENTS.filter(function (c) {
    return c.id.toLowerCase().indexOf(search.toLowerCase()) !== -1;
  });

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-xl font-bold text-[#0D1B2A]">Dashboard</h1>
          <p className="mt-1 text-xs text-[#9C9C9F]">
            Visão geral da carteira base · base carregada em Jun/2024
          </p>
          <div className="mt-1 h-0.5 w-10 bg-[#2E6DA4]" />
        </div>
        <button
          onClick={function () {
            if (setPage) setPage("gerar");
          }}
          className="flex items-center gap-2 px-4 py-2 text-sm font-semibold bg-[#2E6DA4] text-white hover:bg-[#1B3A5C] transition-colors shadow-sm"
        >
          <svg
            width="14"
            height="14"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth="2.5"
          >
            <polygon points="5 3 19 12 5 21 5 3" />
          </svg>
          Nova Simulação
        </button>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-4 gap-4">
        {KPI_CARDS.map(function (k) {
          var badgeCls =
            k.trend === "up"
              ? "bg-[#67DE98]/20 text-[#2E6DA4]"
              : k.trend === "down"
                ? "bg-[#FF5D5C]/20 text-[#DC2F37]"
                : "bg-[#B8D4EC]/40 text-[#3B4049]";
          var arrow =
            k.trend === "up" ? (
              <svg
                width="10"
                height="10"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth="3"
              >
                <polyline points="18 15 12 9 6 15" />
              </svg>
            ) : k.trend === "down" ? (
              <svg
                width="10"
                height="10"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth="3"
              >
                <polyline points="6 9 12 15 18 9" />
              </svg>
            ) : null;

          return (
            <div
              key={k.label}
              className="bg-white border border-[#E8EFF7] shadow-sm p-5 flex flex-col gap-3"
            >
              <div className="flex items-center gap-3">
                <div
                  className="w-10 h-10 flex items-center justify-center flex-shrink-0"
                  style={{ background: k.iconBg, color: k.iconColor }}
                >
                  {k.icon}
                </div>
                <div>
                  <div className="text-sm font-semibold text-[#0D1B2A] leading-tight">
                    {k.label}
                  </div>
                  <div className="text-[11px] text-[#9C9C9F] leading-tight">
                    {k.period}
                  </div>
                </div>
              </div>
              {/* Valor + badge */}
              <div className="flex items-end justify-between">
                <div className="text-2xl font-bold text-[#0D1B2A] leading-none">
                  {k.value}
                </div>
                <span
                  className={
                    "inline-flex items-center gap-0.5 px-2 py-0.5 text-[11px] font-semibold " +
                    badgeCls
                  }
                >
                  {arrow}
                  {k.badge}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      <div className="bg-white border border-[#E8EFF7] shadow-sm overflow-hidden">
        <div className="flex items-center justify-between px-5 py-4 border-b border-[#E8EFF7]">
          <div className="flex items-center gap-2 text-sm font-semibold text-[#0D1B2A]">
            <svg
              width="15"
              height="15"
              fill="none"
              viewBox="0 0 24 24"
              stroke="#9C9C9F"
              strokeWidth="2"
            >
              <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" />
              <circle cx="9" cy="7" r="4" />
            </svg>
            Lista de Clientes
          </div>
          <div className="flex items-center gap-2">
            {[
              {
                label: "Importar",
                icon: (
                  <svg
                    width="12"
                    height="12"
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
                primary: false,
              },
              {
                label: "Exportar",
                icon: (
                  <svg
                    width="12"
                    height="12"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    strokeWidth="2"
                  >
                    <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
                    <polyline points="7 10 12 15 17 10" />
                    <line x1="12" y1="15" x2="12" y2="3" />
                  </svg>
                ),
                primary: false,
                action: exportarCSV,
              },
              {
                label: "Adicionar",
                icon: (
                  <svg
                    width="12"
                    height="12"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    strokeWidth="2.5"
                  >
                    <line x1="12" y1="5" x2="12" y2="19" />
                    <line x1="5" y1="12" x2="19" y2="12" />
                  </svg>
                ),
                primary: true,
              },
            ].map(function (b) {
              return (
                <button
                  key={b.label}
                  onClick={b.action || undefined}
                  className={
                    "flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium border transition-colors " +
                    (b.primary
                      ? "bg-[#2E6DA4] text-white border-[#2E6DA4] hover:bg-[#1B3A5C]"
                      : "bg-white text-[#3B4049] border-[#E8EFF7] hover:bg-[#E2EAF4]")
                  }
                >
                  {b.icon}
                  {b.label}
                </button>
              );
            })}
          </div>
        </div>

        <div className="flex items-center gap-2 px-5 py-3 border-b border-[#E8EFF7]">
          <div className="relative flex-1">
            <svg
              className="absolute left-2.5 top-1/2 -translate-y-1/2 text-[#9C9C9F]"
              width="13"
              height="13"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth="2"
            >
              <circle cx="11" cy="11" r="8" />
              <path d="m21 21-4.35-4.35" />
            </svg>
            <input
              className="w-full pl-8 pr-3 py-1.5 text-sm border border-[#E8EFF7] bg-[#E2EAF4] focus:outline-none focus:border-[#2E6DA4] focus:ring-1 focus:ring-[#2E6DA4]"
              placeholder="Buscar cliente..."
              value={search}
              onChange={function (e) {
                setSearch(e.target.value);
              }}
            />
          </div>
          <button className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium border border-[#E8EFF7] bg-white text-[#3B4049] hover:bg-[#E2EAF4] transition-colors">
            <svg
              width="12"
              height="12"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth="2"
            >
              <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3" />
            </svg>
            Filtrar
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-[#0D1B2A]">
                {[
                  "Cluster",
                  "Score",
                  "Status",
                  "Limite",
                  "Cadastro",
                  "Ações",
                ].map(function (h) {
                  return (
                    <th
                      key={h}
                      className="px-4 py-2.5 text-left text-[11px] font-semibold text-white uppercase tracking-wide"
                    >
                      {h}
                    </th>
                  );
                })}
              </tr>
            </thead>
            <tbody>
              {filtered.map(function (c) {
                return (
                  <tr
                    key={c.id}
                    className="border-b border-[#E2EAF4] hover:bg-[#E2EAF4] transition-colors"
                  >
                    <td className="px-4 py-3 text-sm font-semibold text-[#2E6DA4]">
                      {c.id}
                    </td>
                    <td className="px-4 py-3">
                      <ScoreBar score={c.score} />
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge status={c.status} />
                    </td>
                    <td className="px-4 py-3 text-sm font-medium text-[#0D1B2A]">
                      {c.limite ? fmt(c.limite) : "\u2014"}
                    </td>
                    <td className="px-4 py-3 text-sm text-[#9C9C9F]">
                      {c.cadastro}
                    </td>
                    <td className="px-4 py-3">
                      <DotsMenu />
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        <div className="flex items-center justify-between px-5 py-3 border-t border-[#E8EFF7]">
          <span className="text-xs text-[#9C9C9F]">
            Mostrando 1-{filtered.length} de {filtered.length}
          </span>
          <div className="flex items-center gap-1">
            <button className="px-3 h-7 text-xs text-[#9C9C9F] hover:bg-[#E2EAF4] transition-colors">
              Anterior
            </button>
            {[1, 2, 3].map(function (n) {
              return (
                <button
                  key={n}
                  onClick={function () {
                    setPageNum(n);
                  }}
                  className={
                    "w-7 h-7 text-xs font-medium transition-colors " +
                    (pageNum === n
                      ? "bg-[#2E6DA4] text-white"
                      : "text-[#3B4049] hover:bg-[#E2EAF4]")
                  }
                >
                  {n}
                </button>
              );
            })}
            <button className="px-3 h-7 text-xs text-[#9C9C9F] hover:bg-[#E2EAF4] transition-colors">
              Próximo
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
