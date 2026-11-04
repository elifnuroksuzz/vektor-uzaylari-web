/* Ders oynatıcısı: anlatım (solda, numaralı zaman çizelgesi) + grafik (sağda).
 * Kontroller ve örnek sayılar grafiğin hemen altındadır; grafiğe tıklamak,
 * ▶ düğmesi ya da → tuşu sonraki adıma geçer. Sayılar değiştirilince ya da
 * 🎲 ile rastgele seçilince sunucu dersi yeniden hesaplar; kalınan adım
 * korunur — aynı ispat satırlarının başka sayılarla da geçerli olduğu görülür. */
(function (global) {
  "use strict";

  const VU = global.VU;
  const h = VU.h;

  const TUR_AD = {
    kurulum: "Kurulum", ispat: "İspat", karsi: "Karşı örnek",
    sonuc: "Sonuç", uyari: "Dikkat", muh: "Mühendislik"
  };
  const LEJANT = {
    giris: "girdi", giris2: "girdi", giris3: "girdi", ara: "ara adım", sonuc: "sonuç",
    icerde: "kümede (∈ W)", disarda: "küme dışında / farklı", ters: "ters vektör",
    kuvvet: "kuvvet", hayalet: "önceki adım"
  };
  const OYNAT_ARALIK = 2800;

  function Oynatici(kok) {
    this.kok = kok;
    this.ders = null;
    this.adim = 0;
    this.token = 0;
    this.zaman = null;
    this._kur();
  }

  function dugme(metin, sinif, etiket) {
    const b = h("button", "dugme " + (sinif || ""), metin);
    b.type = "button";
    if (etiket) { b.setAttribute("aria-label", etiket); b.title = etiket; }
    return b;
  }

  Oynatici.prototype._kur = function () {
    const self = this, k = this.kok;
    k.classList.add("oyn");
    k.innerHTML = "";

    // Başlık + iddia
    const bas = h("header", "oyn-bas");
    this.elBaslik = h("h2", "oyn-baslik");
    bas.appendChild(this.elBaslik);
    this.elIddia = h("div", "oyn-iddia");
    bas.appendChild(this.elIddia);
    k.appendChild(bas);

    const govde = h("div", "oyn-govde");

    // Sol: adımlar (zaman çizelgesi)
    const sol = h("div", "oyn-sol");
    this.elAdimlar = h("ol", "oyn-adimlar");
    sol.appendChild(this.elAdimlar);
    govde.appendChild(sol);

    // Sağ: grafik + kontroller + örnek sayılar
    const sag = h("div", "oyn-sag");
    const kutu = h("div", "oyn-grafik-kutu");
    this.svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    this.svg.setAttribute("class", "oyn-svg");
    this.svg.setAttribute("role", "img");
    this.svg.setAttribute("tabindex", "0");
    this.svg.setAttribute("aria-label", "Adım grafiği — tıklayınca sonraki adıma geçer");
    this.svg.addEventListener("click", function () { VU.aktifOynatici = self; self.durdur(); self.ileri(); });
    this.svg.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); self.ileri(); }
    });
    kutu.appendChild(this.svg);
    this.elAltyazi = h("p", "oyn-altyazi");
    this.elAltyazi.setAttribute("aria-live", "polite");
    kutu.appendChild(this.elAltyazi);
    sag.appendChild(kutu);
    this.elLejant = h("div", "oyn-lejant");
    sag.appendChild(this.elLejant);

    const kon = h("div", "oyn-kontrol");
    const geri = dugme("◀", "ikincil yuvarlak", "Önceki adım");
    geri.addEventListener("click", function () { self.durdur(); self.geri(); });
    this.elNoktalar = h("div", "oyn-noktalar");
    const ileri = dugme("▶", "yuvarlak", "Sonraki adım");
    ileri.addEventListener("click", function () { self.durdur(); self.ileri(); });
    this.elSayac = h("span", "oyn-sayac");
    kon.appendChild(geri); kon.appendChild(this.elNoktalar); kon.appendChild(ileri); kon.appendChild(this.elSayac);
    sag.appendChild(kon);

    const kon2 = h("div", "oyn-kontrol2");
    this.elOynat = dugme("⏵ Otomatik oynat", "metin");
    this.elOynat.addEventListener("click", function () { self.oynatDegistir(); });
    const basa = dugme("↺ Baştan", "metin");
    basa.addEventListener("click", function () { self.durdur(); self.git(0); });
    this.elTahta = dugme("⛶ Tahta modu", "metin");
    this.elTahta.addEventListener("click", function () { self.tahta(); });
    kon2.appendChild(this.elOynat); kon2.appendChild(basa); kon2.appendChild(this.elTahta);
    sag.appendChild(kon2);

    // Örnek sayılar çubuğu (grafikle ilgili olduğu için grafiğin altında)
    this.elOrnek = h("div", "ornek-bar");
    sag.appendChild(this.elOrnek);
    this.elHata = h("p", "oyn-hata");
    this.elHata.hidden = true;
    this.elHata.setAttribute("role", "alert");
    sag.appendChild(this.elHata);

    govde.appendChild(sag);
    k.appendChild(govde);

    this.sahne = new global.Diagrams.Sahne(this.svg);
    k.addEventListener("pointerdown", function () { VU.aktifOynatici = self; });
  };

  // --- Yükleme -------------------------------------------------------------
  Oynatici.prototype.yukle = async function (dersId, secenek) {
    secenek = secenek || {};
    const token = ++this.token;
    const govde = { lesson_id: dersId };
    if (secenek.params) govde.params = secenek.params;
    if (secenek.randomize) govde.randomize = true;
    let ders;
    try {
      ders = await VU.api("/api/lesson", govde, { sessiz: true });
    } catch (e) {
      if (token !== this.token) return;
      this.elHata.hidden = false;
      this.elHata.textContent = "⚠ " + e.message;
      return;
    }
    if (token !== this.token) return; // eski cevap yeni dersin üstüne yazılmasın
    this.elHata.hidden = true;
    const ayniDers = this.ders && this.ders.id === ders.id;
    this.ders = ders;
    VU.aktifOynatici = this;
    if (!ayniDers) { this.adim = 0; this.durdur(); this.duzenAcik = false; }
    else this.adim = Math.min(this.adim, ders.steps.length - 1);
    this._baslikCiz();
    this._ornekCiz();
    this._adimlariCiz();
    this._goster(!ayniDers, true);
    if (secenek.kaydir && this.kok.getBoundingClientRect().top < 0) {
      this.kok.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  };

  Oynatici.prototype._baslikCiz = function () {
    const d = this.ders;
    this.elBaslik.textContent = d.title;
    this.elIddia.innerHTML = "";
    if (d.claim) {
      this.elIddia.appendChild(h("span", "iddia-etiket", d.badge === "Karşı örnek" ? "Soru" : "İddia"));
      this.elIddia.appendChild(VU.matYaz(d.claim, "iddia-metin"));
    }
  };

  // --- Örnek sayılar: özet satırı + istenince açılan düzenleme -------------
  Oynatici.prototype._ornekCiz = function () {
    const self = this, kutu = this.elOrnek, d = this.ders;
    kutu.innerHTML = "";
    if (!d.params.length) { kutu.hidden = true; return; }
    kutu.hidden = false;

    const ust = h("div", "ornek-ust");
    const ozet = h("span", "ornek-ozet");
    ozet.appendChild(h("span", "ornek-etiket", "Grafikteki örnek: "));
    d.params.forEach(function (p, i) {
      if (i) ozet.appendChild(document.createTextNode(",  "));
      const deger = p.type === "vec" ? "(" + p.value.join(", ") + ")" : p.value;
      ozet.appendChild(VU.matYaz(p.label + " = " + deger, "ornek-deger"));
    });
    ust.appendChild(ozet);
    const dug = h("span", "ornek-dugmeler");
    if (d.randomizable) {
      const r = dugme("🎲 Başka sayılar", "metin");
      r.addEventListener("click", function () { self.yukle(self.ders.id, { randomize: true }); });
      dug.appendChild(r);
    }
    const duz = dugme(this.duzenAcik ? "✕ Kapat" : "✎ Düzenle", "metin");
    duz.setAttribute("aria-expanded", this.duzenAcik ? "true" : "false");
    duz.addEventListener("click", function () { self.duzenAcik = !self.duzenAcik; self._ornekCiz(); });
    dug.appendChild(duz);
    ust.appendChild(dug);
    kutu.appendChild(ust);

    if (this.duzenAcik) {
      const f = h("form", "ornek-form");
      f.addEventListener("submit", function (e) { e.preventDefault(); self.uygula(f); });
      d.params.forEach(function (p) {
        const lab = h("label", "ornek-girdi");
        lab.appendChild(h("span", "ornek-ad", p.label + " ="));
        const girdiler = p.type === "vec" ? p.value : [p.value];
        if (p.type === "vec") lab.appendChild(document.createTextNode("("));
        girdiler.forEach(function (v, i) {
          if (i) lab.appendChild(document.createTextNode(","));
          const inp = h("input");
          inp.inputMode = "decimal"; inp.dataset.ad = p.name; inp.dataset.i = i; inp.value = v;
          inp.setAttribute("aria-label", p.label + (p.type === "vec" ? " " + (i + 1) + ". bileşen" : ""));
          lab.appendChild(inp);
        });
        if (p.type === "vec") lab.appendChild(document.createTextNode(")"));
        f.appendChild(lab);
      });
      const uy = h("button", "dugme", "Uygula"); uy.type = "submit";
      const vs = dugme("Varsayılan", "metin");
      vs.addEventListener("click", function () { self.yukle(self.ders.id, {}); });
      const sat = h("div", "ornek-form-dugme"); sat.appendChild(uy); sat.appendChild(vs);
      f.appendChild(sat);
      kutu.appendChild(f);
    }
    kutu.appendChild(h("p", "ornek-not", d.param_note ||
      "Sayıları değiştir: grafik değişir, soldaki ispat satırları aynen geçerli kalır."));
  };

  Oynatici.prototype.uygula = function (f) {
    const params = {};
    this.ders.params.forEach(function (p) {
      const girdiler = f.querySelectorAll("input[data-ad='" + p.name + "']");
      if (p.type === "vec") params[p.name] = Array.prototype.map.call(girdiler, function (x) { return x.value.trim(); });
      else params[p.name] = girdiler[0].value.trim();
    });
    this.yukle(this.ders.id, { params: params });
  };

  // --- Adımlar ---------------------------------------------------------------
  Oynatici.prototype._adimlariCiz = function () {
    const self = this, ol = this.elAdimlar;
    ol.innerHTML = "";
    this.elNoktalar.innerHTML = "";
    this.ders.steps.forEach(function (s, i) {
      const li = h("li", "oyn-adim t-" + s.kind);
      li.dataset.no = i + 1;
      const ust = h("div", "oyn-adim-ust");
      ust.appendChild(h("span", "tur-etiket", TUR_AD[s.kind] || s.kind));
      ust.appendChild(h("span", "oyn-adim-baslik", s.title));
      li.appendChild(ust);
      if (s.text) VU.metinYaz(li, s.text, "oyn-metin");
      if (s.math && s.math.length) {
        const mb = h("div", "mat-blok");
        s.math.forEach(function (m, j) {
          const satir = VU.matYaz(m, "mat");
          satir.style.setProperty("--gecikme", (j * 220) + "ms");
          mb.appendChild(satir);
        });
        li.appendChild(mb);
      }
      if (s.why) {
        const w = h("p", "gerekce-satir");
        w.appendChild(h("span", "gerekce-ad", "Gerekçe"));
        w.appendChild(document.createTextNode(s.why));
        li.appendChild(w);
      }
      li.addEventListener("click", function () {
        if (i !== self.adim) { self.durdur(); self.git(i); }
      });
      ol.appendChild(li);

      const n = h("button", "oyn-nokta");
      n.type = "button";
      n.setAttribute("aria-label", (i + 1) + ". adım: " + s.title);
      n.title = (i + 1) + ". " + s.title;
      n.addEventListener("click", function () { self.durdur(); self.git(i); });
      self.elNoktalar.appendChild(n);
    });
  };

  Oynatici.prototype._goster = function (ilk, yenidenHesap) {
    const d = this.ders, i = this.adim, s = d.steps[i];
    const lis = this.elAdimlar.children;
    for (let j = 0; j < lis.length; j++) {
      const li = lis[j];
      const onceGizli = li.hidden;
      li.hidden = j > i;
      li.classList.toggle("aktif", j === i);
      li.classList.toggle("gecmis", j < i);
      if (j === i && (onceGizli || ilk)) {
        li.classList.remove("yeni"); void li.offsetWidth; li.classList.add("yeni");
      }
    }
    const nok = this.elNoktalar.children;
    for (let j = 0; j < nok.length; j++) {
      nok[j].classList.toggle("aktif", j === i);
      nok[j].classList.toggle("gecti", j < i);
      if (j === i) nok[j].setAttribute("aria-current", "step"); else nok[j].removeAttribute("aria-current");
    }
    this.sahne.show(s.scene, d.range);
    this.elAltyazi.textContent = s.caption || "";
    this.elAltyazi.hidden = !s.caption;
    const son = i === d.steps.length - 1;
    this.elSayac.textContent = son ? "Son adım ∎" : (i + 1) + " / " + d.steps.length;
    this._lejant(s.scene);
    const aktifLi = lis[i];
    if (aktifLi && !ilk && !yenidenHesap && aktifLi.scrollIntoView) {
      aktifLi.scrollIntoView({ block: "nearest", behavior: "smooth" });
    }
  };

  Oynatici.prototype._lejant = function (sc) {
    const kutu = this.elLejant;
    kutu.innerHTML = "";
    const gor = {};
    (sc.vectors || []).forEach(function (v) {
      const ad = LEJANT[v.kind];
      if (ad && !gor[ad]) gor[ad] = v.kind;
    });
    Object.keys(gor).forEach(function (ad) {
      const s = h("span", "lejant-oge");
      s.appendChild(h("span", "lejant-renk k-" + gor[ad]));
      s.appendChild(document.createTextNode(ad));
      kutu.appendChild(s);
    });
    if (sc.sweep) {
      const s = h("span", "lejant-oge");
      s.appendChild(h("span", "lejant-renk k-tarama"));
      s.appendChild(document.createTextNode("örnek noktalar (seçili katsayı aralığı)"));
      kutu.appendChild(s);
    }
  };

  Oynatici.prototype.git = function (i) {
    if (!this.ders) return;
    i = Math.max(0, Math.min(this.ders.steps.length - 1, i));
    if (i === this.adim) return;
    this.adim = i;
    this._goster(false);
  };
  Oynatici.prototype.ileri = function () { if (this.ders) this.git(this.adim + 1); };
  Oynatici.prototype.geri = function () { if (this.ders) this.git(this.adim - 1); };

  Oynatici.prototype.oynatDegistir = function () {
    const self = this;
    if (this.zaman) { this.durdur(); return; }
    if (this.adim >= this.ders.steps.length - 1) this.git(0);
    this.elOynat.textContent = "⏸ Duraklat";
    this.zaman = setInterval(function () {
      if (self.adim < self.ders.steps.length - 1) self.ileri();
      else self.durdur();
    }, OYNAT_ARALIK);
  };
  Oynatici.prototype.durdur = function () {
    if (this.zaman) { clearInterval(this.zaman); this.zaman = null; }
    if (this.elOynat) this.elOynat.textContent = "⏵ Otomatik oynat";
  };

  Oynatici.prototype.tahta = function () {
    const acik = !this.kok.classList.contains("tahta-acik");
    document.querySelectorAll(".oyn.tahta-acik").forEach(function (x) { x.classList.remove("tahta-acik"); });
    this.kok.classList.toggle("tahta-acik", acik);
    document.body.classList.toggle("tahta-ders", acik);
    this.elTahta.textContent = acik ? "✕ Tahtadan çık" : "⛶ Tahta modu";
    VU.aktifOynatici = this;
  };

  /** Klavye: ← → adım, Esc tahta modundan çık. */
  Oynatici.prototype.tus = function (e) {
    if (e.key === "ArrowRight" || e.key === "PageDown") { this.durdur(); this.ileri(); return true; }
    if (e.key === "ArrowLeft" || e.key === "PageUp") { this.durdur(); this.geri(); return true; }
    if (e.key === "Escape" && this.kok.classList.contains("tahta-acik")) { this.tahta(); return true; }
    return false;
  };

  global.Oynatici = Oynatici;
})(window);
