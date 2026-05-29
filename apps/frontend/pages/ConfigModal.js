// pages/ConfigModal.js
// Deps globais: Api (api.js), PARAMS_EDITAVEIS, PARAMS_NAO_EDITAVEIS (data.js)

var ConfigModal = function (props) {
  var onClose = props.onClose;

  // Estado inicial vem dos fallbacks de PARAMS_EDITAVEIS.
  // O useEffect abaixo sobrescreve com os valores reais da API assim que ela
  // responde. Apenas os campos que o backend conhece: { t, LGD, u_bar, L_max, T }.
  var initial = PARAMS_EDITAVEIS.reduce(function (acc, p) {
    acc[p.key] = p.value;
    return acc;
  }, {});

  var s1 = React.useState(initial);
  var params = s1[0];
  var setParams = s1[1];

  // Guarda o snapshot vindo da API para o "Cancelar" restaurar o valor salvo,
  // não o fallback local.
  var s5 = React.useState(initial);
  var savedParams = s5[0];
  var setSavedParams = s5[1];

  var s2 = React.useState(null);
  var editing = s2[0];
  var setEditing = s2[1];

  var s3 = React.useState(false);
  var saving = s3[0];
  var setSaving = s3[1];

  var s4 = React.useState(null);
  var apiError = s4[0];
  var setApiError = s4[1];

  var s6 = React.useState(false);
  var resetting = s6[0];
  var setResetting = s6[1];

  // Carrega parâmetros reais do backend ao abrir o modal.
  React.useEffect(function () {
    var alive = true;
    Api.getConfig()
      .then(function (data) {
        if (!alive) return;
        setParams(function (prev) {
          return Object.assign({}, prev, data);
        });
        setSavedParams(function (prev) {
          return Object.assign({}, prev, data);
        });
        setApiError(null);
      })
      .catch(function () {
        if (alive)
          setApiError("Usando parâmetros locais: backend indisponível.");
      });
    return function () {
      alive = false;
    };
  }, []);

  // Formata o valor exibido no card de cada parâmetro.
  function formatVal(key, v) {
    if (key === "L_max") return "R$ " + Number(v).toLocaleString("pt-BR");
    if (key === "t" || key === "LGD" || key === "u_bar")
      return (Number(v) * 100).toFixed(2) + "%";
    if (key === "T") return Number(v) + " meses";
    return v;
  }

  function handleSlider(key, val) {
    setParams(function (prev) {
      var n = Object.assign({}, prev);
      n[key] = parseFloat(val);
      return n;
    });
  }

  // Cancelar restaura o valor que veio da API (não o fallback de data.js).
  function handleCancel(key) {
    setParams(function (prev) {
      var n = Object.assign({}, prev);
      n[key] = savedParams[key];
      return n;
    });
    setEditing(null);
  }

  // Salva todos os parâmetros de uma vez via PUT /api/config.
  // O backend espera exatamente { t, LGD, u_bar, L_max, T }.
  function handleSave() {
    setSaving(true);
    setApiError(null);

    var payload = {
      t: params.t,
      LGD: params.LGD,
      u_bar: params.u_bar,
      L_max: params.L_max,
      T: params.T,
    };

    Api.updateConfig(payload)
      .then(function (data) {
        setParams(function (prev) {
          return Object.assign({}, prev, data);
        });
        setSavedParams(function (prev) {
          return Object.assign({}, prev, data);
        });
        setEditing(null);
      })
      .catch(function (err) {
        setApiError(err.message || "Erro ao salvar parâmetros.");
      })
      .finally(function () {
        setSaving(false);
      });
  }

  // Restaura os valores de fábrica definidos em PARAMS_EDITAVEIS.value
  // e persiste no banco via PUT /api/config.
  function handleReset() {
    if (
      !window.confirm("Restaurar todos os parâmetros para os valores padrão?")
    )
      return;

    var defaults = PARAMS_EDITAVEIS.reduce(function (acc, p) {
      acc[p.key] = p.value;
      return acc;
    }, {});

    setResetting(true);
    setApiError(null);
    setEditing(null);

    Api.updateConfig(defaults)
      .then(function (data) {
        setParams(function (prev) {
          return Object.assign({}, prev, data);
        });
        setSavedParams(function (prev) {
          return Object.assign({}, prev, data);
        });
      })
      .catch(function (err) {
        setApiError(err.message || "Erro ao restaurar padrões.");
      })
      .finally(function () {
        setResetting(false);
      });
  }

  function handleOverlay(e) {
    if (e.target === e.currentTarget) onClose();
  }

  return (
    <div
      className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
      onClick={handleOverlay}
    >
      <div
        className="bg-white shadow-2xl w-full max-w-lg modal-enter border border-[#E8EFF7]"
        onClick={function (e) {
          e.stopPropagation();
        }}
      >
        {/* Header */}
        <div className="flex items-center gap-3 px-6 py-4 border-b border-[#E8EFF7]">
          <div className="w-8 h-8 bg-[#D6E8F5] flex items-center justify-center">
            <svg
              width="16"
              height="16"
              fill="none"
              viewBox="0 0 24 24"
              stroke="#2E6DA4"
              strokeWidth="2"
            >
              <path d="M12 15a3 3 0 100-6 3 3 0 000 6z" />
              <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z" />
            </svg>
          </div>
          <span className="text-base font-semibold text-[#0D1B2A]">
            Configurações
          </span>
          <button
            onClick={onClose}
            className="ml-auto p-1.5 text-[#9C9C9F] hover:text-[#3B4049] hover:bg-[#E2EAF4] transition-colors"
          >
            <svg
              width="16"
              height="16"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth="2"
            >
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        {/* Body */}
        <div className="px-6 py-5 space-y-5 max-h-[70vh] overflow-y-auto">
          {apiError && (
            <div className="text-xs text-[#DC2F37] bg-[#FF5D5C]/10 border border-[#FF5D5C]/30 px-3 py-2">
              {apiError}
            </div>
          )}

          {/* Editáveis */}
          <div>
            <p className="text-[11px] font-semibold text-[#9C9C9F] uppercase tracking-wide mb-3">
              Parâmetros Editáveis
            </p>
            <div className="space-y-3">
              {PARAMS_EDITAVEIS.map(function (p) {
                var isEditing = editing === p.key;
                return (
                  <div
                    key={p.key}
                    className="border border-[#E8EFF7] bg-[#E2EAF4] p-4"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="text-xs font-medium text-[#9C9C9F]">
                          {p.label}
                        </div>
                        <div className="text-lg font-bold text-[#0D1B2A] mt-0.5">
                          {formatVal(p.key, params[p.key])}
                        </div>
                      </div>
                      {!isEditing && (
                        <button
                          onClick={function () {
                            setEditing(p.key);
                          }}
                          className="p-2 hover:bg-[#E8EFF7] text-[#9C9C9F] transition-colors"
                        >
                          <svg
                            width="14"
                            height="14"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                            strokeWidth="2"
                          >
                            <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" />
                            <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" />
                          </svg>
                        </button>
                      )}
                    </div>

                    {isEditing && (
                      <div className="mt-4 space-y-3">
                        <div className="flex justify-between text-xs text-[#9C9C9F]">
                          <span>{p.label}</span>
                          <span className="font-semibold text-[#2E6DA4]">
                            {formatVal(p.key, params[p.key])}
                          </span>
                        </div>
                        <input
                          type="range"
                          className="slider-range w-full"
                          min={p.min}
                          max={p.max}
                          step={p.step}
                          value={params[p.key]}
                          onChange={function (e) {
                            handleSlider(p.key, e.target.value);
                          }}
                        />
                        <div className="flex justify-between text-[10px] text-[#9C9C9F]">
                          <span>{formatVal(p.key, p.min)}</span>
                          <span>{formatVal(p.key, p.max)}</span>
                        </div>
                        <div className="flex gap-2">
                          <button
                            onClick={handleSave}
                            disabled={saving}
                            className="flex-1 py-1.5 text-xs font-semibold bg-[#2E6DA4] text-white hover:bg-[#1B3A5C] transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
                          >
                            {saving ? "Salvando..." : "Salvar"}
                          </button>
                          <button
                            onClick={function () {
                              handleCancel(p.key);
                            }}
                            disabled={saving}
                            className="flex-1 py-1.5 text-xs font-semibold bg-[#E8EFF7] text-[#3B4049] hover:bg-[#B8D4EC] transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
                          >
                            Cancelar
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Não editáveis */}
          <div>
            <p className="text-[11px] font-semibold text-[#9C9C9F] uppercase tracking-wide mb-3">
              Parâmetros Não Editáveis
            </p>
            <div className="grid grid-cols-2 gap-2">
              {PARAMS_NAO_EDITAVEIS.map(function (p, i) {
                return (
                  <div
                    key={i}
                    className="bg-[#E2EAF4] border border-[#E8EFF7] px-4 py-3"
                  >
                    <div className="text-[10px] text-[#9C9C9F] font-medium">
                      {p.label}
                    </div>
                    <div className="text-sm font-semibold text-[#3B4049] mt-0.5">
                      {p.value}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-[#E8EFF7] flex items-center justify-between">
          <button
            onClick={handleReset}
            disabled={saving || resetting}
            className="flex items-center gap-1.5 text-xs font-medium text-[#9C9C9F] hover:text-[#DC2F37] transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <svg
              width="13"
              height="13"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
              <path d="M3 3v5h5" />
            </svg>
            {resetting ? "Restaurando..." : "Restaurar padrões"}
          </button>
          <button
            onClick={onClose}
            disabled={saving || resetting}
            className="px-4 py-1.5 text-xs font-semibold bg-[#E8EFF7] text-[#3B4049] hover:bg-[#B8D4EC] transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          >
            Fechar
          </button>
        </div>
      </div>
    </div>
  );
};
