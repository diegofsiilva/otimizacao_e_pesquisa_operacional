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
//   BarChartP5  → top 15 clusters por limite_otimizado
//   DonutChartP5   → distribuição de clientes (ofertado / elegível s/ limite / inelegível)
//   LineChartP5 → evolução do z_otimo entre safras (quando há 2+ consultas)
//   RiskHistP5  → histograma de PD média por faixa de risco (clusters)

// ============================================================================
// Componentes de gráfico em p5.js (instance mode)
// ----------------------------------------------------------------------------
// Os quatro gráficos abaixo foram reescritos de SVG estático para p5.js,
// atendendo ao requisito da disciplina de "canvas com animações e interações
// programadas em p5.js". Cada componente:
//   - desenha em um <canvas> próprio via `new p5(sketch, node)` (instance mode,
//     sem poluir o escopo global);
//   - executa uma animação de entrada (barras/linha/rosca crescem com easing);
//   - reage ao mouse com DESTAQUE do elemento sob o cursor + TOOLTIP desenhado
//     no próprio canvas.
//
// As props de cada componente são idênticas às versões SVG anteriores, então
// os call sites (Resultados.js, GerarLimites.js, Clientes.js) não mudam de
// contrato — apenas o nome passou de *SVG para *P5.
//
//   BarChartP5  → top 15 clusters por limite_otimizado          props: { data:[{label,value}] }
//   LineChartP5 → evolução do z_otimo / séries temporais         props: { data:[{label,value}] }
//   DonutChartP5→ distribuição de clientes                       props: { data:[{name,value,color}] }
//   RiskHistP5  → histograma de PD média por faixa de risco      props: { clusters:[{pd_media}] }
// ============================================================================

// ---- helpers compartilhados ------------------------------------------------

// Easing suave para as animações de entrada (desacelera no fim).
function _easeOutCubic(t) {
  return 1 - Math.pow(1 - t, 3);
}

// Formata valores em R$ de forma compacta (para rótulos curtos nos eixos/barras).
function _fmtCompact(v) {
  if (v >= 1000000) return "R$" + (v / 1000000).toFixed(1) + "M";
  if (v >= 1000) return "R$" + (v / 1000).toFixed(1) + "k";
  return "R$" + Math.round(v);
}
function _fmtAxis(v) {
  if (v >= 1000000) return "R$" + (v / 1000000).toFixed(0) + "M";
  if (v >= 1000) return "R$" + (v / 1000).toFixed(0) + "k";
  return "R$" + Math.round(v);
}
// Valor monetário completo (usado nos tooltips).
function _fmtFull(v) {
  return "R$ " + Number(Math.round(v)).toLocaleString("pt-BR");
}

// Desenha um tooltip seguindo o mouse, com as linhas de texto recebidas.
// A primeira linha é exibida em negrito. O balão se reposiciona para não
// vazar das bordas do canvas.
function _drawTooltip(p, lines) {
  p.push();
  p.textSize(11);
  var padIn = 8;
  var lh = 15;
  var boxW = 0;
  lines.forEach(function (ln, idx) {
    p.textStyle(idx === 0 ? p.BOLD : p.NORMAL);
    boxW = Math.max(boxW, p.textWidth(ln));
  });
  boxW += padIn * 2;
  var boxH = lines.length * lh + padIn * 2 - 3;
  var x = p.mouseX + 14;
  var y = p.mouseY + 14;
  if (x + boxW > p.width) x = p.mouseX - boxW - 14;
  if (y + boxH > p.height) y = p.mouseY - boxH - 14;
  if (x < 2) x = 2;
  if (y < 2) y = 2;
  p.noStroke();
  p.fill(13, 27, 42, 240); // #0D1B2A
  p.rect(x, y, boxW, boxH, 6);
  p.textAlign(p.LEFT, p.TOP);
  lines.forEach(function (ln, idx) {
    p.textStyle(idx === 0 ? p.BOLD : p.NORMAL);
    if (idx === 0) p.fill(255);
    else p.fill(205, 215, 228);
    p.text(ln, x + padIn, y + padIn + idx * lh);
  });
  p.pop();
}

// ============================================================================
// BarChartP5 - barras verticais animadas, com destaque + tooltip no hover
// ============================================================================
var BarChartP5 = function (props) {
  var ref = React.useRef(null);
  var dataKey = JSON.stringify(props.data || []);

  React.useEffect(
    function () {
      var node = ref.current;
      if (!node) return;
      var data = (props.data || []).filter(function (d) {
        return d != null;
      });
      if (data.length === 0) return;

      var sketch = function (p) {
        var W = 420;
        var H = 220;
        var padB = { top: 28, right: 12, bottom: 34, left: 56 };
        var start = 0;
        var DUR = 750;
        var max =
          Math.max.apply(
            null,
            data.map(function (d) {
              return d.value;
            }),
          ) || 1;

        p.setup = function () {
          W = node.offsetWidth || 420;
          p.createCanvas(W, H);
          start = p.millis();
          p.textFont("Circular, Arial, sans-serif");
        };
        p.windowResized = function () {
          W = node.offsetWidth || 420;
          p.resizeCanvas(W, H);
        };
        p.draw = function () {
          p.clear();
          var cw = W - padB.left - padB.right;
          var ch = H - padB.top - padB.bottom;
          var t = _easeOutCubic(p.constrain((p.millis() - start) / DUR, 0, 1));

          // gridlines + rótulos do eixo Y
          [0, 0.25, 0.5, 0.75, 1].forEach(function (f) {
            var y = padB.top + ch * (1 - f);
            p.stroke("#E8EFF7");
            p.strokeWeight(1);
            p.line(padB.left, y, padB.left + cw, y);
            if (f > 0) {
              p.noStroke();
              p.fill("#9C9C9F");
              p.textSize(9);
              p.textAlign(p.RIGHT, p.CENTER);
              p.text(_fmtAxis(max * f), padB.left - 8, y);
            }
          });

          var slot = cw / data.length;
          var bw = Math.min(30, slot * 0.6);
          var hover = -1;

          for (var i = 0; i < data.length; i++) {
            var x = padB.left + slot * i + (slot - bw) / 2;
            var full =
              data[i].value > 0 ? Math.max(ch * (data[i].value / max), 2) : 3;
            var bh = full * t;
            var y = padB.top + ch - bh;
            var over =
              p.mouseX >= x - 2 &&
              p.mouseX <= x + bw + 2 &&
              p.mouseY >= padB.top &&
              p.mouseY <= padB.top + ch;
            if (over) hover = i;

            p.noStroke();
            if (data[i].value > 0) p.fill(over ? "#1B4F82" : "#2E6DA4");
            else p.fill("#E8EFF7");
            p.rect(x, y, bw, bh, 2, 2, 0, 0);

            // rótulo do valor no topo (aparece ao final da animação)
            if (t > 0.85 && data[i].value > 0) {
              p.fill("#3B4049");
              p.textAlign(p.CENTER, p.BOTTOM);
              p.textSize(8);
              p.textStyle(p.BOLD);
              p.text(_fmtCompact(data[i].value), x + bw / 2, y - 3);
              p.textStyle(p.NORMAL);
            }
            // rótulo do eixo X
            p.fill("#9C9C9F");
            p.textAlign(p.CENTER, p.TOP);
            p.textSize(8);
            p.text(data[i].label, x + bw / 2, padB.top + ch + 6);
          }

          if (hover >= 0) {
            _drawTooltip(p, [data[hover].label, _fmtFull(data[hover].value)]);
            p.cursor(p.HAND);
          } else {
            p.cursor(p.ARROW);
          }
        };
      };

      var instance = new p5(sketch, node);
      return function () {
        instance.remove();
      };
    },
    [dataKey],
  );

  if (!props.data || props.data.length === 0) return null;
  return <div ref={ref} style={{ width: "100%" }} />;
};

// ============================================================================
// LineChartP5 - linha temporal com traçado animado, pontos e tooltip no hover
// ============================================================================
var LineChartP5 = function (props) {
  var ref = React.useRef(null);
  var data = props.data || [];
  var dataKey = JSON.stringify(data);

  React.useEffect(
    function () {
      var node = ref.current;
      if (!node) return;
      if (!data || data.length < 2) return;

      var sketch = function (p) {
        var W = 420;
        var H = 200;
        var padL = { top: 26, right: 22, bottom: 28, left: 52 };
        var start = 0;
        var DUR = 900;
        var max =
          (Math.max.apply(
            null,
            data.map(function (d) {
              return d.value;
            }),
          ) || 1) * 1.15;

        function fmtVal(v) {
          if (v >= 1000000) return "R$" + (v / 1000000).toFixed(1) + "M";
          if (v >= 1000) return "R$" + (v / 1000).toFixed(0) + "k";
          return v % 1 === 0 ? "R$" + v : "R$" + v.toFixed(2);
        }

        p.setup = function () {
          W = node.offsetWidth || 420;
          p.createCanvas(W, H);
          start = p.millis();
          p.textFont("Circular, Arial, sans-serif");
        };
        p.windowResized = function () {
          W = node.offsetWidth || 420;
          p.resizeCanvas(W, H);
        };
        p.draw = function () {
          p.clear();
          var cw = W - padL.left - padL.right;
          var ch = H - padL.top - padL.bottom;
          var t = _easeOutCubic(p.constrain((p.millis() - start) / DUR, 0, 1));

          var pts = data.map(function (d, i) {
            return {
              x: padL.left + (cw / (data.length - 1)) * i,
              y: padL.top + ch - (ch * d.value) / max,
              d: d,
            };
          });

          // gridlines + eixo Y
          [0, 0.5, 1].forEach(function (f) {
            var y = padL.top + ch * (1 - f);
            p.stroke("#E8EFF7");
            p.strokeWeight(1);
            p.line(padL.left, y, padL.left + cw, y);
            if (f > 0) {
              p.noStroke();
              p.fill("#9C9C9F");
              p.textSize(9);
              p.textAlign(p.RIGHT, p.CENTER);
              p.text(fmtVal(max * f), padL.left - 8, y);
            }
          });

          // área sob a curva (cresce com a animação)
          var nVis = t * (pts.length - 1);
          p.noStroke();
          p.fill(46, 109, 164, 22);
          p.beginShape();
          p.vertex(pts[0].x, padL.top + ch);
          for (var i = 0; i < pts.length; i++) {
            if (i <= nVis) {
              p.vertex(pts[i].x, pts[i].y);
            } else {
              // ponto interpolado na fronteira da animação
              var prev = pts[i - 1];
              var frac = nVis - (i - 1);
              p.vertex(
                prev.x + (pts[i].x - prev.x) * frac,
                prev.y + (pts[i].y - prev.y) * frac,
              );
              break;
            }
          }
          var lastVisX =
            nVis >= pts.length - 1
              ? pts[pts.length - 1].x
              : pts[Math.floor(nVis)].x +
                (pts[Math.ceil(nVis)].x - pts[Math.floor(nVis)].x) *
                  (nVis - Math.floor(nVis));
          p.vertex(lastVisX, padL.top + ch);
          p.endShape(p.CLOSE);

          // linha (traçado progressivo)
          p.noFill();
          p.stroke("#2E6DA4");
          p.strokeWeight(2.5);
          p.strokeJoin(p.ROUND);
          p.beginShape();
          for (var j = 0; j < pts.length; j++) {
            if (j <= nVis) {
              p.vertex(pts[j].x, pts[j].y);
            } else {
              var pv = pts[j - 1];
              var fr = nVis - (j - 1);
              p.vertex(pv.x + (pts[j].x - pv.x) * fr, pv.y + (pts[j].y - pv.y) * fr);
              break;
            }
          }
          p.endShape();

          // hover: ponto mais próximo no eixo X
          var hover = -1;
          var bestDx = 24;
          for (var k = 0; k < pts.length; k++) {
            var dx = Math.abs(p.mouseX - pts[k].x);
            if (dx < bestDx && p.mouseY > padL.top - 10 && p.mouseY < padL.top + ch + 10) {
              bestDx = dx;
              hover = k;
            }
          }

          // pontos + rótulos (aparecem conforme a linha avança)
          for (var m = 0; m < pts.length; m++) {
            if (m > nVis + 0.001) continue;
            var isH = m === hover;
            p.stroke("#fff");
            p.strokeWeight(2);
            p.fill(isH ? "#1B4F82" : "#2E6DA4");
            p.circle(pts[m].x, pts[m].y, isH ? 11 : 8);
            if (!isH) {
              p.noStroke();
              p.fill("#3B4049");
              p.textSize(9);
              p.textStyle(p.BOLD);
              p.textAlign(p.CENTER, p.BOTTOM);
              var ly = m % 2 === 0 ? pts[m].y - 9 : pts[m].y + 19;
              p.text(fmtVal(pts[m].d.value), pts[m].x, ly);
              p.textStyle(p.NORMAL);
            }
            // rótulo do eixo X
            p.noStroke();
            p.fill("#9C9C9F");
            p.textSize(9);
            p.textStyle(p.NORMAL);
            p.textAlign(p.CENTER, p.TOP);
            p.text(pts[m].d.label, pts[m].x, padL.top + ch + 8);
          }

          if (hover >= 0 && hover <= nVis + 0.001) {
            // linha guia vertical
            p.stroke(46, 109, 164, 90);
            p.strokeWeight(1);
            p.line(pts[hover].x, padL.top, pts[hover].x, padL.top + ch);
            _drawTooltip(p, [
              String(pts[hover].d.label),
              _fmtFull(pts[hover].d.value),
            ]);
            p.cursor(p.HAND);
          } else {
            p.cursor(p.ARROW);
          }
        };
      };

      var instance = new p5(sketch, node);
      return function () {
        instance.remove();
      };
    },
    [dataKey],
  );

  if (!data || data.length < 2) {
    return (
      <div className="flex items-center justify-center h-32 text-xs text-[#9C9C9F]">
        Necessário pelo menos 2 simulações para exibir a evolução.
      </div>
    );
  }
  return <div ref={ref} style={{ width: "100%" }} />;
};

// ============================================================================
// DonutChartP5 - rosca com varredura animada, fatia destacada + tooltip
// ============================================================================
var DonutChartP5 = function (props) {
  var ref = React.useRef(null);
  var data = (props.data || []).filter(function (d) {
    return d && d.value > 0;
  });
  var dataKey = JSON.stringify(props.data || []);

  React.useEffect(
    function () {
      var node = ref.current;
      if (!node || data.length === 0) return;

      var sketch = function (p) {
        var SIZE = 150;
        var cx = SIZE / 2;
        var cy = SIZE / 2;
        var rOut = 60;
        var rIn = 38;
        var start = 0;
        var DUR = 800;
        var total =
          data.reduce(function (s, d) {
            return s + d.value;
          }, 0) || 1;

        p.setup = function () {
          p.createCanvas(SIZE, SIZE);
          start = p.millis();
          p.textFont("Circular, Arial, sans-serif");
          p.angleMode(p.RADIANS);
        };
        p.draw = function () {
          p.clear();
          var t = _easeOutCubic(p.constrain((p.millis() - start) / DUR, 0, 1));

          // ângulo do mouse relativo ao centro (para hover)
          var mdx = p.mouseX - cx;
          var mdy = p.mouseY - cy;
          var mdist = Math.sqrt(mdx * mdx + mdy * mdy);
          var mang = Math.atan2(mdy, mdx); // -PI..PI, 0 = direita
          // normaliza para começar em -90° (topo), sentido horário, 0..2PI
          var mNorm = mang + Math.PI / 2;
          if (mNorm < 0) mNorm += Math.PI * 2;
          var overRing = mdist >= rIn - 2 && mdist <= rOut + 8;

          var ang = -Math.PI / 2;
          var hover = -1;
          var acc = 0;
          // primeiro: descobrir fatia sob o mouse (na geometria completa)
          for (var i = 0; i < data.length; i++) {
            var sweepFull = (data[i].value / total) * Math.PI * 2;
            if (overRing && mNorm >= acc && mNorm < acc + sweepFull) hover = i;
            acc += sweepFull;
          }

          for (var j = 0; j < data.length; j++) {
            var sweep = (data[j].value / total) * Math.PI * 2 * t;
            if (sweep <= 0.0001) {
              ang += (data[j].value / total) * Math.PI * 2 * t;
              continue;
            }
            var isH = j === hover;
            var ro = isH ? rOut + 6 : rOut;
            // deslocamento da fatia destacada para fora
            var mid = ang + sweep / 2;
            var ox = isH ? Math.cos(mid) * 4 : 0;
            var oy = isH ? Math.sin(mid) * 4 : 0;

            p.push();
            p.translate(ox, oy);
            p.noStroke();
            p.fill(data[j].color);
            // setor em anel como um único polígono fechado (arco externo de ida
            // + arco interno de volta) — evita costuras internas entre triângulos.
            var steps = Math.max(2, Math.ceil((sweep / (Math.PI * 2)) * 96));
            p.beginShape();
            for (var s = 0; s <= steps; s++) {
              var ao = ang + (sweep * s) / steps;
              p.vertex(cx + Math.cos(ao) * ro, cy + Math.sin(ao) * ro);
            }
            for (var s2 = steps; s2 >= 0; s2--) {
              var ai = ang + (sweep * s2) / steps;
              p.vertex(cx + Math.cos(ai) * rIn, cy + Math.sin(ai) * rIn);
            }
            p.endShape(p.CLOSE);
            p.pop();

            ang += sweep;
          }

          // texto central: total ou valor da fatia em hover
          p.noStroke();
          p.textAlign(p.CENTER, p.CENTER);
          if (hover >= 0) {
            var pct = ((data[hover].value / total) * 100).toFixed(1);
            p.fill("#0D1B2A");
            p.textSize(17);
            p.textStyle(p.BOLD);
            p.text(pct + "%", cx, cy - 4);
            p.textStyle(p.NORMAL);
            p.fill("#9C9C9F");
            p.textSize(8);
            p.text(
              Number(data[hover].value).toLocaleString("pt-BR"),
              cx,
              cy + 12,
            );
          } else {
            p.fill("#0D1B2A");
            p.textSize(16);
            p.textStyle(p.BOLD);
            p.text(Number(total).toLocaleString("pt-BR"), cx, cy - 3);
            p.textStyle(p.NORMAL);
            p.fill("#9C9C9F");
            p.textSize(8);
            p.text("total", cx, cy + 12);
          }

          if (hover >= 0) {
            _drawTooltip(p, [
              String(data[hover].name),
              Number(data[hover].value).toLocaleString("pt-BR") +
                " (" +
                ((data[hover].value / total) * 100).toFixed(1) +
                "%)",
            ]);
            p.cursor(p.HAND);
          } else {
            p.cursor(p.ARROW);
          }
        };
      };

      var instance = new p5(sketch, node);
      return function () {
        instance.remove();
      };
    },
    [dataKey],
  );

  return (
    <div
      ref={ref}
      style={{ width: 150, height: 150, flexShrink: 0 }}
    />
  );
};

// ============================================================================
// RiskHistP5 - histograma de PD média por faixa, com destaque + tooltip
// ============================================================================
var RiskHistP5 = function (props) {
  var ref = React.useRef(null);
  var clusters = props.clusters || [];
  var dataKey = JSON.stringify(
    clusters.map(function (c) {
      return c.pd_media;
    }),
  );

  React.useEffect(
    function () {
      var node = ref.current;
      if (!node || clusters.length === 0) return;

      var sketch = function (p) {
        var W = 420;
        var H = 200;
        var padH = { top: 26, right: 12, bottom: 34, left: 44 };
        var start = 0;
        var DUR = 750;
        var colors = [
          "#67DE98",
          "#A8E6B0",
          "#FAE95D",
          "#FFC87A",
          "#FF8C6B",
          "#FF5D5C",
        ];
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
        var max =
          Math.max.apply(
            null,
            bins.map(function (b) {
              return b.count;
            }),
          ) || 1;

        p.setup = function () {
          W = node.offsetWidth || 420;
          p.createCanvas(W, H);
          start = p.millis();
          p.textFont("Circular, Arial, sans-serif");
        };
        p.windowResized = function () {
          W = node.offsetWidth || 420;
          p.resizeCanvas(W, H);
        };
        p.draw = function () {
          p.clear();
          var cw = W - padH.left - padH.right;
          var ch = H - padH.top - padH.bottom;
          var t = _easeOutCubic(p.constrain((p.millis() - start) / DUR, 0, 1));

          [0, 0.5, 1].forEach(function (f) {
            var y = padH.top + ch * (1 - f);
            p.stroke("#E8EFF7");
            p.strokeWeight(1);
            p.line(padH.left, y, padH.left + cw, y);
            if (f > 0) {
              p.noStroke();
              p.fill("#9C9C9F");
              p.textSize(9);
              p.textAlign(p.RIGHT, p.CENTER);
              p.text(Math.round(max * f), padH.left - 8, y);
            }
          });

          var slot = cw / bins.length;
          var bw = Math.min(46, slot * 0.66);
          var hover = -1;

          for (var i = 0; i < bins.length; i++) {
            var x = padH.left + slot * i + (slot - bw) / 2;
            var full = bins[i].count > 0 ? Math.max(ch * (bins[i].count / max), 2) : 0;
            var bh = full * t;
            var y = padH.top + ch - bh;
            var over =
              p.mouseX >= x - 2 &&
              p.mouseX <= x + bw + 2 &&
              p.mouseY >= padH.top &&
              p.mouseY <= padH.top + ch;
            if (over) hover = i;

            if (bins[i].count > 0) {
              p.noStroke();
              var col = p.color(colors[i]);
              col.setAlpha(over ? 255 : 230);
              p.fill(col);
              p.rect(x, y, bw, bh, 2, 2, 0, 0);
              if (t > 0.85) {
                p.fill("#3B4049");
                p.textAlign(p.CENTER, p.BOTTOM);
                p.textSize(9);
                p.textStyle(p.BOLD);
                p.text(bins[i].count, x + bw / 2, y - 3);
                p.textStyle(p.NORMAL);
              }
            }
            p.noStroke();
            p.fill("#9C9C9F");
            p.textAlign(p.CENTER, p.TOP);
            p.textSize(8);
            p.text(bins[i].label, x + bw / 2, padH.top + ch + 6);
          }

          if (hover >= 0) {
            _drawTooltip(p, [
              "PD " + bins[hover].label,
              bins[hover].count + (bins[hover].count === 1 ? " cluster" : " clusters"),
            ]);
            p.cursor(p.HAND);
          } else {
            p.cursor(p.ARROW);
          }
        };
      };

      var instance = new p5(sketch, node);
      return function () {
        instance.remove();
      };
    },
    [dataKey],
  );

  if (!clusters || clusters.length === 0) return null;
  return <div ref={ref} style={{ width: "100%" }} />;
};

// ============================================================================
// PulpSimplexCompareP5 - compara limite Simplex x PuLP por cluster
// ============================================================================
var PulpSimplexCompareP5 = function (props) {
  var ref = React.useRef(null);
  var data = props.data || [];
  var dataKey = JSON.stringify(data);

  React.useEffect(
    function () {
      var node = ref.current;
      if (!node || !data.length) return;

      var sketch = function (p) {
        var W = 520;
        var H = 260;
        var start = 0;
        var DUR = 800;
        var pad = { top: 28, right: 22, bottom: 38, left: 58 };
        var max =
          Math.max.apply(
            null,
            data.map(function (d) {
              return Math.max(d.simplex, d.pulp);
            }),
          ) || 1;

        p.setup = function () {
          W = node.offsetWidth || 520;
          p.createCanvas(W, H);
          start = p.millis();
          p.textFont("Circular, Arial, sans-serif");
        };

        p.windowResized = function () {
          W = node.offsetWidth || 520;
          p.resizeCanvas(W, H);
        };

        p.draw = function () {
          p.clear();
          var cw = W - pad.left - pad.right;
          var ch = H - pad.top - pad.bottom;
          var t = _easeOutCubic(p.constrain((p.millis() - start) / DUR, 0, 1));

          [0, 0.25, 0.5, 0.75, 1].forEach(function (f) {
            var y = pad.top + ch * (1 - f);
            p.stroke("#E8EFF7");
            p.strokeWeight(1);
            p.line(pad.left, y, pad.left + cw, y);
            if (f > 0) {
              p.noStroke();
              p.fill("#9C9C9F");
              p.textSize(9);
              p.textAlign(p.RIGHT, p.CENTER);
              p.text(_fmtAxis(max * f), pad.left - 8, y);
            }
          });

          var slot = cw / data.length;
          var bw = Math.min(16, slot * 0.28);
          var hover = null;

          data.forEach(function (d, i) {
            var cx = pad.left + slot * i + slot / 2;
            var x1 = cx - bw - 2;
            var x2 = cx + 2;
            var h1 = Math.max(2, ch * (d.simplex / max) * t);
            var h2 = Math.max(2, ch * (d.pulp / max) * t);
            var y1 = pad.top + ch - h1;
            var y2 = pad.top + ch - h2;

            var over =
              p.mouseX >= cx - slot / 2 &&
              p.mouseX <= cx + slot / 2 &&
              p.mouseY >= pad.top &&
              p.mouseY <= pad.top + ch;
            if (over) hover = d;

            p.noStroke();
            p.fill(over ? "#1B4F82" : "#2E6DA4");
            p.rect(x1, y1, bw, h1, 2, 2, 0, 0);
            p.fill(over ? "#C6B514" : "#FAE95D");
            p.rect(x2, y2, bw, h2, 2, 2, 0, 0);

            p.fill("#9C9C9F");
            p.textAlign(p.CENTER, p.TOP);
            p.textSize(8);
            p.text(d.label, cx, pad.top + ch + 8);
          });

          p.noStroke();
          [
            { label: "Simplex", color: "#2E6DA4", x: pad.left },
            { label: "PuLP", color: "#FAE95D", x: pad.left + 76 },
          ].forEach(function (item) {
            p.fill(item.color);
            p.rect(item.x, H - 14, 10, 10, 2);
            p.fill("#3B4049");
            p.textAlign(p.LEFT, p.CENTER);
            p.textSize(10);
            p.text(item.label, item.x + 14, H - 9);
          });

          if (hover) {
            var delta = hover.pulp - hover.simplex;
            _drawTooltip(p, [
              hover.label,
              "Simplex: " + _fmtFull(hover.simplex),
              "PuLP: " + _fmtFull(hover.pulp),
              "Dif.: " + (delta >= 0 ? "+" : "-") + _fmtFull(Math.abs(delta)),
            ]);
            p.cursor(p.HAND);
          } else {
            p.cursor(p.ARROW);
          }
        };
      };

      var instance = new p5(sketch, node);
      return function () {
        instance.remove();
      };
    },
    [dataKey],
  );

  if (!data.length) return null;
  return <div ref={ref} style={{ width: "100%" }} />;
};

// ============================================================================
// SankeyPipelineP5 - fluxo do pipeline em diagrama de Sankey (p5.js)
// ----------------------------------------------------------------------------
// Mostra como a base de clientes flui pelas etapas ate receber (ou nao) limite:
//   Base total -> Elegibilidade -> Clusters -> Faixa de limite
//
// Adaptacoes para o volume real de dados (muitos clusters):
//   - Clusters: Top N maiores individualmente + um no "Outros" (resto agregado),
//     empilhados por limite (maior no topo, "sem oferta" embaixo).
//   - Limite: agregado em FAIXAS (R$15k+ / R$5-15k / ate R$5k / Sem oferta).
//   - Cor = camada de informacao de RISCO (PD media): verde (baixo) -> vermelho.
//
// Duas leituras (toggle):
//   - CLIENTES: a largura das fitas = numero de pessoas que fluem.
//   - CREDITO (R$): a largura = R$ concedido (limite x clientes). Nesse modo o
//     diagrama representa literalmente o FLUXO DE CONCESSAO de credito; quem nao
//     recebe oferta (limite 0) some, pois nao concede credito.
//
// Interacoes (p5.js): hover destaca o fluxo e mostra tooltip (clientes, %, PD e
// R$ concedido); clique TRAVA o foco; animacao revela as colunas em sequencia.
// No canto: total de credito concedido (soma de todos os clusters).
//
// props: { total, elegiveis, clusters:[{cluster_id,n_clientes,pd_media,limite_otimizado}], topN }
// ============================================================================

// paleta de risco por PD media (mesma do histograma RiskHistP5)
function _sankeyRiscoCor(pd) {
  if (pd == null) return [150, 155, 165];
  if (pd < 0.05) return [103, 222, 152];
  if (pd < 0.1) return [168, 230, 176];
  if (pd < 0.15) return [250, 233, 93];
  if (pd < 0.2) return [255, 200, 122];
  if (pd < 0.25) return [255, 140, 107];
  return [255, 93, 92];
}
function _sankeyFaixaLimite(v) {
  if (!v || v <= 0) return 0;
  if (v <= 5000) return 1;
  if (v <= 15000) return 2;
  return 3;
}
var _SANKEY_FAIXA_META = [
  { label: "Sem oferta", cor: [200, 90, 80] },
  { label: "Ate R$ 5k", cor: [150, 180, 210] },
  { label: "R$ 5-15k", cor: [90, 150, 205] },
  { label: "R$ 15k+", cor: [46, 109, 164] },
];

function _sankeyFmtNum(n) {
  if (n >= 1e6) return (n / 1e6).toFixed(1) + "M";
  if (n >= 1e3) return (n / 1e3).toFixed(1) + "K";
  return Math.round(n).toLocaleString("pt-BR");
}
function _sankeyFmtReais(v) {
  if (v >= 1e9) return "R$ " + (v / 1e9).toFixed(2) + " bi";
  if (v >= 1e6) return "R$ " + (v / 1e6).toFixed(1) + " mi";
  if (v >= 1e3) return "R$ " + (v / 1e3).toFixed(0) + " mil";
  return "R$ " + Math.round(v);
}

var SankeyPipelineP5 = function (props) {
  var ref = React.useRef(null);
  var sTop = React.useState(props.topN || 8);
  var topN = sTop[0];
  var setTopN = sTop[1];
  var sMode = React.useState("clientes"); // "clientes" | "credito"
  var mode = sMode[0];
  var setMode = sMode[1];

  var total = props.total || 0;
  var elig = props.elegiveis || 0;
  var clusters = (props.clusters || []).filter(function (c) {
    return c && c.n_clientes > 0;
  });
  var creditoTotal = clusters.reduce(function (sum, c) {
    return sum + (c.limite_otimizado || 0) * c.n_clientes;
  }, 0);

  var dataKey = JSON.stringify({
    total: total,
    elig: elig,
    topN: topN,
    mode: mode,
    c: clusters.map(function (c) {
      return [c.cluster_id, c.n_clientes, c.pd_media, c.limite_otimizado];
    }),
  });

  React.useEffect(
    function () {
      var node = ref.current;
      if (!node || total <= 0 || clusters.length === 0) return;

      var sketch = function (p) {
        var W = 960;
        var H = 460;
        var nodes = [];
        var links = [];
        var hovN = null,
          hovL = null,
          lockN = null,
          lockL = null;
        var start = 0;
        var INTRO = 1100;
        var introDone = false;
        var creditoTotal = 0;
        var isCred = mode === "credito";

        function ease(x) {
          return 1 - Math.pow(1 - x, 3);
        }
        // formata o valor "ativo" (clientes ou R$) conforme o modo
        function fmtVal(v) {
          return isCred ? _sankeyFmtReais(v) : _sankeyFmtNum(v);
        }
        // metrica ativa de um cluster
        function metric(c) {
          return isCred ? (c.limite_otimizado || 0) * c.n_clientes : c.n_clientes;
        }

        function build() {
          nodes = [];
          links = [];

          // total de credito concedido (todos os clusters) - usado no readout
          creditoTotal = clusters.reduce(function (s, c) {
            return s + (c.limite_otimizado || 0) * c.n_clientes;
          }, 0);

          // valor "ativo" dos nos de origem
          var vTotal = isCred ? creditoTotal : total;
          var vElig = isCred ? creditoTotal : elig; // todo o credito vem dos elegiveis
          var vNao = isCred ? 0 : Math.max(0, total - elig);

          var nTotal = { id: "total", col: 0, label: "Clientes", value: vTotal, cli: total, cred: creditoTotal, cor: [100, 120, 160] };
          var nElig = { id: "elig", col: 1, label: "Elegiveis", value: vElig, cli: elig, cred: creditoTotal, cor: [60, 140, 200] };
          nodes.push(nTotal, nElig);
          links.push({ src: nTotal, dst: nElig, val: vElig, cor: nElig.cor });

          if (vNao > 0) {
            var nNao = { id: "nao", col: 1, label: "Inelegiveis", value: vNao, cli: Math.max(0, total - elig), cred: 0, cor: [160, 160, 170] };
            nodes.push(nNao);
            links.push({ src: nTotal, dst: nNao, val: vNao, cor: nNao.cor });
          }

          // Top N por tamanho; empilha por limite (maior no topo)
          var sorted = clusters.slice().sort(function (a, b) {
            return b.n_clientes - a.n_clientes;
          });
          // Empilha por RISCO (PD media) crescente: menor risco (verde) no topo,
          // maior risco (vermelho) embaixo. Cruzamentos ocasionais sao aceitaveis.
          var top = sorted.slice(0, topN).sort(function (a, b) {
            return (a.pd_media || 0) - (b.pd_media || 0);
          });
          var rest = sorted.slice(topN);

          // Faixas COMPARTILHADAS pelos clusters do Top N...
          var sharedFaixa = {};
          function getShared(idx) {
            if (!sharedFaixa[idx]) {
              var m = _SANKEY_FAIXA_META[idx];
              sharedFaixa[idx] = { id: "fxs" + idx, col: 3, label: m.label, value: 0, cli: 0, cred: 0, cor: m.cor, faixa: true };
            }
            return sharedFaixa[idx];
          }
          // ...e faixas PROPRIAS do no "Outros" (separadas, ficam embaixo).
          var outrosFaixa = {};
          function getOutros(idx) {
            if (!outrosFaixa[idx]) {
              var m = _SANKEY_FAIXA_META[idx];
              outrosFaixa[idx] = { id: "fxo" + idx, col: 3, label: m.label, value: 0, cli: 0, cred: 0, cor: m.cor, faixa: true, doOutros: true };
            }
            return outrosFaixa[idx];
          }

          top.forEach(function (c) {
            var v = metric(c);
            if (v <= 0) return; // no modo credito, clusters sem oferta somem
            var cor = _sankeyRiscoCor(c.pd_media);
            var nc = {
              id: "c" + c.cluster_id,
              col: 2,
              label: "CLU-" + c.cluster_id,
              value: v,
              cli: c.n_clientes,
              cred: (c.limite_otimizado || 0) * c.n_clientes,
              cor: cor,
              pd: c.pd_media,
              limite: c.limite_otimizado,
            };
            nodes.push(nc);
            links.push({ src: nElig, dst: nc, val: v, cor: cor });
            var fx = getShared(_sankeyFaixaLimite(c.limite_otimizado));
            fx.value += v;
            fx.cli += c.n_clientes;
            fx.cred += (c.limite_otimizado || 0) * c.n_clientes;
            links.push({ src: nc, dst: fx, val: v, cor: cor });
          });

          if (rest.length > 0) {
            var restV = rest.reduce(function (s, c) {
              return s + metric(c);
            }, 0);
            if (restV > 0) {
              var restCli = rest.reduce(function (s, c) {
                return s + c.n_clientes;
              }, 0);
              var restCred = rest.reduce(function (s, c) {
                return s + (c.limite_otimizado || 0) * c.n_clientes;
              }, 0);
              var nOut = { id: "outros", col: 2, label: "Outros (" + rest.length + ")", value: restV, cli: restCli, cred: restCred, cor: [165, 170, 180], outros: true };
              nodes.push(nOut);
              links.push({ src: nElig, dst: nOut, val: restV, cor: [180, 185, 195] });
              var byFaixa = {};
              rest.forEach(function (c) {
                var v = metric(c);
                if (v <= 0) return;
                var f = _sankeyFaixaLimite(c.limite_otimizado);
                if (!byFaixa[f]) byFaixa[f] = { v: 0, cli: 0, cred: 0 };
                byFaixa[f].v += v;
                byFaixa[f].cli += c.n_clientes;
                byFaixa[f].cred += (c.limite_otimizado || 0) * c.n_clientes;
              });
              Object.keys(byFaixa).forEach(function (fk) {
                var fx = getOutros(parseInt(fk, 10));
                fx.value += byFaixa[fk].v;
                fx.cli += byFaixa[fk].cli;
                fx.cred += byFaixa[fk].cred;
                links.push({ src: nOut, dst: fx, val: byFaixa[fk].v, cor: [180, 185, 195] });
              });
            }
          }

          // col3: faixas compartilhadas no topo (desc) e, abaixo, as faixas
          // proprias do "Outros" (desc) - mantem os dois grupos separados.
          Object.keys(sharedFaixa)
            .map(Number)
            .sort(function (a, b) { return b - a; })
            .forEach(function (k) { nodes.push(sharedFaixa[k]); });
          Object.keys(outrosFaixa)
            .map(Number)
            .sort(function (a, b) { return b - a; })
            .forEach(function (k) { nodes.push(outrosFaixa[k]); });

          layout();
        }

        function layout() {
          var mTop = 86,
            mBot = 30,
            mX = 92,
            nW = 20,
            pad = 10;
          var uW = W - 2 * mX;
          var uH = H - mTop - mBot;
          var colSp = uW / 3;
          var cols = [[], [], [], []];
          nodes.forEach(function (n) {
            cols[n.col].push(n);
          });
          for (var c = 0; c < 4; c++) {
            var col = cols[c];
            var tot =
              col.reduce(function (sum, n) {
                return sum + n.value;
              }, 0) || 1;
            var availH = uH - (col.length - 1) * pad;
            var y = mTop;
            col.forEach(function (n) {
              n.h = Math.max(9, (n.value / tot) * availH);
              n.x = mX + c * colSp - nW / 2;
              n.y = y;
              n.w = nW;
              y += n.h + pad;
            });
            var totalH = y - pad - mTop;
            var off = (uH - totalH) / 2;
            col.forEach(function (n) {
              n.y += off;
            });
          }
          var outOff = {},
            inOff = {};
          nodes.forEach(function (n) {
            outOff[n.id] = 0;
            inOff[n.id] = 0;
          });
          links.forEach(function (lk) {
            var srcOut =
              links
                .filter(function (l) {
                  return l.src.id === lk.src.id;
                })
                .reduce(function (sum, l) {
                  return sum + l.val;
                }, 0) || 1;
            var dstIn =
              links
                .filter(function (l) {
                  return l.dst.id === lk.dst.id;
                })
                .reduce(function (sum, l) {
                  return sum + l.val;
                }, 0) || 1;
            lk.srcH = (lk.val / srcOut) * lk.src.h;
            lk.dstH = (lk.val / dstIn) * lk.dst.h;
            lk.srcX = lk.src.x + lk.src.w;
            lk.srcY = lk.src.y + outOff[lk.src.id];
            lk.dstX = lk.dst.x;
            lk.dstY = lk.dst.y + inOff[lk.dst.id];
            outOff[lk.src.id] += lk.srcH;
            inOff[lk.dst.id] += lk.dstH;
          });
        }

        p.setup = function () {
          W = node.offsetWidth || 960;
          p.createCanvas(W, H);
          p.textFont("Circular, Arial, sans-serif");
          start = p.millis();
          build();
        };
        p.windowResized = function () {
          W = node.offsetWidth || 960;
          p.resizeCanvas(W, H);
          build();
        };

        function nodeContains(n, mx, my) {
          return mx >= n.x - 2 && mx <= n.x + n.w + 2 && my >= n.y && my <= n.y + n.h;
        }
        function linkContains(lk, mx, my) {
          if (mx < lk.srcX || mx > lk.dstX) return false;
          var t = (mx - lk.srcX) / (lk.dstX - lk.srcX || 1);
          var topY = p.lerp(lk.srcY, lk.dstY, t);
          var botY = p.lerp(lk.srcY + lk.srcH, lk.dstY + lk.dstH, t);
          return my >= topY && my <= botY;
        }

        function fNode() {
          return lockN || hovN;
        }
        function fLink() {
          return lockL || hovL;
        }
        function isNodeOn(n) {
          var fn = fNode(),
            fl = fLink();
          if (!fn && !fl) return true;
          if (fn)
            return (
              n === fn ||
              links.some(function (l) {
                return (l.src === fn && l.dst === n) || (l.dst === fn && l.src === n);
              })
            );
          return fl.src === n || fl.dst === n;
        }
        function isLinkOn(lk) {
          var fn = fNode(),
            fl = fLink();
          if (!fn && !fl) return true;
          if (fn) return lk.src === fn || lk.dst === fn;
          return lk === fl;
        }

        function drawLink(lk, intro) {
          var on = isLinkOn(lk);
          var a = (on ? 95 : 16) * intro;
          p.noStroke();
          p.fill(lk.cor[0], lk.cor[1], lk.cor[2], a);
          var cpX = (lk.srcX + lk.dstX) / 2;
          p.beginShape();
          p.vertex(lk.srcX, lk.srcY);
          for (var t = 0; t <= 1.0001; t += 0.05)
            p.vertex(p.bezierPoint(lk.srcX, cpX, cpX, lk.dstX, t), p.bezierPoint(lk.srcY, lk.srcY, lk.dstY, lk.dstY, t));
          p.vertex(lk.dstX, lk.dstY + lk.dstH);
          for (var u = 1; u >= -0.0001; u -= 0.05)
            p.vertex(
              p.bezierPoint(lk.srcX, cpX, cpX, lk.dstX, u),
              p.bezierPoint(lk.srcY + lk.srcH, lk.srcY + lk.srcH, lk.dstY + lk.dstH, lk.dstY + lk.dstH, u),
            );
          p.vertex(lk.srcX, lk.srcY + lk.srcH);
          p.endShape(p.CLOSE);
        }

        function drawNode(n, intro) {
          var on = isNodeOn(n);
          p.noStroke();
          p.fill(n.cor[0], n.cor[1], n.cor[2], (on ? 255 : 80) * intro);
          p.rect(n.x, n.y, n.w, n.h, 3);
          if (n.h < 13 && !on) return;
          var rightSide = n.col >= 2;
          var ax = rightSide ? n.x + n.w + 8 : n.x - 8;
          p.textAlign(rightSide ? p.LEFT : p.RIGHT, p.CENTER);
          var fade = intro * (on ? 1 : 0.7);
          // faixas (col 3): mostram a metrica ativa + a outra em linha menor
          var extra = n.col === 3 ? (isCred ? _sankeyFmtNum(n.cli) : _sankeyFmtReais(n.cred)) : null;
          var midY = n.y + n.h / 2;
          p.fill(58, 64, 73, 255 * fade);
          p.textSize(12);
          p.textStyle(p.BOLD);
          p.text(n.label, ax, midY - (extra ? 12 : 7));
          p.fill(120, 128, 138, 255 * fade);
          p.textSize(10);
          p.textStyle(p.NORMAL);
          p.text(fmtVal(n.value), ax, midY + (extra ? -0 : 8));
          if (extra) {
            p.fill(150, 156, 164, 255 * fade);
            p.textSize(9);
            p.text(extra, ax, midY + 12);
          }
        }

        function drawTip(n) {
          var lines = [n.label];
          var pct = isCred
            ? creditoTotal > 0
              ? ((n.cred / creditoTotal) * 100).toFixed(1)
              : "0"
            : ((n.cli / total) * 100).toFixed(1);
          lines.push(_sankeyFmtNum(n.cli) + " clientes (" + pct + "%)");
          if (n.cred > 0) lines.push(_sankeyFmtReais(n.cred) + " concedido");
          if (n.pd != null) lines.push("PD media: " + (n.pd * 100).toFixed(1) + "%");
          if (n.faixa) lines.push("Faixa de limite");
          if (n.outros) lines.push("Demais clusters agregados");
          _drawTooltip(p, lines);
        }

        p.draw = function () {
          p.clear();
          var raw = p.constrain((p.millis() - start) / INTRO, 0, 1);
          introDone = raw >= 1;
          function colIntro(col) {
            return p.constrain((raw - col * 0.22) / 0.34, 0, 1);
          }

          hovN = null;
          hovL = null;
          if (introDone) {
            for (var i = 0; i < nodes.length; i++) {
              if (nodeContains(nodes[i], p.mouseX, p.mouseY)) {
                hovN = nodes[i];
                break;
              }
            }
            if (!hovN) {
              for (var j = 0; j < links.length; j++) {
                if (linkContains(links[j], p.mouseX, p.mouseY)) {
                  hovL = links[j];
                  break;
                }
              }
            }
          }

          // titulos das colunas + processos
          p.noStroke();
          p.textAlign(p.CENTER, p.TOP);
          var colSp = (W - 184) / 3;
          var titles = ["BASE TOTAL", "ELEGIBILIDADE", "CLUSTERS", "LIMITE"];
          p.textSize(10);
          p.textStyle(p.BOLD);
          for (var c = 0; c < 4; c++) {
            p.fill(150, 155, 162, 255 * ease(colIntro(c)));
            p.text(titles[c], 92 + c * colSp, 30);
          }
          p.textSize(10);
          p.textStyle(p.NORMAL);
          var procs = ["Filtro de elegibilidade", "Clusterizacao (CART)", "Otimizacao (Simplex)"];
          for (var pc = 0; pc < 3; pc++) {
            p.fill(120, 150, 190, 230 * ease(colIntro(pc + 1)));
            p.text(procs[pc], 92 + colSp * (pc + 0.5), 46);
          }

          links.forEach(function (lk) {
            drawLink(lk, ease(colIntro(lk.dst.col)));
          });
          nodes.forEach(function (n) {
            drawNode(n, ease(colIntro(n.col)));
          });

          var tip = hovN || (hovL ? hovL.dst : null);
          if (tip && introDone) drawTip(tip);

          if (lockN || lockL) {
            p.noStroke();
            p.fill(120, 130, 145);
            p.textSize(10);
            p.textStyle(p.NORMAL);
            p.textAlign(p.LEFT, p.BOTTOM);
            p.text("foco travado - clique no vazio para soltar", 92, H - 8);
          }

          p.cursor(hovN || hovL ? p.HAND : p.ARROW);
        };

        p.mousePressed = function () {
          if (!introDone) return;
          if (p.mouseX < 0 || p.mouseX > W || p.mouseY < 0 || p.mouseY > H) return;
          if (hovN) {
            lockN = lockN === hovN ? null : hovN;
            lockL = null;
          } else if (hovL) {
            lockL = lockL === hovL ? null : hovL;
            lockN = null;
          } else {
            lockN = null;
            lockL = null;
          }
        };
      };

      var instance = new p5(sketch, node);
      return function () {
        instance.remove();
      };
    },
    [dataKey],
  );

  if (!props.total || !(props.clusters || []).length) return null;

  var topBtn = function (n) {
    return (
      <button
        key={n}
        onClick={function () {
          setTopN(n);
        }}
        className={
          "px-2.5 py-1 text-[11px] font-medium border transition-colors " +
          (topN === n
            ? "bg-[#2E6DA4] text-white border-[#2E6DA4]"
            : "bg-white text-[#3B4049] border-[#E8EFF7] hover:bg-[#E2EAF4]")
        }
      >
        Top {n}
      </button>
    );
  };
  var modeBtn = function (key, label) {
    return (
      <button
        key={key}
        onClick={function () {
          setMode(key);
        }}
        className={
          "px-2.5 py-1 text-[11px] font-medium border transition-colors " +
          (mode === key
            ? "bg-[#0D1B2A] text-white border-[#0D1B2A]"
            : "bg-white text-[#3B4049] border-[#E8EFF7] hover:bg-[#E2EAF4]")
        }
      >
        {label}
      </button>
    );
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-2 flex-wrap gap-3">
        <div className="flex items-center gap-3 flex-wrap">
          <div className="flex items-center gap-1.5">
            {modeBtn("clientes", "Clientes")}
            {modeBtn("credito", "Crédito (R$)")}
          </div>
          <div className="flex items-center gap-3 text-[11px] text-[#9C9C9F]">
            <span className="flex items-center gap-1">
              <span className="inline-block w-2.5 h-2.5" style={{ background: "#67DE98" }} /> baixo risco
            </span>
            <span className="flex items-center gap-1">
              <span className="inline-block w-2.5 h-2.5" style={{ background: "#FAE95D" }} /> medio
            </span>
            <span className="flex items-center gap-1">
              <span className="inline-block w-2.5 h-2.5" style={{ background: "#FF5D5C" }} /> alto risco
            </span>
          </div>
        </div>
        <div className="flex items-center gap-4 flex-wrap">
          <div className="text-right leading-tight">
            <div className="text-[10px] text-[#9C9C9F] uppercase tracking-wide">
              Crédito concedido
            </div>
            <div className="text-sm font-bold text-[#2E6DA4]">
              {_sankeyFmtReais(creditoTotal)}
            </div>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="text-[11px] text-[#9C9C9F] mr-1">Clusters:</span>
            {[5, 8, 12].map(topBtn)}
          </div>
        </div>
      </div>
      <div ref={ref} style={{ width: "100%" }} />
    </div>
  );
};

// ============================================================================
// ScatterSVG - Simplex vs PuLP por cluster
// ============================================================================
var ScatterSVG = function (props) {
  var clusters = props.clusters;
  if (!clusters || clusters.length === 0) return null;

  var hasPulp = clusters.some(function (c) {
    return c.limite_otimizado_pulp != null;
  });
  if (!hasPulp) {
    return (
      <p className="text-xs text-[#9C9C9F]">
        Dados PuLP indisponíveis para esta simulação.
      </p>
    );
  }

  var w = 420;
  var h = 260;
  var pad = { top: 16, right: 16, bottom: 44, left: 56 };
  var cw = w - pad.left - pad.right;
  var ch = h - pad.top - pad.bottom;

  var maxVal =
    Math.max.apply(
      null,
      clusters.reduce(function (acc, c) {
        acc.push(c.limite_otimizado || 0);
        if (c.limite_otimizado_pulp != null) acc.push(c.limite_otimizado_pulp);
        return acc;
      }, [1]),
    ) * 1.05;

  function scaleX(v) {
    return pad.left + (v / maxVal) * cw;
  }
  function scaleY(v) {
    return pad.top + ch - (v / maxVal) * ch;
  }

  function fmtAxis(v) {
    if (v >= 1000) return "R$" + (v / 1000).toFixed(0) + "k";
    return "R$" + v;
  }

  var ticks = [0, 0.25, 0.5, 0.75, 1];

  // classifica por divergência para colorir
  function classify(c) {
    if (c.limite_otimizado_pulp == null) return "na";
    var diff = Math.abs(c.limite_otimizado - c.limite_otimizado_pulp);
    if (diff < 50) return "match";
    if (diff < 500) return "small";
    return "large";
  }

  var colorMap = { match: "#22c55e", small: "#f59e0b", large: "#ef4444", na: "#cbd5e1" };

  // ordena: divergentes por cima para facilitar leitura
  var sorted = clusters.slice().sort(function (a, b) {
    var order = { match: 0, small: 1, large: 2, na: -1 };
    return order[classify(a)] - order[classify(b)];
  });

  // contagens para legenda
  var nMatch = clusters.filter(function (c) { return classify(c) === "match"; }).length;
  var nSmall = clusters.filter(function (c) { return classify(c) === "small"; }).length;
  var nLarge = clusters.filter(function (c) { return classify(c) === "large"; }).length;

  return (
    <div>
      <svg viewBox={"0 0 " + w + " " + h} width="100%" style={{ overflow: "visible" }}>
        {/* grid lines */}
        {ticks.map(function (f) {
          var x = pad.left + f * cw;
          var y = pad.top + ch - f * ch;
          return (
            <g key={f}>
              <line x1={x} x2={x} y1={pad.top} y2={pad.top + ch} stroke="#E8EFF7" strokeWidth="1" />
              <line x1={pad.left} x2={pad.left + cw} y1={y} y2={y} stroke="#E8EFF7" strokeWidth="1" />
              {f > 0 && (
                <g>
                  <text x={x} y={pad.top + ch + 14} textAnchor="middle" fontSize="8" fill="#9C9C9F">
                    {fmtAxis(maxVal * f)}
                  </text>
                  <text x={pad.left - 6} y={y + 3} textAnchor="end" fontSize="8" fill="#9C9C9F">
                    {fmtAxis(maxVal * f)}
                  </text>
                </g>
              )}
            </g>
          );
        })}

        {/* diagonal de referência y = x */}
        <line
          x1={scaleX(0)} y1={scaleY(0)}
          x2={scaleX(maxVal)} y2={scaleY(maxVal)}
          stroke="#2E6DA4" strokeWidth="1" strokeDasharray="4 3" opacity="0.4"
        />

        {/* pontos */}
        {sorted.map(function (c, i) {
          if (c.limite_otimizado_pulp == null) return null;
          var cls = classify(c);
          return (
            <circle
              key={i}
              cx={scaleX(c.limite_otimizado)}
              cy={scaleY(c.limite_otimizado_pulp)}
              r="2.5"
              fill={colorMap[cls]}
              fillOpacity="0.75"
            />
          );
        })}

        {/* labels dos eixos */}
        <text
          x={pad.left + cw / 2}
          y={h - 4}
          textAnchor="middle"
          fontSize="9"
          fill="#9C9C9F"
        >
          Simplex (R$)
        </text>
        <text
          x={10}
          y={pad.top + ch / 2}
          textAnchor="middle"
          fontSize="9"
          fill="#9C9C9F"
          transform={"rotate(-90, 10, " + (pad.top + ch / 2) + ")"}
        >
          PuLP (R$)
        </text>
      </svg>

      {/* legenda */}
      <div className="flex items-center gap-4 mt-1">
        {[
          { color: "#22c55e", label: "Match (Δ < R$50)", n: nMatch },
          { color: "#f59e0b", label: "Δ R$50–500", n: nSmall },
          { color: "#ef4444", label: "Δ > R$500", n: nLarge },
        ].map(function (l) {
          return (
            <div key={l.label} className="flex items-center gap-1.5 text-[10px] text-[#9C9C9F]">
              <div className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: l.color }} />
              {l.label}
              <span className="font-semibold text-[#3B4049]">{l.n}</span>
            </div>
          );
        })}
      </div>
    </div>
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

  function getLimitePulp(c) {
    if (!c) return null;
    return c.limite_otimizado_pulp != null ? c.limite_otimizado_pulp : null;
  }

  var pulpSimplexData = clusters
    .filter(function (c) {
      return getLimitePulp(c) != null;
    })
    .slice()
    .sort(function (a, b) {
      var diffA = Math.abs(getLimitePulp(a) - (a.limite_otimizado || 0));
      var diffB = Math.abs(getLimitePulp(b) - (b.limite_otimizado || 0));
      return diffB - diffA;
    })
    .slice(0, 12)
    .map(function (c) {
      return {
        label: "CLU-" + c.cluster_id,
        simplex: c.limite_otimizado || 0,
        pulp: getLimitePulp(c) || 0,
      };
    });

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
              pulpOk:
                selectedConsulta.z_pulp != null && selectedConsulta.delta_z_pct != null
                  ? selectedConsulta.delta_z_pct < 0.01
                  : null,
              pulpDelta:
                selectedConsulta.delta_z_pct != null
                  ? selectedConsulta.delta_z_pct
                  : null,
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
                {k.pulpOk !== null && k.pulpOk !== undefined && (
                  <div className="flex items-center gap-1.5 mt-2">
                    <div
                      className={
                        "w-1.5 h-1.5 rounded-full flex-shrink-0 " +
                        (k.pulpOk ? "bg-[#22c55e]" : "bg-[#f59e0b]")
                      }
                    />
                    <span
                      className={
                        "text-[10px] font-semibold " +
                        (k.pulpOk ? "text-[#15803d]" : "text-[#92400e]")
                      }
                    >
                      {k.pulpOk
                        ? "PuLP confirma"
                        : "Δ " + k.pulpDelta.toFixed(4) + "%"}
                    </span>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Validação PuLP */}
      {selectedConsulta && selectedConsulta.z_pulp != null && (
        <div className="bg-white border border-[#E8EFF7] shadow-sm p-5">
          <div className="flex items-center gap-2 mb-4">
            <div className="text-sm font-semibold text-[#0D1B2A]">Validação PuLP</div>
            {selectedConsulta.delta_z_pct != null && (
              <span
                className={
                  "text-xs font-semibold px-2 py-0.5 " +
                  (selectedConsulta.delta_z_pct < 0.01
                    ? "bg-[#67DE98]/20 text-[#1A7A40]"
                    : selectedConsulta.delta_z_pct < 1
                    ? "bg-[#FAE95D]/30 text-[#7A6010]"
                    : "bg-[#FF5D5C]/15 text-[#DC2F37]")
                }
              >
                Δz = {selectedConsulta.delta_z_pct.toFixed(4)}%
              </span>
            )}
          </div>
          <div className="grid grid-cols-3 gap-px bg-[#E8EFF7]">
            {[
              {
                label: "z · Simplex (projeto)",
                value: selectedConsulta.z_otimo != null ? fmtZ(selectedConsulta.z_otimo) : "-",
                sub: selectedConsulta.status_lp || "-",
              },
              {
                label: "z · PuLP / CBC",
                value: fmtZ(selectedConsulta.z_pulp),
                sub: selectedConsulta.status_lp_pulp || "-",
              },
              {
                label: "Diferença relativa",
                value:
                  selectedConsulta.delta_z_pct != null
                    ? selectedConsulta.delta_z_pct.toFixed(6) + "%"
                    : "-",
                sub: selectedConsulta.delta_z_pct < 0.01 ? "✓ dentro da tolerância" : "⚠ verificar",
              },
            ].map(function (k) {
              return (
                <div key={k.label} className="bg-white px-5 py-4">
                  <div className="text-[10px] font-medium text-[#9C9C9F] uppercase tracking-wide mb-1">
                    {k.label}
                  </div>
                  <div className="text-lg font-bold text-[#0D1B2A] leading-tight">{k.value}</div>
                  <div className="text-xs text-[#9C9C9F] mt-1">{k.sub}</div>
                </div>
              );
            })}
          </div>
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
            {/* Scatter Simplex vs PuLP */}
            <div className="bg-white border border-[#E8EFF7] shadow-sm p-5">
              <div className="text-sm font-semibold text-[#0D1B2A] mb-1">
                Simplex vs PuLP por Cluster
              </div>
              <div className="text-xs text-[#9C9C9F] mb-3">
                Cada ponto é um cluster — na diagonal significa concordância perfeita
              </div>
              {clusters.length > 0 ? (
                <ScatterSVG clusters={clusters} />
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
                  <DonutChartP5 data={donutData} />
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

          {pulpSimplexData.length > 0 && (
            <div className="bg-white border border-[#E8EFF7] shadow-sm p-5">
              <div className="text-sm font-semibold text-[#0D1B2A] mb-1">
                Comparação PuLP x Simplex
              </div>
              <div className="text-xs text-[#9C9C9F] mb-4">
                Top 12 clusters com maior diferença de limite otimizado
              </div>
              <PulpSimplexCompareP5 data={pulpSimplexData} />
            </div>
          )}

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
              <LineChartP5 data={evolucaoData} />
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
                <RiskHistP5 clusters={clusters} />
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
      {/* Fluxo do pipeline (Sankey) */}
      {selectedConsulta && clusters && clusters.length > 0 && (
        <div className="bg-white border border-[#E8EFF7] shadow-sm p-5">
          <div className="text-sm font-semibold text-[#0D1B2A] mb-1">
            Fluxo do Pipeline
          </div>
          <div className="text-xs text-[#9C9C9F] mb-3">
            Como a base de clientes flui da elegibilidade aos clusters e às faixas de limite
          </div>
          <SankeyPipelineP5
            total={selectedConsulta.n_clientes_total}
            elegiveis={selectedConsulta.n_clientes_elegiveis}
            clusters={clusters}
          />
        </div>
      )}
    </div>
  );
};
