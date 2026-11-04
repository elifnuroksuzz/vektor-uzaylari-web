/* Vektör Uzayları — tarayıcı kontrol katmanı.
 * Bütün matematik kararları sunucudan (POST /api/...) gelir; burada yalnızca
 * istek, animasyon ve görüntüleme yapılır. */
(function () {
  "use strict";

  const VU = window.VU, h = VU.h, api = VU.api;
  const fracEl = VU.fracEl, vektorYaz = VU.vektorYaz;
  let icerik = null;

  // --- Sekmeler ------------------------------------------------------------
  const paneller = {};
  ["giris", "kurallar", "altuzaylar", "germe", "bagimsizlik", "kendi", "sorular"].forEach(function (k) {
    paneller[k] = document.getElementById("panel-" + k);
  });
  const oynaticilar = {};
  const ilkDers = { kurallar: "V1", altuzaylar: "S_y2x", germe: "G_kur", bagimsizlik: "B_cokgen" };

  document.getElementById("tabs").addEventListener("click", function (e) {
    const t = e.target.closest(".tab");
    if (t) sekmeSec(t.dataset.tab);
  });
  function sekmeSec(ad) {
    document.querySelectorAll(".tab").forEach(function (b) {
      const secili = b.dataset.tab === ad;
      b.setAttribute("aria-selected", secili ? "true" : "false");
      if (secili && b.scrollIntoView) b.scrollIntoView({ block: "nearest", inline: "nearest" });
    });
    for (const k in paneller) paneller[k].hidden = (k !== ad);
    document.body.dataset.bolum = ad;
    if (ad === "giris") ilerlemeGuncelle();
    if (ilkDers[ad]) {
      const o = oynaticiAl(ad);
      if (!o.ders) dersAc(ad, ilkDers[ad], false);
      else VU.aktifOynatici = o;
    }
    if (history.replaceState) history.replaceState(null, "", "#" + ad);
  }

  // --- Tamamlanan dersler ve başlangıç sayfası ----------------------------
  const DERS_SEKMELERI = ["kurallar", "altuzaylar", "germe", "bagimsizlik"];
  const bitenler = new Set();
  try { JSON.parse(localStorage.getItem("vu-bitenler") || "[]").forEach(function (x) { bitenler.add(x); }); }
  catch (e) { /* depolama kapalıysa ilerleme yalnızca bu oturumda tutulur */ }

  document.addEventListener("vu:ders-bitti", function (e) {
    const id = e.detail && e.detail.id;
    if (!id || bitenler.has(id)) return;
    bitenler.add(id);
    try { localStorage.setItem("vu-bitenler", JSON.stringify(Array.from(bitenler))); } catch (err) { /* yok say */ }
    document.querySelectorAll('.menu-oge[data-ders="' + id + '"]').forEach(function (b) {
      b.classList.add("bitti", "yeni-bitti");
    });
    ilerlemeGuncelle();
  });

  function ilerlemeGuncelle() {
    if (!icerik) return;
    let toplamHepsi = 0, bitenHepsi = 0, ilkEksik = null;
    DERS_SEKMELERI.forEach(function (sekme) {
      const dersler = icerik.lesson_catalog.filter(function (d) { return d.tab === sekme; });
      const biten = dersler.filter(function (d) { return bitenler.has(d.id); }).length;
      toplamHepsi += dersler.length; bitenHepsi += biten;
      if (ilkEksik === null && biten < dersler.length) ilkEksik = sekme;
      const kart = document.querySelector('.yol-kart[data-bolum="' + sekme + '"]');
      if (!kart) return;
      const oran = dersler.length ? biten / dersler.length : 0;
      kart.querySelector(".yol-dolgu").style.width = (oran * 100) + "%";
      kart.querySelector(".yol-sayi").textContent = biten + " / " + dersler.length + " ders";
      kart.classList.toggle("tamam", dersler.length > 0 && biten === dersler.length);
      kart.querySelector("button").textContent = biten === 0 ? "Başla" : (biten === dersler.length ? "Tekrar et" : "Devam et");
    });
    const basla = document.getElementById("hero-basla");
    const yazi = document.getElementById("hero-ilerleme");
    if (basla) {
      basla.dataset.git = ilkEksik || "kurallar";
      basla.textContent = bitenHepsi === 0 ? "Baştan başla →" : (ilkEksik ? "Kaldığın yerden devam et →" : "Baştan tekrar et →");
    }
    if (yazi) {
      yazi.hidden = bitenHepsi === 0;
      yazi.textContent = "Tamamlanan: " + bitenHepsi + " / " + toplamHepsi + " ders";
    }
  }

  document.addEventListener("click", function (e) {
    const g = e.target.closest && e.target.closest("[data-git]");
    if (!g || !paneller[g.dataset.git]) return;
    sekmeSec(g.dataset.git);
    window.scrollTo({ top: 0, behavior: "smooth" });
  });

  function oynaticiAl(sekme) {
    if (!oynaticilar[sekme]) oynaticilar[sekme] = new window.Oynatici(document.getElementById(sekme + "-oyn"));
    return oynaticilar[sekme];
  }

  function dersAc(sekme, dersId, kaydir, secenek) {
    const o = oynaticiAl(sekme);
    secenek = secenek || {};
    secenek.kaydir = kaydir;
    o.yukle(dersId, secenek);
    document.querySelectorAll("#" + sekme + "-menu [data-ders]").forEach(function (b) {
      if (b.dataset.ders === dersId) b.setAttribute("aria-current", "true");
      else b.removeAttribute("aria-current");
    });
  }

  // --- Sol ders menüsü (gruplu) ----------------------------------------------
  function turSinif(rozet) {
    rozet = rozet || "";
    if (/Karşı|✗/.test(rozet)) return "karsi";
    if (/Mühendislik/.test(rozet)) return "muh";
    return "ispat";
  }
  function menuKur(sekme) {
    const nav = document.getElementById(sekme + "-menu");
    nav.innerHTML = "";
    const formuller = {};
    icerik.axioms.cards.forEach(function (c) { formuller[c.id] = c.formula.replace(/-/g, "−"); });
    const gruplar = {}, sira = [];
    icerik.lesson_catalog.forEach(function (d) {
      if (d.tab !== sekme) return;
      if (!gruplar[d.group]) { gruplar[d.group] = []; sira.push(d.group); }
      gruplar[d.group].push(d);
    });
    sira.forEach(function (g) {
      const blok = h("div", "menu-blok" + (gruplar[g].length > 4 ? " genis" : ""));
      blok.appendChild(h("div", "menu-grup", g));
      const ul = h("ul", "menu-liste");
      gruplar[g].forEach(function (d) {
        const li = h("li");
        const b = h("button", "menu-oge m-" + turSinif(d.badge));
        b.type = "button";
        b.dataset.ders = d.id;
        if (bitenler.has(d.id)) b.classList.add("bitti");
        // "V1 — Toplamada birleşme" → küçük etiket + ana metin
        const parca = d.title.split(" — ");
        const ust = parca.length > 1 ? parca[0] : "";
        const ana = parca.length > 1 ? parca.slice(1).join(" — ") : d.title;
        if (ust) b.appendChild(h("span", "menu-ust", ust));
        b.appendChild(h("span", "menu-ana", ana));
        if (formuller[d.id]) b.appendChild(h("span", "menu-alt", formuller[d.id]));
        b.addEventListener("click", function () { dersAc(sekme, d.id, true); });
        li.appendChild(b);
        ul.appendChild(li);
      });
      blok.appendChild(ul);
      nav.appendChild(blok);
    });
  }

  function kurallariKur() { menuKur("kurallar"); }

  // ======================================================================
  // 4.1.1 ALT UZAYLAR — karşılaştırma tablosu
  // ======================================================================
  function altUzaylariKur() {
    menuKur("altuzaylar");
    const kbtn = document.getElementById("altuzay-karsilastir");
    kbtn.addEventListener("click", function () {
      const t = document.getElementById("altuzay-tablo");
      const acik = t.hidden;
      t.hidden = !acik;
      kbtn.setAttribute("aria-expanded", acik ? "true" : "false");
      if (acik) karsilastirmaCiz();
    });
  }
  function karsilastirmaCiz() {
    const t = document.getElementById("altuzay-tablo");
    t.innerHTML = "";
    const tablo = h("table", "kosul-tablo karsilastirma");
    const bas = h("tr");
    ["Küme", "Sıfır vektörü", "Toplamaya kapalı", "Skalerle çarpmaya kapalı", "Alt uzay"].forEach(function (x) { bas.appendChild(h("th", null, x)); });
    const thead = h("thead"); thead.appendChild(bas); tablo.appendChild(thead);
    const tb = h("tbody");
    icerik.lessons.subspace.examples.forEach(function (e) {
      const tr = h("tr");
      tr.appendChild(h("td", null, e.label));
      [e.checks.zero.holds, e.checks.add.holds, e.checks.scalar.holds, e.is_subspace].forEach(function (v, i) {
        const td = h("td");
        td.appendChild(h(i === 3 ? "strong" : "span", v ? "esit-ok" : "esit-hata", v ? "✓ Evet" : "✗ Hayır"));
        tr.appendChild(td);
      });
      tb.appendChild(tr);
    });
    tablo.appendChild(tb);
    t.appendChild(tablo);
    t.appendChild(h("p", "not", "“Evet” hücreleri genel cebirle, “Hayır” hücreleri tek bir karşı örnekle gösterilir (derslere bak)."));
  }

  // ======================================================================
  // 4.1.2 DOĞRUSAL GERME — sürgü laboratuvarı
  // ======================================================================
  function germeyiKur() {
    menuKur("germe");
    const g = icerik.lessons.span;
    document.getElementById("germe-span-not").textContent = g.linear_combo_note;
    const sec = document.getElementById("germe-secici");
    sec.innerHTML = "";
    g.examples.forEach(function (ex) {
      const b = h("button", "dugme ikincil", ex.label);
      b.type = "button";
      b.setAttribute("aria-pressed", "false");
      b.addEventListener("click", function () { germeOrnekSec(ex); });
      sec.appendChild(b);
    });
    ["v1x", "v1y", "v2x", "v2y", "alfa", "beta"].forEach(function (id) {
      document.getElementById(id).addEventListener("input", germeGuncelle);
    });
    document.getElementById("hedef-dene").addEventListener("click", germeUyelik);
    document.getElementById("germe-animasyon").addEventListener("click", function () {
      const tek = document.getElementById("beta-satir").style.display === "none";
      dersAc("germe", "G_kur", true, { params: {
        v1: [val("v1x"), val("v1y")],
        v2: tek ? ["0", "0"] : [val("v2x"), val("v2y")],
        al: val("alfa"), be: tek ? "0" : val("beta")
      } });
    });
    germeOrnekSec(g.examples.filter(function (e) { return e.id === "duzlem"; })[0] || g.examples[0]);
    fazorKur();
  }
  function val(id) { return document.getElementById(id).value.trim(); }

  function germeOrnekSec(ex) {
    document.getElementById("v1x").value = ex.v1[0];
    document.getElementById("v1y").value = ex.v1[1];
    document.getElementById("v2x").value = ex.v2[0];
    document.getElementById("v2y").value = ex.v2[1];
    document.querySelectorAll("#germe-secici .dugme").forEach(function (b) {
      b.setAttribute("aria-pressed", b.textContent === ex.label ? "true" : "false");
    });
    document.getElementById("germe-ornek-aciklama").textContent = ex.description || "";
    const tek = !!ex.single;
    document.getElementById("v2-satir").style.display = tek ? "none" : "";
    document.getElementById("beta-satir").style.display = tek ? "none" : "";
    if (tek) document.getElementById("beta").value = "0";
    germeGuncelle();
  }

  let germeZaman = null, germeToken = 0;
  function germeGuncelle() {
    document.getElementById("alfa-deger").textContent = val("alfa").replace("-", "−");
    document.getElementById("beta-deger").textContent = val("beta").replace("-", "−");
    clearTimeout(germeZaman);
    germeZaman = setTimeout(germeHesapla, 90);
  }
  async function germeHesapla() {
    const token = ++germeToken;
    const v1 = [val("v1x"), val("v1y")], v2 = [val("v2x"), val("v2y")];
    const a = val("alfa"), b = val("beta");
    let res;
    try { res = await api("/api/combination", { vectors: [v1, v2], coeffs: [a, b] }); }
    catch (e) { return; }
    if (token !== germeToken) return;
    VU.hataTemizle();
    const tek = document.getElementById("beta-satir").style.display === "none";
    const sonuc = document.getElementById("germe-sonuc");
    sonuc.innerHTML = "";
    sonuc.appendChild(document.createTextNode(tek ? ("w = " + a + "·v₁ = ") : ("w = " + a + "·v₁ + " + b + "·v₂ = ")));
    sonuc.appendChild(vektorYaz(res.result));
    document.getElementById("germe-formul").textContent = tek
      ? ("Genel: w = α·v₁. Seçili α = " + a + " → w = (" + res.result.join(", ") + "). Bütün α değerleri span’i verir.")
      : ("Genel: w = α·v₁ + β·v₂. Seçili α = " + a + ", β = " + b + " → w = (" + res.result.join(", ") + "). Bütün (α, β) çiftleri span’i verir.");
    const rankMetin = { 2: "Rank 2 → span bütün ℝ² (det ≠ 0).", 1: "Rank 1 → span orijinden geçen bir doğru.", 0: "Rank 0 → span yalnızca orijin." };
    document.getElementById("germe-rank").textContent = rankMetin[res.rank] || "";

    const N = window.Diagrams.toNum;
    const R = 3 * Math.max(Math.abs(N(v1[0])) + Math.abs(N(v2[0])), Math.abs(N(v1[1])) + Math.abs(N(v2[1])));
    const o = { range: Math.max(3, Math.min(12, Math.ceil(R + 0.5))) };
    if (res.rank === 1) {
      const yon = (window.Diagrams.toNum(v1[0]) !== 0 || window.Diagrams.toNum(v1[1]) !== 0) ? v1 : v2;
      o.spanLine = [yon[0], yon[1]];
    } else if (res.rank === 2) {
      o.region = "all";
    }
    const st = res.steps;
    o.vectors = [{ id: "a", x: st[0].scaled[0], y: st[0].scaled[1], label: "αv₁", kind: "giris" }];
    if (!tek) o.vectors.push({ id: "b", x: res.result[0], y: res.result[1], from: st[0].scaled, label: "βv₂", kind: "giris2" });
    o.vectors.push({ id: "w", x: res.result[0], y: res.result[1], label: "w", kind: "sonuc" });
    window.Diagrams.drawSet(document.getElementById("germe-svg"), o, { dur: 220 });
  }
  async function germeUyelik() {
    const hx = val("hx"), hy = val("hy");
    const el = document.getElementById("uyelik-sonuc");
    if (hx === "" || hy === "") { el.textContent = "Önce hedefin iki bileşenini yazın."; return; }
    let res;
    try { res = await api("/api/span", { vectors: [[val("v1x"), val("v1y")], [val("v2x"), val("v2y")]], target: [hx, hy], symbols: ["x", "y"] }); }
    catch (e) { return; }
    el.innerHTML = "";
    const m = res.membership;
    if (m.status === "inconsistent") {
      el.appendChild(h("span", "esit-hata", "Hayır"));
      el.appendChild(document.createTextNode(" — hedef span dışında (çelişki satırı: 0 = sıfırdan farklı). " +
        (res.homogeneous_conditions.conditions.length ? "Span koşulu: " + res.homogeneous_conditions.conditions.join(", ") : "")));
    } else {
      el.appendChild(h("span", "esit-ok", "Evet"));
      el.appendChild(document.createTextNode(m.status === "unique" ? " — tek temsil, katsayılar: " : " — sonsuz temsil; biri (serbest = 0): "));
      el.appendChild(vektorYaz(m.coefficients || m.particular));
    }
  }

  // --- Fazör / süperpozisyon laboratuvarı ----------------------------------
  let fazorZaman = null, fazorToken = 0;
  function fazorKur() {
    ["fa1", "fb1", "fa2", "fb2"].forEach(function (id) {
      document.getElementById(id).addEventListener("input", function () {
        document.getElementById(id + "-d").textContent = val(id).replace("-", "−");
        clearTimeout(fazorZaman);
        fazorZaman = setTimeout(fazorHesapla, 60);
      });
    });
    document.getElementById("fazor-lab").addEventListener("toggle", fazorHesapla);
    fazorHesapla();
  }
  async function fazorHesapla() {
    const token = ++fazorToken;
    const p1 = [val("fa1"), val("fb1")], p2 = [val("fa2"), val("fb2")];
    let res;
    try { res = await api("/api/combination", { vectors: [p1, p2], coeffs: ["1", "1"] }); }
    catch (e) { return; }
    if (token !== fazorToken) return;
    const s = res.result, N = window.Diagrams.toNum;
    window.Diagrams.draw(document.getElementById("fazor-svg"), [
      { id: "p1", x: p1[0], y: p1[1], label: "y₁", kind: "giris" },
      { id: "p2", x: s[0], y: s[1], from: p1, label: "y₂", kind: "giris2" },
      { id: "s", x: s[0], y: s[1], label: "y₁+y₂", kind: "sonuc" }
    ], { dur: 200 });
    window.Diagrams.dalga(document.getElementById("dalga-svg"), [
      { a: N(p1[0]), b: N(p1[1]), cls: "c-y1", label: "y₁", labelT: 0.2 },
      { a: N(p2[0]), b: N(p2[1]), cls: "c-y2", label: "y₂", labelT: 1.9 },
      { a: N(s[0]), b: N(s[1]), cls: "c-top", label: "y₁ + y₂", labelT: 3.6 }
    ]);
    const kutu = document.getElementById("fazor-sonuc");
    kutu.innerHTML = "";
    function satir(ad, v) {
      const p = h("p");
      p.appendChild(h("strong", null, ad + ": "));
      p.appendChild(document.createTextNode(fmt(v[0]) + "·cos t " + isaretli(v[1]) + "·sin t   ↔   fazör "));
      p.appendChild(vektorYaz(v));
      const R = Math.hypot(N(v[0]), N(v[1]));
      p.appendChild(document.createTextNode("   · genlik R = √(a² + b²) ≈ " + R.toFixed(3)));
      kutu.appendChild(p);
    }
    satir("y₁", p1); satir("y₂", p2); satir("y₁ + y₂", s);
    kutu.appendChild(h("p", "not", "Toplam sinyalin katsayıları, fazörlerin vektör toplamıdır (sunucuda kesin hesaplandı). Genlik a cos t + b sin t = R cos(t − φ) yazımındaki R’dir (ondalık yaklaşık)."));
  }
  function fmt(x) { return String(x).replace("-", "−"); }
  function isaretli(x) { x = String(x); return x.charAt(0) === "-" ? "− " + x.slice(1) : "+ " + x; }

  // ======================================================================
  // 4.2 BAĞIMSIZLIK
  // ======================================================================
  function bagimsizligiKur() { menuKur("bagimsizlik"); }

  // ======================================================================
  // KENDİ VEKTÖRLERİN (genel m×n)
  // ======================================================================
  let kendiM = 3, kendiN = 2;
  function clampInt(v, lo, hi) { v = parseInt(v, 10); if (isNaN(v)) v = lo; return Math.max(lo, Math.min(hi, v)); }
  function symbolsFor(m) {
    const harf = ["x", "y", "z", "t", "u", "v", "w", "s"];
    if (m <= harf.length) return harf.slice(0, m);
    const arr = []; for (let i = 1; i <= m; i++) arr.push("x" + i); return arr;
  }

  function kendiKur() {
    document.getElementById("kendi-olustur").addEventListener("click", kendiTabloOlustur);
    document.getElementById("kendi-span-btn").addEventListener("click", kendiSpanIncele);
    document.getElementById("kendi-bag-btn").addEventListener("click", kendiBagimsizlik);
    document.getElementById("kendi-hedef-btn").addEventListener("click", function () {
      const a = document.getElementById("kendi-hedef-alan"); a.hidden = !a.hidden;
    });
    document.getElementById("kendi-hedef-hesapla").addEventListener("click", kendiHedefHesapla);
    kendiTabloOlustur();
  }

  function kendiTabloOlustur() {
    const m = clampInt(val("kendi-m"), 1, 8), n = clampInt(val("kendi-n"), 1, 8);
    kendiM = m; kendiN = n;
    document.getElementById("kendi-m").value = m;
    document.getElementById("kendi-n").value = n;
    const ornek = (m === 3 && n === 2) ? [["1", "0", "1"], ["0", "1", "1"]] : null;
    const t = h("table", "matris kendi-tablo");
    const baslik = h("tr");
    baslik.appendChild(h("td"));
    for (let j = 0; j < n; j++) baslik.appendChild(h("td", "kafa", "v" + (j + 1)));
    t.appendChild(baslik);
    for (let i = 0; i < m; i++) {
      const tr = h("tr");
      tr.appendChild(h("td", "kafa", (i + 1) + ". bileşen"));
      for (let j = 0; j < n; j++) {
        const td = h("td"), inp = h("input");
        inp.inputMode = "decimal"; inp.id = "k-c-" + i + "-" + j;
        inp.setAttribute("aria-label", "v" + (j + 1) + " " + (i + 1) + ". bileşen");
        inp.value = ornek ? ornek[j][i] : "0";
        td.appendChild(inp); tr.appendChild(td);
      }
      t.appendChild(tr);
    }
    const alan = document.getElementById("kendi-tablo-alan");
    alan.innerHTML = "";
    const sarma = h("div", "matris-sarma"); sarma.appendChild(t); alan.appendChild(sarma);
    const hg = document.getElementById("kendi-hedef-girdi");
    hg.innerHTML = ""; hg.appendChild(document.createTextNode("("));
    for (let i = 0; i < m; i++) {
      if (i) hg.appendChild(document.createTextNode(", "));
      const inp = h("input"); inp.inputMode = "decimal"; inp.id = "k-h-" + i; inp.value = "0";
      inp.setAttribute("aria-label", "hedef " + (i + 1) + ". bileşen");
      hg.appendChild(inp);
    }
    hg.appendChild(document.createTextNode(")"));
    document.getElementById("kendi-islem").hidden = false;
    document.getElementById("kendi-hedef-alan").hidden = true;
    document.getElementById("kendi-adim-det").hidden = true;
    const s = document.getElementById("kendi-sonuc"); s.innerHTML = "";
    s.appendChild(h("p", "gerekce", "Bir işlem seçin."));
    document.getElementById("kendi-svg").style.display = "none";
    document.getElementById("kendi-grafik-not").style.display = "none";
  }
  function kendiReadVectors() {
    const vs = [];
    for (let j = 0; j < kendiN; j++) {
      const v = [];
      for (let i = 0; i < kendiM; i++) v.push(val("k-c-" + i + "-" + j));
      vs.push(v);
    }
    return vs;
  }
  function kendiReadTarget() { const t = []; for (let i = 0; i < kendiM; i++) t.push(val("k-h-" + i)); return t; }

  async function kendiSpanIncele() {
    const vs = kendiReadVectors();
    let res;
    try { res = await api("/api/span", { vectors: vs, symbols: symbolsFor(kendiM) }); } catch (e) { return; }
    const hc = res.homogeneous_conditions;
    const el = document.getElementById("kendi-sonuc");
    el.innerHTML = "";
    el.appendChild(h("h3", null, "Gerilen uzay"));
    const p = h("p");
    p.appendChild(h("strong", null, hc.spans_ambient
      ? "Bu vektörler ℝ" + ust(hc.ambient_dim) + "’nin tamamını gerer."
      : "ℝ" + ust(hc.ambient_dim) + "’nin tamamını germez."));
    p.appendChild(document.createTextNode(" rank = " + hc.rank + (hc.spans_ambient ? " = boyut." : " → " + hc.rank + " boyutlu bir alt uzay.")));
    el.appendChild(p);
    if (hc.conditions && hc.conditions.length) {
      el.appendChild(h("p", null, "Span’i tanımlayan homojen denklemler:"));
      hc.conditions.forEach(function (c) { el.appendChild(VU.matYaz(c, "kosul-kutu")); });
    } else if (hc.spans_ambient) {
      el.appendChild(h("p", "gerekce", "Ek koşul yok: her hedefe ulaşılabilir."));
    }
    el.appendChild(dogrulamaSatiri(hc.verification));
    renderKendiAdimlar(hc.steps);
    drawKendi(vs, null, null);
  }

  async function kendiBagimsizlik() {
    const vs = kendiReadVectors();
    let res;
    try { res = await api("/api/dependence", { vectors: vs }); } catch (e) { return; }
    const el = document.getElementById("kendi-sonuc");
    el.innerHTML = "";
    el.appendChild(h("h3", null, "Bağımsızlık ve baz"));
    bagimlilikSonucu(el, res);
    renderKendiAdimlar(res.steps);
    drawKendi(vs, null, null, res);
  }

  function bagimlilikSonucu(el, res) {
    const kutu = h("div", res.independent ? "sonuc-kutu" : "sonuc-kutu yok");
    kutu.appendChild(h("strong", null, res.independent ? "Doğrusal BAĞIMSIZ." : "Doğrusal BAĞIMLI."));
    kutu.appendChild(h("p", null, res.reason));
    if (res.relation) {
      const p = h("p");
      p.appendChild(document.createTextNode("Sıfır olmayan bir bağıntı (c₁, …, cₖ) = "));
      p.appendChild(vektorYaz(res.relation));
      p.appendChild(document.createTextNode(" :  " + res.relation.map(function (c, i) {
        return (c.charAt(0) === "-" ? "− " + c.slice(1) : (i ? "+ " : "") + c) + "·v" + (i + 1);
      }).join(" ").replace(/-/g, "−") + " = 0"));
      kutu.appendChild(p);
      if (res.relations.length > 1) kutu.appendChild(h("p", "gerekce", "Çözüm uzayının boyutu " + res.relations.length + ": birbirinden bağımsız " + res.relations.length + " bağıntı var."));
    }
    el.appendChild(kutu);
    const b = h("p");
    b.appendChild(h("strong", null, "Gerilen uzay için baz: "));
    b.appendChild(document.createTextNode("{" + res.basis_indices.map(function (i) { return "v" + (i + 1); }).join(", ") + "}  =  "));
    res.basis.forEach(function (v, i) { if (i) b.appendChild(document.createTextNode(", ")); b.appendChild(vektorYaz(v)); });
    el.appendChild(b);
    el.appendChild(h("p", "gerekce", "Boyut = rank = " + res.rank + ". Baz, indirgenmiş matristen değil, pivot sütunlarına karşılık gelen ORİJİNAL vektörlerden seçildi." +
      (res.is_basis_of_ambient ? " Bu küme ℝ" + ust(res.ambient_dim) + "’nin bir bazıdır." : "")));
  }

  async function kendiHedefHesapla() {
    const vs = kendiReadVectors(), hedef = kendiReadTarget();
    let res;
    try { res = await api("/api/span", { vectors: vs, target: hedef, symbols: symbolsFor(kendiM) }); } catch (e) { return; }
    const mem = res.membership;
    const el = document.getElementById("kendi-sonuc");
    el.innerHTML = "";
    el.appendChild(h("h3", null, "Hedef kontrolü"));
    const kutu = h("div", mem.status === "inconsistent" ? "sonuc-kutu yok" : "sonuc-kutu");
    if (mem.status === "inconsistent") kutu.appendChild(document.createTextNode("Hedef span’in DIŞINDA — çelişki satırı çıktı (0 = sıfırdan farklı)."));
    else if (mem.status === "unique") { kutu.appendChild(document.createTextNode("Hedef span’in İÇİNDE. Tek temsil, katsayılar: ")); kutu.appendChild(vektorYaz(mem.coefficients)); }
    else { kutu.appendChild(document.createTextNode("Hedef span’in İÇİNDE (sonsuz temsil). Bir temsil (serbest = 0 seçildi): ")); kutu.appendChild(vektorYaz(mem.particular)); }
    el.appendChild(kutu);
    el.appendChild(h("p", "gerekce", "rank = " + mem.rank + " / boyut = " + mem.ambient_dim + ". (Bir hedefe ulaşmak, bütün uzayı germekten farklıdır.)"));
    renderKendiAdimlar(mem.steps);
    drawKendi(vs, hedef, mem);
  }

  function renderKendiAdimlar(steps) {
    const det = document.getElementById("kendi-adim-det"), c = document.getElementById("kendi-adimlar");
    c.innerHTML = ""; det.hidden = false;
    if (!steps || !steps.length) { c.appendChild(h("p", "gerekce", "Satır işlemi gerekmedi.")); return; }
    const b0 = h("div", "adim-blok");
    b0.appendChild(h("div", "op-metin", "Başlangıç matrisi"));
    b0.appendChild(matrisCiz(steps[0].before, steps[0].rhs_before, null));
    c.appendChild(b0);
    steps.forEach(function (s) {
      const blok = h("div", "adim-blok");
      blok.appendChild(h("div", "op-metin", s.operation_text));
      if (s.reason) blok.appendChild(h("p", "gerekce", s.reason));
      blok.appendChild(matrisCiz(s.after, s.rhs_after, s.pivot, s.target_row));
      c.appendChild(blok);
    });
  }

  function drawKendi(vs, hedef, mem, bag) {
    const svg = document.getElementById("kendi-svg"), not = document.getElementById("kendi-grafik-not");
    if (kendiM === 2) {
      not.style.display = "none"; svg.style.display = "";
      const vekt = vs.map(function (v, i) { return { id: "v" + i, x: v[0], y: v[1], label: "v" + (i + 1), kind: ["giris", "giris2", "giris3"][i % 3] }; });
      if (hedef) vekt.push({ id: "h", x: hedef[0], y: hedef[1], label: "hedef", kind: mem && mem.status !== "inconsistent" ? "icerde" : "disarda" });
      window.Diagrams.draw(svg, vekt);
      if (bag && !bag.independent) {
        not.style.display = ""; not.textContent = "Bağımlılık için “4.2 Bağımsızlık ve Baz → Bağımlılık = kapanan çokgen” dersinde aynı vektörleri deneyebilirsin.";
      }
    } else {
      svg.style.display = "none"; not.style.display = "";
      not.textContent = "m = " + kendiM + ": " + (kendiM > 3 ? "4+ boyutlu vektörler 2B okla gösterilmez. " : "3B çizim bu sürümde yok. ") + "Matris, denklemler ve adım adım hesap aşağıdadır.";
    }
  }

  function ust(n) { return String(n).split("").map(function (d) { return "⁰¹²³⁴⁵⁶⁷⁸⁹"[+d]; }).join(""); }

  // ======================================================================
  // SORULAR
  // ======================================================================
  let soruToken = 0, aktifFrame = 0, oynatZaman = null, frames = null;

  function sorulariKur() {
    const liste = document.getElementById("soru-liste");
    liste.innerHTML = "";
    icerik.questions.forEach(function (q) {
      const b = h("button", "soru-oge");
      b.type = "button";
      b.appendChild(h("span", "no", (q.number ? q.number + ". " : "") + q.title));
      b.appendChild(h("span", "tier", q.tier));
      b.addEventListener("click", function () { soruSec(q, b); });
      liste.appendChild(b);
    });
  }

  async function soruSec(q, dugme) {
    const token = ++soruToken;
    document.querySelectorAll(".soru-oge").forEach(function (x) { x.removeAttribute("aria-current"); });
    if (dugme) dugme.setAttribute("aria-current", "true");
    durdurOynat();
    let res;
    try { res = await api("/api/solve", { question_id: q.id }); } catch (e) { return; }
    if (token !== soruToken) return;
    aktifFrame = 0;
    soruCiz(res);
  }

  function framesOlustur(steps) {
    const fr = [{ intro: true }];
    if (!steps || !steps.length) return fr;
    fr.push({ matrix: steps[0].before, rhs: steps[0].rhs_before, op: null, step: null });
    steps.forEach(function (s) { fr.push({ matrix: s.after, rhs: s.rhs_after, op: s.operation_text, step: s }); });
    return fr;
  }

  function soruCiz(res) {
    const govde = document.getElementById("soru-govde"), q = res.question;
    govde.innerHTML = "";
    govde.appendChild(h("h2", null, (q.number ? q.number + ". " : "") + q.title));
    const soru = h("p"); soru.appendChild(h("strong", null, "Soru: ")); soru.appendChild(document.createTextNode(q.prompt)); govde.appendChild(soru);
    const ist = h("p"); ist.appendChild(h("strong", null, "Ne isteniyor? ")); ist.appendChild(document.createTextNode(q.asked)); govde.appendChild(ist);
    if (q.type === "dependence" || q.type === "basis") {
      govde.appendChild(h("p", "gerekce", "Yöntem: vektörleri sütun yap, c₁v₁ + … + cₖvₖ = 0 homojen sistemini satır işlemleriyle çöz. Pivotsuz (serbest) sütun ⇔ bağımlılık."));
    }
    if (q.type === "guided_parameter") { rehberliCiz(govde, res); return; }

    frames = framesOlustur(res.steps);
    if (res.yorum && res.yorum.length) {
      const son = frames[frames.length - 1];
      frames.push({ yorum: res.yorum, matrix: son.matrix, rhs: son.rhs });
    }
    const alan = h("div"); alan.id = "adim-alan"; govde.appendChild(alan);
    const kontrol = h("div", "adim-kontrol");
    function dug(metin, sinif, fn) { const b = h("button", "dugme " + sinif, metin); b.type = "button"; b.addEventListener("click", fn); kontrol.appendChild(b); return b; }
    dug("⏮ Başa dön", "ikincil", function () { aktifFrame = 0; durdurOynat(); frameCiz(); });
    dug("◀ Geri", "ikincil", function () { if (aktifFrame > 0) aktifFrame--; durdurOynat(); frameCiz(); });
    dug("İleri ▶", "", function () { if (aktifFrame < frames.length - 1) aktifFrame++; durdurOynat(); frameCiz(); });
    const ob = dug("▶ Oynat", "ikincil", function () { oynatToggle(ob); }); ob.id = "k-oynat";
    dug("Tahta modu", "ikincil", function () { document.body.classList.toggle("tahta"); });
    dug("Tam ekran", "ikincil", tamEkran);
    const sayac = h("span", "adim-sayac"); sayac.id = "adim-sayac"; kontrol.appendChild(sayac);
    govde.insertBefore(kontrol, alan);
    frameCiz();
    sonucCiz(govde, res);
  }

  function frameCiz() {
    const alan = document.getElementById("adim-alan");
    if (!alan || !frames) return;
    const f = frames[aktifFrame];
    alan.innerHTML = "";
    const sayac = document.getElementById("adim-sayac");
    if (f.intro) {
      alan.appendChild(h("p", "gerekce", "Soruyu okuyun. Hazır olunca İleri’ye (veya → tuşuna) basın: önce başlangıç matrisi, sonra her satır işlemi ayrı adımda, en sonda da sonucun yorumu gelecek."));
      if (sayac) sayac.textContent = "Adım 0 / " + (frames.length - 1) + " (soru)";
      return;
    }
    if (f.yorum) {
      alan.appendChild(h("div", "op-metin", "📝 Sonucun yorumu"));
      if (f.matrix) {
        const k = h("div", "yorum-matris");
        k.appendChild(h("span", "gerekce", "Son matris:"));
        k.appendChild(matrisCiz(f.matrix, f.rhs, null, null));
        alan.appendChild(k);
      }
      alan.appendChild(yorumCiz(f.yorum));
      if (sayac) sayac.textContent = "Adım " + aktifFrame + " / " + (frames.length - 1) + " (yorum)";
      return;
    }
    alan.appendChild(h("div", "op-metin", f.op || "Başlangıç matrisi (sütunlar = vektörler)"));
    if (f.step && f.step.reason) alan.appendChild(h("p", "gerekce", f.step.reason));
    alan.appendChild(matrisCiz(f.matrix, f.rhs, f.step ? f.step.pivot : null, f.step ? f.step.target_row : null, true));
    if (f.step && f.step.cell_calculations && f.step.cell_calculations.length) {
      const det = h("details", "kapali-bolum");
      det.appendChild(h("summary", null, "Neden bu işlem? (hücre hesapları)"));
      f.step.cell_calculations.forEach(function (cc) {
        det.appendChild(h("p", "hucre-hesap", (cc.column === "rhs" ? "sağ taraf: " : (cc.column + 1) + ". sütun: ") + cc.text));
      });
      alan.appendChild(det);
    }
    if (sayac) sayac.textContent = "Adım " + aktifFrame + " / " + (frames.length - 1);
  }

  function matrisCiz(matrix, rhs, pivot, hedefSatir, canli) {
    const sarma = h("div", "matris-sarma"), t = h("table", "matris");
    matrix.forEach(function (row, ri) {
      const tr = h("tr");
      if (canli && hedefSatir === ri) tr.className = "degisen";
      row.forEach(function (hucre, ci) {
        const td = h("td");
        if (pivot && pivot.row === ri && pivot.column === ci) td.className = "pivot";
        td.appendChild(fracEl(hucre));
        tr.appendChild(td);
      });
      if (rhs) { const td = h("td", "rhs"); td.appendChild(VU.matYaz(rhs[ri], "rhs-ic")); tr.appendChild(td); }
      t.appendChild(tr);
    });
    sarma.appendChild(t);
    return sarma;
  }

  function sonucCiz(govde, res) {
    const q = res.question;
    const det = h("details", "kapali-bolum");
    det.appendChild(h("summary", null, "Sonucu göster"));
    const kutu = h("div");
    if (q.type === "combination") {
      if (res.status === "inconsistent") { kutu.className = "sonuc-kutu yok"; kutu.textContent = "Sistem tutarsız: hedef bu vektörlerin doğrusal birleşimi olarak yazılamaz."; }
      else if (res.status === "unique") { kutu.className = "sonuc-kutu"; kutu.appendChild(document.createTextNode("Evet. Katsayılar (tek çözüm): ")); kutu.appendChild(vektorYaz(res.coefficients)); }
      else {
        kutu.className = "sonuc-kutu";
        kutu.appendChild(document.createTextNode("Evet (sonsuz temsil). Bir temsil (serbest = 0): "));
        kutu.appendChild(vektorYaz(res.particular));
        kutu.appendChild(h("p", "gerekce", res.note || ""));
      }
      kutu.appendChild(rankSatiri(res));
    } else if (q.type === "conditions") {
      kutu.className = "sonuc-kutu";
      if (res.spans_ambient) kutu.appendChild(document.createTextNode("Rank = boyut: bu vektörler uzayın tamamını gerer; ek koşul yoktur."));
      else {
        kutu.appendChild(h("p", null, "Homojen koşul(lar):"));
        res.conditions.forEach(function (c) { kutu.appendChild(VU.matYaz(c, "kosul-kutu")); });
      }
      kutu.appendChild(rankSatiri(res));
      kutu.appendChild(dogrulamaSatiri(res.verification));
      if (q.note) kutu.appendChild(h("p", "gerekce", q.note));
    } else if (q.type === "target_unknowns") {
      kutu.className = "sonuc-kutu";
      kutu.appendChild(h("p", null, "Bilinmeyenler:"));
      for (const k in res.solution) {
        const d = h("div", "kosul-kutu"); d.appendChild(document.createTextNode(k + " = ")); d.appendChild(fracEl(res.solution[k])); kutu.appendChild(d);
      }
      if (res.representation) {
        const rp = h("p"); rp.appendChild(document.createTextNode("Bir temsil (katsayılar): "));
        rp.appendChild(vektorYaz(res.representation.coefficients || res.representation.particular || []));
        kutu.appendChild(rp);
      }
      if (q.note) kutu.appendChild(h("p", "gerekce", q.note));
    } else if (q.type === "dependence" || q.type === "basis") {
      bagimlilikSonucu(kutu, res);
      if (q.note) kutu.appendChild(h("p", "gerekce", q.note));
    }
    det.appendChild(kutu);
    govde.appendChild(det);
  }

  function rankSatiri(res) {
    const parca = ["rank = " + res.rank];
    if (res.num_vectors) parca.push(res.num_vectors + " vektör");
    if (res.ambient_dim) parca.push("ortam uzayı ℝ" + ust(res.ambient_dim));
    return h("p", "gerekce", parca.join(" · "));
  }

  const YORUM_IKON = { denklem: "✎", kontrol: "✓", anlam: "💡", ipucu: "🎯" };
  function yorumCiz(maddeler) {
    const ol = h("ol", "yorum-liste");
    maddeler.forEach(function (m, i) {
      const li = h("li", "yorum-madde y-" + m.tur);
      li.style.setProperty("--gecikme", (i * 260) + "ms");
      const bas = h("div", "yorum-baslik");
      bas.appendChild(h("span", "yorum-ikon", YORUM_IKON[m.tur] || "•"));
      bas.appendChild(document.createTextNode(m.baslik));
      li.appendChild(bas);
      if (m.metin) li.appendChild(h("p", "yorum-metin", m.metin));
      (m.mat || []).forEach(function (x) { li.appendChild(VU.matYaz(x, "mat")); });
      ol.appendChild(li);
    });
    return ol;
  }
  function dogrulamaSatiri(v) {
    return h("p", "gerekce", "Doğrulama: HA = 0 → " + (v.HA_is_zero ? "evet" : "hayır") + " ; rank(H) = " + v.rank_H + " (beklenen " + v.expected_rank_H + ") → " + (v.ok ? "tutarlı ✓" : "tutarsız"));
  }

  function rehberliCiz(govde, res) {
    const g = res.guided;
    const kutu = h("div");
    kutu.appendChild(h("p", "gerekce", g.scope));
    kutu.appendChild(h("p", null, "Denklemler (λ₁..λ₄):"));
    g.equations.forEach(function (eq) { kutu.appendChild(VU.matYaz(eq, "kosul-kutu")); });
    kutu.appendChild(h("p", null, "Türetilen:"));
    g.derived.forEach(function (eq) { kutu.appendChild(VU.matYaz(eq, "kosul-kutu")); });
    kutu.appendChild(h("p", null, "Dallar:"));
    g.branches.forEach(function (br) { kutu.appendChild(VU.matYaz(br.case + ": " + br.result, "kosul-kutu")); });
    kutu.appendChild(VU.matYaz("Cevap: " + g.answer, "sonuc-kutu"));
    govde.appendChild(kutu);
  }

  function oynatToggle(btn) {
    if (oynatZaman) { durdurOynat(); return; }
    btn.textContent = "⏸ Duraklat";
    oynatZaman = setInterval(function () {
      if (aktifFrame < frames.length - 1) { aktifFrame++; frameCiz(); } else durdurOynat();
    }, 1400);
  }
  function durdurOynat() {
    if (oynatZaman) { clearInterval(oynatZaman); oynatZaman = null; }
    const b = document.getElementById("k-oynat"); if (b) b.textContent = "▶ Oynat";
  }
  function tamEkran() {
    if (!document.fullscreenElement) { if (document.documentElement.requestFullscreen) document.documentElement.requestFullscreen(); }
    else if (document.exitFullscreen) document.exitFullscreen();
  }

  // --- Klavye: aktif paneldeki oynatıcıya ya da soru adımlarına yönlendir -------
  document.addEventListener("keydown", function (e) {
    const t = e.target;
    if (t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.isContentEditable)) return;
    if (e.altKey || e.ctrlKey || e.metaKey) return;
    if (!paneller.sorular.hidden) {
      if (!frames) return;
      if (e.key === "ArrowRight") { if (aktifFrame < frames.length - 1) aktifFrame++; durdurOynat(); frameCiz(); e.preventDefault(); }
      else if (e.key === "ArrowLeft") { if (aktifFrame > 0) aktifFrame--; durdurOynat(); frameCiz(); e.preventDefault(); }
      else if (e.key === "Escape") document.body.classList.remove("tahta");
      return;
    }
    let o = VU.aktifOynatici;
    if (!o || !VU.gorunur(o.kok)) {
      for (const k in oynaticilar) if (VU.gorunur(oynaticilar[k].kok)) o = oynaticilar[k];
    }
    if (o && VU.gorunur(o.kok) && o.tus(e)) e.preventDefault();
  });

  // ======================================================================
  // Başlat
  // ======================================================================
  (async function init() {
    try { icerik = await api("/api/content"); }
    catch (e) { VU.durumGoster("İçerik yüklenemedi. Sunucu çalışıyor mu? (py -3 app.py)", true); return; }
    document.title = icerik.title;
    kurallariKur();
    altUzaylariKur();
    germeyiKur();
    bagimsizligiKur();
    kendiKur();
    sorulariKur();
    const hash = (location.hash || "").slice(1);
    ilerlemeGuncelle();
    sekmeSec(paneller[hash] ? hash : "giris");
  })();
})();
