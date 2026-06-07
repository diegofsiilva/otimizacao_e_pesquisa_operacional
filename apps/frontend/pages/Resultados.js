// pages/Resultados.js
// Deps globais: Api (api.js), fmt, fmtZ (data.js)
//
// Este arquivo define os chart components compartilhados (usados também em
// GerarLimites.js, carregado antes) e o componente Resultados.
//
// Ao montar, carrega todas as consultas concluídas + safras e seleciona a
// mais recente. O seletor no topo permite alternar entre simulações passadas.
//
// Gráficos com dados reais:
//   BarChartSVG  → top 15 clusters por limite_otimizado
//   DonutChart   → distribuição de clientes (ofertado / elegível s/ limite / inelegível)
//   LineChartSVG → evolução do z_otimo entre safras (quando há 2+ consultas)
//   RiskHistSVG  → histograma de PD média por faixa de risco (clusters)

// ============================================================================
// BarChartSVG - barras verticais, label em cada barra
// ============================================================================
var BarChartSVG = function (props) {
  var data = props.data;
  if (!data || data.length === 0) return null;

  var w = 420;
  var h = 200;
  var pad = { top: 24, right: 10, bottom: 28, left: 52 };
  var cw = w - pad.left - pad.right;
  var ch = h - pad.top - pad.bottom;
  var max =
    Math.max.apply(
      null,
      data.map(function (d) {
        return d.value;
      }),
    ) || 1;
  var bw = Math.floor((cw / data.length) * 0.55);

  function fmtLabel(v) {
    if (v === 0) return null;
    if (v >= 1000000) return "R$" + (v / 1000000).toFixed(1) + "M";
    if (v >= 1000) return "R$" + (v / 1000).toFixed(1) + "k";
    return "R$" + v;
  }

  function fmtAxis(v) {
    if (v >= 1000000) return "R$" + (v / 1000000).toFixed(0) + "M";
    if (v >= 1000) return "R$" + (v / 1000).toFixed(0) + "k";
    return "R$" + Math.round(v);
  }

  return (
    <svg
      viewBox={"0 0 " + w + " " + h}
      width="100%"
      style={{ overflow: "visible" }}
    >
      {[0, 0.25, 0.5, 0.75, 1].map(function (f) {
        var y = pad.top + ch * (1 - f);
        return (
          <g key={f}>
            <line
              x1={pad.left}
              x2={pad.left + cw}
              y1={y}
              y2={y}
              stroke="#E8EFF7"
              strokeWidth="1"
            />
            {f > 0 && (
              <text
                x={pad.left - 6}
                y={y + 4}
                textAnchor="end"
                fontSize="9"
                fill="#9C9C9F"
              >
                {fmtAxis(max * f)}
              </text>
            )}
          </g>
        );
      })}
      {data.map(function (d, i) {
        var x = pad.left + (cw / data.length) * i + (cw / data.length - bw) / 2;
        var bh = d.value > 0 ? Math.max(ch * (d.value / max), 2) : 3;
        var y = pad.top + ch - bh;
        var lbl = fmtLabel(d.value);
        return (
          <g key={i}>
            <rect
              x={x}
              y={y}
              width={bw}
              height={bh}
              fill={d.value > 0 ? "#2E6DA4" : "#E8EFF7"}
            />
            {lbl && (
              <text
                x={x + bw / 2}
                y={y - 5}
                textAnchor="middle"
                fontSize="8"
                fontWeight="600"
                fill="#3B4049"
              >
                {lbl}
              </text>
            )}
            <text
              x={x + bw / 2}
              y={h - pad.bottom + 14}
              textAnchor="middle"
              fontSize="8"
              fill="#9C9C9F"
            >
              {d.label}
            </text>
          </g>
        );
      })}
    </svg>
  );
};

// ============================================================================
// LineChartSVG - linha temporal com pontos e rótulos alternados
// ============================================================================
var LineChartSVG = function (props) {
  var data = props.data;
  if (!data || data.length < 2)
    return (
      <div className="flex items-center justify-center h-32 text-xs text-[#9C9C9F]">
        Necessário pelo menos 2 simulações para exibir a evolução.
      </div>
    );

  var w = 420;
  var h = 175;
  var pad = { top: 24, right: 20, bottom: 24, left: 48 };
  var cw = w - pad.left - pad.right;
  var ch = h - pad.top - pad.bottom;
  var max =
    Math.max.apply(
      null,
      data.map(function (d) {
        return d.value;
      }),
    ) * 1.15 || 1;

  var pts = data.map(function (d, i) {
    return [
      pad.left + (cw / (data.length - 1)) * i,
      pad.top + ch - (ch * d.value) / max,
    ];
  });

  var polyline = pts
    .map(function (p) {
      return p[0] + "," + p[1];
    })
    .join(" ");

  var area =
    "M" +
    pts[0][0] +
    "," +
    pts[0][1] +
    pts
      .slice(1)
      .map(function (p) {
        return " L" + p[0] + "," + p[1];
      })
      .join("") +
    " L" +
    pts[pts.length - 1][0] +
    "," +
    (pad.top + ch) +
    " L" +
    pts[0][0] +
    "," +
    (pad.top + ch) +
    " Z";

  function fmtVal(v) {
    if (v >= 1000000) return "R$" + (v / 1000000).toFixed(1) + "M";
    if (v >= 1000) return "R$" + (v / 1000).toFixed(0) + "k";
    return "R$" + v.toFixed(0);
  }

  return (
    <svg
      viewBox={"0 0 " + w + " " + h}
      width="100%"
      style={{ overflow: "visible" }}
    >
      {[0, 0.5, 1].map(function (f) {
        var y = pad.top + ch * (1 - f);
        return (
          <g key={f}>
            <line
              x1={pad.left}
              x2={pad.left + cw}
              y1={y}
              y2={y}
              stroke="#E8EFF7"
              strokeWidth="1"
            />
            {f > 0 && (
              <text
                x={pad.left - 6}
                y={y + 4}
                textAnchor="end"
                fontSize="9"
                fill="#9C9C9F"
              >
                {fmtVal(max * f)}
              </text>
            )}
          </g>
        );
      })}
      <path d={area} fill="#2E6DA4" fillOpacity="0.08" />
      <polyline
        points={polyline}
        fill="none"
        stroke="#2E6DA4"
        strokeWidth="2.5"
        strokeLinejoin="round"
      />
      {pts.map(function (p, i) {
        var d = data[i];
        var labelY = i % 2 === 0 ? p[1] - 10 : p[1] + 18;
        return (
          <g key={i}>
            <circle
              cx={p[0]}
              cy={p[1]}
              r="4"
              fill="#2E6DA4"
              stroke="#fff"
              strokeWidth="2"
            />
            <text
              x={p[0]}
              y={labelY}
              textAnchor="middle"
              fontSize="9"
              fontWeight="600"
              fill="#3B4049"
            >
              {fmtVal(d.value)}
            </text>
            <text
              x={p[0]}
              y={h - pad.bottom + 14}
              textAnchor="middle"
              fontSize="9"
              fill="#9C9C9F"
            >
              {d.label}
            </text>
          </g>
        );
      })}
    </svg>
  );
};

// ============================================================================
// DonutChart - gráfico de rosca com legenda lateral
// ============================================================================
var DonutChart = function (props) {
  var data = props.data;
  var r = 60;
  var ri = 38;
  var cx = 80;
  var cy = 80;
  var total =
    data.reduce(function (s, d) {
      return s + d.value;
    }, 0) || 1;

  var slices = [];
  var angle = -90;
  data.forEach(function (d) {
    var sweep = (d.value / total) * 360;
    if (sweep === 0) return;
    var a1 = (angle * Math.PI) / 180;
    var a2 = ((angle + sweep) * Math.PI) / 180;
    var x1 = cx + r * Math.cos(a1);
    var y1 = cy + r * Math.sin(a1);
    var x2 = cx + r * Math.cos(a2);
    var y2 = cy + r * Math.sin(a2);
    var xi1 = cx + ri * Math.cos(a1);
    var yi1 = cy + ri * Math.sin(a1);
    var xi2 = cx + ri * Math.cos(a2);
    var yi2 = cy + ri * Math.sin(a2);
    var large = sweep > 180 ? 1 : 0;
    slices.push({
      path:
        "M" +
        x1 +
        "," +
        y1 +
        " A" +
        r +
        "," +
        r +
        " 0 " +
        large +
        ",1 " +
        x2 +
        "," +
        y2 +
        " L" +
        xi2 +
        "," +
        yi2 +
        " A" +
        ri +
        "," +
        ri +
        " 0 " +
        large +
        ",0 " +
        xi1 +
        "," +
        yi1 +
        " Z",
      color: d.color,
    });
    angle += sweep;
  });

  return (
    <svg
      viewBox="0 0 160 160"
      width="140"
      height="140"
      style={{ flexShrink: 0 }}
    >
      {slices.map(function (s, i) {
        return <path key={i} d={s.path} fill={s.color} />;
      })}
      <circle cx={cx} cy={cy} r={ri - 2} fill="white" />
    </svg>
  );
};

// ============================================================================
// RiskHistSVG - histograma de distribuição de PD média por faixa
// ============================================================================
var RiskHistSVG = function (props) {
  var clusters = props.clusters;
  if (!clusters || clusters.length === 0) return null;

  var bins = [
    { label: "0–5%", min: 0, max: 0.05, count: 0 },
    { label: "5–10%", min: 0.05, max: 0.1, count: 0 },
    { label: "10–15%", min: 0.1, max: 0.15, count: 0 },
    { label: "15–20%", min: 0.15, max: 0.2, count: 0 },
    { label: "20–25%", min: 0.2, max: 0.25, count: 0 },
    { label: "25%+", min: 0.25, max: Infinity, count: 0 },
  ];

  clusters.forEach(function (c) {
    for (var i = 0; i < bins.length; i++) {
      if (c.pd_media >= bins[i].min && c.pd_media < bins[i].max) {
        bins[i].count++;
        break;
      }
    }
  });

  var w = 420;
  var h = 175;
  var pad = { top: 24, right: 10, bottom: 28, left: 40 };
  var cw = w - pad.left - pad.right;
  var ch = h - pad.top - pad.bottom;
  var max =
    Math.max.apply(
      null,
      bins.map(function (b) {
        return b.count;
      }),
    ) || 1;
  var bw = Math.floor((cw / bins.length) * 0.65);

  return (
    <svg
      viewBox={"0 0 " + w + " " + h}
      width="100%"
      style={{ overflow: "visible" }}
    >
      {[0, 0.5, 1].map(function (f) {
        var y = pad.top + ch * (1 - f);
        return (
          <g key={f}>
            <line
              x1={pad.left}
              x2={pad.left + cw}
              y1={y}
              y2={y}
              stroke="#E8EFF7"
              strokeWidth="1"
            />
            {f > 0 && (
              <text
                x={pad.left - 6}
                y={y + 4}
                textAnchor="end"
                fontSize="9"
                fill="#9C9C9F"
              >
                {Math.round(max * f)}
              </text>
            )}
          </g>
        );
      })}
      {bins.map(function (b, i) {
        var x = pad.left + (cw / bins.length) * i + (cw / bins.length - bw) / 2;
        var bh = b.count > 0 ? Math.max(ch * (b.count / max), 2) : 0;
        var y = pad.top + ch - bh;
        // Color by risk: green → yellow → red
        var colors = [
          "#67DE98",
          "#A8E6B0",
          "#FAE95D",
          "#FFC87A",
          "#FF8C6B",
          "#FF5D5C",
        ];
        return (
          <g key={i}>
            {b.count > 0 && (
              <rect
                x={x}
                y={y}
                width={bw}
                height={bh}
                fill={colors[i]}
                fillOpacity="0.9"
              />
            )}
            {b.count > 0 && (
              <text
                x={x + bw / 2}
                y={y - 5}
                textAnchor="middle"
                fontSize="9"
                fontWeight="600"
                fill="#3B4049"
              >
                {b.count}
              </text>
            )}
            <text
              x={x + bw / 2}
              y={h - pad.bottom + 14}
              textAnchor="middle"
              fontSize="8"
              fill="#9C9C9F"
            >
              {b.label}
            </text>
          </g>
        );
      })}
    </svg>
  );
};

// ============================================================================
// PolicyFunnelSVG - funil de decisao de credito
// ============================================================================
var PolicyFunnelSVG = function (props) {
  var data = props.data || [];
  if (data.length === 0) return null;

  var w = 420;
  var h = 170;
  var pad = { top: 18, right: 18, bottom: 26, left: 130 };
  var cw = w - pad.left - pad.right;
  var rowH = 34;
  var max =
    Math.max.apply(
      null,
      data.map(function (d) {
        return d.value;
      }),
    ) || 1;

  return (
    <svg viewBox={"0 0 " + w + " " + h} width="100%">
      {data.map(function (d, i) {
        var y = pad.top + i * rowH;
        var bw = Math.max(4, cw * (d.value / max));
        var pct = data[0] && data[0].value ? (d.value / data[0].value) * 100 : 0;
        return (
          <g key={d.label}>
            <text
              x={pad.left - 10}
              y={y + 16}
              textAnchor="end"
              fontSize="11"
              fontWeight="600"
              fill="#3B4049"
            >
              {d.label}
            </text>
            <rect x={pad.left} y={y} width={cw} height="20" fill="#E8EFF7" />
            <rect x={pad.left} y={y} width={bw} height="20" fill={d.color} />
            <text
              x={pad.left + bw + 8 > w - 34 ? pad.left + bw - 8 : pad.left + bw + 8}
              y={y + 15}
              textAnchor={pad.left + bw + 8 > w - 34 ? "end" : "start"}
              fontSize="10"
              fontWeight="600"
              fill={pad.left + bw + 8 > w - 34 ? "#fff" : "#0D1B2A"}
            >
              {Number(d.value).toLocaleString("pt-BR")} ({pct.toFixed(1)}%)
            </text>
          </g>
        );
      })}
    </svg>
  );
};

// ============================================================================
// RiskReturnScatterSVG - retorno liquido esperado x risco medio do cluster
// ============================================================================
var RiskReturnScatterSVG = function (props) {
  var points = props.points || [];
  if (points.length === 0) return null;

  var w = 460;
  var h = 230;
  var pad = { top: 22, right: 20, bottom: 36, left: 58 };
  var cw = w - pad.left - pad.right;
  var ch = h - pad.top - pad.bottom;

  var maxPd =
    Math.max.apply(
      null,
      points.map(function (p) {
        return p.pd;
      }),
    ) || 0.01;
  var minReturn =
    Math.min.apply(
      null,
      points.map(function (p) {
        return p.netPerClient;
      }),
    );
  var maxReturn =
    Math.max.apply(
      null,
      points.map(function (p) {
        return p.netPerClient;
      }),
    );
  var maxClients =
    Math.max.apply(
      null,
      points.map(function (p) {
        return p.clients;
      }),
    ) || 1;

  var yMin = Math.min(0, minReturn);
  var yMax = Math.max(1, maxReturn);
  if (yMax === yMin) yMax = yMin + 1;
  var zeroY = pad.top + ch - ((0 - yMin) / (yMax - yMin)) * ch;

  function xScale(pd) {
    return pad.left + (pd / maxPd) * cw;
  }

  function yScale(v) {
    return pad.top + ch - ((v - yMin) / (yMax - yMin)) * ch;
  }

  function fmtMoney(v) {
    if (Math.abs(v) >= 1000) return "R$" + (v / 1000).toFixed(1) + "k";
    return "R$" + Math.round(v);
  }

  return (
    <svg viewBox={"0 0 " + w + " " + h} width="100%" style={{ overflow: "visible" }}>
      {[0, 0.5, 1].map(function (f) {
        var y = pad.top + ch * (1 - f);
        var val = yMin + (yMax - yMin) * f;
        return (
          <g key={f}>
            <line x1={pad.left} x2={pad.left + cw} y1={y} y2={y} stroke="#E8EFF7" />
            <text x={pad.left - 8} y={y + 4} textAnchor="end" fontSize="9" fill="#9C9C9F">
              {fmtMoney(val)}
            </text>
          </g>
        );
      })}
      <line x1={pad.left} x2={pad.left + cw} y1={zeroY} y2={zeroY} stroke="#DC2F37" strokeDasharray="4 4" />
      {[0, 0.5, 1].map(function (f) {
        var x = pad.left + cw * f;
        var pd = maxPd * f * 100;
        return (
          <g key={f}>
            <line x1={x} x2={x} y1={pad.top} y2={pad.top + ch} stroke="#F3F4F9" />
            <text x={x} y={h - 14} textAnchor="middle" fontSize="9" fill="#9C9C9F">
              {pd.toFixed(1)}%
            </text>
          </g>
        );
      })}
      {points.map(function (p) {
        var r = 4 + 10 * Math.sqrt(p.clients / maxClients);
        var color = p.limit > 0 && p.netPerClient >= 0 ? "#0B8AA5" : p.limit > 0 ? "#FAE95D" : "#FF5D5C";
        return (
          <g key={p.id}>
            <circle
              cx={xScale(p.pd)}
              cy={yScale(p.netPerClient)}
              r={r}
              fill={color}
              fillOpacity="0.75"
              stroke="#fff"
              strokeWidth="1.5"
            />
            {p.rank <= 5 && (
              <text x={xScale(p.pd)} y={yScale(p.netPerClient) - r - 4} textAnchor="middle" fontSize="8" fontWeight="600" fill="#3B4049">
                CLU-{p.id}
              </text>
            )}
          </g>
        );
      })}
      <text x={pad.left + cw / 2} y={h - 2} textAnchor="middle" fontSize="10" fill="#9C9C9F">
        PD media do cluster
      </text>
    </svg>
  );
};

// ============================================================================
// ExposureParetoSVG - concentracao acumulada da exposicao aprovada
// ============================================================================
var ExposureParetoSVG = function (props) {
  var data = props.data || [];
  if (data.length === 0) return null;

  var w = 460;
  var h = 220;
  var pad = { top: 22, right: 38, bottom: 34, left: 54 };
  var cw = w - pad.left - pad.right;
  var ch = h - pad.top - pad.bottom;
  var maxExposure =
    Math.max.apply(
      null,
      data.map(function (d) {
        return d.exposure;
      }),
    ) || 1;
  var bw = Math.floor((cw / data.length) * 0.52);

  var total = data.reduce(function (s, d) {
    return s + d.exposure;
  }, 0);
  var running = 0;
  var linePts = data.map(function (d, i) {
    running += d.exposure;
    return {
      x: pad.left + (cw / data.length) * i + cw / data.length / 2,
      y: pad.top + ch - (running / total) * ch,
      pct: running / total,
    };
  });
  var polyline = linePts
    .map(function (p) {
      return p.x + "," + p.y;
    })
    .join(" ");

  function fmtShort(v) {
    if (v >= 1000000000) return "R$" + (v / 1000000000).toFixed(1) + "B";
    if (v >= 1000000) return "R$" + (v / 1000000).toFixed(0) + "M";
    if (v >= 1000) return "R$" + (v / 1000).toFixed(0) + "k";
    return "R$" + Math.round(v);
  }

  return (
    <svg viewBox={"0 0 " + w + " " + h} width="100%" style={{ overflow: "visible" }}>
      {[0, 0.5, 1].map(function (f) {
        var y = pad.top + ch * (1 - f);
        return (
          <g key={f}>
            <line x1={pad.left} x2={pad.left + cw} y1={y} y2={y} stroke="#E8EFF7" />
            {f > 0 && (
              <text x={pad.left - 8} y={y + 4} textAnchor="end" fontSize="9" fill="#9C9C9F">
                {fmtShort(maxExposure * f)}
              </text>
            )}
            <text x={pad.left + cw + 8} y={y + 4} fontSize="9" fill="#9C9C9F">
              {(f * 100).toFixed(0)}%
            </text>
          </g>
        );
      })}
      {data.map(function (d, i) {
        var x = pad.left + (cw / data.length) * i + (cw / data.length - bw) / 2;
        var bh = Math.max(2, ch * (d.exposure / maxExposure));
        var y = pad.top + ch - bh;
        return (
          <g key={d.label}>
            <rect x={x} y={y} width={bw} height={bh} fill="#2E6DA4" />
            <text x={x + bw / 2} y={h - 16} textAnchor="middle" fontSize="8" fill="#9C9C9F">
              {d.label}
            </text>
          </g>
        );
      })}
      <polyline points={polyline} fill="none" stroke="#DC2F37" strokeWidth="2.5" />
      {linePts.map(function (p, i) {
        return <circle key={i} cx={p.x} cy={p.y} r="3" fill="#DC2F37" stroke="#fff" strokeWidth="1.5" />;
      })}
    </svg>
  );
};

// ============================================================================
// RiskBandAllocationSVG - exposicao por faixa de risco
// ============================================================================
var RiskBandAllocationSVG = function (props) {
  var bands = props.bands || [];
  if (bands.length === 0) return null;

  var w = 460;
  var h = 205;
  var pad = { top: 22, right: 16, bottom: 42, left: 54 };
  var cw = w - pad.left - pad.right;
  var ch = h - pad.top - pad.bottom;
  var maxExposure =
    Math.max.apply(
      null,
      bands.map(function (b) {
        return b.exposure;
      }),
    ) || 1;
  var bw = Math.floor((cw / bands.length) * 0.58);
  var colors = ["#0B8AA5", "#67DE98", "#FAE95D", "#FF8C6B", "#FF5D5C"];

  function fmtShort(v) {
    if (v >= 1000000000) return "R$" + (v / 1000000000).toFixed(1) + "B";
    if (v >= 1000000) return "R$" + (v / 1000000).toFixed(0) + "M";
    if (v >= 1000) return "R$" + (v / 1000).toFixed(0) + "k";
    return "R$" + Math.round(v);
  }

  return (
    <svg viewBox={"0 0 " + w + " " + h} width="100%" style={{ overflow: "visible" }}>
      {[0, 0.5, 1].map(function (f) {
        var y = pad.top + ch * (1 - f);
        return (
          <g key={f}>
            <line x1={pad.left} x2={pad.left + cw} y1={y} y2={y} stroke="#E8EFF7" />
            {f > 0 && (
              <text x={pad.left - 8} y={y + 4} textAnchor="end" fontSize="9" fill="#9C9C9F">
                {fmtShort(maxExposure * f)}
              </text>
            )}
          </g>
        );
      })}
      {bands.map(function (b, i) {
        var x = pad.left + (cw / bands.length) * i + (cw / bands.length - bw) / 2;
        var bh = b.exposure > 0 ? Math.max(2, ch * (b.exposure / maxExposure)) : 0;
        var y = pad.top + ch - bh;
        return (
          <g key={b.label}>
            {bh > 0 && <rect x={x} y={y} width={bw} height={bh} fill={colors[i]} />}
            <text x={x + bw / 2} y={y - 5} textAnchor="middle" fontSize="9" fontWeight="600" fill="#3B4049">
              {b.clusters}
            </text>
            <text x={x + bw / 2} y={h - 22} textAnchor="middle" fontSize="8" fill="#9C9C9F">
              {b.label}
            </text>
            <text x={x + bw / 2} y={h - 10} textAnchor="middle" fontSize="8" fill="#9C9C9F">
              {b.approval.toFixed(0)}% ofert.
            </text>
          </g>
        );
      })}
    </svg>
  );
};

// ============================================================================
// Resultados
// ============================================================================
var Resultados = function (props) {
  var setPage = props.setPage;
  // hasData mantido por compatibilidade com App, mas não é mais a fonte de verdade.

  // -------------------------------------------------------------------------
  // Estado
  // -------------------------------------------------------------------------

  var s1 = React.useState([]);
  var consultas = s1[0];
  var setConsultas = s1[1];

  var s2 = React.useState({});
  var safraMap = s2[0];
  var setSafraMap = s2[1];

  var s3 = React.useState(null);
  var selectedId = s3[0];
  var setSelectedId = s3[1];

  var s4 = React.useState([]);
  var clusters = s4[0];
  var setClusters = s4[1];

  var s5 = React.useState(true);
  var loadingPage = s5[0];
  var setLoadingPage = s5[1];

  var s6 = React.useState(false);
  var loadingClusters = s6[0];
  var setLoadingClusters = s6[1];

  var s7 = React.useState(null);
  var erroLoad = s7[0];
  var setErroLoad = s7[1];

  var s8 = React.useState(false);
  var showParams = s8[0];
  var setShowParams = s8[1];

  // -------------------------------------------------------------------------
  // Carrega consultas + safras ao montar
  // -------------------------------------------------------------------------

  React.useEffect(function () {
    Promise.all([Api.listConsultas(), Api.listSafras()])
      .then(function (results) {
        var todas = results[0];
        var safras = results[1];

        var mapa = {};
        safras.forEach(function (s) {
          mapa[s.id] = s;
        });
        setSafraMap(mapa);

        var concluidas = todas.filter(function (c) {
          return c.status_consulta === "concluido";
        });
        setConsultas(concluidas);

        if (concluidas.length > 0) {
          setSelectedId(concluidas[0].id);
          setLoadingClusters(true);
          return Api.getClusters(concluidas[0].id).then(function (cls) {
            setClusters(cls || []);
            setLoadingClusters(false);
            setLoadingPage(false);
          });
        } else {
          setLoadingPage(false);
        }
      })
      .catch(function (err) {
        setErroLoad(err.message || "Erro ao carregar dados.");
        setLoadingPage(false);
      });
  }, []);

  // -------------------------------------------------------------------------
  // Troca de consulta selecionada
  // -------------------------------------------------------------------------

  function handleSelectConsulta(id) {
    if (id === selectedId) return;
    setSelectedId(id);
    setClusters([]);
    setLoadingClusters(true);
    Api.getClusters(id)
      .then(function (cls) {
        setClusters(cls || []);
        setLoadingClusters(false);
      })
      .catch(function () {
        setLoadingClusters(false);
      });
  }

  // -------------------------------------------------------------------------
  // Export CSV de clientes
  // -------------------------------------------------------------------------

  function handleExportar() {
    if (!selectedId) return;
    Api.exportClientes(selectedId)
      .then(function (blob) {
        var c = selectedConsulta;
        var safra = c ? safraMap[c.safra_id] : null;
        var filename =
          "clientes_" + (safra ? safra.nome : selectedId.slice(0, 8)) + ".csv";
        var url = URL.createObjectURL(blob);
        var a = document.createElement("a");
        a.href = url;
        a.download = filename;
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
  // Helpers
  // -------------------------------------------------------------------------

  function formatDateTime(iso) {
    if (!iso) return "-";
    return new Date(iso).toLocaleString("pt-BR", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  function formatPct(v) {
    if (v == null) return "-";
    return (v * 100).toFixed(2) + "%";
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

  // Top 15 clusters por limite (bar chart)
  var barData = clusters
    .slice()
    .sort(function (a, b) {
      return b.limite_otimizado - a.limite_otimizado;
    })
    .slice(0, 15)
    .map(function (c) {
      return { label: "CLU-" + c.cluster_id, value: c.limite_otimizado };
    });

  // Donut: distribuição de clientes
  var donutData = [];
  if (selectedConsulta) {
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

  // Evolução do z entre consultas (linha temporal, ordenada da mais antiga)
  var evolucaoData = consultas
    .slice()
    .reverse()
    .map(function (c) {
      var safra = safraMap[c.safra_id];
      return {
        label: safra ? safra.nome : c.id.slice(0, 4),
        value: c.z_otimo || 0,
      };
    });

  // Parâmetros da consulta selecionada
  var params = selectedConsulta ? selectedConsulta.parametros : null;

  // -------------------------------------------------------------------------
  // Render - carregando
  // -------------------------------------------------------------------------

  if (loadingPage) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-xl font-bold text-[#0D1B2A]">Resultados</h1>
          <div className="mt-1 h-0.5 w-10 bg-[#2E6DA4]" />
        </div>
        <div className="flex items-center justify-center py-24 gap-2 text-sm text-[#9C9C9F]">
          <svg
            className="animate-spin"
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="#2E6DA4"
            strokeWidth="2"
          >
            <path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0" />
          </svg>
          Carregando simulações...
        </div>
      </div>
    );
  }

  // -------------------------------------------------------------------------
  // Render - sem dados
  // -------------------------------------------------------------------------

  if (consultas.length === 0) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-xl font-bold text-[#0D1B2A]">Resultados</h1>
          <p className="mt-1 text-xs text-[#9C9C9F]">
            Nenhuma simulação concluída
          </p>
          <div className="mt-1 h-0.5 w-10 bg-[#2E6DA4]" />
        </div>

        {erroLoad && (
          <div className="flex items-center gap-2 px-4 py-3 bg-[#FF5D5C]/10 border border-[#FF5D5C]/30 text-xs text-[#DC2F37]">
            <svg
              width="13"
              height="13"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth="2.5"
            >
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            {erroLoad}
          </div>
        )}

        <div className="bg-white border border-[#E8EFF7] shadow-sm flex flex-col items-center justify-center py-24 px-6 text-center gap-5">
          <div className="w-14 h-14 bg-[#D6E8F5] flex items-center justify-center">
            <svg
              width="24"
              height="24"
              fill="none"
              viewBox="0 0 24 24"
              stroke="#2E6DA4"
              strokeWidth="1.5"
            >
              <polyline points="22 7 13.5 15.5 8.5 10.5 2 17" />
              <polyline points="16 7 22 7 22 13" />
            </svg>
          </div>
          <div>
            <p className="text-sm font-semibold text-[#0D1B2A] mb-1">
              Nenhuma simulação concluída
            </p>
            <p className="text-xs text-[#9C9C9F] max-w-xs">
              Carregue uma base .parquet e execute o Simplex em{" "}
              <strong className="text-[#0D1B2A]">Gerar Limites</strong> para
              visualizar os resultados aqui.
            </p>
          </div>
          <button
            onClick={function () {
              if (setPage) setPage("gerar");
            }}
            className="flex items-center gap-2 px-5 py-2.5 text-sm font-semibold bg-[#2E6DA4] text-white hover:bg-[#1B3A5C] transition-colors shadow-sm"
          >
            <svg
              width="14"
              height="14"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth="2.5"
            >
              <polygon points="5 3 19 12 5 21 5 3" />
            </svg>
            Ir para Gerar Limites
          </button>
        </div>
      </div>
    );
  }

  // -------------------------------------------------------------------------
  // Render - resultados
  // -------------------------------------------------------------------------

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <h1 className="text-xl font-bold text-[#0D1B2A]">Resultados</h1>
          <p className="mt-1 text-xs text-[#9C9C9F]">
            {selectedConsulta
              ? selectedConsulta.nome_arquivo_parquet +
                (safraMap[selectedConsulta.safra_id]
                  ? " · Safra " + safraMap[selectedConsulta.safra_id].nome
                  : "") +
                " · " +
                formatDateTime(selectedConsulta.concluido_em)
              : ""}
          </p>
          <div className="mt-1 h-0.5 w-10 bg-[#2E6DA4]" />
        </div>

        <div className="flex items-center gap-2 flex-shrink-0">
          {/* Seletor de simulação */}
          <div className="relative">
            <select
              value={selectedId || ""}
              onChange={function (e) {
                handleSelectConsulta(e.target.value);
              }}
              className="appearance-none pl-3 pr-8 py-2 text-xs font-medium border border-[#E8EFF7] bg-white text-[#3B4049] focus:outline-none focus:border-[#2E6DA4] cursor-pointer"
            >
              {consultas.map(function (c) {
                var safra = safraMap[c.safra_id];
                var label =
                  (safra ? safra.nome + " · " : "") + c.nome_arquivo_parquet;
                if (label.length > 40) label = label.slice(0, 38) + "…";
                return (
                  <option key={c.id} value={c.id}>
                    {label}
                  </option>
                );
              })}
            </select>
            <svg
              className="absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none"
              width="11"
              height="11"
              fill="none"
              viewBox="0 0 24 24"
              stroke="#9C9C9F"
              strokeWidth="2.5"
            >
              <polyline points="6 9 12 15 18 9" />
            </svg>
          </div>

          {/* Exportar clientes */}
          <button
            onClick={handleExportar}
            className="flex items-center gap-1.5 px-3 py-2 text-xs font-semibold border border-[#E8EFF7] bg-white text-[#3B4049] hover:bg-[#E2EAF4] transition-colors shadow-sm"
          >
            <svg
              width="12"
              height="12"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
              <polyline points="7 10 12 15 17 10" />
              <line x1="12" y1="15" x2="12" y2="3" />
            </svg>
            Exportar clientes CSV
          </button>
        </div>
      </div>

      {/* KPI cards */}
      {selectedConsulta && (
        <div className="grid grid-cols-4 gap-4">
          {[
            {
              label: "Total de Clusters",
              value:
                selectedConsulta.n_clusters != null
                  ? String(selectedConsulta.n_clusters)
                  : "-",
              sub: "segmentação CART",
              highlight: false,
            },
            {
              label: "Valor Objetivo (z)",
              value:
                selectedConsulta.z_otimo != null
                  ? fmtZ(selectedConsulta.z_otimo)
                  : "-",
              sub:
                selectedConsulta.status_lp === "multiplas_solucoes"
                  ? "Múltiplas soluções"
                  : "Solução ótima · Simplex",
              highlight: true,
            },
            {
              label: "Clientes Elegíveis",
              value:
                selectedConsulta.n_clientes_elegiveis != null
                  ? Number(
                      selectedConsulta.n_clientes_elegiveis,
                    ).toLocaleString("pt-BR")
                  : "-",
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
                  : "-",
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
      )}

      {/* Gráficos - linha 1 */}
      {loadingClusters ? (
        <div className="flex items-center justify-center py-16 gap-2 text-sm text-[#9C9C9F] bg-white border border-[#E8EFF7]">
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
          Carregando clusters...
        </div>
      ) : (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            {/* Limites por cluster */}
            <div className="bg-white border border-[#E8EFF7] shadow-sm p-5">
              <div className="text-sm font-semibold text-[#0D1B2A] mb-1">
                Top 15 Clusters por Limite
              </div>
              <div className="text-xs text-[#9C9C9F] mb-4">
                Limite ótimo atribuído a cada cluster pelo Simplex (R$)
              </div>
              {barData.length > 0 ? (
                <BarChartSVG data={barData} />
              ) : (
                <p className="text-xs text-[#9C9C9F]">Sem dados de clusters.</p>
              )}
            </div>

            {/* Distribuição de clientes */}
            <div className="bg-white border border-[#E8EFF7] shadow-sm p-5">
              <div className="text-sm font-semibold text-[#0D1B2A] mb-1">
                Distribuição de Clientes
              </div>
              <div className="text-xs text-[#9C9C9F] mb-4">
                Proporção por elegibilidade e oferta de limite
              </div>
              {donutData.length > 0 ? (
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
              ) : (
                <p className="text-xs text-[#9C9C9F]">
                  Sem dados de distribuição.
                </p>
              )}
            </div>
          </div>

          {/* Gráficos - linha 2 */}
          <div className="grid grid-cols-2 gap-4">
            {/* Evolução do z entre safras */}
            <div className="bg-white border border-[#E8EFF7] shadow-sm p-5">
              <div className="text-sm font-semibold text-[#0D1B2A] mb-1">
                Evolução do Valor Objetivo
              </div>
              <div className="text-xs text-[#9C9C9F] mb-4">
                z ótimo (R$) ao longo das simulações concluídas
              </div>
              <LineChartSVG data={evolucaoData} />
            </div>

            {/* Histograma de risco */}
            <div className="bg-white border border-[#E8EFF7] shadow-sm p-5">
              <div className="text-sm font-semibold text-[#0D1B2A] mb-1">
                Distribuição de Risco
              </div>
              <div className="text-xs text-[#9C9C9F] mb-4">
                Número de clusters por faixa de PD média
              </div>
              {clusters.length > 0 ? (
                <RiskHistSVG clusters={clusters} />
              ) : (
                <p className="text-xs text-[#9C9C9F]">Sem dados de clusters.</p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Parâmetros utilizados */}
      {params && (
        <div className="bg-white border border-[#E8EFF7] shadow-sm overflow-hidden">
          <button
            onClick={function () {
              setShowParams(function (v) {
                return !v;
              });
            }}
            className="w-full flex items-center justify-between px-5 py-4 text-sm font-semibold text-[#0D1B2A] hover:bg-[#E2EAF4] transition-colors"
          >
            <div className="flex items-center gap-2">
              <svg
                width="14"
                height="14"
                fill="none"
                viewBox="0 0 24 24"
                stroke="#9C9C9F"
                strokeWidth="2"
              >
                <path d="M12 15a3 3 0 100-6 3 3 0 000 6z" />
                <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z" />
              </svg>
              Parâmetros utilizados nesta simulação
            </div>
            <svg
              width="13"
              height="13"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth="2.5"
              style={{
                transform: showParams ? "rotate(180deg)" : "rotate(0deg)",
                transition: "transform 0.15s",
              }}
            >
              <polyline points="6 9 12 15 18 9" />
            </svg>
          </button>

          {showParams && (
            <div className="grid grid-cols-3 gap-px bg-[#E8EFF7] border-t border-[#E8EFF7]">
              {[
                {
                  label: "Taxa de interchange (t)",
                  value: formatPct(params.t),
                },
                {
                  label: "Loss Given Default (LGD)",
                  value: formatPct(params.LGD),
                },
                {
                  label: "Utilização esperada (u_bar)",
                  value: formatPct(params.u_bar),
                },
                { label: "Limite máximo (L_max)", value: fmt(params.L_max) },
                { label: "Horizonte de uso (T)", value: params.T + " meses" },
              ].map(function (p) {
                return (
                  <div key={p.label} className="bg-white px-5 py-4">
                    <div className="text-[10px] font-medium text-[#9C9C9F] uppercase tracking-wide">
                      {p.label}
                    </div>
                    <div className="text-sm font-semibold text-[#0D1B2A] mt-1">
                      {p.value}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
