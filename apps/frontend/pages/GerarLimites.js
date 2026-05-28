// pages/GerarLimites.js
// Deps globais: Api (api.js), fmt, fmtZ (data.js)
// Deps de render: BarChartSVG, DonutChart (definidos em Resultados.js, carregado depois)
//
// Fluxo:
//   1. Usuário faz upload de um .parquet (drag & drop ou clique)
//   2. Modal "Enviando..." bloqueia a UI durante o POST /api/consultas
//   3. Backend responde imediatamente com status "pendente"
//   4. Consulta aparece na lista de simulações com spinner
//   5. Polling a cada 60s via GET /api/consultas/{id}
//   6. Ao atingir "concluido": busca clusters e exibe resultados inline
//   7. Em caso de "erro": exibe etapa e mensagem do backend

var GerarLimites = function (props) {
  var setPage = props.setPage;
  var setHasData = props.setHasData;

  // -------------------------------------------------------------------------
  // Estado
  // -------------------------------------------------------------------------

  // Upload
  var su1 = React.useState(null);
  var file = su1[0];
  var setFile = su1[1];
  var su2 = React.useState(false);
  var drag = su2[0];
  var setDrag = su2[1];
  var su3 = React.useState("");
  var safraInput = su3[0];
  var setSafraInput = su3[1];
  var su4 = React.useState(false);
  var mostrarOpcAvancadas = su4[0];
  var setMostrarOpcAvancadas = su4[1];
  var su5 = React.useState(null);
  var uploadError = su5[0];
  var setUploadError = su5[1];

  // Modal de envio com progresso de chunks
  var sm1 = React.useState(false);
  var envioModal = sm1[0];
  var setEnvioModal = sm1[1];
  var sm2 = React.useState(0);
  var uploadProgress = sm2[0];
  var setUploadProgress = sm2[1];
  var sm3 = React.useState("iniciando");
  var uploadStep = sm3[0];
  var setUploadStep = sm3[1];

  // Tamanho de cada chunk: 5MB — confortavelmente abaixo de qualquer timeout de túnel
  var CHUNK_SIZE = 5 * 1024 * 1024;

  // Conflito 409 (safra já existe)
  var sc1 = React.useState(false);
  var showConflito = sc1[0];
  var setShowConflito = sc1[1];
  var sc2 = React.useState(null);
  var safraConflitada = sc2[0];
  var setSafraConflitada = sc2[1];

  // Histórico de consultas
  var sh1 = React.useState([]);
  var consultas = sh1[0];
  var setConsultas = sh1[1];
  var sh2 = React.useState(true);
  var loadingHistory = sh2[0];
  var setLoadingHistory = sh2[1];

  // Mapa safra_id → SafraResponse
  var sf1 = React.useState({});
  var safraMap = sf1[0];
  var setSafraMap = sf1[1];

  // Consulta sendo monitorada ativamente
  var sa1 = React.useState(null);
  var activeId = sa1[0];
  var setActiveId = sa1[1];

  // Clusters da consulta selecionada para exibição de resultados
  var sr1 = React.useState(null);
  var clusters = sr1[0];
  var setClusters = sr1[1];
  var sr2 = React.useState(null);
  var selectedId = sr2[0];
  var setSelectedId = sr2[1];
  var sr3 = React.useState(false);
  var loadingClusters = sr3[0];
  var setLoadingClusters = sr3[1];

  // Paginação da tabela de clusters
  var sp1 = React.useState(1);
  var tablePage = sp1[0];
  var setTablePage = sp1[1];
  var TABLE_PER_PAGE = 20;

  // -------------------------------------------------------------------------
  // Refs
  // -------------------------------------------------------------------------

  var inputRef = React.useRef(null);
  // { timer: TimeoutId | null, consultaId: string | null }
  var pollRef = React.useRef({ timer: null, consultaId: null });

  // -------------------------------------------------------------------------
  // Efeito: carrega histórico e safras ao montar; limpa timer ao desmontar
  // -------------------------------------------------------------------------

  React.useEffect(function () {
    Promise.all([Api.listConsultas(), Api.listSafras()])
      .then(function (results) {
        setConsultas(results[0]);
        var map = {};
        results[1].forEach(function (s) {
          map[s.id] = s;
        });
        setSafraMap(map);
        setLoadingHistory(false);
      })
      .catch(function () {
        setLoadingHistory(false);
      });

    return function () {
      if (pollRef.current.timer) clearTimeout(pollRef.current.timer);
    };
  }, []);

  // -------------------------------------------------------------------------
  // Polling
  // -------------------------------------------------------------------------

  function atualizarConsultaNaLista(atualizada) {
    setConsultas(function (prev) {
      return prev.map(function (c) {
        return c.id === atualizada.id ? atualizada : c;
      });
    });
    // Atualiza o safraMap se a safra for nova
    if (atualizada.safra_id) {
      Api.listSafras()
        .then(function (safras) {
          var map = {};
          safras.forEach(function (s) {
            map[s.id] = s;
          });
          setSafraMap(map);
        })
        .catch(function () {});
    }
  }

  function verificarConsulta(consultaId) {
    Api.getConsulta(consultaId)
      .then(function (c) {
        atualizarConsultaNaLista(c);

        if (c.status_consulta === "concluido") {
          // Pipeline terminou — busca clusters e exibe resultados
          setLoadingClusters(true);
          Api.getClusters(c.id)
            .then(function (cls) {
              setClusters(cls);
              setSelectedId(c.id);
              setLoadingClusters(false);
              if (setHasData) setHasData(true);
            })
            .catch(function () {
              setLoadingClusters(false);
            });
          // Não agenda próximo tick
        } else if (c.status_consulta === "erro") {
          // Para de pingar
        } else {
          // Ainda "pendente" ou "executando" — agenda próximo ping em 60s
          pollRef.current.timer = setTimeout(function () {
            verificarConsulta(consultaId);
          }, 60000);
        }
      })
      .catch(function () {
        // Erro de rede — tenta novamente em 60s
        pollRef.current.timer = setTimeout(function () {
          verificarConsulta(consultaId);
        }, 60000);
      });
  }

  function iniciarPolling(consultaId) {
    if (pollRef.current.timer) clearTimeout(pollRef.current.timer);
    pollRef.current.consultaId = consultaId;
    // Primeiro ping em 5s (tempo para o backend iniciar o background task)
    pollRef.current.timer = setTimeout(function () {
      verificarConsulta(consultaId);
    }, 5000);
  }

  function handleVerificarAgora() {
    var cid = pollRef.current.consultaId;
    if (!cid) return;
    if (pollRef.current.timer) clearTimeout(pollRef.current.timer);
    verificarConsulta(cid);
  }

  // -------------------------------------------------------------------------
  // Handlers de upload
  // -------------------------------------------------------------------------

  function handleFile(f) {
    if (!f) return;
    if (!f.name.endsWith(".parquet")) {
      setUploadError("Formato inválido. Apenas arquivos .parquet são aceitos.");
      return;
    }
    setUploadError(null);
    setFile(f);
  }

  function onDrop(e) {
    e.preventDefault();
    setDrag(false);
    if (e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0]);
  }

  function iniciarUpload(usarSafraExistente) {
    setShowConflito(false);
    setUploadError(null);
    setUploadProgress(0);
    setUploadStep("iniciando");
    setEnvioModal(true);

    var safraNum = safraInput.trim() ? parseInt(safraInput.trim(), 10) : null;
    if (safraNum !== null && isNaN(safraNum)) safraNum = null;

    var totalChunks = Math.ceil(file.size / CHUNK_SIZE);
    var uploadId = null;

    // 1. Iniciar sessão de upload
    Api.iniciarUpload(file.name)
      .then(function (res) {
        uploadId = res.upload_id;
        setUploadStep("enviando");

        // 2. Enviar chunks sequencialmente via Promise chain
        var chain = Promise.resolve();
        for (var i = 0; i < totalChunks; i++) {
          (function (index) {
            chain = chain.then(function () {
              var start = index * CHUNK_SIZE;
              var end = Math.min(start + CHUNK_SIZE, file.size);
              var blob = file.slice(start, end);
              return Api.enviarChunk(uploadId, index, blob, file.name).then(
                function () {
                  setUploadProgress(
                    Math.round(((index + 1) / totalChunks) * 100),
                  );
                },
              );
            });
          })(i);
        }
        return chain;
      })
      .then(function () {
        // 3. Finalizar — remonta o arquivo no servidor e dispara o pipeline
        setUploadStep("finalizando");
        return Api.finalizarUpload(
          uploadId,
          null,
          safraNum,
          usarSafraExistente || false,
        );
      })
      .then(function (c) {
        setEnvioModal(false);
        setFile(null);
        setSafraInput("");
        setMostrarOpcAvancadas(false);

        setConsultas(function (prev) {
          return [c].concat(
            prev.filter(function (x) {
              return x.id !== c.id;
            }),
          );
        });

        setActiveId(c.id);
        iniciarPolling(c.id);
      })
      .catch(function (err) {
        setEnvioModal(false);
        if (err.status === 409) {
          setSafraConflitada(safraNum);
          setShowConflito(true);
        } else {
          setUploadError(
            err.message || "Erro ao enviar arquivo. Tente novamente.",
          );
        }
      });
  }

  function handleExecutar() {
    iniciarUpload(false);
  }

  // -------------------------------------------------------------------------
  // Handler: selecionar consulta concluída para ver resultados
  // -------------------------------------------------------------------------

  function handleSelecionarConsulta(c) {
    if (c.status_consulta !== "concluido") return;
    if (selectedId === c.id) return;
    setSelectedId(c.id);
    setClusters(null);
    setTablePage(1);
    setLoadingClusters(true);
    Api.getClusters(c.id)
      .then(function (cls) {
        setClusters(cls);
        setLoadingClusters(false);
      })
      .catch(function () {
        setLoadingClusters(false);
      });
  }

  // -------------------------------------------------------------------------
  // Handler: exportar CSV de clientes
  // -------------------------------------------------------------------------

  function handleExportar(consultaId) {
    Api.exportClientes(consultaId)
      .then(function (blob) {
        var url = URL.createObjectURL(blob);
        var a = document.createElement("a");
        a.href = url;
        a.download = "clientes_" + consultaId.slice(0, 8) + ".csv";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      })
      .catch(function (err) {
        alert("Erro ao exportar: " + err.message);
      });
  }

  // -------------------------------------------------------------------------
  // Helpers de formatação
  // -------------------------------------------------------------------------

  function formatBytes(bytes) {
    if (!bytes) return "";
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(2) + " MB";
  }

  function formatDateTime(iso) {
    if (!iso) return "—";
    return new Date(iso).toLocaleString("pt-BR", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  function formatDuration(inicio, fim) {
    if (!inicio || !fim) return null;
    var ms = new Date(fim) - new Date(inicio);
    var s = Math.floor(ms / 1000);
    if (s < 60) return s + "s";
    return Math.floor(s / 60) + "m " + (s % 60) + "s";
  }

  function getStatusMeta(status) {
    if (status === "pendente")
      return {
        label: "Aguardando início",
        cor: "#FAE95D",
        corTexto: "#7a6a00",
        spinning: false,
      };
    if (status === "executando")
      return {
        label: "Em execução",
        cor: "#2E6DA4",
        corTexto: "#2E6DA4",
        spinning: true,
      };
    if (status === "concluido")
      return {
        label: "Concluído",
        cor: "#67DE98",
        corTexto: "#1a7a4a",
        spinning: false,
      };
    if (status === "erro")
      return {
        label: "Erro",
        cor: "#FF5D5C",
        corTexto: "#DC2F37",
        spinning: false,
      };
    return {
      label: status,
      cor: "#9C9C9F",
      corTexto: "#9C9C9F",
      spinning: false,
    };
  }

  function getEtapaLabel(etapa) {
    if (etapa === "calibracao") return "Calibração";
    if (etapa === "clustering") return "Clustering (CART)";
    if (etapa === "otimizacao") return "Otimização (Simplex)";
    return etapa || "Desconhecida";
  }

  // -------------------------------------------------------------------------
  // Derivados
  // -------------------------------------------------------------------------

  var selectedConsulta = null;
  for (var i = 0; i < consultas.length; i++) {
    if (consultas[i].id === selectedId) {
      selectedConsulta = consultas[i];
      break;
    }
  }

  var activeConsulta = null;
  for (var j = 0; j < consultas.length; j++) {
    if (consultas[j].id === activeId) {
      activeConsulta = consultas[j];
      break;
    }
  }

  var isRunning =
    activeConsulta &&
    (activeConsulta.status_consulta === "pendente" ||
      activeConsulta.status_consulta === "executando");

  // Dados para gráfico de barras (top 15 clusters por limite)
  var barData = [];
  if (clusters) {
    var sorted = clusters.slice().sort(function (a, b) {
      return b.limite_otimizado - a.limite_otimizado;
    });
    barData = sorted.slice(0, 15).map(function (c) {
      return { label: "CLU-" + c.cluster_id, value: c.limite_otimizado };
    });
  }

  // Dados para donut (distribuição de clientes)
  var donutData = [];
  if (selectedConsulta && selectedConsulta.status_consulta === "concluido") {
    var nOfer = selectedConsulta.n_clientes_ofertados || 0;
    var nEleg = selectedConsulta.n_clientes_elegiveis || 0;
    var nTotal = selectedConsulta.n_clientes_total || 0;
    donutData = [
      { name: "Com limite", value: nOfer, color: "#67DE98" },
      {
        name: "Elegível, sem limite",
        value: Math.max(0, nEleg - nOfer),
        color: "#FAE95D",
      },
      {
        name: "Inelegível",
        value: Math.max(0, nTotal - nEleg),
        color: "#B8D4EC",
      },
    ];
  }

  // Paginação da tabela de clusters
  var clustersPaginados = clusters
    ? clusters.slice(
        (tablePage - 1) * TABLE_PER_PAGE,
        tablePage * TABLE_PER_PAGE,
      )
    : [];
  var totalPaginas = clusters ? Math.ceil(clusters.length / TABLE_PER_PAGE) : 1;

  // -------------------------------------------------------------------------
  // Render
  // -------------------------------------------------------------------------

  return (
    <div className="space-y-6">
      {/* ------------------------------------------------------------------ */}
      {/* Header                                                               */}
      {/* ------------------------------------------------------------------ */}
      <div>
        <h1 className="text-xl font-bold text-[#0D1B2A]">Gerar Limites</h1>
        <p className="mt-1 text-xs text-[#9C9C9F]">
          Faça upload da base em formato .parquet e execute o pipeline de
          otimização
        </p>
        <div className="mt-1 h-0.5 w-10 bg-[#2E6DA4]" />
      </div>

      {/* Modal de envio com progresso de chunks */}
      {envioModal && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
          <div className="bg-white border border-[#E8EFF7] shadow-2xl w-full max-w-sm p-8 flex flex-col items-center gap-5 text-center">
            {/* Ícone */}
            <div className="w-14 h-14 bg-[#D6E8F5] flex items-center justify-center">
              <svg
                width="24"
                height="24"
                fill="none"
                viewBox="0 0 24 24"
                stroke="#2E6DA4"
                strokeWidth="2"
              >
                <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
                <polyline points="17 8 12 3 7 8" />
                <line x1="12" y1="3" x2="12" y2="15" />
              </svg>
            </div>

            {/* Título e subtítulo */}
            <div>
              <p className="text-sm font-semibold text-[#0D1B2A]">
                {uploadStep === "iniciando" && "Preparando upload..."}
                {uploadStep === "enviando" && "Enviando arquivo..."}
                {uploadStep === "finalizando" && "Registrando simulação..."}
              </p>
              <p className="text-xs text-[#9C9C9F] mt-1">
                {uploadStep === "enviando"
                  ? "O arquivo está sendo enviado em partes. Não feche esta janela."
                  : "Aguarde um momento."}
              </p>
            </div>

            {/* Barra de progresso — só aparece durante o envio de chunks */}
            {uploadStep === "enviando" && (
              <div className="w-full space-y-1.5">
                <div className="w-full bg-[#E2EAF4] h-2">
                  <div
                    className="h-2 bg-[#2E6DA4] transition-all duration-300"
                    style={{ width: uploadProgress + "%" }}
                  />
                </div>
                <div className="flex justify-between text-[11px] text-[#9C9C9F]">
                  <span>{uploadProgress}%</span>
                  <span>
                    {formatBytes(
                      Math.round((file.size * uploadProgress) / 100),
                    )}{" "}
                    de {formatBytes(file.size)}
                  </span>
                </div>
              </div>
            )}

            {/* Informações do arquivo */}
            {file && (
              <div className="w-full bg-[#E2EAF4] border border-[#E8EFF7] px-4 py-3 text-left">
                <div className="flex items-center gap-2">
                  <svg
                    width="14"
                    height="14"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="#2E6DA4"
                    strokeWidth="2"
                  >
                    <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
                    <polyline points="14 2 14 8 20 8" />
                  </svg>
                  <span className="text-xs font-semibold text-[#0D1B2A] truncate">
                    {file.name}
                  </span>
                </div>
                <p className="text-[10px] text-[#9C9C9F] mt-1 pl-5">
                  {formatBytes(file.size)}
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------------ */}
      {/* Seção de upload                                                      */}
      {/* ------------------------------------------------------------------ */}
      <div className="bg-white border border-[#E8EFF7] shadow-sm p-5 space-y-5">
        <div className="flex items-center gap-2">
          <svg
            width="15"
            height="15"
            fill="none"
            viewBox="0 0 24 24"
            stroke="#2E6DA4"
            strokeWidth="2"
          >
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
            <polyline points="17 8 12 3 7 8" />
            <line x1="12" y1="3" x2="12" y2="15" />
          </svg>
          <span className="text-sm font-semibold text-[#0D1B2A]">
            Nova Simulação
          </span>
        </div>

        {/* Estrutura esperada do parquet */}
        <div>
          <p className="text-xs font-semibold text-[#9C9C9F] uppercase tracking-wide mb-2">
            Colunas esperadas no .parquet
          </p>
          <div className="overflow-x-auto border border-[#E8EFF7]">
            <table className="w-full text-xs">
              <thead>
                <tr className="bg-[#0D1B2A]">
                  {["Coluna", "Tipo", "Descrição"].map(function (h) {
                    return (
                      <th
                        key={h}
                        className="px-3 py-2 text-left font-semibold text-white uppercase tracking-wide whitespace-nowrap"
                      >
                        {h}
                      </th>
                    );
                  })}
                </tr>
              </thead>
              <tbody>
                {[
                  {
                    col: "token",
                    tipo: "int",
                    desc: "Identificador único do cliente",
                  },
                  {
                    col: "flag_filtros",
                    tipo: "int",
                    desc: "0 = elegível para otimização · 1 = excluído",
                  },
                  {
                    col: "score_interno",
                    tipo: "int",
                    desc: "Score interno do produto",
                  },
                  {
                    col: "pd_produto",
                    tipo: "float",
                    desc: "Probabilidade de default do produto",
                  },
                  {
                    col: "score_credito_cross",
                    tipo: "int",
                    desc: "Score de crédito cross (300–900)",
                  },
                  {
                    col: "score_propensao_contrato",
                    tipo: "float",
                    desc: "Score de propensão ao contrato (3–846)",
                  },
                  {
                    col: "capacidade_pagamento",
                    tipo: "float?",
                    desc: "Capacidade de pagamento em R$ (opcional)",
                  },
                  {
                    col: "renda_estimada",
                    tipo: "float?",
                    desc: "Renda estimada em R$ (opcional)",
                  },
                  {
                    col: "fx_idade",
                    tipo: "string",
                    desc: "Faixa etária categórica (ex: 26-35)",
                  },
                  {
                    col: "flag_contrato",
                    tipo: "int",
                    desc: "1 = cliente com contrato ativo",
                  },
                  {
                    col: "flag_ativacao",
                    tipo: "int",
                    desc: "1 = cliente ativado",
                  },
                ].map(function (r, i) {
                  return (
                    <tr
                      key={r.col}
                      className={
                        "border-t border-[#E8EFF7] " +
                        (i % 2 === 0 ? "" : "bg-[#E2EAF4]/50")
                      }
                    >
                      <td className="px-3 py-2 font-mono font-semibold text-[#2E6DA4] whitespace-nowrap">
                        {r.col}
                      </td>
                      <td className="px-3 py-2 text-[#9C9C9F] whitespace-nowrap font-mono">
                        {r.tipo}
                      </td>
                      <td className="px-3 py-2 text-[#3B4049]">{r.desc}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Dropzone */}
        <div>
          <input
            ref={inputRef}
            type="file"
            accept=".parquet"
            className="hidden"
            onChange={function (e) {
              handleFile(e.target.files[0]);
            }}
          />
          <div
            className={[
              "flex flex-col items-center justify-center gap-3 border-2 border-dashed py-12 px-6 cursor-pointer transition-colors",
              drag
                ? "border-[#2E6DA4] bg-[#D6E8F5]"
                : file
                  ? "border-[#2E6DA4] bg-[#D6E8F5]/40"
                  : "border-[#B8D4EC] bg-[#F7FAFD] hover:border-[#2E6DA4] hover:bg-[#D6E8F5]/30",
            ].join(" ")}
            onDragOver={function (e) {
              e.preventDefault();
              setDrag(true);
            }}
            onDragLeave={function () {
              setDrag(false);
            }}
            onDrop={onDrop}
            onClick={function () {
              inputRef.current.click();
            }}
          >
            <div
              className={[
                "w-14 h-14 flex items-center justify-center transition-colors",
                file ? "bg-[#2E6DA4]" : "bg-[#D6E8F5]",
              ].join(" ")}
            >
              <svg
                width="24"
                height="24"
                fill="none"
                viewBox="0 0 24 24"
                stroke={file ? "white" : "#2E6DA4"}
                strokeWidth="2"
              >
                <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
                <polyline points="17 8 12 3 7 8" />
                <line x1="12" y1="3" x2="12" y2="15" />
              </svg>
            </div>

            {file ? (
              <div className="text-center">
                <p className="text-sm font-semibold text-[#0D1B2A]">
                  {file.name}
                </p>
                <p className="text-xs text-[#9C9C9F] mt-0.5">
                  {formatBytes(file.size)}
                </p>
                <p className="text-xs text-[#2E6DA4] mt-1">
                  Clique para substituir ou arraste outro arquivo
                </p>
              </div>
            ) : (
              <div className="text-center">
                <p className="text-sm font-semibold text-[#0D1B2A]">
                  Arraste o arquivo aqui ou clique para selecionar
                </p>
                <p className="text-xs text-[#9C9C9F] mt-0.5">
                  Somente arquivos{" "}
                  <span className="font-semibold">.parquet</span>
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Erro de validação */}
        {uploadError && (
          <div className="flex items-start gap-2 px-3 py-2.5 bg-[#FF5D5C]/10 border border-[#FF5D5C]/30 text-xs text-[#DC2F37]">
            <svg
              width="13"
              height="13"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth="2.5"
              className="flex-shrink-0 mt-0.5"
            >
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            {uploadError}
          </div>
        )}

        {/* Conflito 409 */}
        {showConflito && (
          <div className="border border-[#FAE95D]/70 bg-[#FAE95D]/10 p-4 space-y-3">
            <div className="flex items-start gap-2">
              <svg
                width="15"
                height="15"
                fill="none"
                viewBox="0 0 24 24"
                stroke="#7a6a00"
                strokeWidth="2"
                className="flex-shrink-0 mt-0.5"
              >
                <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
                <line x1="12" y1="9" x2="12" y2="13" />
                <line x1="12" y1="17" x2="12.01" y2="17" />
              </svg>
              <div>
                <p className="text-xs font-semibold text-[#3B4049]">
                  Safra M{safraConflitada} já existe
                </p>
                <p className="text-xs text-[#9C9C9F] mt-0.5">
                  Deseja criar a consulta vinculada à safra existente, ou
                  cancelar e informar outro número?
                </p>
              </div>
            </div>
            <div className="flex gap-2">
              <button
                onClick={function () {
                  iniciarUpload(true);
                }}
                className="flex-1 py-1.5 text-xs font-semibold bg-[#2E6DA4] text-white hover:bg-[#1B3A5C] transition-colors"
              >
                Usar safra existente
              </button>
              <button
                onClick={function () {
                  setShowConflito(false);
                }}
                className="flex-1 py-1.5 text-xs font-semibold bg-[#E8EFF7] text-[#3B4049] hover:bg-[#B8D4EC] transition-colors"
              >
                Cancelar
              </button>
            </div>
          </div>
        )}

        {/* Opções avançadas */}
        <div>
          <button
            onClick={function () {
              setMostrarOpcAvancadas(function (v) {
                return !v;
              });
            }}
            className="flex items-center gap-1.5 text-xs font-medium text-[#9C9C9F] hover:text-[#3B4049] transition-colors"
          >
            <svg
              width="12"
              height="12"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth="2.5"
              style={{
                transform: mostrarOpcAvancadas
                  ? "rotate(90deg)"
                  : "rotate(0deg)",
                transition: "transform 0.15s",
              }}
            >
              <polyline points="9 18 15 12 9 6" />
            </svg>
            Opções avançadas
          </button>

          {mostrarOpcAvancadas && (
            <div className="mt-3 p-4 bg-[#E2EAF4] border border-[#E8EFF7] space-y-1">
              <label className="text-xs font-semibold text-[#3B4049]">
                Número da safra{" "}
                <span className="text-[#9C9C9F] font-normal">
                  (opcional — deixe em branco para incremento automático)
                </span>
              </label>
              <div className="flex items-center gap-2 mt-1.5">
                <span className="text-sm font-bold text-[#2E6DA4]">M</span>
                <input
                  type="number"
                  min="1"
                  placeholder="ex: 4"
                  value={safraInput}
                  onChange={function (e) {
                    setSafraInput(e.target.value);
                  }}
                  className="w-32 px-3 py-1.5 text-sm border border-[#E8EFF7] bg-white focus:outline-none focus:border-[#2E6DA4] focus:ring-1 focus:ring-[#2E6DA4]"
                />
              </div>
              <p className="text-[11px] text-[#9C9C9F]">
                Se a safra já existir, o sistema pedirá confirmação antes de
                reutilizá-la.
              </p>
            </div>
          )}
        </div>

        {/* Botão executar */}
        {file && (
          <div className="flex items-center gap-3 pt-1">
            <button
              onClick={handleExecutar}
              className="flex items-center gap-2 px-5 py-2.5 text-sm font-semibold bg-[#2E6DA4] text-white hover:bg-[#1B3A5C] transition-colors shadow-sm"
            >
              <svg
                width="15"
                height="15"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth="2.5"
              >
                <polygon points="5 3 19 12 5 21 5 3" />
              </svg>
              Executar Simplex
            </button>
            <div className="flex items-center gap-1.5 text-xs text-[#9C9C9F]">
              <svg
                width="12"
                height="12"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth="2"
              >
                <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
                <polyline points="14 2 14 8 20 8" />
              </svg>
              {file.name} · {formatBytes(file.size)}
            </div>
          </div>
        )}
      </div>

      {/* ------------------------------------------------------------------ */}
      {/* Lista de simulações                                                  */}
      {/* ------------------------------------------------------------------ */}
      <div className="bg-white border border-[#E8EFF7] shadow-sm overflow-hidden">
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
            Simulações
          </div>

          {isRunning && (
            <button
              onClick={handleVerificarAgora}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium border border-[#E8EFF7] text-[#3B4049] hover:bg-[#E2EAF4] transition-colors"
            >
              <svg
                width="12"
                height="12"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth="2"
              >
                <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
                <path d="M3 3v5h5" />
              </svg>
              Verificar agora
            </button>
          )}
        </div>

        {loadingHistory ? (
          <div className="flex items-center justify-center py-12 gap-2 text-sm text-[#9C9C9F]">
            <svg
              className="animate-spin"
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0" />
            </svg>
            Carregando histórico...
          </div>
        ) : consultas.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 gap-2 text-center">
            <svg
              width="32"
              height="32"
              fill="none"
              viewBox="0 0 24 24"
              stroke="#B8D4EC"
              strokeWidth="1.5"
            >
              <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
              <polyline points="14 2 14 8 20 8" />
            </svg>
            <p className="text-sm text-[#9C9C9F]">
              Nenhuma simulação registrada
            </p>
            <p className="text-xs text-[#9C9C9F]">
              Faça upload de um .parquet para começar
            </p>
          </div>
        ) : (
          <div className="divide-y divide-[#E8EFF7]">
            {consultas.map(function (c) {
              var meta = getStatusMeta(c.status_consulta);
              var safra = safraMap[c.safra_id];
              var isSelected = c.id === selectedId;
              var isActive = c.id === activeId;

              return (
                <div
                  key={c.id}
                  className={[
                    "px-5 py-4 transition-colors",
                    c.status_consulta === "concluido"
                      ? "cursor-pointer hover:bg-[#E2EAF4]"
                      : "",
                    isSelected ? "bg-[#D6E8F5]/60" : "",
                  ].join(" ")}
                  onClick={function () {
                    handleSelecionarConsulta(c);
                  }}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex items-start gap-3 min-w-0">
                      {/* Ícone de status */}
                      <div className="flex-shrink-0 mt-0.5">
                        {meta.spinning ? (
                          <svg
                            className="animate-spin"
                            width="16"
                            height="16"
                            viewBox="0 0 24 24"
                            fill="none"
                          >
                            <circle
                              cx="12"
                              cy="12"
                              r="10"
                              stroke="#E8EFF7"
                              strokeWidth="3"
                            />
                            <path
                              d="M12 2a10 10 0 0 1 10 10"
                              stroke="#2E6DA4"
                              strokeWidth="3"
                              strokeLinecap="round"
                            />
                          </svg>
                        ) : c.status_consulta === "concluido" ? (
                          <svg
                            width="16"
                            height="16"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="#1a7a4a"
                            strokeWidth="2.5"
                          >
                            <circle
                              cx="12"
                              cy="12"
                              r="10"
                              fill="#67DE98"
                              fillOpacity="0.2"
                              stroke="#67DE98"
                            />
                            <polyline
                              points="9 12 11 14 15 10"
                              stroke="#1a7a4a"
                            />
                          </svg>
                        ) : c.status_consulta === "erro" ? (
                          <svg
                            width="16"
                            height="16"
                            fill="none"
                            viewBox="0 0 24 24"
                          >
                            <circle
                              cx="12"
                              cy="12"
                              r="10"
                              fill="#FF5D5C"
                              fillOpacity="0.15"
                              stroke="#FF5D5C"
                              strokeWidth="2"
                            />
                            <line
                              x1="9"
                              y1="9"
                              x2="15"
                              y2="15"
                              stroke="#DC2F37"
                              strokeWidth="2.5"
                            />
                            <line
                              x1="15"
                              y1="9"
                              x2="9"
                              y2="15"
                              stroke="#DC2F37"
                              strokeWidth="2.5"
                            />
                          </svg>
                        ) : (
                          <svg
                            width="16"
                            height="16"
                            fill="none"
                            viewBox="0 0 24 24"
                          >
                            <circle
                              cx="12"
                              cy="12"
                              r="10"
                              fill="#FAE95D"
                              fillOpacity="0.3"
                              stroke="#FAE95D"
                              strokeWidth="2"
                            />
                            <line
                              x1="12"
                              y1="8"
                              x2="12"
                              y2="12"
                              stroke="#7a6a00"
                              strokeWidth="2"
                            />
                            <line
                              x1="12"
                              y1="16"
                              x2="12.01"
                              y2="16"
                              stroke="#7a6a00"
                              strokeWidth="2"
                            />
                          </svg>
                        )}
                      </div>

                      {/* Info principal */}
                      <div className="min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="text-sm font-semibold text-[#0D1B2A] truncate">
                            {c.nome_arquivo_parquet}
                          </span>
                          {safra && (
                            <span className="inline-flex items-center px-2 py-0.5 text-[11px] font-semibold bg-[#D6E8F5] text-[#2E6DA4]">
                              {safra.nome}
                            </span>
                          )}
                          {isActive && isRunning && (
                            <span className="inline-flex items-center px-2 py-0.5 text-[11px] font-medium bg-[#2E6DA4]/10 text-[#2E6DA4]">
                              atual
                            </span>
                          )}
                        </div>

                        {/* Status label */}
                        <p
                          className="text-xs mt-0.5"
                          style={{ color: meta.corTexto }}
                        >
                          {meta.label}
                        </p>

                        {/* Detalhes por status */}
                        {(c.status_consulta === "pendente" ||
                          c.status_consulta === "executando") && (
                          <div className="flex items-center gap-3 mt-2">
                            {[
                              "Calibração",
                              "Clustering (CART)",
                              "Otimização (Simplex)",
                            ].map(function (etapa, idx) {
                              return (
                                <div
                                  key={etapa}
                                  className="flex items-center gap-1.5"
                                >
                                  {idx > 0 && (
                                    <svg
                                      width="10"
                                      height="10"
                                      fill="none"
                                      viewBox="0 0 24 24"
                                      stroke="#B8D4EC"
                                      strokeWidth="2.5"
                                    >
                                      <polyline points="9 18 15 12 9 6" />
                                    </svg>
                                  )}
                                  <span className="flex items-center gap-1 text-[11px] text-[#9C9C9F]">
                                    <span className="w-1.5 h-1.5 rounded-full bg-[#2E6DA4] animate-pulse inline-block" />
                                    {etapa}
                                  </span>
                                </div>
                              );
                            })}
                          </div>
                        )}

                        {c.status_consulta === "concluido" && (
                          <div className="flex items-center gap-3 mt-1.5 text-[11px] text-[#9C9C9F] flex-wrap">
                            {c.n_clusters != null && (
                              <span>{c.n_clusters} clusters</span>
                            )}
                            {c.n_clientes_elegiveis != null && (
                              <span>
                                ·{" "}
                                {Number(c.n_clientes_elegiveis).toLocaleString(
                                  "pt-BR",
                                )}{" "}
                                elegíveis
                              </span>
                            )}
                            {c.z_otimo != null && (
                              <span>· z = {fmtZ(c.z_otimo)}</span>
                            )}
                            {formatDuration(c.iniciado_em, c.concluido_em) && (
                              <span>
                                ·{" "}
                                {formatDuration(c.iniciado_em, c.concluido_em)}
                              </span>
                            )}
                          </div>
                        )}

                        {c.status_consulta === "erro" && (
                          <div className="mt-2 space-y-0.5">
                            <p className="text-[11px] font-semibold text-[#DC2F37]">
                              Falhou em: {getEtapaLabel(c.erro_etapa)}
                            </p>
                            {c.erro_mensagem && (
                              <p
                                className="text-[11px] text-[#9C9C9F] font-mono truncate max-w-sm"
                                title={c.erro_mensagem}
                              >
                                {c.erro_mensagem}
                              </p>
                            )}
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Direita: data + ações */}
                    <div className="flex-shrink-0 text-right space-y-2">
                      <p className="text-[11px] text-[#9C9C9F]">
                        {formatDateTime(c.criado_em)}
                      </p>

                      {c.status_consulta === "concluido" && (
                        <div className="flex items-center gap-1 justify-end">
                          <button
                            onClick={function (e) {
                              e.stopPropagation();
                              handleSelecionarConsulta(c);
                            }}
                            className={
                              "px-2.5 py-1 text-[11px] font-semibold transition-colors " +
                              (isSelected
                                ? "bg-[#2E6DA4] text-white"
                                : "border border-[#E8EFF7] text-[#3B4049] hover:bg-[#E2EAF4]")
                            }
                          >
                            {isSelected ? "Selecionado" : "Ver resultados"}
                          </button>
                          <button
                            onClick={function (e) {
                              e.stopPropagation();
                              handleExportar(c.id);
                            }}
                            className="px-2.5 py-1 text-[11px] font-medium border border-[#E8EFF7] text-[#9C9C9F] hover:bg-[#E2EAF4] transition-colors"
                            title="Exportar clientes CSV"
                          >
                            <svg
                              width="11"
                              height="11"
                              fill="none"
                              viewBox="0 0 24 24"
                              stroke="currentColor"
                              strokeWidth="2"
                            >
                              <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
                              <polyline points="7 10 12 15 17 10" />
                              <line x1="12" y1="15" x2="12" y2="3" />
                            </svg>
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Rodapé: polling info */}
        {isRunning && (
          <div className="flex items-center gap-2 px-5 py-2.5 border-t border-[#E8EFF7] bg-[#E2EAF4]/50">
            <svg
              className="animate-spin"
              width="11"
              height="11"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#2E6DA4"
              strokeWidth="2.5"
            >
              <path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0" />
            </svg>
            <span className="text-[11px] text-[#9C9C9F]">
              Verificando automaticamente a cada 60 segundos ·{" "}
              <button
                onClick={handleVerificarAgora}
                className="text-[#2E6DA4] hover:underline font-medium"
              >
                verificar agora
              </button>
            </span>
          </div>
        )}
      </div>

      {/* ------------------------------------------------------------------ */}
      {/* Resultados da consulta selecionada                                   */}
      {/* ------------------------------------------------------------------ */}
      {selectedConsulta && selectedConsulta.status_consulta === "concluido" && (
        <div className="space-y-5">
          {/* Header de resultados */}
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-[#0D1B2A]">
                Resultados da Simulação
              </h2>
              <p className="text-xs text-[#9C9C9F] mt-0.5">
                {selectedConsulta.nome_arquivo_parquet}
                {safraMap[selectedConsulta.safra_id] &&
                  " · Safra " + safraMap[selectedConsulta.safra_id].nome}
                {" · Concluído em " +
                  formatDateTime(selectedConsulta.concluido_em)}
              </p>
            </div>
            <button
              onClick={function () {
                handleExportar(selectedConsulta.id);
              }}
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

          {/* KPIs */}
          <div className="grid grid-cols-4 gap-4">
            {[
              {
                label: "Total de Clusters",
                value:
                  selectedConsulta.n_clusters != null
                    ? String(selectedConsulta.n_clusters)
                    : "—",
                sub: "segmentação CART",
                highlight: false,
              },
              {
                label: "Valor Objetivo (z)",
                value:
                  selectedConsulta.z_otimo != null
                    ? fmtZ(selectedConsulta.z_otimo)
                    : "—",
                sub:
                  selectedConsulta.status_lp === "multiplas_solucoes"
                    ? "Múltiplas soluções"
                    : "Solução ótima",
                highlight: true,
              },
              {
                label: "Clientes Elegíveis",
                value:
                  selectedConsulta.n_clientes_elegiveis != null
                    ? Number(
                        selectedConsulta.n_clientes_elegiveis,
                      ).toLocaleString("pt-BR")
                    : "—",
                sub:
                  selectedConsulta.n_clientes_total != null
                    ? "de " +
                      Number(selectedConsulta.n_clientes_total).toLocaleString(
                        "pt-BR",
                      ) +
                      " na base"
                    : "na base",
                highlight: false,
              },
              {
                label: "Clientes Ofertados",
                value:
                  selectedConsulta.n_clientes_ofertados != null
                    ? Number(
                        selectedConsulta.n_clientes_ofertados,
                      ).toLocaleString("pt-BR")
                    : "—",
                sub: selectedConsulta.n_clientes_elegiveis
                  ? (
                      (selectedConsulta.n_clientes_ofertados /
                        selectedConsulta.n_clientes_elegiveis) *
                      100
                    ).toFixed(1) + "% dos elegíveis"
                  : "",
                highlight: false,
              },
            ].map(function (k) {
              return (
                <div
                  key={k.label}
                  className={
                    "border shadow-sm p-5 " +
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
                      "text-xl font-bold mb-1 leading-tight " +
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

          {/* Loading de clusters */}
          {loadingClusters && (
            <div className="flex items-center justify-center py-10 gap-2 text-sm text-[#9C9C9F] bg-white border border-[#E8EFF7]">
              <svg
                className="animate-spin"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0" />
              </svg>
              Carregando dados dos clusters...
            </div>
          )}

          {/* Gráficos */}
          {clusters && !loadingClusters && (
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-white border border-[#E8EFF7] shadow-sm p-5">
                <div className="text-sm font-semibold text-[#0D1B2A] mb-1">
                  Top 15 Clusters por Limite
                </div>
                <div className="text-xs text-[#9C9C9F] mb-4">
                  Limite ótimo atribuído a cada cluster pelo Simplex (R$)
                </div>
                <BarChartSVG data={barData} />
              </div>

              <div className="bg-white border border-[#E8EFF7] shadow-sm p-5">
                <div className="text-sm font-semibold text-[#0D1B2A] mb-1">
                  Distribuição de Clientes
                </div>
                <div className="text-xs text-[#9C9C9F] mb-4">
                  Proporção por elegibilidade e oferta de limite
                </div>
                <div className="flex items-center gap-6">
                  <DonutChart data={donutData} />
                  <div className="space-y-3 flex-1">
                    {donutData.map(function (d) {
                      return (
                        <div
                          key={d.name}
                          className="flex items-center gap-2 text-sm"
                        >
                          <div
                            className="w-2.5 h-2.5 flex-shrink-0"
                            style={{ background: d.color }}
                          />
                          <span className="font-medium text-[#3B4049] flex-1">
                            {d.name}
                          </span>
                          <span className="font-semibold text-[#0D1B2A]">
                            {Number(d.value).toLocaleString("pt-BR")}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Tabela de clusters */}
          {clusters && !loadingClusters && (
            <div className="bg-white border border-[#E8EFF7] shadow-sm overflow-hidden">
              <div className="flex items-center justify-between px-5 py-4 border-b border-[#E8EFF7]">
                <div className="text-sm font-semibold text-[#0D1B2A]">
                  Clusters — Resultados Detalhados
                </div>
                <span className="text-xs text-[#9C9C9F]">
                  {clusters.length} clusters · página {tablePage} de{" "}
                  {totalPaginas}
                </span>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="bg-[#0D1B2A]">
                      {[
                        "Cluster",
                        "Clientes",
                        "PD Média",
                        "Score Cross Médio",
                        "Fator Alavancagem",
                        "Limite Otimizado",
                        "Status",
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
                    {clustersPaginados.map(function (c, i) {
                      var temLimite = c.limite_otimizado > 0;
                      return (
                        <tr
                          key={c.cluster_id}
                          className={
                            "border-b border-[#E2EAF4] hover:bg-[#E2EAF4] transition-colors " +
                            (i % 2 === 0 ? "" : "bg-[#F7FAFD]")
                          }
                        >
                          <td className="px-3 py-2.5 font-mono font-semibold text-[#2E6DA4]">
                            CLU-{c.cluster_id}
                          </td>
                          <td className="px-3 py-2.5 text-[#3B4049]">
                            {Number(c.n_clientes).toLocaleString("pt-BR")}
                          </td>
                          <td className="px-3 py-2.5 text-[#3B4049]">
                            {(c.pd_media * 100).toFixed(2)}%
                          </td>
                          <td className="px-3 py-2.5 text-[#3B4049]">
                            {Math.round(c.score_credito_cross_medio)}
                          </td>
                          <td className="px-3 py-2.5 text-[#3B4049]">
                            {c.fator_alavancagem.toFixed(2)}x
                          </td>
                          <td className="px-3 py-2.5 font-semibold text-[#0D1B2A]">
                            {temLimite ? fmt(c.limite_otimizado) : "—"}
                          </td>
                          <td className="px-3 py-2.5">
                            {temLimite ? (
                              <span className="inline-flex items-center gap-1 px-2 py-0.5 text-[11px] font-semibold bg-[#67DE98]/20 text-[#1a7a4a] border border-[#67DE98]/50">
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
                              <span className="inline-flex items-center gap-1 px-2 py-0.5 text-[11px] font-semibold bg-[#FF5D5C]/10 text-[#DC2F37] border border-[#FF5D5C]/30">
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
                                Sem solução
                              </span>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>

              {/* Paginação */}
              {totalPaginas > 1 && (
                <div className="flex items-center justify-between px-5 py-3 border-t border-[#E8EFF7]">
                  <span className="text-xs text-[#9C9C9F]">
                    {(tablePage - 1) * TABLE_PER_PAGE + 1}–
                    {Math.min(tablePage * TABLE_PER_PAGE, clusters.length)} de{" "}
                    {clusters.length}
                  </span>
                  <div className="flex items-center gap-1">
                    <button
                      disabled={tablePage === 1}
                      onClick={function () {
                        setTablePage(function (p) {
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
                          Math.min(tablePage - 2, totalPaginas - 4),
                        );
                        var n = start + i;
                        return (
                          <button
                            key={n}
                            onClick={function () {
                              setTablePage(n);
                            }}
                            className={
                              "w-7 h-7 text-xs font-medium transition-colors " +
                              (tablePage === n
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
                      disabled={tablePage === totalPaginas}
                      onClick={function () {
                        setTablePage(function (p) {
                          return p + 1;
                        });
                      }}
                      className="px-3 h-7 text-xs text-[#9C9C9F] hover:bg-[#E2EAF4] disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                    >
                      Próximo
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
