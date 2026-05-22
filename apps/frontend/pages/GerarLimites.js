// ─────────────────────────────────────────
//  pages/GerarLimites.js  –  upload de base + tabela de clusters
//  Depende de: data.js (CLUSTERS_UPLOAD, fmt)
// ─────────────────────────────────────────

var GerarLimites = function() {
  var _f = React.useState(null);
  var file = _f[0];
  var setFile = _f[1];

  var _d = React.useState(false);
  var drag = _d[0];
  var setDrag = _d[1];

  var inputRef = React.useRef();

  function handleFile(f) {
    if (f) setFile(f);
  }

  function onDrop(e) {
    e.preventDefault();
    setDrag(false);
    handleFile(e.dataTransfer.files[0]);
  }

  var total  = CLUSTERS_UPLOAD.length;
  var viavel = CLUSTERS_UPLOAD.filter(function(c) { return c.status === 'viavel'; }).length;
  var sem    = CLUSTERS_UPLOAD.filter(function(c) { return c.status === 'sem'; }).length;

  var zoneClass = 'upload-zone'
    + (drag ? ' drag' : '')
    + (file ? ' has-file' : '');

  return (
    <div className="page">
      <h1 className="page-title">Carregar Base &amp; Gerar Limites</h1>
      <div className="page-title-underline" />

      {/* Upload */}
      <div style={{ marginBottom: 24 }}>
        <p style={{ fontWeight:600, marginBottom:12, fontSize:14 }}>Fazer Upload</p>
        <div
          className={zoneClass}
          onDragOver={function(e) { e.preventDefault(); setDrag(true); }}
          onDragLeave={function() { setDrag(false); }}
          onDrop={onDrop}
          onClick={function() { inputRef.current.click(); }}
        >
          <input
            ref={inputRef}
            type="file"
            accept=".csv,.xlsx"
            style={{ display:'none' }}
            onChange={function(e) { handleFile(e.target.files[0]); }}
          />

          <div className="upload-icon-wrap">
            <svg width="28" height="28" fill="none" viewBox="0 0 24 24" stroke="#64748b" strokeWidth="2">
              <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
              <polyline points="17 8 12 3 7 8"/>
              <line x1="12" y1="3" x2="12" y2="15"/>
            </svg>
          </div>

          {file ? (
            <>
              <p className="upload-main">Arquivo carregado: {file.name}</p>
              <p className="upload-sub">Clique para substituir ou arraste outro arquivo</p>
            </>
          ) : (
            <>
              <p className="upload-main">Arraste seu arquivo aqui ou clique para selecionar</p>
              <p className="upload-sub">Formatos suportados: CSV, XLSX</p>
            </>
          )}
        </div>
      </div>

      {/* Resultado do upload */}
      {file && (
        <div>
          <div style={{ display:'flex', alignItems:'center', gap:8, marginBottom:16, fontWeight:600, fontSize:16 }}>
            <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="#0ea5e9" strokeWidth="2.5">
              <polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/>
              <polyline points="16 7 22 7 22 13"/>
            </svg>
            Limites Gerados por Cluster
          </div>

          {/* Mini cards */}
          <div className="cluster-stats">
            <div className="cluster-stat-card">
              <div className="cluster-stat-label">Total de Clusters</div>
              <div className="cluster-stat-val">{total}</div>
            </div>
            <div className="cluster-stat-card green">
              <div className="cluster-stat-label">Com Solução Viável</div>
              <div className="cluster-stat-val green">{viavel}</div>
            </div>
            <div className="cluster-stat-card yellow">
              <div className="cluster-stat-label">Sem Solução</div>
              <div className="cluster-stat-val yellow">{sem}</div>
            </div>
          </div>

          {/* Tabela */}
          <div className="section-card" style={{ padding:0, overflow:'hidden' }}>
            <table className="table-dark">
              <thead>
                <tr>
                  <th>Cluster ID</th>
                  <th>Limite Sugerido</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {CLUSTERS_UPLOAD.map(function(c) {
                  return (
                    <tr key={c.id}>
                      <td style={{ fontWeight:500 }}>{c.id}</td>
                      <td style={{ fontWeight:500 }}>
                        {c.limite ? fmt(c.limite) + ',00' : '—'}
                      </td>
                      <td>
                        {c.status === 'viavel' ? (
                          <span className="badge badge-viavel">
                            <svg width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="#16a34a" strokeWidth="2.5">
                              <circle cx="12" cy="12" r="10"/>
                              <path d="M9 12l2 2 4-4"/>
                            </svg>
                            Solução Viável
                          </span>
                        ) : (
                          <span className="badge badge-sem">
                            <svg width="13" height="13" fill="none" viewBox="0 0 24 24" stroke="#dc2626" strokeWidth="2.5">
                              <circle cx="12" cy="12" r="10"/>
                              <line x1="15" y1="9" x2="9" y2="15"/>
                              <line x1="9"  y1="9" x2="15" y2="15"/>
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
      )}
    </div>
  );
};
