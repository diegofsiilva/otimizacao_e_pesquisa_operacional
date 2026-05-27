// api.js -- cliente HTTP simples para integrar frontend e backend FastAPI.

var API_BASE_URL =
  window.API_BASE_URL ||
  localStorage.getItem("API_BASE_URL") ||
  "http://127.0.0.1:8000/api";

var Api = {
  baseUrl: API_BASE_URL,

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
          throw new Error(txt || "Erro na requisicao: " + res.status);
        });
      }
      if (res.status === 204) return null;
      return res.json();
    });
  },

  getDashboard: function () {
    return Api.request("/dashboard");
  },

  listCluster: function (params) {
    var query = new URLSearchParams(params || {}).toString();
    return Api.request("/cluster" + (query ? "?" + query : ""));
  },

  getConfig: function () {
    return Api.request("/config");
  },

  updateConfig: function (params) {
    return Api.request("/config", {
      method: "PUT",
      body: params,
    });
  },

  gerarLimites: function (file, nClusters) {
    var form = new FormData();
    form.append("file", file);
    var query = nClusters ? "?n_clusters=" + encodeURIComponent(nClusters) : "";
    return Api.request("/limites/gerar" + query, {
      method: "POST",
      body: form,
    });
  },

  getResultados: function () {
    return Api.request("/resultados");
  },

  exportResultados: function () {
    return fetch(API_BASE_URL + "/resultados/export").then(function (res) {
      if (!res.ok) throw new Error("Erro ao exportar resultados.");
      return res.blob();
    });
  },
};
