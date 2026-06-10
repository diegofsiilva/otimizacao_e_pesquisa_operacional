// pages/Clientes.js
// Deps globais: Api (api.js), fmt, fmtZ (data.js), LineChartP5 (Resultados.js)
//
// Permite ao analista buscar um cliente por token e visualizar sua evolução
// entre safras: limite otimizado, PD calibrada, cluster atribuído e demais
// indicadores relevantes para análise de crédito.

var Clientes = function (props) {
  // -------------------------------------------------------------------------
  // Estado
  // -------------------------------------------------------------------------

  var s1 = React.useState("");
  var tokenInput = s1[0];
  var setTokenInput = s1[1];

  var s2 = React.useState(null);
  var resultado = s2[0];
  var setResultado = s2[1];

  var s3 = React.useState(false);
  var loading = s3[0];
  var setLoading = s3[1];

  var s4 = React.useState(null);
  var erro = s4[0];
  var setErro = s4[1];

  var s5 = React.useState(false);
  var buscou = s5[0];
  var setBuscou = s5[1];

  var inputRef = React.useRef(null);

  // -------------------------------------------------------------------------
  // Busca
  // -------------------------------------------------------------------------

  function handleBuscar() {
    var token = tokenInput.trim();
    if (!token || isNaN(parseInt(token, 10))) {
      setErro("Informe um token numérico válido.");
      return;
    }

    setLoading(true);
    setErro(null);
    setResultado(null);
    setBuscou(true);

    Api.getHistoricoCliente(parseInt(token, 10))
      .then(function (data) {
        setResultado(data);
        setLoading(false);
      })
      .catch(function (err) {
        if (err.status === 404) {
          setErro("Token não encontrado em nenhuma simulação.");
        } else {
          setErro(err.message || "Erro ao buscar cliente.");
        }
        setLoading(false);
      });
  }

  function handleKeyDown(e) {
    if (e.key === "Enter") handleBuscar();
  }

  function handleLimpar() {
    setTokenInput("");
    setResultado(null);
    setErro(null);
    setBuscou(false);
    if (inputRef.current) inputRef.current.focus();
  }

  // -------------------------------------------------------------------------
  // Helpers
  // -------------------------------------------------------------------------

  function formatPct(v) {
    if (v == null) return "-";
    return (v * 100).toFixed(2) + "%";
  }

  function formatScore(v) {
    if (v == null) return "-";
    return Math.round(v).toLocaleString("pt-BR");
  }

  function deltaLimite(atual, anterior) {
    if (anterior == null || atual == null) return null;
    var d = atual - anterior;
    if (d === 0) return { label: "=", trend: "neutral" };
    var label = (d > 0 ? "+" : "") + fmt(d);
    return { label: label, trend: d > 0 ? "up" : "down" };
  }

  function deltaPD(atual, anterior) {
    if (anterior == null || atual == null) return null;
    var d = atual - anterior;
    if (Math.abs(d) < 0.0001) return { label: "=", trend: "neutral" };
    var label = (d > 0 ? "+" : "") + (d * 100).toFixed(2) + "pp";
    // PD subindo é ruim (down em cor), PD caindo é bom (up em cor)
    return { label: label, trend: d > 0 ? "down" : "up" };
  }

  // -------------------------------------------------------------------------
  // Derivados
  // -------------------------------------------------------------------------

  var historico = resultado ? resultado.historico : [];

  // Dados para o gráfico de linha (limite otimizado por safra)
  var lineData = historico.map(function (h) {
    return { label: h.safra_ref_uso || "-", value: h.limite_otimizado };
  });

  // Dados para o gráfico de PD calibrada por safra
  var pdData = historico.map(function (h) {
    return {
      label: h.safra_ref_uso || "-",
      value: parseFloat((h.pd_calibrada * 100).toFixed(4)),
    };
  });

  // -------------------------------------------------------------------------
  // Render
  // -------------------------------------------------------------------------

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-[#0D1B2A]">
          Histórico de Cliente
        </h1>
        <p className="mt-1 text-xs text-[#9C9C9F]">
          Evolução do limite otimizado e indicadores de risco ao longo das
          safras
        </p>
        <div className="mt-1 h-0.5 w-10 bg-[#2E6DA4]" />
      </div>

      {/* Campo de busca */}
      <div className="bg-white border border-[#E8EFF7] shadow-sm p-5">
        <p className="text-xs font-semibold text-[#9C9C9F] uppercase tracking-wide mb-3">
          Buscar por token
        </p>
        <div className="flex items-center gap-3">
          <div className="relative flex-1 max-w-xs">
            <svg
              className="absolute left-3 top-1/2 -translate-y-1/2 text-[#9C9C9F]"
              width="14"
              height="14"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth="2"
            >
              <circle cx="11" cy="11" r="8" />
              <path d="m21 21-4.35-4.35" />
            </svg>
            <input
              ref={inputRef}
              type="number"
              placeholder="Ex: 1234567"
              value={tokenInput}
              onChange={function (e) {
                setTokenInput(e.target.value);
              }}
              onKeyDown={handleKeyDown}
              className="w-full pl-9 pr-3 py-2 text-sm border border-[#E8EFF7] bg-[#E2EAF4] focus:outline-none focus:border-[#2E6DA4] focus:ring-1 focus:ring-[#2E6DA4]"
            />
          </div>
          <button
            onClick={handleBuscar}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 text-sm font-semibold bg-[#2E6DA4] text-white hover:bg-[#1B3A5C] transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <svg
                  className="animate-spin"
                  width="14"
                  height="14"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0" />
                </svg>
                Buscando...
              </>
            ) : (
              <>
                <svg
                  width="14"
                  height="14"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth="2.5"
                >
                  <circle cx="11" cy="11" r="8" />
                  <path d="m21 21-4.35-4.35" />
                </svg>
                Buscar
              </>
            )}
          </button>
          {buscou && (
            <button
              onClick={handleLimpar}
              className="text-xs text-[#9C9C9F] hover:text-[#3B4049] transition-colors"
            >
              Limpar
            </button>
          )}
        </div>

        {erro && (
          <div className="flex items-center gap-2 mt-3 px-3 py-2 bg-[#FF5D5C]/10 border border-[#FF5D5C]/30 text-xs text-[#DC2F37]">
            <svg
              width="12"
              height="12"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth="2.5"
              className="flex-shrink-0"
            >
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            {erro}
          </div>
        )}
      </div>

      {/* Resultado */}
      {resultado && historico.length > 0 && (
        <div className="space-y-5">
          {/* Cabeçalho do cliente */}
          <div className="flex items-center gap-4 px-5 py-4 bg-white border border-[#E8EFF7] shadow-sm">
            <div className="w-10 h-10 bg-[#D6E8F5] flex items-center justify-center flex-shrink-0">
              <svg
                width="20"
                height="20"
                fill="none"
                viewBox="0 0 24 24"
                stroke="#2E6DA4"
                strokeWidth="2"
              >
                <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2" />
                <circle cx="12" cy="7" r="4" />
              </svg>
            </div>
            <div>
              <div className="text-base font-bold text-[#0D1B2A]">
                Token {resultado.token}
              </div>
              <div className="text-xs text-[#9C9C9F] mt-0.5">
                Aparece em {historico.length}{" "}
                {historico.length === 1 ? "simulação" : "simulações"}
                {" · "}Faixa etária:{" "}
                {historico[historico.length - 1].fx_idade || "-"}
                {historico[historico.length - 1].renda_estimada != null && (
                  <>
                    {" "}
                    · Renda estimada:{" "}
                    {fmt(historico[historico.length - 1].renda_estimada)}
                  </>
                )}
              </div>
            </div>
          </div>

          {/* Cards de evolução por safra */}
          <div>
            <p className="text-xs font-semibold text-[#9C9C9F] uppercase tracking-wide mb-3">
              Evolução por safra
            </p>
            <div
              className="grid gap-3"
              style={{
                gridTemplateColumns:
                  "repeat(" + Math.min(historico.length, 4) + ", 1fr)",
              }}
            >
              {historico.map(function (h, i) {
                var anterior = i > 0 ? historico[i - 1] : null;
                var dLimite = deltaLimite(
                  h.limite_otimizado,
                  anterior && anterior.limite_otimizado,
                );
                var dPD = deltaPD(
                  h.pd_calibrada,
                  anterior && anterior.pd_calibrada,
                );
                var temLimite = h.limite_otimizado > 0;

                return (
                  <div
                    key={h.consulta_id}
                    className={
                      "border shadow-sm p-4 " +
                      (i === historico.length - 1
                        ? "border-[#2E6DA4]/40 bg-[#D6E8F5]"
                        : "bg-white border-[#E8EFF7]")
                    }
                  >
                    {/* Safra */}
                    <div className="flex items-center justify-between mb-3">
                      <span className="inline-flex items-center px-2 py-0.5 text-[11px] font-bold bg-[#0D1B2A] text-white">
                        {h.safra_ref_uso || "-"}
                      </span>
                      {i === historico.length - 1 && (
                        <span className="text-[10px] text-[#2E6DA4] font-semibold">
                          mais recente
                        </span>
                      )}
                    </div>

                    {/* Limite */}
                    <div className="mb-3">
                      <div className="text-[10px] text-[#9C9C9F] font-medium uppercase tracking-wide">
                        Limite otimizado
                      </div>
                      <div
                        className={
                          "text-xl font-bold mt-0.5 " +
                          (temLimite ? "text-[#0D1B2A]" : "text-[#9C9C9F]")
                        }
                      >
                        {temLimite ? fmt(h.limite_otimizado) : "Sem oferta"}
                      </div>
                      {dLimite && (
                        <div
                          className={
                            "flex items-center gap-0.5 mt-0.5 text-[11px] font-semibold " +
                            (dLimite.trend === "up"
                              ? "text-[#1a7a4a]"
                              : dLimite.trend === "down"
                                ? "text-[#DC2F37]"
                                : "text-[#9C9C9F]")
                          }
                        >
                          {dLimite.trend === "up" && (
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
                          )}
                          {dLimite.trend === "down" && (
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
                          )}
                          {dLimite.label}
                        </div>
                      )}
                    </div>

                    {/* Indicadores secundários */}
                    <div className="space-y-1.5 pt-3 border-t border-[#E8EFF7]">
                      <div className="flex justify-between text-xs">
                        <span className="text-[#9C9C9F]">PD calibrada</span>
                        <span className="font-semibold text-[#0D1B2A]">
                          {formatPct(h.pd_calibrada)}
                        </span>
                      </div>
                      {dPD && (
                        <div
                          className={
                            "text-right text-[10px] font-semibold -mt-1 " +
                            (dPD.trend === "up"
                              ? "text-[#1a7a4a]"
                              : dPD.trend === "down"
                                ? "text-[#DC2F37]"
                                : "text-[#9C9C9F]")
                          }
                        >
                          {dPD.label}
                        </div>
                      )}
                      <div className="flex justify-between text-xs">
                        <span className="text-[#9C9C9F]">Score cross</span>
                        <span className="font-semibold text-[#0D1B2A]">
                          {formatScore(h.score_credito_cross)}
                        </span>
                      </div>
                      <div className="flex justify-between text-xs">
                        <span className="text-[#9C9C9F]">Cluster</span>
                        <span className="font-semibold text-[#2E6DA4]">
                          CLU-{h.cluster_id}
                        </span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Gráficos - só aparecem quando há 2+ safras */}
          {historico.length >= 2 && (
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-white border border-[#E8EFF7] shadow-sm p-5">
                <div className="text-sm font-semibold text-[#0D1B2A] mb-1">
                  Evolução do Limite
                </div>
                <div className="text-xs text-[#9C9C9F] mb-4">
                  Limite otimizado (R$) por safra
                </div>
                <LineChartP5 data={lineData} />
              </div>
              <div className="bg-white border border-[#E8EFF7] shadow-sm p-5">
                <div className="text-sm font-semibold text-[#0D1B2A] mb-1">
                  Evolução da PD Calibrada
                </div>
                <div className="text-xs text-[#9C9C9F] mb-4">
                  Probabilidade de inadimplência (%) por safra
                </div>
                <LineChartP5 data={pdData} />
              </div>
            </div>
          )}

          {/* Tabela detalhada */}
          <div className="bg-white border border-[#E8EFF7] shadow-sm overflow-hidden">
            <div className="px-5 py-4 border-b border-[#E8EFF7]">
              <div className="text-sm font-semibold text-[#0D1B2A]">
                Dados por Safra
              </div>
              <div className="text-xs text-[#9C9C9F] mt-0.5">
                Todos os indicadores disponíveis por simulação
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="bg-[#0D1B2A]">
                    {[
                      "Safra",
                      "Cluster",
                      "Limite Otimizado",
                      "PD Calibrada",
                      "Score Crédito Cross",
                      "Score Propensão",
                      "CP Proxy",
                      "Contrato",
                      "Ativação",
                    ].map(function (h) {
                      return (
                        <th
                          key={h}
                          className="px-3 py-2.5 text-left font-semibold text-white uppercase tracking-wide whitespace-nowrap"
                        >
                          {h}
                        </th>
                      );
                    })}
                  </tr>
                </thead>
                <tbody>
                  {historico.map(function (h, i) {
                    var temLimite = h.limite_otimizado > 0;
                    return (
                      <tr
                        key={h.consulta_id}
                        className={
                          "border-b border-[#E2EAF4] hover:bg-[#E2EAF4] transition-colors " +
                          (i % 2 === 0 ? "" : "bg-[#F7FAFD]")
                        }
                      >
                        <td className="px-3 py-2.5">
                          <span className="inline-flex items-center px-2 py-0.5 text-[11px] font-bold bg-[#0D1B2A] text-white">
                            {h.safra_ref_uso || "-"}
                          </span>
                        </td>
                        <td className="px-3 py-2.5 font-mono font-semibold text-[#2E6DA4]">
                          CLU-{h.cluster_id}
                        </td>
                        <td
                          className={
                            "px-3 py-2.5 font-semibold " +
                            (temLimite ? "text-[#0D1B2A]" : "text-[#9C9C9F]")
                          }
                        >
                          {temLimite ? fmt(h.limite_otimizado) : "Sem oferta"}
                        </td>
                        <td className="px-3 py-2.5 text-[#3B4049]">
                          {formatPct(h.pd_calibrada)}
                        </td>
                        <td className="px-3 py-2.5 text-[#3B4049]">
                          {formatScore(h.score_credito_cross)}
                        </td>
                        <td className="px-3 py-2.5 text-[#3B4049]">
                          {h.score_propensao_contrato != null
                            ? h.score_propensao_contrato.toFixed(1)
                            : "-"}
                        </td>
                        <td className="px-3 py-2.5 text-[#3B4049]">
                          {h.cp_proxy != null ? fmt(h.cp_proxy) : "-"}
                        </td>
                        <td className="px-3 py-2.5">
                          <span
                            className={
                              "inline-flex items-center px-2 py-0.5 text-[11px] font-semibold " +
                              (h.flag_contrato === 1
                                ? "bg-[#67DE98]/20 text-[#1a7a4a] border border-[#67DE98]/50"
                                : "bg-[#E2EAF4] text-[#9C9C9F] border border-[#E8EFF7]")
                            }
                          >
                            {h.flag_contrato === 1 ? "Sim" : "Não"}
                          </span>
                        </td>
                        <td className="px-3 py-2.5">
                          <span
                            className={
                              "inline-flex items-center px-2 py-0.5 text-[11px] font-semibold " +
                              (h.flag_ativacao === 1
                                ? "bg-[#67DE98]/20 text-[#1a7a4a] border border-[#67DE98]/50"
                                : "bg-[#E2EAF4] text-[#9C9C9F] border border-[#E8EFF7]")
                            }
                          >
                            {h.flag_ativacao === 1 ? "Sim" : "Não"}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Estado vazio após busca sem resultado */}
      {buscou && !loading && !resultado && !erro && (
        <div className="bg-white border border-[#E8EFF7] shadow-sm flex flex-col items-center justify-center py-16 gap-3 text-center">
          <svg
            width="32"
            height="32"
            fill="none"
            viewBox="0 0 24 24"
            stroke="#B8D4EC"
            strokeWidth="1.5"
          >
            <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2" />
            <circle cx="12" cy="7" r="4" />
          </svg>
          <p className="text-sm text-[#9C9C9F]">Nenhum resultado encontrado</p>
        </div>
      )}
    </div>
  );
};
