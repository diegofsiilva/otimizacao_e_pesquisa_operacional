// pages/Resultados.js
// Deps globais: CLUSTER_LIMITES, STATUS_PIE, EVOLUCAO, SCORE_DIST, SOLVER_COMPARISON, fmt, fmtZ
//
// Regras aplicadas conforme brandbook PAN (gráficos):
// - Azul PAN (#2E6DA4) como cor principal em todos os gráficos
// - Rótulos de dados incluídos para garantir legibilidade
// - Sem gradientes, bordas decorativas ou efeitos visuais nos gráficos
// - Barras verticais para comparações, linha para evolução temporal, setor para proporções
// - Pesos Book/Medium para legendas e textos de apoio
// - Fundo branco para garantir contraste

// Gráfico de barras verticais - limites por cluster
// Azul PAN nas barras com valor; cinza neutro para clusters sem limite atribuído
var BarChartSVG = function (props) {
  var data = props.data;
  var w = 420;
  var h = 200;
  var pad = { top: 24, right: 10, bottom: 28, left: 48 };
  var cw = w - pad.left - pad.right;
  var ch = h - pad.top - pad.bottom;
  var max =
    Math.max.apply(
      null,
      data.map(function (d) {
        return d.value;
      }),
    ) || 1;
  var bw = Math.floor((cw / data.length) * 0.55);

  function fmtLabel(v) {
    if (v === 0) return null;
    if (v >= 1000) return "R$" + (v / 1000).toFixed(1) + "k";
    return "R$" + v;
  }

  return (
    <svg
      viewBox={"0 0 " + w + " " + h}
      width="100%"
      style={{ overflow: "visible" }}
    >
      {[0, 0.25, 0.5, 0.75, 1].map(function (f) {
        var y = pad.top + ch * (1 - f);
        return (
          <g key={f}>
            <line
              x1={pad.left}
              x2={pad.left + cw}
              y1={y}
              y2={y}
              stroke="#E8EFF7"
              strokeWidth="1"
            />
            <text
              x={pad.left - 6}
              y={y + 4}
              textAnchor="end"
              fontSize="9"
              fill="#9C9C9F"
            >
              {f === 0
                ? ""
                : max * f >= 1000
                  ? "R$" + ((max * f) / 1000).toFixed(0) + "k"
                  : "R$" + Math.round(max * f)}
            </text>
          </g>
        );
      })}
      {data.map(function (d, i) {
        var x = pad.left + (cw / data.length) * i + (cw / data.length - bw) / 2;
        var bh = d.value > 0 ? Math.max(ch * (d.value / max), 2) : 3;
        var y = pad.top + ch - bh;
        var label = fmtLabel(d.value);
        return (
          <g key={d.label}>
            <rect
              x={x}
              y={y}
              width={bw}
              height={bh}
              fill={d.value > 0 ? "#2E6DA4" : "#E8EFF7"}
            />
            {label && (
              <text
                x={x + bw / 2}
                y={y - 5}
                textAnchor="middle"
                fontSize="9"
                fontWeight="600"
                fill="#3B4049"
              >
                {label}
              </text>
            )}
            <text
              x={x + bw / 2}
              y={h - pad.bottom + 14}
              textAnchor="middle"
              fontSize="9"
              fill="#9C9C9F"
            >
              {d.label}
            </text>
          </g>
        );
      })}
    </svg>
  );
};

// Gráfico de linha - evolução temporal com rótulo em cada ponto
// data2 opcional: segunda série sobreposta (linha tracejada, cor de contraste)
var LineChartSVG = function (props) {
  var data = props.data;
  var data2 = props.data2 || null;
  var w = 420;
  var h = 175;
  var pad = { top: 24, right: 20, bottom: 24, left: 44 };
  var cw = w - pad.left - pad.right;
  var ch = h - pad.top - pad.bottom;
  var allValues = data.map(function (d) { return d.value; });
  if (data2) data2.forEach(function (d) { allValues.push(d.value); });
  var max = Math.max.apply(null, allValues) * 1.15 || 1;
  var pts = data.map(function (d, i) {
    return [
      pad.left + (cw / (data.length - 1)) * i,
      pad.top + ch - (ch * d.value) / max,
    ];
  });
  var polyline = pts
    .map(function (p) {
      return p[0] + "," + p[1];
    })
    .join(" ");
  var area =
    "M" +
    pts[0][0] +
    "," +
    pts[0][1] +
    pts
      .slice(1)
      .map(function (p) {
        return " L" + p[0] + "," + p[1];
      })
      .join("") +
    " L" +
    pts[pts.length - 1][0] +
    "," +
    (pad.top + ch) +
    " L" +
    pts[0][0] +
    "," +
    (pad.top + ch) +
    " Z";

  return (
    <svg
      viewBox={"0 0 " + w + " " + h}
      width="100%"
      style={{ overflow: "visible" }}
    >
      {[0, 0.5, 1].map(function (f) {
        var y = pad.top + ch * (1 - f);
        return (
          <g key={f}>
            <line
              x1={pad.left}
              x2={pad.left + cw}
              y1={y}
              y2={y}
              stroke="#E8EFF7"
              strokeWidth="1"
            />
            <text
              x={pad.left - 6}
              y={y + 4}
              textAnchor="end"
              fontSize="9"
              fill="#9C9C9F"
            >
              {f > 0 ? "R$" + (max * f).toFixed(0) + "M" : ""}
            </text>
          </g>
        );
      })}
      <path d={area} fill="#2E6DA4" fillOpacity="0.08" />
      <polyline
        points={polyline}
        fill="none"
        stroke="#2E6DA4"
        strokeWidth="2.5"
        strokeLinejoin="round"
      />
      {pts.map(function (p, i) {
        var d = data[i];
        var labelY = i % 2 === 0 ? p[1] - 10 : p[1] + 18;
        return (
          <g key={i}>
            <circle cx={p[0]} cy={p[1]} r="4" fill="#2E6DA4" stroke="#fff" strokeWidth="2" />
            <text x={p[0]} y={labelY} textAnchor="middle" fontSize="9" fontWeight="600" fill="#3B4049">
              R${d.value.toFixed(1)}M
            </text>
            <text x={p[0]} y={h - pad.bottom + 14} textAnchor="middle" fontSize="9" fill="#9C9C9F">
              {d.label}
            </text>
          </g>
        );
      })}
      {data2 && (function () {
        var pts2 = data2.map(function (d, i) {
          return [pad.left + (cw / (data2.length - 1)) * i, pad.top + ch - (ch * d.value) / max];
        });
        var poly2 = pts2.map(function (p) { return p[0] + "," + p[1]; }).join(" ");
        return (
          <g>
            <polyline points={poly2} fill="none" stroke="#FAE95D" strokeWidth="2" strokeDasharray="5,3" strokeLinejoin="round" />
            {pts2.map(function (p, i) {
              return (
                <circle key={i} cx={p[0]} cy={p[1]} r="3.5" fill="#FAE95D" stroke="#fff" strokeWidth="1.5" />
              );
            })}
          </g>
        );
      })()}
    </svg>
  );
};

// Gráfico de distribuição de score - barras verticais com rótulo de contagem
var AreaChartSVG = function (props) {
  var data = props.data;
  var w = 420;
  var h = 175;
  var pad = { top: 24, right: 10, bottom: 28, left: 40 };
  var cw = w - pad.left - pad.right;
  var ch = h - pad.top - pad.bottom;
  var max =
    Math.max.apply(
      null,
      data.map(function (d) {
        return d.value;
      }),
    ) * 1.1 || 1;
  var bw = Math.floor((cw / data.length) * 0.7);

  return (
    <svg
      viewBox={"0 0 " + w + " " + h}
      width="100%"
      style={{ overflow: "visible" }}
    >
      {[0, 0.5, 1].map(function (f) {
        var y = pad.top + ch * (1 - f);
        return (
          <g key={f}>
            <line
              x1={pad.left}
              x2={pad.left + cw}
              y1={y}
              y2={y}
              stroke="#E8EFF7"
              strokeWidth="1"
            />
            <text
              x={pad.left - 6}
              y={y + 4}
              textAnchor="end"
              fontSize="9"
              fill="#9C9C9F"
            >
              {f > 0 ? Math.round(max * f) : ""}
            </text>
          </g>
        );
      })}
      {data.map(function (d, i) {
        var x = pad.left + (cw / data.length) * i + (cw / data.length - bw) / 2;
        var bh = Math.max(ch * (d.value / max), 2);
        var y = pad.top + ch - bh;
        return (
          <g key={d.score}>
            <rect
              x={x}
              y={y}
              width={bw}
              height={bh}
              fill="#2E6DA4"
              fillOpacity="0.85"
            />
            <text
              x={x + bw / 2}
              y={y - 5}
              textAnchor="middle"
              fontSize="8"
              fontWeight="600"
              fill="#3B4049"
            >
              {d.value}
            </text>
            <text
              x={x + bw / 2}
              y={h - pad.bottom + 14}
              textAnchor="middle"
              fontSize="8"
              fill="#9C9C9F"
            >
              {d.label}
            </text>
          </g>
        );
      })}
    </svg>
  );
};

// Gráfico de setor (donut) - proporções de status
// Legenda lateral com percentuais garante rótulos legíveis sem poluir o gráfico
var DonutChart = function (props) {
  var data = props.data;
  var r = 60;
  var ri = 38;
  var cx = 80;
  var cy = 80;
  var total = data.reduce(function (s, d) {
    return s + d.value;
  }, 0);
  var slices = [];
  var angle = -90;
  data.forEach(function (d) {
    var sweep = (d.value / total) * 360;
    var a1 = (angle * Math.PI) / 180;
    var a2 = ((angle + sweep) * Math.PI) / 180;
    var x1 = cx + r * Math.cos(a1);
    var y1 = cy + r * Math.sin(a1);
    var x2 = cx + r * Math.cos(a2);
    var y2 = cy + r * Math.sin(a2);
    var xi1 = cx + ri * Math.cos(a1);
    var yi1 = cy + ri * Math.sin(a1);
    var xi2 = cx + ri * Math.cos(a2);
    var yi2 = cy + ri * Math.sin(a2);
    var large = sweep > 180 ? 1 : 0;
    slices.push({
      path:
        "M" +
        x1 +
        "," +
        y1 +
        " A" +
        r +
        "," +
        r +
        " 0 " +
        large +
        ",1 " +
        x2 +
        "," +
        y2 +
        " L" +
        xi2 +
        "," +
        yi2 +
        " A" +
        ri +
        "," +
        ri +
        " 0 " +
        large +
        ",0 " +
        xi1 +
        "," +
        yi1 +
        " Z",
      color: d.color,
    });
    angle += sweep;
  });

  return (
    <svg viewBox="0 0 160 160" width="160" height="160">
      {slices.map(function (s, i) {
        return <path key={i} d={s.path} fill={s.color} />;
      })}
      <circle cx={cx} cy={cy} r={ri - 2} fill="white" />
    </svg>
  );
};

var EVOLUCAO_PREV = [
  { mes: "Jan", value: 6.8 },
  { mes: "Fev", value: 7.5 },
  { mes: "Mar", value: 8.3 },
  { mes: "Abr", value: 9.1 },
  { mes: "Mai", value: 10.4 },
  { mes: "Jun", value: 12.2 },
];

var Resultados = function (props) {
  var hasData = props.hasData;
  var setPage = props.setPage;
  var sc1 = React.useState(false);
  var showComparison = sc1[0]; var setShowComparison = sc1[1];

  if (!hasData) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-xl font-bold text-[#0D1B2A]">
            Resultados da Simulação
          </h1>
          <p className="mt-1 text-xs text-[#9C9C9F]">
            Nenhuma simulação executada
          </p>
          <div className="mt-1 h-0.5 w-10 bg-[#2E6DA4]" />
        </div>
        <div className="bg-white border border-[#E8EFF7] shadow-sm flex flex-col items-center justify-center py-20 px-6 text-center gap-5">
          <div className="w-14 h-14 bg-[#D6E8F5] flex items-center justify-center">
            <svg
              width="24"
              height="24"
              fill="none"
              viewBox="0 0 24 24"
              stroke="#2E6DA4"
              strokeWidth="1.5"
            >
              <polyline points="22 7 13.5 15.5 8.5 10.5 2 17" />
              <polyline points="16 7 22 7 22 13" />
            </svg>
          </div>
          <div>
            <p className="text-sm font-semibold text-[#0D1B2A] mb-1">
              Nenhuma simulação executada
            </p>
            <p className="text-xs text-[#9C9C9F] max-w-xs">
              Carregue uma base e execute o Simplex em{" "}
              <strong className="text-[#0D1B2A]">Gerar Limites</strong> para
              visualizar os resultados aqui.
            </p>
          </div>
          <button
            onClick={function () {
              if (setPage) setPage("gerar");
            }}
            className="flex items-center gap-2 px-5 py-2.5 text-sm font-semibold bg-[#2E6DA4] text-white hover:bg-[#1B3A5C] transition-colors shadow-sm"
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
            Ir para Gerar Limites
          </button>
        </div>
      </div>
    );
  }

  function exportarLimites() {
    var sc = SOLVER_COMPARISON;
    var header = ["Cluster", "Simplex (R$)", "PuLP/CBC (R$)", "Match"];
    var rows = sc.simplex.clusters.map(function (cs, i) {
      var cp = sc.pulp.clusters[i];
      var match = cs.limite === cp.limite ? "Sim" : "Não";
      return [cs.id, cs.limite || 0, cp.limite || 0, match];
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
    a.download = "limites_clusters.csv";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  var KPIs = [
    {
      label: "Total de Clusters",
      value: "73",
      sub: "\u2191 5 novos clusters",
      highlight: false,
    },
    {
      label: "Limite Total Aprovado",
      value: "R$ 127,4M",
      sub: "\u2191 8,5% vs mês anterior",
      highlight: true,
    },
    {
      label: "Clientes Ativos",
      value: "48.320",
      sub: "\u2191 12 novos este mês",
      highlight: false,
    },
    {
      label: "Taxa de Aprovação",
      value: "87,3%",
      sub: "\u2191 2,3% vs ano anterior",
      highlight: false,
    },
  ];

  var sc = SOLVER_COMPARISON;
  var barData = CLUSTER_LIMITES.map(function (d) {
    return { label: d.name, value: d.limite };
  });
  var lineData = EVOLUCAO.map(function (d) {
    return { label: d.mes, value: d.valor };
  });
  var areaData = SCORE_DIST.map(function (d) {
    return { label: d.score, value: d.n };
  });

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-xl font-bold text-[#0D1B2A]">
            Resultados da Simulação
          </h1>
          <p className="mt-1 text-xs text-[#9C9C9F]">
            Output do algoritmo Simplex · simulação executada em Mai/2025
          </p>
          <div className="mt-1 h-0.5 w-10 bg-[#2E6DA4]" />
        </div>
        <button
          onClick={exportarLimites}
          className="flex items-center gap-2 px-4 py-2 text-sm font-semibold border border-[#E8EFF7] bg-white text-[#3B4049] hover:bg-[#E2EAF4] transition-colors shadow-sm"
        >
          <svg
            width="13"
            height="13"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth="2"
          >
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
            <polyline points="7 10 12 15 17 10" />
            <line x1="12" y1="15" x2="12" y2="3" />
          </svg>
          Exportar CSV
        </button>
      </div>

      <div className="flex items-center gap-3 px-4 py-3 bg-[#D6E8F5] border border-[#2E6DA4]/30 text-sm text-[#1B3A5C]">
        <svg
          width="16"
          height="16"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth="2"
          className="flex-shrink-0"
        >
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="8" x2="12" y2="12" />
          <line x1="12" y1="16" x2="12.01" y2="16" />
        </svg>
        <span>
          Indicadores da última execução do Simplex. Para nova simulação, acesse{" "}
          <strong>Gerar Limites</strong>.
        </span>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-4 gap-4">
        {KPIs.map(function (k) {
          return (
            <div
              key={k.label}
              className={
                "rounded-xl border shadow-sm p-5 " +
                (k.highlight
                  ? "border-[#2E6DA4]/40 bg-[#D6E8F5]"
                  : "bg-white border-[#E8EFF7]")
              }
            >
              <div className="text-xs font-medium text-[#9C9C9F] mb-2">
                {k.label}
              </div>
              <div
                className={
                  "text-2xl font-bold mb-1 " +
                  (k.highlight ? "text-[#2E6DA4]" : "text-[#0D1B2A]")
                }
              >
                {k.value}
              </div>
              <div className="text-xs text-[#9C9C9F]">{k.sub}</div>
            </div>
          );
        })}
      </div>

      {/* Gráficos linha 1 */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white border border-[#E8EFF7] shadow-sm p-5">
          <div className="text-sm font-semibold text-[#0D1B2A] mb-1">
            Limites por Cluster
          </div>
          <div className="text-xs text-[#9C9C9F] mb-4">
            Limite ótimo atribuído a cada cluster pelo Simplex (R$)
          </div>
          <BarChartSVG data={barData} />
        </div>

        <div className="bg-white border border-[#E8EFF7] shadow-sm p-5">
          <div className="text-sm font-semibold text-[#0D1B2A] mb-1">
            Distribuição por Status
          </div>
          <div className="text-xs text-[#9C9C9F] mb-4">
            Proporção de clientes por situação na carteira
          </div>
          <div className="flex items-center gap-6">
            <DonutChart data={STATUS_PIE} />
            <div className="space-y-3 flex-1">
              {STATUS_PIE.map(function (d) {
                return (
                  <div key={d.name} className="flex items-center gap-2 text-sm">
                    <div
                      className="w-2.5 h-2.5 flex-shrink-0"
                      style={{ background: d.color }}
                    />
                    <span className="font-medium text-[#3B4049] flex-1">
                      {d.name}
                    </span>
                    <span className="font-semibold text-[#0D1B2A]">
                      {d.value}%
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white border border-[#E8EFF7] shadow-sm p-5">
        <div className="mb-1 text-sm font-semibold text-[#0D1B2A]">
          Comparação de Solvers: Simplex vs PuLP
        </div>
        <div className="text-xs text-[#9C9C9F] mb-5">
          Validação da solução ótima com biblioteca externa (PuLP / CBC)
        </div>

        <div className="grid grid-cols-2 gap-3 mb-5">
          {[sc.simplex, sc.pulp].map(function (s) {
            return (
              <div
                key={s.label}
                className="rounded-xl border border-[#E8EFF7] bg-[#E2EAF4] p-4"
              >
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-semibold text-[#3B4049]">
                    {s.label}
                  </span>
                  <span className="inline-flex items-center px-2 py-0.5 text-[11px] font-medium bg-[#67DE98]/20 text-[#2E6DA4] border border-[#67DE98]/50">
                    {s.status}
                  </span>
                </div>
                <div className="text-2xl font-bold text-[#2E6DA4] mb-1">
                  {fmtZ(s.z)}
                </div>
                <div className="text-xs text-[#9C9C9F]">Valor objetivo (z)</div>
                <div className="text-xs text-[#9C9C9F] mt-1">
                  Tempo:{" "}
                  <span className="font-medium text-[#3B4049]">
                    {s.tempo_ms} ms
                  </span>
                </div>
              </div>
            );
          })}
        </div>

        <div className="overflow-x-auto border border-[#E8EFF7]">
          <table className="w-full text-xs">
            <thead>
              <tr className="bg-[#0D1B2A]">
                {["Cluster", "Simplex (R$)", "PuLP / CBC (R$)", "Match"].map(
                  function (h) {
                    return (
                      <th
                        key={h}
                        className="px-3 py-2.5 text-left font-semibold text-white uppercase tracking-wide whitespace-nowrap"
                      >
                        {h}
                      </th>
                    );
                  },
                )}
              </tr>
            </thead>
            <tbody>
              {sc.simplex.clusters.map(function (cs, i) {
                var cp = sc.pulp.clusters[i];
                var match = cs.limite === cp.limite;
                return (
                  <tr
                    key={cs.id}
                    className={
                      "border-t border-[#E8EFF7] " +
                      (i % 2 === 0 ? "" : "bg-[#E2EAF4]/60")
                    }
                  >
                    <td className="px-3 py-2 font-mono font-semibold text-[#2E6DA4]">
                      {cs.id}
                    </td>
                    <td className="px-3 py-2 text-[#3B4049]">
                      {cs.limite ? fmt(cs.limite) : "\u2014"}
                    </td>
                    <td className="px-3 py-2 text-[#3B4049]">
                      {cp.limite ? fmt(cp.limite) : "\u2014"}
                    </td>
                    <td className="px-3 py-2">
                      {match ? (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 text-[11px] font-medium bg-[#67DE98]/20 text-[#2E6DA4] border border-[#67DE98]/50">
                          <svg
                            width="10"
                            height="10"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                            strokeWidth="3"
                          >
                            <polyline points="20 6 9 17 4 12" />
                          </svg>
                          Idêntico
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 text-[11px] font-medium bg-[#FAE95D]/30 text-[#3B4049] border border-[#FAE95D]/70">
                          <svg
                            width="10"
                            height="10"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                            strokeWidth="3"
                          >
                            <line x1="12" y1="5" x2="12" y2="19" />
                            <line x1="5" y1="12" x2="19" y2="12" />
                          </svg>
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

        <div className="mt-3 text-xs text-[#9C9C9F]">
          Delta z ={" "}
          <span className="font-semibold text-[#3B4049]">
            {(sc.delta_z_pct * 100).toFixed(4)}%
          </span>
          {" · "}PD financeiro atual:{" "}
          <span className="font-semibold text-[#3B4049]">
            {(sc.pd_fin_atual * 100).toFixed(2)}%
          </span>
        </div>
      </div>

      {/* Gráficos linha 2 */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white border border-[#E8EFF7] shadow-sm p-5">
          <div className="flex items-start justify-between mb-1">
            <div className="text-sm font-semibold text-[#0D1B2A]">Evolução do Limite Total</div>
            <button
              onClick={function () { setShowComparison(function (v) { return !v; }); }}
              className={"flex items-center gap-1.5 px-2.5 py-1 text-[11px] font-medium border transition-colors " + (showComparison ? "bg-[#2E6DA4] text-white border-[#2E6DA4]" : "border-[#E8EFF7] text-[#3B4049] hover:bg-[#E2EAF4]")}
            >
              <svg width="11" height="11" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5"><path d="M8 3H5a2 2 0 00-2 2v3m18 0V5a2 2 0 00-2-2h-3M3 16v3a2 2 0 002 2h3m8 0h3a2 2 0 002-2v-3"/></svg>
              Comparar simulação anterior
            </button>
          </div>
          <div className="text-xs text-[#9C9C9F] mb-3">
            Crescimento mensal do limite aprovado em R$ milhões
          </div>
          {showComparison && (
            <div className="flex items-center gap-4 mb-3 text-xs">
              <span className="flex items-center gap-1.5"><span className="inline-block w-6 h-0.5 bg-[#2E6DA4]"></span><span className="text-[#3B4049] font-medium">Simulação atual (Mai/2025)</span></span>
              <span className="flex items-center gap-1.5"><span className="inline-block w-6 border-t-2 border-dashed border-[#FAE95D]"></span><span className="text-[#3B4049] font-medium">Simulação anterior (Abr/2025)</span></span>
            </div>
          )}
          <LineChartSVG data={lineData} data2={showComparison ? EVOLUCAO_PREV : null} />
        </div>

        <div className="bg-white border border-[#E8EFF7] shadow-sm p-5">
          <div className="text-sm font-semibold text-[#0D1B2A] mb-1">
            Distribuição de Score
          </div>
          <div className="text-xs text-[#9C9C9F] mb-4">
            Número de clientes por faixa de score de crédito
          </div>
          <AreaChartSVG data={areaData} />
        </div>
      </div>
    </div>
  );
};
