// pages/ConfigModal.js  –  Deps globals: PARAMS_EDITAVEIS, PARAMS_NAO_EDITAVEIS

var ConfigModal = function(props) {
  var onClose = props.onClose;

  var initial = PARAMS_EDITAVEIS.reduce(function(acc, p) {
    acc[p.key] = p.value; return acc;
  }, {});

  var s1 = React.useState(initial); var params = s1[0]; var setParams = s1[1];
  var s2 = React.useState(null);    var editing = s2[0]; var setEditing = s2[1];

  function formatVal(key, v) {
    if (key === 'L_max') return 'R$ ' + Number(v).toLocaleString('pt-BR');
    if (key === 't' || key === 'LGD' || key === 'u_bar') return (Number(v) * 100).toFixed(0) + '%';
    return v;
  }

  function handleSlider(key, val) {
    setParams(function(prev) { var n = Object.assign({}, prev); n[key] = parseFloat(val); return n; });
  }

  function handleCancel(key) {
    var orig = PARAMS_EDITAVEIS.find(function(x){ return x.key === key; }).value;
    setParams(function(prev) { var n = Object.assign({}, prev); n[key] = orig; return n; });
    setEditing(null);
  }

  function handleOverlay(e) { if (e.target === e.currentTarget) onClose(); }

  return (
    <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4" onClick={handleOverlay}>
      <div className="bg-[#F7E7CE]  shadow-2xl w-full max-w-lg modal-enter" onClick={function(e){ e.stopPropagation(); }}>

        {/* Header */}
        <div className="flex items-center gap-3 px-6 py-4 border-b border-slate-100">
          <div className="w-8 h-8  bg-[#D4EDE8] flex items-center justify-center">
            <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="#102C26" strokeWidth="2">
              <path d="M12 15a3 3 0 100-6 3 3 0 000 6z"/>
              <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"/>
            </svg>
          </div>
          <span className="text-base font-semibold text-slate-800">Configurações</span>
          <button onClick={onClose} className="ml-auto p-1.5  text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors">
            <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>

        {/* Body */}
        <div className="px-6 py-5 space-y-5 max-h-[70vh] overflow-y-auto">

          {/* Editáveis */}
          <div>
            <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-wide mb-3">Parâmetros Editáveis</p>
            <div className="space-y-3">
              {PARAMS_EDITAVEIS.map(function(p) {
                var isEditing = editing === p.key;
                return (
                  <div key={p.key} className=" border border-slate-200 bg-slate-50 p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="text-xs font-medium text-slate-500">{p.label}</div>
                        <div className="text-lg font-bold text-slate-800 mt-0.5">{formatVal(p.key, params[p.key])}</div>
                      </div>
                      {!isEditing && (
                        <button onClick={function(){ setEditing(p.key); }}
                          className="p-2  hover:bg-slate-200 text-slate-400 transition-colors">
                          <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                            <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/>
                            <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
                          </svg>
                        </button>
                      )}
                    </div>

                    {isEditing && (
                      <div className="mt-4 space-y-3">
                        <div className="flex justify-between text-xs text-slate-500">
                          <span>{p.label}</span>
                          <span className="font-semibold text-[#102C26]">{formatVal(p.key, params[p.key])}</span>
                        </div>
                        <input type="range" className="slider-range w-full"
                          min={p.min} max={p.max} step={p.step} value={params[p.key]}
                          onChange={function(e){ handleSlider(p.key, e.target.value); }} />
                        <div className="flex justify-between text-[10px] text-slate-400">
                          <span>{p.min}</span><span>{p.max}</span>
                        </div>
                        <div className="flex gap-2">
                          <button onClick={function(){ setEditing(null); }}
                            className="flex-1 py-1.5  text-xs font-semibold bg-green-500 text-white hover:bg-green-600 transition-colors">
                            Salvar
                          </button>
                          <button onClick={function(){ handleCancel(p.key); }}
                            className="flex-1 py-1.5  text-xs font-semibold bg-slate-300 text-slate-700 hover:bg-slate-400 transition-colors">
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
            <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-wide mb-3">Parâmetros Não Editáveis</p>
            <div className="grid grid-cols-2 gap-2">
              {PARAMS_NAO_EDITAVEIS.map(function(p, i) {
                return (
                  <div key={i} className=" bg-slate-100 px-4 py-3">
                    <div className="text-[10px] text-slate-500 font-medium">{p.label}</div>
                    <div className="text-sm font-semibold text-slate-700 mt-0.5">{p.value}</div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
