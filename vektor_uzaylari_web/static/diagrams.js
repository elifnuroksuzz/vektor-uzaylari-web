/* Vektör Uzayları — SVG sahne motoru (yalnızca görüntüleme ve animasyon).
 *
 * Bütün koordinatlar sunucudan (Python, kesin kesir) gelir. Bu dosya onları
 * çizer ve adımlar arasında YUMUŞAK geçiş yapar:
 *   - aynı kimlikli ok yeni konumuna kayar (ör. v, u'nun ucuna taşınır),
 *   - yeni ok başlangıç noktasından "uzayarak" çıkar,
 *   - kaybolan nesne solar,
 *   - tarama noktaları sırayla belirir, span doğrusu çizilerek uzar.
 * prefers-reduced-motion açıksa animasyon yapılmaz.
 */
(function (global) {
  "use strict";

  const SVGNS = "http://www.w3.org/2000/svg";
  const W = 400, H = 400, PAD = 16;
  const SURE = 650; // ms, adım geçişi
  let sayac = 0;

  const KINDS = ["giris", "giris2", "giris3", "ara", "sonuc", "icerde", "disarda", "ters", "kuvvet", "hayalet"];

  function el(name, attrs, parent) {
    const node = document.createElementNS(SVGNS, name);
    if (attrs) for (const k in attrs) node.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(node);
    return node;
  }

  function toNum(v) {
    if (typeof v === "number") return v;
    if (typeof v !== "string") return 0;
    v = v.replace("−", "-");
    if (v.indexOf("/") >= 0) {
      const p = v.split("/");
      return parseFloat(p[0]) / parseFloat(p[1]);
    }
    return parseFloat(v);
  }
  function P(p) { return [toNum(p[0]), toNum(p[1])]; }

  function hareketAzalt() {
    return !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
  }
  function yumusak(t) { return t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; }
  function lerp(a, b, t) { return a + (b - a) * t; }

  function mapping(range) {
    const scale = (W / 2 - PAD) / range;
    return {
      range: range, scale: scale,
      px: function (x) { return W / 2 + x * scale; },
      py: function (y) { return H / 2 - y * scale; }
    };
  }

  // ======================================================================
  // Sahne
  // ======================================================================
  function Sahne(svg) {
    this.svg = svg;
    this.on = "s" + (++sayac);
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    const defs = el("defs", {}, svg);
    KINDS.forEach(function (k) {
      const m = el("marker", {
        id: this.on + "-ok-" + k, markerWidth: 10, markerHeight: 10, refX: 7.5, refY: 3,
        orient: "auto", markerUnits: "strokeWidth"
      }, defs);
      el("path", { d: "M0,0 L8,3 L0,6 Z", "class": "ok-ucu k-" + k }, m);
    }, this);
    const clip = el("clipPath", { id: this.on + "-kirp" }, defs);
    el("rect", { x: PAD, y: PAD, width: W - 2 * PAD, height: H - 2 * PAD }, clip);
    const kirp = "url(#" + this.on + "-kirp)";

    this.gBg = el("g", { "clip-path": kirp }, svg);
    this.gEks = el("g", {}, svg);
    this.gArka = el("g", { "clip-path": kirp }, svg);
    this.gTara = el("g", { "clip-path": kirp }, svg);
    this.gPoly = el("g", { "clip-path": kirp }, svg);
    this.gVec = el("g", { "clip-path": kirp }, svg);
    // Vektör etiketleri okların üstünde ayrı katmanda: başka bir ok etiketi örtmesin.
    this.gEtk = el("g", { "clip-path": kirp }, svg);
    this.gPt = el("g", {}, svg);

    this.range = null;
    this.vecs = {}; this.pts = {}; this.polys = {};
    this.arkaKey = null; this.taraKey = null;
    this.anims = []; this.raf = null;
  }

  Sahne.prototype._loop = function () {
    const self = this;
    if (this.raf) return;
    function tick(now) {
      self.anims = self.anims.filter(function (a) {
        if (a.start == null) a.start = now;
        const t = a.dur <= 0 ? 1 : Math.min(1, (now - a.start) / a.dur);
        a.fn(yumusak(t));
        if (t >= 1 && a.done) a.done();
        return t < 1;
      });
      self._etiketAyir();
      if (self.anims.length) self.raf = requestAnimationFrame(tick);
      else self.raf = null;
    }
    this.raf = requestAnimationFrame(tick);
  };
  Sahne.prototype._tween = function (key, dur, fn, done) {
    this.anims = this.anims.filter(function (a) { return a.key !== key; });
    if (dur <= 0) { fn(1); if (done) done(); this._etiketAyir(); return; }
    fn(0); // ilk karede doğru yerde dursun
    this.anims.push({ key: key, dur: dur, fn: fn, done: done, start: null });
    this._loop();
  };

  Sahne.prototype._eksenler = function () {
    const g = this.gEks, m = this.m;
    while (g.firstChild) g.removeChild(g.firstChild);
    const r = m.range;
    for (let i = -r; i <= r; i++) {
      if (i === 0) continue;
      el("line", { x1: m.px(i), y1: PAD, x2: m.px(i), y2: H - PAD, "class": "izgara" }, g);
      el("line", { x1: PAD, y1: m.py(i), x2: W - PAD, y2: m.py(i), "class": "izgara" }, g);
    }
    el("line", { x1: PAD, y1: m.py(0), x2: W - PAD, y2: m.py(0), "class": "eksen" }, g);
    el("line", { x1: m.px(0), y1: PAD, x2: m.px(0), y2: H - PAD, "class": "eksen" }, g);
    const adim = r > 6 ? 2 : 1;
    for (let i = -r + (r % adim); i <= r; i += adim) {
      if (i === 0 || Math.abs(i) === r) continue;
      el("text", { x: m.px(i), y: m.py(0) + 13, "class": "eksen-sayi", "text-anchor": "middle" }, g).textContent = String(i).replace("-", "−");
      el("text", { x: m.px(0) - 5, y: m.py(i) + 3, "class": "eksen-sayi", "text-anchor": "end" }, g).textContent = String(i).replace("-", "−");
    }
    el("text", { x: W - PAD - 2, y: m.py(0) - 6, "class": "eksen-ad", "text-anchor": "end" }, g).textContent = "x";
    el("text", { x: m.px(0) + 6, y: PAD + 10, "class": "eksen-ad" }, g).textContent = "y";
    el("circle", { cx: m.px(0), cy: m.py(0), r: 2.5, "class": "orijin" }, g);
  };

  Sahne.prototype._sifirla = function () {
    [this.gBg, this.gArka, this.gTara, this.gPoly, this.gVec, this.gEtk, this.gPt].forEach(function (g) {
      while (g.firstChild) g.removeChild(g.firstChild);
    });
    this.vecs = {}; this.pts = {}; this.polys = {};
    this.arkaKey = null; this.taraKey = null;
    this.anims = [];
  };

  // --- Arka plan: küme, ek doğrular, span doğruları, düzlem, baz ızgarası ---
  Sahne.prototype._arkaPlan = function (sc, dur) {
    const key = JSON.stringify([sc.set || null, sc.lines || null, sc.spanLines || null, sc.plane || false, sc.grid || null]);
    if (key === this.arkaKey) return;
    this.arkaKey = key;
    const m = this.m, r = m.range;
    const eskiBg = Array.prototype.slice.call(this.gBg.childNodes);
    const eskiArka = Array.prototype.slice.call(this.gArka.childNodes);
    eskiBg.concat(eskiArka).forEach(function (n) { soldurVeSil(n, dur * 0.5); });

    const bg = el("g", {}, this.gBg);
    const ark = el("g", {}, this.gArka);
    const set = sc.set;
    if (sc.plane || (set && set.region === "all")) {
      el("rect", { x: PAD, y: PAD, width: W - 2 * PAD, height: H - 2 * PAD, "class": "bolge" }, bg);
    }
    if (set && set.type === "region") {
      if (set.region === "q1" || set.region === "q13") {
        el("rect", { x: m.px(0), y: PAD, width: W - PAD - m.px(0), height: m.py(0) - PAD, "class": "bolge" }, bg);
        if (set.region === "q1") {
          // Eksenler dahil değil: kesikli sınır
          el("line", { x1: m.px(0), y1: m.py(0), x2: W - PAD, y2: m.py(0), "class": "acik-sinir" }, ark);
          el("line", { x1: m.px(0), y1: m.py(0), x2: m.px(0), y2: PAD, "class": "acik-sinir" }, ark);
        }
      }
      if (set.region === "q13") {
        el("rect", { x: PAD, y: m.py(0), width: m.px(0) - PAD, height: H - PAD - m.py(0), "class": "bolge" }, bg);
      }
      el("text", { x: W - PAD - 6, y: PAD + 16, "class": "kume-ad", "text-anchor": "end" }, ark).textContent = "W";
    }
    const self = this;
    function dogruCiz(mm, bb, cls, etiket) {
      const x1 = -r - 1, x2 = r + 1;
      const ln = el("line", { x1: m.px(x1), y1: m.py(mm * x1 + bb), x2: m.px(x2), y2: m.py(mm * x2 + bb), "class": cls }, ark);
      cizerekUzat(ln, dur * 1.2);
      if (etiket) {
        // Etiketi doğrunun görünür ucuna yakın koy
        let tx = r * 0.55, ty = mm * tx + bb;
        if (Math.abs(ty) > r * 0.85) { ty = (ty > 0 ? 1 : -1) * r * 0.8; tx = (ty - bb) / mm; }
        el("text", { x: m.px(tx) + 8, y: m.py(ty), "class": "kume-ad" }, ark).textContent = etiket;
      }
    }
    if (set && set.type === "line") dogruCiz(toNum(set.m), toNum(set.b || "0"), "kume-dogru", "W");
    (sc.lines || []).forEach(function (l) { dogruCiz(toNum(l.m), toNum(l.b), "ek-dogru", l.label); });

    (sc.spanLines || []).forEach(function (s) {
      const d = P(s.dir);
      const mag = Math.max(Math.abs(d[0]), Math.abs(d[1])) || 1;
      const k = (r + 2) / mag;
      const a = el("line", { x1: m.px(0), y1: m.py(0), x2: m.px(k * d[0]), y2: m.py(k * d[1]), "class": "span-dogru" }, ark);
      const b = el("line", { x1: m.px(0), y1: m.py(0), x2: m.px(-k * d[0]), y2: m.py(-k * d[1]), "class": "span-dogru" }, ark);
      cizerekUzat(a, dur * 1.3); cizerekUzat(b, dur * 1.3);
      if (s.label) {
        const t = 0.8 * r / mag;
        el("text", { x: m.px(t * d[0]) + 6, y: m.py(t * d[1]) - 6, "class": "span-ad" }, ark).textContent = s.label;
      }
    });

    if (sc.grid) {
      const b1 = P(sc.grid.b1), b2 = P(sc.grid.b2);
      const N = Math.ceil(2.2 * r / Math.max(0.3, Math.min(Math.hypot(b1[0], b1[1]), Math.hypot(b2[0], b2[1])))) + 2;
      const L = N * 3;
      for (let i = -N; i <= N; i++) {
        [[b1, b2], [b2, b1]].forEach(function (par) {
          const a0 = [i * par[0][0] - L * par[1][0], i * par[0][1] - L * par[1][1]];
          const a1 = [i * par[0][0] + L * par[1][0], i * par[0][1] + L * par[1][1]];
          el("line", { x1: m.px(a0[0]), y1: m.py(a0[1]), x2: m.px(a1[0]), y2: m.py(a1[1]), "class": i === 0 ? "baz-izgara ana" : "baz-izgara" }, bg);
        });
      }
    }
    if (dur > 0) { belir(bg, dur); }
  };

  // --- Oklar ---------------------------------------------------------------
  Sahne.prototype._vekGeom = function (v) {
    const to = P(v.to);
    const fr = v.from ? P(v.from) : [0, 0];
    return { fx: fr[0], fy: fr[1], tx: to[0], ty: to[1] };
  };
  Sahne.prototype._vekCiz = function (o) {
    const m = this.m, g = o.cur;
    let x1 = m.px(g.fx), y1 = m.py(g.fy), x2 = m.px(g.tx), y2 = m.py(g.ty);
    let dx = x2 - x1, dy = y2 - y1;
    const len = Math.hypot(dx, dy);
    if (o.offset && len > 0.5) {
      const ox = (-dy / len) * 9, oy = (dx / len) * 9;
      x1 += ox; y1 += oy; x2 += ox; y2 += oy;
    }
    const gorunur = len > 1.5;
    o.line.setAttribute("x1", x1); o.line.setAttribute("y1", y1);
    o.line.setAttribute("x2", x2); o.line.setAttribute("y2", y2);
    o.line.style.visibility = gorunur ? "visible" : "hidden";
    if (o.text) {
      // Etiket okun ortasının yanında: uç uca eklemelerde uçlar üst üste
      // bindiği için etiketi uca koymak okunaksız olur.
      const ux = len ? dx / len : 0, uy = len ? dy / len : 0;
      // Girdiler okun soluna, sonuçlar sağına: aynı yöndeki oklar çakışmasın.
      const sag = o.kind === "sonuc" || o.kind === "icerde" || o.kind === "disarda";
      const nx = sag ? -uy : uy, ny = sag ? ux : -ux;
      const t = len < 40 ? 1 : 0.58;
      const k = len < 40 ? 8 : 11;
      const mx = x1 + dx * t + nx * k, my = y1 + dy * t + ny * k;
      o.text.setAttribute("x", mx);
      o.text.setAttribute("y", my + 4 + (ny > 0.3 ? 3 : 0));
      o.text.setAttribute("text-anchor", nx > 0.3 ? "start" : (nx < -0.3 ? "end" : "middle"));
      o.nx = nx; o.ny = ny;
      o.text.style.visibility = gorunur ? "visible" : "hidden";
    }
  };
  // Vektör etiketleri birbirinin ya da başka bir etiketin üstüne binerse,
  // her birini kendi okuna dik yönde adım adım uzaklaştırır.
  Sahne.prototype._etiketAyir = function () {
    if (!this.vecs || !this.svg || !this.svg.getBBox) return;
    const svg = this.svg;
    const dolu = [];
    const kutu = function (t) {
      try { const b = t.getBBox(); return b.width ? { x: b.x - 2, y: b.y - 1, w: b.width + 4, h: b.height + 2 } : null; }
      catch (e) { return null; }
    };
    const carpisir = function (a) {
      return dolu.some(function (b) { return a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h; });
    };
    svg.querySelectorAll(".kume-ad, .span-ad, .alan-ad, .nokta-ad").forEach(function (t) {
      if (t.style.visibility === "hidden" || !t.textContent) return;
      const b = kutu(t); if (b) dolu.push(b);
    });
    for (const id in this.vecs) {
      const o = this.vecs[id], t = o.text;
      if (!t || !t.textContent || t.style.visibility === "hidden") continue;
      let b = kutu(t); if (!b) continue;
      // Önce grafik alanının içine çek (uzun etiketler kenardan taşmasın).
      let dx = 0, dy = 0;
      const sinir = PAD + 2; // etiket katmanı bu çerçeveye kırpılır
      if (b.x + b.w > W - sinir) dx = (W - sinir) - (b.x + b.w);
      if (b.x + dx < sinir) dx = sinir - b.x;
      if (b.y + b.h > H - sinir) dy = (H - sinir) - (b.y + b.h);
      if (b.y + dy < sinir) dy = sinir - b.y;
      if (dx || dy) {
        t.setAttribute("x", parseFloat(t.getAttribute("x")) + dx);
        t.setAttribute("y", parseFloat(t.getAttribute("y")) + dy);
        b = kutu(t) || b;
      }
      const x0 = parseFloat(t.getAttribute("x")), y0 = parseFloat(t.getAttribute("y"));
      const nx = o.nx || 0, ny = o.ny || -1;
      // Önce okun kendi tarafına, olmazsa karşı tarafa doğru dene.
      const denemeler = [];
      for (let k = 1; k <= 6; k++) { denemeler.push(k * 9); denemeler.push(-k * 9 - 14); }
      for (let i = 0; i < denemeler.length && carpisir(b); i++) {
        const d = denemeler[i];
        t.setAttribute("x", x0 + nx * d); t.setAttribute("y", y0 + ny * d);
        b = kutu(t) || b;
      }
      if (carpisir(b)) { t.setAttribute("x", x0); t.setAttribute("y", y0); b = kutu(t) || b; }
      dolu.push(b);
    }
  };

  Sahne.prototype._vekTur = function (o, kind) {
    o.kind = kind;
    o.g.setAttribute("class", "vek k-" + kind);
    if (o.tg) o.tg.setAttribute("class", "vek k-" + kind);
    o.line.setAttribute("marker-end", "url(#" + this.on + "-ok-" + kind + ")");
  };

  Sahne.prototype._oklar = function (liste, dur) {
    const self = this, yeni = {};
    (liste || []).forEach(function (v, i) {
      const id = v.id || ("v" + i);
      const hedef = self._vekGeom(v);
      let o = self.vecs[id];
      if (!o) {
        const g = el("g", {}, self.gVec);
        const tg = el("g", {}, self.gEtk);
        o = { g: g, tg: tg, line: el("line", {}, g), text: el("text", { "class": "vek-ad" }, tg) };
        o.cur = { fx: hedef.fx, fy: hedef.fy, tx: hedef.fx, ty: hedef.fy }; // başlangıçtan uzayarak çık
      } else {
        delete self.vecs[id];
      }
      self._vekTur(o, v.kind || "giris");
      o.offset = !!v.offset;
      o.text.textContent = v.label || "";
      const bas = { fx: o.cur.fx, fy: o.cur.fy, tx: o.cur.tx, ty: o.cur.ty };
      self._tween("v:" + id, dur, function (t) {
        o.cur = {
          fx: lerp(bas.fx, hedef.fx, t), fy: lerp(bas.fy, hedef.fy, t),
          tx: lerp(bas.tx, hedef.tx, t), ty: lerp(bas.ty, hedef.ty, t)
        };
        self._vekCiz(o);
      });
      yeni[id] = o;
    });
    for (const id in this.vecs) {
      const o = this.vecs[id];
      this.anims = this.anims.filter(function (a) { return a.key !== "v:" + id; });
      soldurVeSil(o.g, dur * 0.6);
      if (o.tg) soldurVeSil(o.tg, dur * 0.6);
    }
    this.vecs = yeni;
  };

  // --- Noktalar ------------------------------------------------------------
  Sahne.prototype._noktalar = function (liste, dur) {
    const self = this, yeni = {}, m = this.m;
    (liste || []).forEach(function (p, i) {
      const id = p.id || ("p" + i);
      const at = P(p.at);
      let o = self.pts[id];
      if (!o) {
        const g = el("g", {}, self.gPt);
        o = { g: g, halka: el("circle", { r: 10, "class": "halka" }, g), dot: el("circle", { r: 5.5, "class": "nokta" }, g),
              text: el("text", { "class": "nokta-ad" }, g), cur: at.slice() };
        if (dur > 0) belir(g, dur, true);
      } else {
        delete self.pts[id];
      }
      o.g.setAttribute("class", "nok k-" + (p.kind || "nokta"));
      o.text.textContent = p.label || "";
      const bas = o.cur.slice();
      self._tween("p:" + id, dur, function (t) {
        o.cur = [lerp(bas[0], at[0], t), lerp(bas[1], at[1], t)];
        const x = m.px(o.cur[0]), y = m.py(o.cur[1]);
        o.halka.setAttribute("cx", x); o.halka.setAttribute("cy", y);
        o.dot.setAttribute("cx", x); o.dot.setAttribute("cy", y);
        const sag = x < W - 120;
        o.text.setAttribute("x", sag ? x + 13 : x - 13);
        o.text.setAttribute("text-anchor", sag ? "start" : "end");
        o.text.setAttribute("y", y > PAD + 20 ? y - 10 : y + 20);
      });
      yeni[id] = o;
    });
    for (const id in this.pts) soldurVeSil(this.pts[id].g, dur * 0.6);
    this.pts = yeni;
  };

  // --- Çokgenler (paralelkenar alanı, kuvvet çokgeni) ----------------------
  Sahne.prototype._cokgenler = function (liste, dur) {
    const self = this, yeni = {}, m = this.m;
    function yol(pts) {
      return pts.map(function (p, i) { return (i ? "L" : "M") + m.px(p[0]) + "," + m.py(p[1]); }).join(" ") + " Z";
    }
    (liste || []).forEach(function (pg, i) {
      const id = pg.id || ("pg" + i);
      const pts = pg.pts.map(P);
      let o = self.polys[id];
      if (o && o.cur.length !== pts.length) { soldurVeSil(o.g, 0); o = null; delete self.polys[id]; }
      if (!o) {
        const g = el("g", {}, self.gPoly);
        o = { g: g, path: el("path", {}, g), text: el("text", { "class": "alan-ad", "text-anchor": "middle" }, g), cur: pts.map(function (p) { return p.slice(); }) };
        if (dur > 0) belir(g, dur);
      } else {
        delete self.polys[id];
      }
      o.g.setAttribute("class", "cokgen k-" + (pg.kind || "alan"));
      o.text.textContent = pg.label || "";
      const bas = o.cur.map(function (p) { return p.slice(); });
      self._tween("g:" + id, dur, function (t) {
        o.cur = bas.map(function (b, j) { return [lerp(b[0], pts[j][0], t), lerp(b[1], pts[j][1], t)]; });
        o.path.setAttribute("d", yol(o.cur));
        let cx = 0, cy = 0;
        o.cur.forEach(function (p) { cx += p[0]; cy += p[1]; });
        o.text.setAttribute("x", m.px(cx / o.cur.length));
        o.text.setAttribute("y", m.py(cy / o.cur.length) + 4);
      });
      yeni[id] = o;
    });
    for (const id in this.polys) soldurVeSil(this.polys[id].g, dur * 0.6);
    this.polys = yeni;
  };

  // --- Tarama (seçili katsayı aralığı) -------------------------------------
  Sahne.prototype._tarama = function (sw, dur) {
    const key = sw ? JSON.stringify(sw.points) : null;
    if (key === this.taraKey) return;
    this.taraKey = key;
    const eski = Array.prototype.slice.call(this.gTara.childNodes);
    eski.forEach(function (n) { soldurVeSil(n, dur * 0.5); });
    if (!sw) return;
    const g = el("g", { "class": "tarama" }, this.gTara), m = this.m;
    const n = sw.points.length;
    const toplam = Math.min(1600, 18 * n + 300);
    sw.points.forEach(function (p, i) {
      const q = P(p);
      const c = el("circle", { cx: m.px(q[0]), cy: m.py(q[1]), r: 2.6, "class": "tarama-nokta" }, g);
      if (dur > 0 && c.animate) {
        c.style.opacity = 0;
        c.animate([{ opacity: 0, transform: "scale(0.2)" }, { opacity: 1, transform: "scale(1)" }],
          { duration: 260, delay: (i / Math.max(1, n)) * toplam, fill: "forwards", easing: "ease-out" });
      }
    });
    if (sw.label) {
      el("text", { x: PAD + 6, y: H - PAD - 6, "class": "tarama-ad" }, g).textContent = "• " + sw.label + " (seçili katsayı aralığı)";
    }
  };

  Sahne.prototype._odak = function (ids) {
    const self = this;
    ["vecs", "pts"].forEach(function (k) {
      for (const id in self[k]) self[k][id].g.classList.remove("odak");
    });
    (ids || []).forEach(function (id) {
      const o = self.vecs[id] || self.pts[id];
      if (o) {
        o.g.classList.remove("odak");
        void o.g.getBBox; // yeniden tetikle
        setTimeout(function () { o.g.classList.add("odak"); }, 20);
      }
    });
  };

  /** Sahneyi göster. sc: sunucu sahnesi, range: eksen yarıçapı. */
  Sahne.prototype.show = function (sc, range, secenek) {
    secenek = secenek || {};
    sc = sc || {};
    let dur = secenek.animate === false || hareketAzalt() ? 0 : (secenek.dur || SURE);
    range = Math.max(2, Math.round(range || kapsam(sc)));
    if (range !== this.range) {
      this.range = range;
      this.m = mapping(range);
      this._sifirla();
      this._eksenler();
    }
    this._arkaPlan(sc, dur);
    this._tarama(sc.sweep || null, dur);
    this._cokgenler(sc.polygons, dur);
    this._oklar(sc.vectors, dur);
    this._noktalar(sc.points, dur);
    this._odak(sc.focus);
  };

  function kapsam(sc) {
    let mx = 1;
    function g(p) { if (p) { const q = P(p); mx = Math.max(mx, Math.abs(q[0]), Math.abs(q[1])); } }
    (sc.vectors || []).forEach(function (v) { g(v.to); g(v.from); });
    (sc.points || []).forEach(function (p) { g(p.at); });
    (sc.polygons || []).forEach(function (pg) { pg.pts.forEach(g); });
    return Math.min(12, Math.max(3, Math.ceil(mx + 0.75)));
  }

  function soldurVeSil(node, dur) {
    if (!node || !node.parentNode) return;
    if (dur > 0 && node.animate) {
      const a = node.animate([{ opacity: getComputedStyle(node).opacity || 1 }, { opacity: 0 }], { duration: dur, fill: "forwards" });
      a.onfinish = function () { if (node.parentNode) node.parentNode.removeChild(node); };
    } else {
      node.parentNode.removeChild(node);
    }
  }
  function belir(node, dur, buyu) {
    if (!node.animate) return;
    node.animate(buyu
      ? [{ opacity: 0 }, { opacity: 1 }]
      : [{ opacity: 0 }, { opacity: 1 }], { duration: dur, easing: "ease-out" });
  }
  function cizerekUzat(line, dur) {
    if (!(dur > 0) || !line.animate) return;
    const L = Math.hypot(line.x2.baseVal.value - line.x1.baseVal.value, line.y2.baseVal.value - line.y1.baseVal.value);
    const kesik = getComputedStyle(line).strokeDasharray;
    if (kesik && kesik !== "none") {
      line.animate([{ opacity: 0 }, { opacity: 1 }], { duration: dur });
      return;
    }
    line.style.strokeDasharray = L + " " + L;
    const a = line.animate([{ strokeDashoffset: L }, { strokeDashoffset: 0 }], { duration: dur, easing: "ease-out", fill: "forwards" });
    a.onfinish = function () { line.style.strokeDasharray = ""; };
  }

  function sahneAl(svg) {
    if (!svg._sahne) svg._sahne = new Sahne(svg);
    return svg._sahne;
  }

  // ======================================================================
  // Eski arayüz (laboratuvarlar için): draw / drawSet
  // ======================================================================
  function draw(svg, vectors, secenek) {
    const sc = { vectors: vectors.map(function (v, i) {
      const o = { id: v.id || ("v" + i), to: [String(v.x), String(v.y)], label: v.label, kind: v.kind };
      if (v.from) o.from = v.from;
      if (v.offset) o.offset = true;
      return o;
    }) };
    sahneAl(svg).show(sc, null, secenek || { dur: 300 });
  }

  function drawSet(svg, opts, secenek) {
    opts = opts || {};
    const sc = {};
    if (opts.line) sc.set = { type: "line", m: opts.line.m, b: opts.line.b };
    if (opts.region === "all") sc.plane = true;
    else if (opts.region) sc.set = { type: "region", region: opts.region };
    if (opts.spanLine) sc.spanLines = [{ id: "sl", dir: opts.spanLine, label: "" }];
    sc.vectors = [];
    (opts.samples || []).forEach(function (s, i) {
      sc.vectors.push({ id: "s" + i, to: s, label: "(" + s[0] + ", " + s[1] + ")", kind: "giris" });
    });
    (opts.vectors || []).forEach(function (v, i) {
      const o = { id: v.id || ("x" + i), to: [String(v.x), String(v.y)], label: v.label, kind: v.kind };
      if (v.from) o.from = v.from;
      sc.vectors.push(o);
    });
    if (opts.point) sc.points = [{ id: "pt", at: [String(opts.point.x), String(opts.point.y)], label: "(0, 0)", kind: opts.point.in ? "icerde" : "disarda" }];
    const r = opts.range || Math.max(3, kapsam(sc));
    sahneAl(svg).show(sc, r, secenek || { dur: 280 });
  }

  // ======================================================================
  // Dalga grafiği: y(t) = a·cos t + b·sin t   (fazör laboratuvarı)
  // ======================================================================
  function dalga(svg, egriler) {
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    const GW = 560, GH = 260, sol = 34, sag = 10, ust = 14, alt = 26;
    svg.setAttribute("viewBox", "0 0 " + GW + " " + GH);
    let R = 1;
    egriler.forEach(function (c) { R = Math.max(R, Math.hypot(c.a, c.b)); });
    R = Math.ceil(R + 0.2);
    const T = 4 * Math.PI;
    const px = function (t) { return sol + (t / T) * (GW - sol - sag); };
    const py = function (y) { return ust + (1 - (y + R) / (2 * R)) * (GH - ust - alt); };
    for (let k = 1; k <= 4; k++) {
      el("line", { x1: px(k * Math.PI), y1: ust, x2: px(k * Math.PI), y2: GH - alt, "class": "izgara" }, svg);
      el("text", { x: px(k * Math.PI), y: GH - 8, "class": "eksen-sayi", "text-anchor": "middle" }, svg).textContent = (k === 1 ? "" : k) + "π";
    }
    for (let y = -R; y <= R; y++) {
      if (y === 0) continue;
      el("line", { x1: sol, y1: py(y), x2: GW - sag, y2: py(y), "class": "izgara" }, svg);
      el("text", { x: sol - 5, y: py(y) + 3, "class": "eksen-sayi", "text-anchor": "end" }, svg).textContent = String(y).replace("-", "−");
    }
    el("line", { x1: sol, y1: py(0), x2: GW - sag, y2: py(0), "class": "eksen" }, svg);
    el("line", { x1: sol, y1: ust, x2: sol, y2: GH - alt, "class": "eksen" }, svg);
    el("text", { x: GW - sag, y: py(0) - 5, "class": "eksen-ad", "text-anchor": "end" }, svg).textContent = "t";
    egriler.forEach(function (c) {
      let d = "";
      for (let i = 0; i <= 240; i++) {
        const t = (i / 240) * T;
        d += (i ? "L" : "M") + px(t).toFixed(1) + "," + py(c.a * Math.cos(t) + c.b * Math.sin(t)).toFixed(1);
      }
      el("path", { d: d, "class": "dalga " + c.cls }, svg);
      if (c.label) {
        const t0 = c.labelT || 0.35;
        el("text", { x: px(t0) + 4, y: py(c.a * Math.cos(t0) + c.b * Math.sin(t0)) - 6, "class": "dalga-ad " + c.cls }, svg).textContent = c.label;
      }
    });
  }

  global.Diagrams = { Sahne: Sahne, sahneAl: sahneAl, draw: draw, drawSet: drawSet, dalga: dalga, toNum: toNum };
})(window);
