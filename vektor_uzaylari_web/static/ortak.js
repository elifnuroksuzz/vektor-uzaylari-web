/* Ortak yardımcılar: API çağrısı, durum mesajı, güvenli metin/kesir çizimi.
 * Kullanıcı ya da sunucu metni hiçbir zaman ham innerHTML olarak basılmaz. */
(function (global) {
  "use strict";

  const durumEl = document.getElementById("durum");

  function durumGoster(mesaj, hata) {
    if (!durumEl) return;
    if (!mesaj) { durumEl.hidden = true; return; }
    durumEl.hidden = false;
    durumEl.textContent = mesaj;
    durumEl.classList.toggle("hata", !!hata);
  }

  let bekleyen = 0;
  async function api(yol, govde, secenek) {
    secenek = secenek || {};
    bekleyen++;
    const zaman = setTimeout(function () { if (bekleyen) durumGoster("Hesaplanıyor…", false); }, 250);
    try {
      const istek = { method: govde ? "POST" : "GET", headers: { "Content-Type": "application/json" } };
      if (govde) istek.body = JSON.stringify(govde);
      const cevap = await fetch(yol, istek);
      const veri = await cevap.json();
      if (!cevap.ok) throw new Error(veri.error || "Sunucu hatası.");
      return veri;
    } catch (e) {
      if (!secenek.sessiz) durumGoster("Hata: " + e.message + " (tekrar deneyebilirsiniz)", true);
      throw e;
    } finally {
      bekleyen--;
      clearTimeout(zaman);
      if (!bekleyen && durumEl && !durumEl.classList.contains("hata")) durumGoster(null);
    }
  }
  function hataTemizle() { if (durumEl && durumEl.classList.contains("hata")) durumGoster(null); }

  function h(etiket, sinif, metin) {
    const n = document.createElement(etiket);
    if (sinif) n.className = sinif;
    if (metin != null) n.textContent = metin;
    return n;
  }

  // --- Kesir: "7/3" → pay/payda düzeni -------------------------------------
  function fracEl(s) {
    s = String(s).replace(/-/g, "−");
    const m = /^(−?)(\d+)\/(\d+)$/.exec(s.trim());
    if (m) {
      const sp = h("span", "frac-wrap");
      if (m[1]) sp.appendChild(document.createTextNode("−"));
      const f = h("span", "frac");
      f.appendChild(h("span", "pay", m[2]));
      f.appendChild(h("span", "payda", m[3]));
      sp.appendChild(f);
      return sp;
    }
    return h("span", null, s);
  }

  function vektorYaz(arr) {
    const sp = h("span", "vektor");
    sp.appendChild(document.createTextNode("("));
    arr.forEach(function (v, i) {
      if (i) sp.appendChild(document.createTextNode(", "));
      sp.appendChild(fracEl(v));
    });
    sp.appendChild(document.createTextNode(")"));
    return sp;
  }

  /** Matematik satırı: içindeki a/b kesirlerini dikey yazar. */
  function matYaz(metin, sinif) {
    const d = h("div", sinif || "mat");
    // Sunucudan gelen "-1/3" gibi değerlerde ASCII tireyi gerçek eksiye çevir.
    String(metin).replace(/-/g, "−").split(/(−?\d+\/\d+)/).forEach(function (parca) {
      if (!parca) return;
      if (/^−?\d+\/\d+$/.test(parca)) d.appendChild(fracEl(parca));
      else d.appendChild(document.createTextNode(parca));
    });
    return d;
  }

  /** **kalın** biçimini ve \n paragraflarını destekleyen güvenli metin. */
  function metinYaz(parent, metin, sinif) {
    String(metin || "").split("\n").forEach(function (par) {
      if (!par.trim()) return;
      const p = h("p", sinif || null);
      par.split(/(\*\*[^*]+\*\*)/).forEach(function (parca) {
        if (/^\*\*[^*]+\*\*$/.test(parca)) p.appendChild(h("strong", null, parca.slice(2, -2)));
        else if (parca) p.appendChild(document.createTextNode(parca));
      });
      parent.appendChild(p);
    });
  }

  // offsetParent, position:fixed öğelerde (tahta modu) null döner; kutu sayısına bak.
  function gorunur(elm) { return !!(elm && elm.getClientRects().length > 0); }

  global.VU = {
    api: api, durumGoster: durumGoster, hataTemizle: hataTemizle,
    h: h, fracEl: fracEl, vektorYaz: vektorYaz, matYaz: matYaz, metinYaz: metinYaz,
    gorunur: gorunur, aktifOynatici: null
  };
})(window);
