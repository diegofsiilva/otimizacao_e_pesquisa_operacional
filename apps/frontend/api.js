// api.js -- cliente HTTP para o backend FastAPI.
//
// Endpoints:
//   GET    /api/health
//   GET    /api/safras
//   GET    /api/consultas
//   GET    /api/consultas/{id}
//   GET    /api/consultas/{id}/clusters
//   GET    /api/consultas/{id}/clientes?limit&offset
//   GET    /api/consultas/{id}/clientes/export
//   GET    /api/clientes/{token}
//   GET    /api/config
//   PUT    /api/config                             (JSON)
//
// Upload em chunks (para arquivos grandes):
//   POST   /api/uploads/iniciar?nome_arquivo=...
//   POST   /api/uploads/{id}/chunk?index=N        (multipart, um chunk por vez)
//   POST   /api/uploads/{id}/finalizar            (remonta e dispara pipeline)

var API_BASE_URL =
  window.API_BASE_URL ||
  localStorage.getItem("API_BASE_URL") ||
  "http://127.0.0.1:8000/api";

var Api = {
  // -------------------------------------------------------------------------
  // Núcleo
  // -------------------------------------------------------------------------

  // Faz uma requisição JSON ou multipart.
  // Regra: se body for FormData, deixa o browser definir o Content-Type
  // (necessário para o boundary do multipart). Qualquer outro body é
  // serializado como JSON.
  request: function (path, options) {
    var cfg = options || {};
    var headers = cfg.headers || {};

    if (cfg.body && !(cfg.body instanceof FormData)) {
      headers["Content-Type"] = "application/json";
      cfg.body = JSON.stringify(cfg.body);
    }

    cfg.headers = headers;

    return fetch(API_BASE_URL + path, cfg).then(function (res) {
      if (!res.ok) {
        return res.text().then(function (txt) {
          var msg;
          try {
            // FastAPI devolve {"detail": "..."} em erros
            msg = JSON.parse(txt).detail || txt;
          } catch (_) {
            msg = txt;
          }
          var err = new Error(msg || "Erro na requisicao: " + res.status);
          err.status = res.status;
          return Promise.reject(err);
        });
      }
      if (res.status === 204) return null;
      return res.json();
    });
  },

  // -------------------------------------------------------------------------
  // Health
  // -------------------------------------------------------------------------

  // GET /api/health
  // Retorna: { status: "ok" }
  health: function () {
    return Api.request("/health");
  },

  // -------------------------------------------------------------------------
  // Safras
  // -------------------------------------------------------------------------

  // GET /api/safras
  // Retorna: SafraResponse[]
  //   { id, numero, nome, criado_em }
  listSafras: function () {
    return Api.request("/safras");
  },

  // -------------------------------------------------------------------------
  // Consultas
  // -------------------------------------------------------------------------

  // GET /api/consultas
  // Retorna: ConsultaResponse[] (ordenado por criado_em DESC)
  //   { id, safra_id, nome_arquivo_parquet, parametros, status_consulta,
  //     status_lp, z_otimo, n_clientes_total, n_clientes_elegiveis,
  //     n_clientes_ofertados, n_clusters, criado_em, iniciado_em,
  //     concluido_em, erro_etapa, erro_mensagem }
  listConsultas: function () {
    return Api.request("/consultas");
  },

  // GET /api/consultas/{id}
  // Retorna: ConsultaResponse
  getConsulta: function (consultaId) {
    return Api.request("/consultas/" + encodeURIComponent(consultaId));
  },

  // Polling de status de uma consulta até ela sair de "pendente"/"executando".
  //
  // Parâmetros:
  //   consultaId   string    UUID da consulta
  //   onUpdate     function  chamada a cada tick com a ConsultaResponse atual
  //   intervalMs   int       intervalo entre ticks em ms (default 2000)
  //
  // Retorna uma Promise que resolve com a ConsultaResponse final
  // ("concluido" ou "erro") e rejeita em caso de erro de rede.
  //
  // Para cancelar o polling antes da conclusão, chame o método cancel()
  // no objeto retornado:
  //   var poll = Api.pollConsulta(id, cb);
  //   poll.cancel();
  pollConsulta: function (consultaId, onUpdate, intervalMs) {
    var delay = intervalMs || 2000;
    var cancelled = false;
    var timerId = null;

    var promise = new Promise(function (resolve, reject) {
      function tick() {
        if (cancelled) return;

        Api.getConsulta(consultaId)
          .then(function (consulta) {
            if (cancelled) return;

            if (onUpdate) onUpdate(consulta);

            var consultaStatus = consulta.status_consulta;
            if (consultaStatus === "concluido" || consultaStatus === "erro") {
              resolve(consulta);
            } else {
              // ainda "pendente" ou "executando" - agenda próximo tick
              timerId = setTimeout(tick, delay);
            }
          })
          .catch(function (err) {
            if (!cancelled) reject(err);
          });
      }

      tick();
    });

    promise.cancel = function () {
      cancelled = true;
      if (timerId != null) clearTimeout(timerId);
    };

    return promise;
  },

  // -------------------------------------------------------------------------
  // Upload em chunks
  //
  // Para arquivos grandes, use este fluxo em vez de createConsulta():
  //   1. Api.iniciarUpload(nomeArquivo)          -> { upload_id }
  //   2. Api.enviarChunk(uploadId, index, blob)  -> { ok, index, bytes }  (repetir)
  //   3. Api.finalizarUpload(uploadId, ...)      -> ConsultaResponse
  //
  // O GerarLimites.js divide o File em slices de CHUNK_SIZE bytes e chama
  // enviarChunk() sequencialmente, atualizando a barra de progresso a cada chunk.
  // -------------------------------------------------------------------------

  // POST /api/uploads/iniciar?nome_arquivo={nome}
  // Retorna: { upload_id }
  iniciarUpload: function (nomeArquivo) {
    var qs = "nome_arquivo=" + encodeURIComponent(nomeArquivo);
    return Api.request("/uploads/iniciar?" + qs, { method: "POST" });
  },

  // POST /api/uploads/{id}/chunk?index={n}  (multipart com o blob do chunk)
  // Retorna: { ok, index, bytes }
  enviarChunk: function (uploadId, index, blob, nomeArquivo) {
    var form = new FormData();
    form.append("file", blob, nomeArquivo || "chunk");
    return Api.request(
      "/uploads/" + encodeURIComponent(uploadId) + "/chunk?index=" + index,
      { method: "POST", body: form },
    );
  },

  // POST /api/uploads/{id}/finalizar
  // Remonta o arquivo a partir dos chunks e dispara o pipeline em background.
  // Aceita os mesmos parâmetros opcionais de createConsulta.
  // Retorna: ConsultaResponse com status_consulta = "pendente"
  // Lança erro com status 409 se safraNumero já existir e usarSafraExistente = false.
  finalizarUpload: function (
    uploadId,
    params,
    safraNumero,
    usarSafraExistente,
  ) {
    var query = new URLSearchParams();

    if (safraNumero != null) {
      query.append("safra_numero", String(safraNumero));
    }
    query.append("usar_safra_existente", usarSafraExistente ? "true" : "false");

    // parâmetros do modelo - apenas os que foram informados
    var p = params || {};
    if (p.t != null) query.append("t", String(p.t));
    if (p.LGD != null) query.append("LGD", String(p.LGD));
    if (p.u_bar != null) query.append("u_bar", String(p.u_bar));
    if (p.L_max != null) query.append("L_max", String(p.L_max));
    if (p.T != null) query.append("T", String(p.T));

    var qs = query.toString();
    return Api.request(
      "/uploads/" +
        encodeURIComponent(uploadId) +
        "/finalizar" +
        (qs ? "?" + qs : ""),
      { method: "POST" },
    );
  },

  // -------------------------------------------------------------------------
  // Clusters de uma consulta
  // -------------------------------------------------------------------------

  // GET /api/consultas/{id}/clusters
  // Retorna: ClusterResultadoResponse[]
  //   { cluster_id, n_clientes, pd_media, pi_media, cp_percentil5,
  //     score_credito_cross_medio, ck_medio, fator_alavancagem, limite_otimizado }
  getClusters: function (consultaId) {
    return Api.request(
      "/consultas/" + encodeURIComponent(consultaId) + "/clusters",
    );
  },

  // -------------------------------------------------------------------------
  // Clientes de uma consulta
  // -------------------------------------------------------------------------

  // GET /api/consultas/{id}/clientes?limit={limit}&offset={offset}
  // Retorna: ClienteResultadoResponse[]
  // limit: 1-1000, default 100 | offset: default 0
  getClientes: function (consultaId, limit, offset) {
    var q = new URLSearchParams();
    if (limit != null) q.append("limit", String(limit));
    if (offset != null) q.append("offset", String(offset));
    var qs = q.toString();
    return Api.request(
      "/consultas/" +
        encodeURIComponent(consultaId) +
        "/clientes" +
        (qs ? "?" + qs : ""),
    );
  },

  // GET /api/consultas/{id}/clientes/export
  // Retorna: Blob (text/csv) para download direto.
  exportClientes: function (consultaId) {
    return fetch(
      API_BASE_URL +
        "/consultas/" +
        encodeURIComponent(consultaId) +
        "/clientes/export",
    ).then(function (res) {
      if (!res.ok) throw new Error("Erro ao exportar clientes.");
      return res.blob();
    });
  },

  // -------------------------------------------------------------------------
  // Histórico de cliente individual
  // -------------------------------------------------------------------------

  // GET /api/clientes/{token}
  // Retorna: ClienteHistoricoResponse
  //   { token, historico: ClienteResultadoResponse[] }
  getHistoricoCliente: function (token) {
    return Api.request("/clientes/" + encodeURIComponent(token));
  },

  // -------------------------------------------------------------------------
  // Configuração (parâmetros do modelo)
  // -------------------------------------------------------------------------

  // GET /api/config
  // Retorna: ParametrosModelo
  //   { t, LGD, u_bar, L_max, T }
  getConfig: function () {
    return Api.request("/config");
  },

  // PUT /api/config
  // Body: ParametrosModelo { t, LGD, u_bar, L_max, T }
  // Retorna: ParametrosModelo atualizado
  updateConfig: function (params) {
    return Api.request("/config", {
      method: "PUT",
      body: params,
    });
  },
};
