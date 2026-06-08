// pages/Cockpit.js  (componente: Cockpit)
// Deps globais: Api (api.js), fmt, fmtZ (data.js)
//
// Carrega ao montar:
//   1. GET /api/consultas  → encontra a mais recente concluída (atual) e a anterior
//   2. GET /api/safras     → resolve nome da safra (M1, M2...)
//   3. GET /api/consultas/{id}/clusters → tabela e KPIs derivados
//
// KPIs exibem delta vs a consulta anterior concluída quando disponível.

var Cockpit = function (props) {
  var setPage = props.setPage;

  // -------------------------------------------------------------------------
  // Estado
  // -------------------------------------------------------------------------

  var s1 = React.useState(null);
  var consultaAtual = s1[0];
  var setConsultaAtual = s1[1];

  var s2 = React.useState(null);
  var consultaAnterior = s2[0];
  var setConsultaAnterior = s2[1];

  var s3 = React.useState(null);
  var safraAtual = s3[0];
  var setSafraAtual = s3[1];

  var s4 = React.useState([]);
  var clusters = s4[0];
  var setClusters = s4[1];

  var s5 = React.useState(true);
  var loading = s5[0];
  var setLoading = s5[1];

  var s6 = React.useState(null);
  var erroLoad = s6[0];
  var setErroLoad = s6[1];

  var s7 = React.useState("");
  var search = s7[0];
  var setSearch = s7[1];

  var s8 = React.useState(1);
  var pageNum = s8[0];
  var setPageNum = s8[1];

  var TABLE_PER_PAGE = 15;

  // -------------------------------------------------------------------------
  // Carrega dados ao montar
  // -------------------------------------------------------------------------

  React.useEffect(function () {
    Promise.all([Api.listConsultas(), Api.listSafras()])
      .then(function (results) {
        var consultas = results[0];
        var safras = results[1];

        var concluidas = consultas.filter(function (c) {
          return c.status_consulta === "concluido";
        });

        if (concluidas.length === 0) {
          setLoading(false);
          return;
        }

        var atual = concluidas[0];
        var anterior = concluidas[1] || null;

        setConsultaAtual(atual);
        setConsultaAnterior(anterior);

        var safra = null;
        for (var i = 0; i < safras.length; i++) {
          if (safras[i].id === atual.safra_id) {
            safra = safras[i];
            break;
          }
        }
        setSafraAtual(safra);

        return Api.getClusters(atual.id).then(function (cls) {
          setClusters(cls || []);
          setLoading(false);
        });
      })
      .catch(function (err) {
        setErroLoad(err.message || "Erro ao carregar dados.");
        setLoading(false);
      });
  }, []);

  // -------------------------------------------------------------------------
  // Helpers
  // -------------------------------------------------------------------------

  function formatDateTime(iso) {
    if (!iso) return "-";
    return new Date(iso).toLocaleString("pt-BR", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  // Formata delta numérico como "+1.234" / "-1.234" / "="
  function formatDelta(atual, anterior) {
    if (atual == null || anterior == null) return null;
    var d = atual - anterior;
    if (d === 0) return { label: "=", trend: "neutral" };
    var abs = Math.abs(d);
    var label = (d > 0 ? "+" : "-") + Number(abs).toLocaleString("pt-BR");
    return { label: label, trend: d > 0 ? "up" : "down" };
  }

  // Formata delta percentual como "+1,23%" / "-0,45%"
  function formatDeltaPct(atual, anterior) {
    if (atual == null || anterior == null || anterior === 0) return null;
    var d = ((atual - anterior) / anterior) * 100;
    if (Math.abs(d) < 0.01) return { label: "=", trend: "neutral" };
    var label = (d > 0 ? "+" : "") + d.toFixed(2) + "%";
    return { label: label, trend: d > 0 ? "up" : "down" };
  }

  function getLimitePulp(c) {
    if (!c) return null;
    if (c.limite_pulp != null) return c.limite_pulp;
    if (c.limite_pulp_otimizado != null) return c.limite_pulp_otimizado;
    if (c.pulp_limite_otimizado != null) return c.pulp_limite_otimizado;
    return null;
  }

  // -------------------------------------------------------------------------
  // Exportar clusters como CSV (gerado no browser)
  // -------------------------------------------------------------------------

  function exportarClusters() {
    var header = [
      "Cluster ID",
      "Clientes",
      "PD Média (%)",
      "Score Cross Médio",
      "Fator Alavancagem",
      "Limite Otimizado (R$)",
      "Limite PuLP (R$)",
      "Delta vs PuLP (R$)",
      "Status",
    ];
    var rows = clusters.map(function (c) {
      var limitePulp = getLimitePulp(c);
      var deltaPulp =
        limitePulp == null ? "" : (c.limite_otimizado || 0) - limitePulp;
      return [
        "CLU-" + c.cluster_id,
        c.n_clientes,
        (c.pd_media * 100).toFixed(2),
        Math.round(c.score_credito_cross_medio),
        c.fator_alavancagem.toFixed(2),
        c.limite_otimizado || "",
        limitePulp == null ? "" : limitePulp,
        deltaPulp,
        c.limite_otimizado > 0 ? "Viável" : "Sem Solução",
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
    a.download =
      "clusters_" + (safraAtual ? safraAtual.nome : "atual") + ".csv";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  // -------------------------------------------------------------------------
  // Derivados
  // -------------------------------------------------------------------------

  var filtered = clusters.filter(function (c) {
    return (
      ("CLU-" + c.cluster_id).toLowerCase().indexOf(search.toLowerCase()) !== -1
    );
  });

  var totalPaginas = Math.max(1, Math.ceil(filtered.length / TABLE_PER_PAGE));
  var clustersPaginados = filtered.slice(
    (pageNum - 1) * TABLE_PER_PAGE,
    pageNum * TABLE_PER_PAGE,
  );

  // Conta clusters viáveis (limite > 0)
  var nViavel = clusters.filter(function (c) {
    return c.limite_otimizado > 0;
  }).length;
  var nViavelPulp = clusters.filter(function (c) {
    return getLimitePulp(c) > 0;
  }).length;
  var temComparacaoPulp = clusters.some(function (c) {
    return getLimitePulp(c) != null;
  });

  // -------------------------------------------------------------------------
  // KPI cards - dados reais com delta vs consulta anterior
  // -------------------------------------------------------------------------

  var kpis = consultaAtual
    ? [
        {
          label: "Total de Clientes",
          period: "na base processada",
          value:
            consultaAtual.n_clientes_total != null
              ? Number(consultaAtual.n_clientes_total).toLocaleString("pt-BR")
              : "-",
          delta: formatDelta(
            consultaAtual.n_clientes_total,
            consultaAnterior && consultaAnterior.n_clientes_total,
          ),
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
          period: "segmentação CART",
          value:
            consultaAtual.n_clusters != null
              ? String(consultaAtual.n_clusters)
              : "-",
          delta: formatDelta(
            consultaAtual.n_clusters,
            consultaAnterior && consultaAnterior.n_clusters,
          ),
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
              <rect x="2" y="17" width="20" height="4" />
              <rect x="2" y="11" width="20" height="4" />
              <rect x="2" y="5" width="20" height="4" />
            </svg>
          ),
        },
        {
          label: "Clientes Elegíveis",
          period: "aptos à otimização",
          value:
            consultaAtual.n_clientes_elegiveis != null
              ? Number(consultaAtual.n_clientes_elegiveis).toLocaleString(
                  "pt-BR",
                )
              : "-",
          delta: formatDelta(
            consultaAtual.n_clientes_elegiveis,
            consultaAnterior && consultaAnterior.n_clientes_elegiveis,
          ),
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
              <path d="M22 11.08V12a10 10 0 11-5.93-9.14" />
              <polyline points="22 4 12 14.01 9 11.01" />
            </svg>
          ),
        },
        {
          label: "Valor Objetivo (z)",
          period:
            consultaAtual.status_lp === "multiplas_solucoes"
              ? "Múltiplas soluções"
              : "Solução ótima · Simplex",
          value:
            consultaAtual.z_otimo != null ? fmtZ(consultaAtual.z_otimo) : "-",
          delta: formatDeltaPct(
            consultaAtual.z_otimo,
            consultaAnterior && consultaAnterior.z_otimo,
          ),
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
              <polyline points="22 7 13.5 15.5 8.5 10.5 2 17" />
              <polyline points="16 7 22 7 22 13" />
            </svg>
          ),
        },
      ]
    : [];

  // -------------------------------------------------------------------------
  // Render - estado de carregamento
  // -------------------------------------------------------------------------

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-xl font-bold text-[#0D1B2A]">Cockpit</h1>
          <div className="mt-1 h-0.5 w-10 bg-[#2E6DA4]" />
        </div>
        <div className="flex items-center justify-center py-24 gap-2 text-sm text-[#9C9C9F]">
          <svg
            className="animate-spin"
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="#2E6DA4"
            strokeWidth="2"
          >
            <path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0" />
          </svg>
          Carregando dados da última simulação...
        </div>
      </div>
    );
  }

  // -------------------------------------------------------------------------
  // Render - estado vazio (nenhuma simulação concluída)
  // -------------------------------------------------------------------------

  if (!consultaAtual) {
    return (
      <div className="space-y-6">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-xl font-bold text-[#0D1B2A]">Cockpit</h1>
            <p className="mt-1 text-xs text-[#9C9C9F]">
              Nenhuma simulação concluída ainda
            </p>
            <div className="mt-1 h-0.5 w-10 bg-[#2E6DA4]" />
          </div>
        </div>

        {erroLoad && (
          <div className="flex items-center gap-2 px-4 py-3 bg-[#FF5D5C]/10 border border-[#FF5D5C]/30 text-xs text-[#DC2F37]">
            <svg
              width="13"
              height="13"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth="2.5"
            >
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            {erroLoad}
          </div>
        )}

        <div className="bg-white border border-[#E8EFF7] shadow-sm flex flex-col items-center justify-center py-24 px-6 text-center gap-5">
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
              Nenhuma simulação concluída
            </p>
            <p className="text-xs text-[#9C9C9F] max-w-xs">
              Faça upload de uma base .parquet em{" "}
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

  // -------------------------------------------------------------------------
  // Render - estado normal (consulta concluída disponível)
  // -------------------------------------------------------------------------

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-xl font-bold text-[#0D1B2A]">Cockpit</h1>
          <p className="mt-1 text-xs text-[#9C9C9F]">
            Visão geral da última simulação
            {safraAtual ? " · Safra " + safraAtual.nome : ""}
            {" · "}
            {formatDateTime(consultaAtual.concluido_em)}
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

      {/* Banner de referência quando há consulta anterior */}
      {consultaAnterior && (
        <div className="flex items-center gap-2 px-4 py-2.5 bg-[#E2EAF4] border border-[#E8EFF7] text-xs text-[#9C9C9F]">
          <svg
            width="12"
            height="12"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth="2"
          >
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          Deltas calculados em relação à simulação anterior
          {consultaAnterior.concluido_em
            ? " (" + formatDateTime(consultaAnterior.concluido_em) + ")"
            : ""}
          .
        </div>
      )}

      {/* KPI cards */}
      <div className="grid grid-cols-4 gap-4">
        {kpis.map(function (k) {
          var delta = k.delta;
          var badgeCls = !delta
            ? ""
            : delta.trend === "up"
              ? "bg-[#67DE98]/20 text-[#1a7a4a]"
              : delta.trend === "down"
                ? "bg-[#FF5D5C]/20 text-[#DC2F37]"
                : "bg-[#B8D4EC]/40 text-[#3B4049]";
          var arrow = !delta ? null : delta.trend === "up" ? (
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
          ) : delta.trend === "down" ? (
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
              <div className="flex items-end justify-between">
                <div className="text-2xl font-bold text-[#0D1B2A] leading-none">
                  {k.value}
                </div>
                {delta ? (
                  <span
                    className={
                      "inline-flex items-center gap-0.5 px-2 py-0.5 text-[11px] font-semibold " +
                      badgeCls
                    }
                  >
                    {arrow}
                    {delta.label}
                  </span>
                ) : (
                  <span className="text-[11px] text-[#B8D4EC]">-</span>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Tabela de clusters */}
      <div className="bg-white border border-[#E8EFF7] shadow-sm overflow-hidden">
        {/* Header da tabela */}
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
              <rect x="2" y="17" width="20" height="4" />
              <rect x="2" y="11" width="20" height="4" />
              <rect x="2" y="5" width="20" height="4" />
            </svg>
            Clusters
            {temComparacaoPulp && (
              <span className="text-[11px] font-normal text-[#9C9C9F]">
                PuLP: {nViavelPulp}
              </span>
            )}
            {clusters.length > 0 && (
              <span className="text-[11px] font-normal text-[#9C9C9F]">
                - {nViavel} viáveis · {clusters.length - nViavel} sem solução
              </span>
            )}
          </div>
          <button
            onClick={exportarClusters}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium border border-[#E8EFF7] bg-white text-[#3B4049] hover:bg-[#E2EAF4] transition-colors"
          >
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
            Exportar CSV
          </button>
        </div>

        {/* Busca */}
        <div className="px-5 py-3 border-b border-[#E8EFF7]">
          <div className="relative max-w-xs">
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
              placeholder="Buscar cluster..."
              value={search}
              onChange={function (e) {
                setSearch(e.target.value);
                setPageNum(1);
              }}
            />
          </div>
        </div>

        {/* Tabela */}
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-[#0D1B2A]">
                {[
                  "Cluster ID",
                  "Clientes",
                  "PD Média",
                  "Score Cross Médio",
                  "Fator Alavancagem",
                  "Limite Otimizado",
                  "Limite PuLP",
                  "Delta",
                  "Status",
                ].map(function (h) {
                  return (
                    <th
                      key={h}
                      className="px-4 py-2.5 text-left text-[11px] font-semibold text-white uppercase tracking-wide whitespace-nowrap"
                    >
                      {h}
                    </th>
                  );
                })}
              </tr>
            </thead>
            <tbody>
              {clustersPaginados.length === 0 ? (
                <tr>
                  <td
                    colSpan="9"
                    className="px-4 py-10 text-center text-sm text-[#9C9C9F]"
                  >
                    Nenhum cluster encontrado
                  </td>
                </tr>
              ) : (
                clustersPaginados.map(function (c, i) {
                  var viavel = c.limite_otimizado > 0;
                  var limitePulp = getLimitePulp(c);
                  var deltaPulp =
                    limitePulp == null ? null : c.limite_otimizado - limitePulp;
                  return (
                    <tr
                      key={c.cluster_id}
                      className={
                        "border-b border-[#E2EAF4] hover:bg-[#E2EAF4] transition-colors " +
                        (i % 2 === 0 ? "" : "bg-[#F7FAFD]")
                      }
                    >
                      <td className="px-4 py-3 font-mono font-semibold text-[#2E6DA4]">
                        CLU-{c.cluster_id}
                      </td>
                      <td className="px-4 py-3 font-medium text-[#0D1B2A]">
                        {Number(c.n_clientes).toLocaleString("pt-BR")}
                      </td>
                      <td className="px-4 py-3 text-[#3B4049]">
                        {(c.pd_media * 100).toFixed(2)}%
                      </td>
                      <td className="px-4 py-3 text-[#3B4049]">
                        {Math.round(c.score_credito_cross_medio)}
                      </td>
                      <td className="px-4 py-3 text-[#3B4049]">
                        {c.fator_alavancagem.toFixed(2)}x
                      </td>
                      <td className="px-4 py-3 font-semibold text-[#0D1B2A]">
                        {viavel ? fmt(c.limite_otimizado) : "-"}
                      </td>
                      <td className="px-4 py-3 font-semibold text-[#3B4049]">
                        {limitePulp != null && limitePulp > 0
                          ? fmt(limitePulp)
                          : limitePulp === 0
                            ? "-"
                            : "N/D"}
                      </td>
                      <td className="px-4 py-3 text-[#3B4049]">
                        {deltaPulp == null
                          ? "N/D"
                          : deltaPulp === 0
                            ? "="
                            : (deltaPulp > 0 ? "+" : "") + fmt(deltaPulp)}
                      </td>
                      <td className="px-4 py-3">
                        {viavel ? (
                          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 text-xs font-semibold bg-[#67DE98]/20 text-[#1a7a4a] border border-[#67DE98]/50">
                            <svg
                              width="9"
                              height="9"
                              fill="none"
                              viewBox="0 0 24 24"
                              stroke="currentColor"
                              strokeWidth="3"
                            >
                              <polyline points="20 6 9 17 4 12" />
                            </svg>
                            Viável
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 text-xs font-semibold bg-[#FF5D5C]/10 text-[#DC2F37] border border-[#FF5D5C]/30">
                            <svg
                              width="9"
                              height="9"
                              fill="none"
                              viewBox="0 0 24 24"
                              stroke="currentColor"
                              strokeWidth="3"
                            >
                              <line x1="18" y1="6" x2="6" y2="18" />
                              <line x1="6" y1="6" x2="18" y2="18" />
                            </svg>
                            Sem Solução
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Paginação */}
        <div className="flex items-center justify-between px-5 py-3 border-t border-[#E8EFF7]">
          <span className="text-xs text-[#9C9C9F]">
            {filtered.length > 0
              ? (pageNum - 1) * TABLE_PER_PAGE +
                1 +
                "–" +
                Math.min(pageNum * TABLE_PER_PAGE, filtered.length) +
                " de " +
                filtered.length +
                " clusters"
              : "0 clusters"}
          </span>
          {totalPaginas > 1 && (
            <div className="flex items-center gap-1">
              <button
                disabled={pageNum === 1}
                onClick={function () {
                  setPageNum(function (p) {
                    return p - 1;
                  });
                }}
                className="px-3 h-7 text-xs text-[#9C9C9F] hover:bg-[#E2EAF4] disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              >
                Anterior
              </button>
              {Array.from(
                { length: Math.min(5, totalPaginas) },
                function (_, i) {
                  var start = Math.max(
                    1,
                    Math.min(pageNum - 2, totalPaginas - 4),
                  );
                  var n = start + i;
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
                },
              )}
              <button
                disabled={pageNum === totalPaginas}
                onClick={function () {
                  setPageNum(function (p) {
                    return p + 1;
                  });
                }}
                className="px-3 h-7 text-xs text-[#9C9C9F] hover:bg-[#E2EAF4] disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              >
                Próximo
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
