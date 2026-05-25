// pages/GerarLimites.js  –  Deps globals: CLUSTERS_UPLOAD, fmt

var GerarLimites = function(props) {
  var setPage = props.setPage;
  var s1 = React.useState(null);  var file = s1[0]; var setFile = s1[1];
  var s2 = React.useState(false); var drag = s2[0]; var setDrag = s2[1];
  var s3 = React.useState(false); var ran  = s3[0]; var setRan  = s3[1];
  var s4 = React.useState(false); var running = s4[0]; var setRunning = s4[1];
  var inputRef = React.useRef(null);

  function handleFile(f) { if (f) { setFile(f); setRan(false); } }
  function onDrop(e) { e.preventDefault(); setDrag(false); handleFile(e.dataTransfer.files[0]); }
  function handleExecutar() {
    setRunning(true);
    setTimeout(function() { setRunning(false); setRan(true); }, 1200);
  }

  var total  = CLUSTERS_UPLOAD.length;
  var viavel = CLUSTERS_UPLOAD.filter(function(c) { return c.status === 'viavel'; }).length;
  var sem    = total - viavel;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-slate-800">Carregar Base &amp; Gerar Limites</h1>
        <div className="mt-1 h-0.5 w-10 bg-sky-500 rounded-full" />
      </div>

      {/* Dropzone */}
      <div>
        <p className="text-sm font-semibold text-slate-700 mb-3">Fazer Upload</p>
        <div
          className={'upload-zone flex flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed py-14 px-6 cursor-pointer '
            + (drag ? 'border-sky-400 bg-sky-50' : file ? 'border-green-400 bg-green-50' : 'border-slate-300 bg-[#F0EEE4] hover:border-sky-400 hover:bg-sky-50')}
          onDragOver={function(e) { e.preventDefault(); setDrag(true); }}
          onDragLeave={function() { setDrag(false); }}
          onDrop={onDrop}
          onClick={function() { inputRef.current.click(); }}
        >
          <input ref={inputRef} type="file" accept=".csv,.xlsx" className="hidden"
            onChange={function(e) { handleFile(e.target.files[0]); }} />
          <div className="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center">
            <svg width="22" height="22" fill="none" viewBox="0 0 24 24" stroke="#64748b" strokeWidth="2">
              <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
              <polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>
            </svg>
          </div>
          {file ? (
            <>
              <p className="text-sm font-semibold text-slate-700">Arquivo carregado: {file.name}</p>
              <p className="text-xs text-slate-400">Clique para substituir ou arraste outro arquivo</p>
            </>
          ) : (
            <>
              <p className="text-sm font-semibold text-slate-700">Arraste seu arquivo aqui ou clique para selecionar</p>
              <p className="text-xs text-slate-400">Formatos suportados: CSV, XLSX</p>
            </>
          )}
        </div>
      </div>

      {/* Botão executar – aparece após upload, antes de rodar */}
      {file && !ran && (
        <div className="flex items-center gap-3">
          <button
            onClick={handleExecutar}
            disabled={running}
            className={'flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-semibold transition-colors shadow-sm '
              + (running ? 'bg-sky-300 text-white cursor-not-allowed' : 'bg-sky-500 text-white hover:bg-sky-600')}>
            {running ? (
              <>
                <svg className="animate-spin" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0"/></svg>
                Executando...
              </>
            ) : (
              <>
                <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5"><polygon points="5 3 19 12 5 21 5 3"/></svg>
                Executar Simplex
              </>
            )}
          </button>
          <span className="text-xs text-slate-400">Arquivo: {file.name}</span>
        </div>
      )}

      {/* Resultado */}
      {ran && (
        <div className="space-y-4">
          <div className="flex items-center gap-2 text-base font-semibold text-slate-800">
            <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="#0ea5e9" strokeWidth="2.5">
              <polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>
            </svg>
            Limites Gerados por Cluster
          </div>

          {/* Mini cards */}
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-[#F0EEE4] rounded-xl border border-slate-200 shadow-sm p-5">
              <div className="text-xs font-medium text-slate-500 mb-1">Total de Clusters</div>
              <div className="text-3xl font-bold text-slate-800">{total}</div>
            </div>
            <div className="bg-[#F0EEE4] rounded-xl border border-green-200 shadow-sm p-5">
              <div className="text-xs font-medium text-green-600 mb-1">Com Solução Viável</div>
              <div className="text-3xl font-bold text-green-600">{viavel}</div>
            </div>
            <div className="bg-[#F0EEE4] rounded-xl border border-amber-200 shadow-sm p-5">
              <div className="text-xs font-medium text-amber-700 mb-1">Sem Solução</div>
              <div className="text-3xl font-bold text-amber-700">{sem}</div>
            </div>
          </div>

          {/* Tabela */}
          <div className="bg-[#F0EEE4] rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-800">
                  {['Cluster ID','Limite Sugerido','Status'].map(function(h) {
                    return <th key={h} className="px-4 py-2.5 text-left text-[11px] font-semibold text-white uppercase tracking-wide">{h}</th>;
                  })}
                </tr>
              </thead>
              <tbody>
                {CLUSTERS_UPLOAD.map(function(c) {
                  return (
                    <tr key={c.id} className="border-b border-slate-50 hover:bg-slate-50">
                      <td className="px-4 py-3 font-medium text-slate-800">{c.id}</td>
                      <td className="px-4 py-3 font-medium text-slate-700">{c.limite ? fmt(c.limite) + ',00' : '—'}</td>
                      <td className="px-4 py-3">
                        {c.status === 'viavel' ? (
                          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-50 text-green-700 border border-green-200">
                            <svg width="11" height="11" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5"><circle cx="12" cy="12" r="10"/><path d="M9 12l2 2 4-4"/></svg>
                            Solução Viável
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-50 text-red-600 border border-red-200">
                            <svg width="11" height="11" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
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

          {/* CTA navegação */}
          <div className="flex justify-end">
            <button
              onClick={function() { if (setPage) setPage('resultados'); }}
              className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold text-sky-600 border border-sky-300 bg-sky-50 hover:bg-sky-100 transition-colors">
              Ver análise completa em Resultados
              <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
