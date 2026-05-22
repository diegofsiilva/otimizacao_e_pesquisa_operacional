// ─────────────────────────────────────────
//  pages/ConfigModal.js  –  modal de configurações (parâmetros)
//  Depende de: data.js (PARAMS_EDITAVEIS, PARAMS_NAO_EDITAVEIS)
// ─────────────────────────────────────────

var ConfigModal = function({ onClose }) {
  var initialParams = PARAMS_EDITAVEIS.reduce(function(acc, p) {
    acc[p.key] = p.value;
    return acc;
  }, {});

  var _p = React.useState(initialParams);
  var params = _p[0];
  var setParams = _p[1];

  var _e = React.useState(null);
  var editing = _e[0];
  var setEditing = _e[1];

  function formatVal(key, v) {
    if (key === 'L_max') return 'R$ ' + Number(v).toLocaleString('pt-BR');
    return v;
  }

  function handleOverlayClick(e) {
    if (e.target === e.currentTarget) onClose();
  }

  return (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className="modal">

        {/* Header */}
        <div className="modal-header">
          <div className="modal-header-left">
            <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="#0ea5e9" strokeWidth="2">
              <path d="M12 15a3 3 0 100-6 3 3 0 000 6z"/>
              <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"/>
            </svg>
            Configurações
          </div>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        {/* Body */}
        <div className="modal-body">

          {/* Parâmetros Editáveis */}
          <p className="modal-section-title">Parâmetros Editáveis</p>

          {PARAMS_EDITAVEIS.map(function(p) {
            var isEditing = editing === p.key;
            return (
              <div key={p.key} className="param-row">
                <div className="param-row-header">
                  <div>
                    <div className="param-label">{p.label}</div>
                    <div className="param-value">{formatVal(p.key, params[p.key])}</div>
                  </div>
                  {!isEditing && (
                    <button
                      className="param-edit-btn"
                      onClick={function() { setEditing(p.key); }}
                    >
                      <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                        <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/>
                        <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
                      </svg>
                    </button>
                  )}
                </div>

                {/* Slider de edição */}
                {isEditing && (
                  <div className="param-editing">
                    <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:4 }}>
                      <span style={{ fontSize:12, color:'#64748b' }}>{p.label}</span>
                      <span className="slider-value">{formatVal(p.key, params[p.key])}</span>
                    </div>
                    <input
                      type="range"
                      className="slider-track"
                      min={p.min}
                      max={p.max}
                      step={p.step}
                      value={params[p.key]}
                      onChange={function(e) {
                        var newVal = parseFloat(e.target.value);
                        setParams(function(prev) {
                          var next = Object.assign({}, prev);
                          next[p.key] = newVal;
                          return next;
                        });
                      }}
                    />
                    <div className="slider-labels">
                      <span>{p.min}</span>
                      <span>{p.max}</span>
                    </div>
                    <div className="slider-btns">
                      <button
                        className="btn btn-green"
                        onClick={function() { setEditing(null); }}
                      >
                        Salvar
                      </button>
                      <button
                        className="btn btn-gray"
                        onClick={function() {
                          var original = PARAMS_EDITAVEIS.find(function(x) { return x.key === p.key; }).value;
                          setParams(function(prev) {
                            var next = Object.assign({}, prev);
                            next[p.key] = original;
                            return next;
                          });
                          setEditing(null);
                        }}
                      >
                        Cancelar
                      </button>
                    </div>
                  </div>
                )}
              </div>
            );
          })}

          {/* Parâmetros Não Editáveis */}
          <p className="modal-section-title" style={{ marginTop:24 }}>
            Parâmetros Não Editáveis
          </p>
          <div className="non-editable-grid">
            {PARAMS_NAO_EDITAVEIS.map(function(p, i) {
              return (
                <div key={i} className="non-editable-card">
                  <div className="param-label">{p.label}</div>
                  <div className="param-value">{p.value}</div>
                </div>
              );
            })}
          </div>

        </div>
      </div>
    </div>
  );
};
