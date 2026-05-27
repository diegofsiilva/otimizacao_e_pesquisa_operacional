// pages/GerarLimites.js
// Deps globais: CLUSTERS_UPLOAD, CLUSTER_LIMITES, STATUS_PIE, EVOLUCAO, SCORE_DIST, SOLVER_COMPARISON, fmt, fmtZ
// Após execução, exibe os resultados completos da simulação inline nesta mesma página.

var GerarLimites = function (props) {
  var setPage = props.setPage;
  var setHasData = props.setHasData;
  var s1 = React.useState(null);
  var file = s1[0]; var setFile = s1[1];
  var s2 = React.useState(false);
  var drag = s2[0]; var setDrag = s2[1];
  var s3 = React.useState(false);
  var ran = s3[0]; var setRan = s3[1];
  var s4 = React.useState(false);
  var running = s4[0]; var setRunning = s4[1];
  var sc1 = React.useState(false);
  var showComparison = sc1[0]; var setShowComparison = sc1[1];
  var inputRef = React.useRef(null);

  function handleFile(f) {
    if (f) { setFile(f); setRan(false); }
  }
  function onDrop(e) {
    e.preventDefault();
    setDrag(false);
    handleFile(e.dataTransfer.files[0]);
  }

  function handleExecutar() {
    if (!file) return;
    setRunning(true);
    setApiError(null);
    Api.gerarLimites(file)
      .then(function (result) {
        setUploadResult(result);
        setRan(true);
        if (setHasData) setHasData(true);
      })
      .catch(function (err) {
        setApiError(err.message || "Erro ao gerar limites.");
      })
      .finally(function () {
        setRunning(false);
      });
  }

  function exportarLimites() {
    var sc = SOLVER_COMPARISON;
    var header = ["Cluster", "Simplex (R$)", "PuLP/CBC (R$)", "Match"];
    var rows = sc.simplex.clusters.map(function (cs, i) {
      var cp = sc.pulp.clusters[i];
      var match = cs.limite === cp.limite ? "Sim" : "Não";
      return [cs.id, cs.limite || 0, cp.limite || 0, match];
    });
    var csv = [header].concat(rows).map(function (r) { return r.join(";"); }).join("\n");
    var blob = new Blob(["﻿" + csv], { type: "text/csv;charset=utf-8;" });
    var url = URL.createObjectURL(blob);
    var a = document.createElement("a");
    a.href = url;
    a.download = "limites_clusters.csv";
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  var total = CLUSTERS_UPLOAD.length;
  var viavel = CLUSTERS_UPLOAD.filter(function (c) { return c.status === "viavel"; }).length;
  var sem = total - viavel;

  var RESULT_KPIS = [
    { label: "Total de Clusters", value: "73", sub: "↑ 5 novos clusters", highlight: false },
    { label: "Limite Total Aprovado", value: "R$ 127,4M", sub: "↑ 8,5% vs mês anterior", highlight: true },
    { label: "Clientes Ativos", value: "48.320", sub: "↑ 12 novos este mês", highlight: false },
    { label: "Taxa de Aprovação", value: "87,3%", sub: "↑ 2,3% vs ano anterior", highlight: false },
  ];

  var sc = SOLVER_COMPARISON;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-[#0D1B2A]">
          {ran ? "Resultados da Simulação" : "Carregar Base & Gerar Limites"}
        </h1>
        {ran && (
          <p className="mt-1 text-xs text-[#9C9C9F]">
            Output do algoritmo Simplex · simulação executada em Mai/2025
          </p>
        )}
        <div className="mt-1 h-0.5 w-10 bg-[#2E6DA4]" />
      </div>

      {/* Fase 1: instruções CSV + upload (sempre visível enquanto não rodou) */}
      {!ran && (
        <>
          <div className="bg-white border border-[#E8EFF7] shadow-sm p-5">
            <div className="flex items-center gap-2 mb-4">
              <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="#2E6DA4" strokeWidth="2">
                <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
                <polyline points="14 2 14 8 20 8" />
                <line x1="16" y1="13" x2="8" y2="13" />
                <line x1="16" y1="17" x2="8" y2="17" />
                <polyline points="10 9 9 9 8 9" />
              </svg>
              <span className="text-sm font-semibold text-[#0D1B2A]">Estrutura esperada do CSV</span>
            </div>

            <div className="overflow-x-auto border border-[#E8EFF7] mb-4">
              <table className="w-full text-xs">
                <thead>
                  <tr className="bg-[#0D1B2A]">
                    {["Coluna", "Tipo", "Descrição", "Exemplo"].map(function (h) {
                      return (
                        <th key={h} className="px-3 py-2.5 text-left font-semibold text-white uppercase tracking-wide whitespace-nowrap">
                          {h}
                        </th>
                      );
                    })}
                  </tr>
                </thead>
                <tbody>
                  {[
                    { col: "token", tipo: "string", desc: "Identificador único do cliente", ex: "CLI001" },
                    { col: "flag_filtros", tipo: "int", desc: "0 = elegível para otimização / 1 = excluído", ex: "0" },
                    { col: "pd_calibrada", tipo: "float", desc: "Probabilidade de default calibrada", ex: "0.05" },
                    { col: "capacidade_pagamento", tipo: "float", desc: "Capacidade de pagamento em R$", ex: "800.0" },
                    { col: "renda_estimada", tipo: "float", desc: "Renda estimada (proxy se capacidade_pagamento for nulo)", ex: "2500.0" },
                    { col: "score_credito_cross", tipo: "float", desc: "Score de crédito, escala 300 a 900", ex: "720" },
                    { col: "score_propensao_contrato", tipo: "float", desc: "Score de propensão ao contrato, escala 3 a 846", ex: "450" },
                    { col: "fx_idade", tipo: "string", desc: "Faixa etária categórica (opcional — não utilizada como feature do CART)", ex: "26-35" },
                  ].map(function (r, i) {
                    return (
                      <tr key={r.col} className={"border-t border-[#E8EFF7] " + (i % 2 === 0 ? "" : "bg-[#E2EAF4]/60")}>
                        <td className="px-3 py-2 font-mono font-semibold text-[#2E6DA4] whitespace-nowrap">{r.col}</td>
                        <td className="px-3 py-2 text-[#9C9C9F] whitespace-nowrap">{r.tipo}</td>
                        <td className="px-3 py-2 text-[#3B4049]">{r.desc}</td>
                        <td className="px-3 py-2 font-mono text-[#9C9C9F] whitespace-nowrap">{r.ex}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            <p className="text-xs text-[#9C9C9F]">
              Mínimo recomendado:{" "}
              <span className="font-semibold text-[#3B4049]">500+ clientes com flag_filtros = 0</span>{" "}
              para o CART (árvore de decisão) gerar clusters com tamanho mínimo adequado (min_samples_leaf=500). O algoritmo pode gerar até 800 clusters.
            </p>
          </div>

          {/* Dropzone */}
          <div>
            <p className="text-sm font-semibold text-[#0D1B2A] mb-3">Fazer Upload</p>
            <div
              className={
                "upload-zone flex flex-col items-center justify-center gap-3 border-2 border-dashed py-14 px-6 cursor-pointer " +
                (drag
                  ? "border-[#2E6DA4] bg-[#D6E8F5]"
                  : file
                    ? "border-[#2E6DA4] bg-[#D6E8F5]/50"
                    : "border-[#B8D4EC] bg-white hover:border-[#2E6DA4] hover:bg-[#D6E8F5]/40")
              }
              onDragOver={function (e) { e.preventDefault(); setDrag(true); }}
              onDragLeave={function () { setDrag(false); }}
              onDrop={onDrop}
              onClick={function () { inputRef.current.click(); }}
            >
              <input ref={inputRef} type="file" accept=".csv,.xlsx" className="hidden" onChange={function (e) { handleFile(e.target.files[0]); }} />
              <div className="w-12 h-12 bg-[#D6E8F5] flex items-center justify-center">
                <svg width="22" height="22" fill="none" viewBox="0 0 24 24" stroke="#2E6DA4" strokeWidth="2">
                  <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
                  <polyline points="17 8 12 3 7 8" />
                  <line x1="12" y1="3" x2="12" y2="15" />
                </svg>
              </div>
              {file ? (
                <>
                  <p className="text-sm font-semibold text-[#0D1B2A]">Arquivo carregado: {file.name}</p>
                  <p className="text-xs text-[#9C9C9F]">Clique para substituir ou arraste outro arquivo</p>
                </>
              ) : (
                <>
                  <p className="text-sm font-semibold text-[#0D1B2A]">Arraste seu arquivo aqui ou clique para selecionar</p>
                  <p className="text-xs text-[#9C9C9F]">Formatos suportados: CSV, XLSX</p>
                </>
              )}
            </div>
          </div>

          {/* Botão executar */}
          {file && (
            <div className="flex items-center gap-3">
              <button
                onClick={handleExecutar}
                disabled={running}
                className={
                  "flex items-center gap-2 px-5 py-2.5 text-sm font-semibold transition-colors shadow-sm " +
                  (running ? "bg-[#2E6DA4] text-white cursor-not-allowed" : "bg-[#2E6DA4] text-white hover:bg-[#1B3A5C]")
                }
              >
                {running ? (
                  <>
                    <svg className="animate-spin" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                      <path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0" />
                    </svg>
                    Executando...
                  </>
                ) : (
                  <>
                    <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
                      <polygon points="5 3 19 12 5 21 5 3" />
                    </svg>
                    Executar Simplex
                  </>
                )}
              </button>
              <span className="text-xs text-[#9C9C9F]">Arquivo: {file.name}</span>
            </div>
          )}
        </>
      )}

      {/* Fase 2: resultados completos */}
      {ran && (
        <div className="space-y-6">

          {/* Header de resultados com exportar */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3 px-4 py-3 bg-[#D6E8F5] border border-[#2E6DA4]/30 text-sm text-[#1B3A5C] flex-1 mr-4">
              <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2" className="flex-shrink-0">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="8" x2="12" y2="12" />
                <line x1="12" y1="16" x2="12.01" y2="16" />
              </svg>
              <span>
                Indicadores da última execução do Simplex. Para nova simulação,{" "}
                <button onClick={function () { setRan(false); setFile(null); }} className="font-bold underline hover:text-[#0D1B2A]">
                  carregue um novo arquivo
                </button>.
              </span>
            </div>
            <button
              onClick={exportarLimites}
              className="flex items-center gap-2 px-4 py-2 text-sm font-semibold border border-[#E8EFF7] bg-white text-[#3B4049] hover:bg-[#E2EAF4] transition-colors shadow-sm whitespace-nowrap"
            >
              <svg width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
                <polyline points="7 10 12 15 17 10" />
                <line x1="12" y1="15" x2="12" y2="3" />
              </svg>
              Exportar CSV
            </button>
          </div>

          {/* KPIs */}
          <div className="grid grid-cols-4 gap-4">
            {RESULT_KPIS.map(function (k) {
              return (
                <div
                  key={k.label}
                  className={"border shadow-sm p-5 " + (k.highlight ? "border-[#2E6DA4]/40 bg-[#D6E8F5]" : "bg-white border-[#E8EFF7]")}
                >
                  <div className="text-xs font-medium text-[#9C9C9F] mb-2">{k.label}</div>
                  <div className={"text-2xl font-bold mb-1 " + (k.highlight ? "text-[#2E6DA4]" : "text-[#0D1B2A]")}>{k.value}</div>
                  <div className="text-xs text-[#9C9C9F]">{k.sub}</div>
                </div>
              );
            })}
          </div>

          {/* Clusters — mini cards + tabela */}
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-base font-semibold text-[#0D1B2A]">
              <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="#2E6DA4" strokeWidth="2.5">
                <polyline points="22 7 13.5 15.5 8.5 10.5 2 17" />
                <polyline points="16 7 22 7 22 13" />
              </svg>
              Limites Gerados por Cluster
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div className="bg-white border border-[#E8EFF7] shadow-sm p-5">
                <div className="text-xs font-medium text-[#9C9C9F] mb-1">Total de Clusters</div>
                <div className="text-3xl font-bold text-[#0D1B2A]">{total}</div>
              </div>
              <div className="bg-white border border-[#67DE98]/50 shadow-sm p-5">
                <div className="text-xs font-medium text-[#2E6DA4] mb-1">Com Solução Viável</div>
                <div className="text-3xl font-bold text-[#2E6DA4]">{viavel}</div>
              </div>
              <div className="bg-white border border-[#FAE95D]/60 shadow-sm p-5">
                <div className="text-xs font-medium text-[#3B4049] mb-1">Sem Solução</div>
                <div className="text-3xl font-bold text-[#3B4049]">{sem}</div>
              </div>
            </div>

            <div className="bg-white border border-[#E8EFF7] shadow-sm overflow-hidden">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-[#0D1B2A]">
                    {["Cluster ID", "Limite Sugerido", "Status"].map(function (h) {
                      return (
                        <th key={h} className="px-4 py-2.5 text-left text-[11px] font-semibold text-white uppercase tracking-wide">
                          {h}
                        </th>
                      );
                    })}
                  </tr>
                </thead>
                <tbody>
                  {CLUSTERS_UPLOAD.map(function (c) {
                    return (
                      <tr key={c.id} className="border-b border-[#E2EAF4] hover:bg-[#E2EAF4] transition-colors">
                        <td className="px-4 py-3 font-semibold text-[#2E6DA4]">{c.id}</td>
                        <td className="px-4 py-3 font-medium text-[#0D1B2A]">
                          {c.limite ? fmt(c.limite) + ",00" : "—"}
                        </td>
                        <td className="px-4 py-3">
                          {c.status === "viavel" ? (
                            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 text-xs font-semibold bg-[#67DE98]/20 text-[#2E6DA4] border border-[#67DE98]/50">
                              <svg width="11" height="11" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
                                <circle cx="12" cy="12" r="10" /><path d="M9 12l2 2 4-4" />
                              </svg>
                              Solução Viável
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 text-xs font-semibold bg-[#FF5D5C]/20 text-[#DC2F37] border border-[#FF5D5C]/40">
                              <svg width="11" height="11" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
                                <circle cx="12" cy="12" r="10" />
                                <line x1="15" y1="9" x2="9" y2="15" /><line x1="9" y1="9" x2="15" y2="15" />
                              </svg>
                              Sem Solução
                            </span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Gráficos linha 1 */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white border border-[#E8EFF7] shadow-sm p-5">
              <div className="text-sm font-semibold text-[#0D1B2A] mb-1">Limites por Cluster</div>
              <div className="text-xs text-[#9C9C9F] mb-4">Limite ótimo atribuído a cada cluster pelo Simplex (R$)</div>
              <BarChartSVG data={CLUSTER_LIMITES.map(function (d) { return { label: d.name, value: d.limite }; })} />
            </div>
            <div className="bg-white border border-[#E8EFF7] shadow-sm p-5">
              <div className="text-sm font-semibold text-[#0D1B2A] mb-1">Distribuição por Status</div>
              <div className="text-xs text-[#9C9C9F] mb-4">Proporção de clientes por situação na carteira</div>
              <div className="flex items-center gap-6">
                <DonutChart data={STATUS_PIE} />
                <div className="space-y-3 flex-1">
                  {STATUS_PIE.map(function (d) {
                    return (
                      <div key={d.name} className="flex items-center gap-2 text-sm">
                        <div className="w-2.5 h-2.5 flex-shrink-0" style={{ background: d.color }} />
                        <span className="font-medium text-[#3B4049] flex-1">{d.name}</span>
                        <span className="font-semibold text-[#0D1B2A]">{d.value}%</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>

          {/* Comparação de Solvers */}
          <div className="bg-white border border-[#E8EFF7] shadow-sm p-5">
            <div className="mb-1 text-sm font-semibold text-[#0D1B2A]">Comparação de Solvers: Simplex vs PuLP</div>
            <div className="text-xs text-[#9C9C9F] mb-5">Validação da solução ótima com biblioteca externa (PuLP / CBC)</div>

            <div className="grid grid-cols-2 gap-3 mb-5">
              {[sc.simplex, sc.pulp].map(function (s) {
                return (
                  <div key={s.label} className="border border-[#E8EFF7] bg-[#E2EAF4] p-4">
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-xs font-semibold text-[#3B4049]">{s.label}</span>
                      <span className="inline-flex items-center px-2 py-0.5 text-[11px] font-medium bg-[#67DE98]/20 text-[#2E6DA4] border border-[#67DE98]/50">{s.status}</span>
                    </div>
                    <div className="text-2xl font-bold text-[#2E6DA4] mb-1">{fmtZ(s.z)}</div>
                    <div className="text-xs text-[#9C9C9F]">Valor objetivo (z)</div>
                    <div className="text-xs text-[#9C9C9F] mt-1">Tempo: <span className="font-medium text-[#3B4049]">{s.tempo_ms} ms</span></div>
                  </div>
                );
              })}
            </div>

            <div className="overflow-x-auto border border-[#E8EFF7]">
              <table className="w-full text-xs">
                <thead>
                  <tr className="bg-[#0D1B2A]">
                    {["Cluster", "Simplex (R$)", "PuLP / CBC (R$)", "Match"].map(function (h) {
                      return (
                        <th key={h} className="px-3 py-2.5 text-left font-semibold text-white uppercase tracking-wide whitespace-nowrap">{h}</th>
                      );
                    })}
                  </tr>
                </thead>
                <tbody>
                  {sc.simplex.clusters.map(function (cs, i) {
                    var cp = sc.pulp.clusters[i];
                    var match = cs.limite === cp.limite;
                    return (
                      <tr key={cs.id} className={"border-t border-[#E8EFF7] " + (i % 2 === 0 ? "" : "bg-[#E2EAF4]/60")}>
                        <td className="px-3 py-2 font-mono font-semibold text-[#2E6DA4]">{cs.id}</td>
                        <td className="px-3 py-2 text-[#3B4049]">{cs.limite ? fmt(cs.limite) : "—"}</td>
                        <td className="px-3 py-2 text-[#3B4049]">{cp.limite ? fmt(cp.limite) : "—"}</td>
                        <td className="px-3 py-2">
                          {match ? (
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 text-[11px] font-medium bg-[#67DE98]/20 text-[#2E6DA4] border border-[#67DE98]/50">
                              <svg width="10" height="10" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="3"><polyline points="20 6 9 17 4 12" /></svg>
                              Idêntico
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 text-[11px] font-medium bg-[#FAE95D]/30 text-[#3B4049] border border-[#FAE95D]/70">
                              <svg width="10" height="10" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="3">
                                <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
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
              Delta z = <span className="font-semibold text-[#3B4049]">{(sc.delta_z_pct * 100).toFixed(4)}%</span>
              {" · "}PD financeiro atual: <span className="font-semibold text-[#3B4049]">{(sc.pd_fin_atual * 100).toFixed(2)}%</span>
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
                  <svg width="11" height="11" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
                    <path d="M8 3H5a2 2 0 00-2 2v3m18 0V5a2 2 0 00-2-2h-3M3 16v3a2 2 0 002 2h3m8 0h3a2 2 0 002-2v-3" />
                  </svg>
                  Comparar simulação anterior
                </button>
              </div>
              <div className="text-xs text-[#9C9C9F] mb-3">Crescimento mensal do limite aprovado em R$ milhões</div>
              {showComparison && (
                <div className="flex items-center gap-4 mb-3 text-xs">
                  <span className="flex items-center gap-1.5"><span className="inline-block w-6 h-0.5 bg-[#2E6DA4]"></span><span className="text-[#3B4049] font-medium">Simulação atual (Mai/2025)</span></span>
                  <span className="flex items-center gap-1.5"><span className="inline-block w-6 border-t-2 border-dashed border-[#FAE95D]"></span><span className="text-[#3B4049] font-medium">Simulação anterior (Abr/2025)</span></span>
                </div>
              )}
              <LineChartSVG
                data={EVOLUCAO.map(function (d) { return { label: d.mes, value: d.valor }; })}
                data2={showComparison ? EVOLUCAO_PREV : null}
              />
            </div>

            <div className="bg-white border border-[#E8EFF7] shadow-sm p-5">
              <div className="text-sm font-semibold text-[#0D1B2A] mb-1">Distribuição de Score</div>
              <div className="text-xs text-[#9C9C9F] mb-4">Número de clientes por faixa de score de crédito</div>
              <AreaChartSVG data={SCORE_DIST.map(function (d) { return { label: d.score, value: d.n }; })} />
            </div>
          </div>

        </div>
      )}
    </div>
  );
};
