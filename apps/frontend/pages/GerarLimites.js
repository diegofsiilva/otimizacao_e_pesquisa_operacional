// pages/GerarLimites.js  –  Deps globals: CLUSTERS_UPLOAD, fmt

var GerarLimites = function(props) {
  var setPage = props.setPage;
  var setHasData = props.setHasData;
  var s1 = React.useState(null);  var file = s1[0]; var setFile = s1[1];
  var s2 = React.useState(false); var drag = s2[0]; var setDrag = s2[1];
  var s3 = React.useState(false); var ran  = s3[0]; var setRan  = s3[1];
  var s4 = React.useState(false); var running = s4[0]; var setRunning = s4[1];
  var inputRef = React.useRef(null);

  function handleFile(f) { if (f) { setFile(f); setRan(false); } }
  function onDrop(e) { e.preventDefault(); setDrag(false); handleFile(e.dataTransfer.files[0]); }
  function handleExecutar() {
    setRunning(true);
    setTimeout(function() {
      setRunning(false);
      setRan(true);
      if (setHasData) setHasData(true);
    }, 1200);
  }

  var total  = CLUSTERS_UPLOAD.length;
  var viavel = CLUSTERS_UPLOAD.filter(function(c) { return c.status === 'viavel'; }).length;
  var sem    = total - viavel;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-slate-800">Carregar Base &amp; Gerar Limites</h1>
        <div className="mt-1 h-0.5 w-10 bg-[#102C26]" />
      </div>

      {/* Estrutura esperada do CSV */}
      <div className="bg-[#F7E7CE]  border border-slate-200 shadow-sm p-5">
        <div className="flex items-center gap-2 mb-4">
          <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="#102C26" strokeWidth="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
          <span className="text-sm font-semibold text-slate-800">Estrutura esperada do CSV</span>
        </div>

        <div className="overflow-x-auto  border border-slate-200 mb-4">
          <table className="w-full text-xs">
            <thead>
              <tr className="bg-[#102C26]">
                {['Coluna','Tipo','Descrição','Exemplo'].map(function(h) {
                  return <th key={h} className="px-3 py-2.5 text-left font-semibold text-[#F7E7CE] uppercase tracking-wide whitespace-nowrap">{h}</th>;
                })}
              </tr>
            </thead>
            <tbody>
              {[
                { col: 'token',                    tipo: 'string', desc: 'Identificador único do cliente',                        ex: 'CLI001'  },
                { col: 'flag_filtros',             tipo: 'int',    desc: '0 = elegível para otimização · 1 = excluído',           ex: '0'       },
                { col: 'pd_calibrada',             tipo: 'float',  desc: 'Probabilidade de default calibrada',                    ex: '0.05'    },
                { col: 'capacidade_pagamento',     tipo: 'float',  desc: 'Capacidade de pagamento em R$',                         ex: '800.0'   },
                { col: 'renda_estimada',           tipo: 'float',  desc: 'Renda estimada (proxy se capacidade_pagamento for nulo)',ex: '2500.0'  },
                { col: 'score_credito_cross',      tipo: 'float',  desc: 'Score de crédito — escala 300 a 900',                   ex: '720'     },
                { col: 'score_propensao_contrato', tipo: 'float',  desc: 'Score de propensão ao contrato — escala 3 a 846',       ex: '450'     },
                { col: 'fx_idade',                 tipo: 'string', desc: 'Faixa etária categórica',                               ex: '26-35'   },
              ].map(function(r, i) {
                return (
                  <tr key={r.col} className={'border-t border-slate-100 ' + (i % 2 === 0 ? '' : 'bg-slate-50/50')}>
                    <td className="px-3 py-2 font-mono font-semibold text-[#102C26] whitespace-nowrap">{r.col}</td>
                    <td className="px-3 py-2 text-slate-500 whitespace-nowrap">{r.tipo}</td>
                    <td className="px-3 py-2 text-slate-600">{r.desc}</td>
                    <td className="px-3 py-2 font-mono text-slate-500 whitespace-nowrap">{r.ex}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        <p className="text-xs text-slate-500">
          Mínimo recomendado: <span className="font-semibold text-slate-700">20–30 clientes com flag_filtros = 0</span> para o K-Means formar os 7 clusters corretamente.
        </p>
      </div>

      {/* Dropzone */}
      <div>
        <p className="text-sm font-semibold text-slate-700 mb-3">Fazer Upload</p>
        <div
          className={'upload-zone flex flex-col items-center justify-center gap-3  border-2 border-dashed py-14 px-6 cursor-pointer '
            + (drag ? 'border-[#102C26] bg-[#E8F4F1]' : file ? 'border-green-400 bg-green-50' : 'border-slate-300 bg-[#F7E7CE] hover:border-[#102C26] hover:bg-[#E8F4F1]')}
          onDragOver={function(e) { e.preventDefault(); setDrag(true); }}
          onDragLeave={function() { setDrag(false); }}
          onDrop={onDrop}
          onClick={function() { inputRef.current.click(); }}
        >
          <input ref={inputRef} type="file" accept=".csv,.xlsx" className="hidden"
            onChange={function(e) { handleFile(e.target.files[0]); }} />
          <div className="w-12 h-12 bg-slate-100 flex items-center justify-center">
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
            className={'flex items-center gap-2 px-5 py-2.5  text-sm font-semibold transition-colors shadow-sm '
              + (running ? 'bg-[#3D7A6B] text-white cursor-not-allowed' : 'bg-[#102C26] text-white hover:bg-[#1a4a3f]')}>
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
            <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="#102C26" strokeWidth="2.5">
              <polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>
            </svg>
            Limites Gerados por Cluster
          </div>

          {/* Mini cards */}
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-[#F7E7CE]  border border-slate-200 shadow-sm p-5">
              <div className="text-xs font-medium text-slate-500 mb-1">Total de Clusters</div>
              <div className="text-3xl font-bold text-slate-800">{total}</div>
            </div>
            <div className="bg-[#F7E7CE]  border border-green-200 shadow-sm p-5">
              <div className="text-xs font-medium text-green-600 mb-1">Com Solução Viável</div>
              <div className="text-3xl font-bold text-green-600">{viavel}</div>
            </div>
            <div className="bg-[#F7E7CE]  border border-amber-200 shadow-sm p-5">
              <div className="text-xs font-medium text-amber-700 mb-1">Sem Solução</div>
              <div className="text-3xl font-bold text-amber-700">{sem}</div>
            </div>
          </div>

          {/* Tabela */}
          <div className="bg-[#F7E7CE]  border border-slate-200 shadow-sm overflow-hidden">
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
                          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 text-xs font-medium bg-green-50 text-green-700 border border-green-200">
                            <svg width="11" height="11" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5"><circle cx="12" cy="12" r="10"/><path d="M9 12l2 2 4-4"/></svg>
                            Solução Viável
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 text-xs font-medium bg-red-50 text-red-600 border border-red-200">
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
              className="flex items-center gap-2 px-4 py-2  text-sm font-semibold text-[#102C26] border border-[#3D7A6B] bg-[#E8F4F1] hover:bg-[#D4EDE8] transition-colors">
              Ver análise completa em Resultados
              <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
