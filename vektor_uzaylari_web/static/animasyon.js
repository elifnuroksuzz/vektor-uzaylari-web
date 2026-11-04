// Arayüz animasyonları: sekme göstergesi, düğme dalgası, kaydırınca belirme,
// içerik yenilenince kısa vurgu. Matematiğe dokunmaz; yalnızca görünüm.
(function () {
  "use strict";

  const azalt = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function yenidenOynat(el, sinif) {
    el.classList.remove(sinif); void el.offsetWidth; el.classList.add(sinif);
  }

  // --- 1. Sekmelerin altında kayan gösterge ---------------------------------
  const sekmeler = document.getElementById("tabs");
  if (sekmeler) {
    const gosterge = document.createElement("span");
    gosterge.className = "tab-gosterge";
    gosterge.setAttribute("aria-hidden", "true");
    sekmeler.appendChild(gosterge);
    sekmeler.classList.add("gostergeli");

    const yerlestir = function () {
      const secili = sekmeler.querySelector('.tab[aria-selected="true"]');
      if (!secili) return;
      gosterge.style.width = secili.offsetWidth + "px";
      gosterge.style.transform = "translateX(" + secili.offsetLeft + "px)";
    };
    new MutationObserver(yerlestir).observe(sekmeler, { attributes: true, subtree: true, attributeFilter: ["aria-selected"] });
    window.addEventListener("resize", yerlestir);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(yerlestir);
    yerlestir();
    // İlk yerleşimde kaymasın; sonra geçiş açılsın.
    requestAnimationFrame(function () { requestAnimationFrame(function () { gosterge.classList.add("hazir"); }); });
  }

  // --- 2. Düğmelere tıklama dalgası -----------------------------------------
  if (!azalt) {
    document.addEventListener("pointerdown", function (e) {
      const b = e.target.closest && e.target.closest(".dugme, .tab, .menu-oge, .soru-oge");
      if (!b || b.disabled) return;
      const r = b.getBoundingClientRect();
      const boy = Math.max(r.width, r.height) * 2;
      const d = document.createElement("span");
      d.className = "dalga-efekt";
      d.style.width = d.style.height = boy + "px";
      d.style.left = (e.clientX - r.left - boy / 2) + "px";
      d.style.top = (e.clientY - r.top - boy / 2) + "px";
      b.appendChild(d);
      d.addEventListener("animationend", function () { d.remove(); });
    });
  }

  // --- 3. Kaydırınca beliren bölümler ---------------------------------------
  if (!azalt && "IntersectionObserver" in window) {
    const io = new IntersectionObserver(function (girdiler) {
      girdiler.forEach(function (g) {
        if (g.isIntersecting) { g.target.classList.add("gorundu"); io.unobserve(g.target); }
      });
    }, { rootMargin: "0px 0px -40px 0px", threshold: 0.05 });
    document.querySelectorAll(".lab, .karsilastir-alan, .site-footer").forEach(function (el) {
      el.classList.add("belir");
      io.observe(el);
    });
  }

  // --- 4. İçerik değişince kısa "yenilendi" animasyonu ----------------------
  const izle = [
    ["soru-govde", "icerik-gir"],
    ["kendi-sonuc", "icerik-gir"],
    ["kendi-tablo-alan", "icerik-gir"],
    ["altuzay-tablo", "icerik-gir"],
    ["uyelik-sonuc", "vurgu-gir"],
    ["germe-span-not", "vurgu-gir"]
  ];
  izle.forEach(function (c) {
    const el = document.getElementById(c[0]);
    if (!el) return;
    let bekle = 0;
    new MutationObserver(function () {
      cancelAnimationFrame(bekle);
      bekle = requestAnimationFrame(function () { yenidenOynat(el, c[1]); });
    }).observe(el, { childList: true, characterData: true, subtree: c[1] === "vurgu-gir" });
  });

  // Germe sonucu: sürgü oynadıkça küçük bir nabız.
  const germeSonuc = document.getElementById("germe-sonuc");
  if (germeSonuc) {
    new MutationObserver(function () { yenidenOynat(germeSonuc, "nabiz-gir"); })
      .observe(germeSonuc, { childList: true, characterData: true, subtree: true });
  }

  // --- 5. Ders menüsü ve soru listesi doldurulunca sırayla gelsin ------------
  document.querySelectorAll(".ders-menu, .soru-liste").forEach(function (m) {
    const kademele = function () {
      const ogeler = m.querySelectorAll(".menu-oge, .soru-oge, .menu-grup");
      ogeler.forEach(function (o, i) {
        if (o.dataset.geldi) return;
        o.dataset.geldi = "1";
        o.style.setProperty("--sira", Math.min(i, 20));
        o.classList.add("kademe-gir");
      });
    };
    new MutationObserver(kademele).observe(m, { childList: true, subtree: true });
    kademele();
  });
})();
