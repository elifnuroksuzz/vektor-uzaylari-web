"""Çözülen sorular için otomatik "sonucun yorumu".

Her yorum maddesi motorun bulduğu sonuçlardan HESAPLANIR (sabit metin değil):
son matrisin denklem karşılığı, yerine koyarak kontrol, geometrik anlam,
fazla vektörler ve sınav ipucu. Kontrol satırları kesin kesirle yeniden
hesaplanır; böylece "✓" işareti gerçekten doğrulanmış bir eşitliği gösterir.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Dict, List, Sequence

from . import analysis, arithmetic

MINUS = "−"
_ALT = "₀₁₂₃₄₅₆₇₈₉"
_UST = "⁰¹²³⁴⁵⁶⁷⁸⁹"


def _alt(n: int) -> str:
    return "".join(_ALT[int(d)] for d in str(n))


def _ust(n: int) -> str:
    return "".join(_UST[int(d)] for d in str(n))


def _f(x) -> str:
    return arithmetic.format_fraction(Fraction(x)).replace("-", MINUS)


def _v(v: Sequence) -> str:
    return "(" + ", ".join(_f(x) for x in v) + ")"


def _R(m: int) -> str:
    return "ℝ" + _ust(m)


def _toplam(terimler) -> str:
    """[(katsayı, ad), …] → "a·v₁ − b·v₂ + …" (sıfırlar atlanır)."""

    parcalar: List[str] = []
    for c, ad in terimler:
        c = Fraction(c)
        if c == 0:
            continue
        mag = abs(c)
        t = ad if mag == 1 else f"{_f(mag)}·{ad}"
        if not parcalar:
            parcalar.append((MINUS if c < 0 else "") + t)
        else:
            parcalar.append((f" {MINUS} " if c < 0 else " + ") + t)
    return "".join(parcalar) or "0"


def _madde(baslik: str, metin: str = "", mat: Sequence[str] = (), tur: str = "anlam") -> Dict:
    return {"baslik": baslik, "metin": metin, "mat": list(mat), "tur": tur}


def _Fv(v) -> List[Fraction]:
    return [Fraction(x) for x in v]


def _kosul_metni(metin: str) -> str:
    return metin.replace("-", MINUS)


def _normal_kosullar(res: Dict):
    """Koşulları ilk katsayısı pozitif olacak biçimde (gerekirse −1 ile çarpıp) döndürür.

    Dönüş: (metinler, H satırları). Aynı denklemin katı olduğu için çözüm kümesi değişmez.
    """

    sem = res["symbols"]
    metinler, satirlar = [], []
    for ifade in res["condition_exprs"]:
        kats = [Fraction(ifade["terms"].get(x, "0")) for x in sem]
        sabit = Fraction(ifade["const"])
        ilk = next((c for c in kats if c != 0), Fraction(1))
        if ilk < 0:
            kats = [-c for c in kats]
            sabit = -sabit
        terimler = [(kats[i], sem[i]) for i in range(len(sem))]
        sol = _toplam(terimler)
        if sabit != 0:
            sol += (f" {MINUS} " if sabit < 0 else " + ") + _f(abs(sabit))
        metinler.append(sol + " = 0")
        satirlar.append(kats)
    return metinler, satirlar


def _fazla_vektorler(vectors) -> List[str]:
    """Pivotsuz (fazla) her vektörü, seçilen baz vektörleri cinsinden yazar."""

    dep = analysis.dependence_analysis(vectors)
    baz = dep["basis_indices"]
    satirlar = []
    for j in range(len(vectors)):
        if j in baz:
            continue
        cozum = analysis.solve_combination([vectors[i] for i in baz], vectors[j]) if baz else None
        if not baz:
            satirlar.append(f"v{_alt(j + 1)} = 0")
            continue
        katsayi = cozum.get("coefficients") or cozum.get("particular")
        ifade = _toplam([(katsayi[t], f"v{_alt(baz[t] + 1)}") for t in range(len(baz))])
        satirlar.append(f"v{_alt(j + 1)} = {ifade}")
    return satirlar


def _geometri(rank: int, m: int) -> str:
    if rank == 0:
        return "yalnızca orijin {0}"
    if rank == m:
        return f"{_R(m)}’ün tamamı"
    if rank == 1:
        return f"{_R(m)} içinde orijinden geçen bir DOĞRU"
    if rank == 2 and m == 3:
        return "ℝ³ içinde orijinden geçen bir DÜZLEM"
    return f"{_R(m)} içinde {rank} boyutlu bir alt uzay"


# --- Soru türleri ---------------------------------------------------------


def _birlesim(res: Dict) -> List[Dict]:
    vs = [_Fv(v) for v in res["vectors"]]
    k, m, r = len(vs), res["ambient_dim"], res["rank"]
    lam = [f"λ{_alt(i + 1)}" for i in range(k)]
    adlar = [f"v{_alt(i + 1)}" for i in range(k)]
    A, b = res["final_matrix"], res["final_rhs"]
    out: List[Dict] = []

    if res["status"] == "inconsistent":
        for i, satir in enumerate(A):
            if all(Fraction(x) == 0 for x in satir) and Fraction(b[i]) != 0:
                out.append(_madde(
                    "Son satırı oku",
                    "Sol tarafın tamamı sıfır ama sağ taraf değil. Hiçbir λ seçimi bunu sağlayamaz: ÇELİŞKİ.",
                    [f"0·λ{_alt(1)} + … + 0·λ{_alt(k)} = {_f(b[i])}"], "denklem"))
                break
        out.append(_madde(
            "Anlamı",
            f"Hedef {_v(res['target'])}, Span{{{', '.join(adlar)}}} kümesinin DIŞINDA. rank = {r} < {m} olduğundan "
            f"bu vektörler {_R(m)}’ü germez; gerilen küme {_geometri(r, m)}."))
        out.append(_madde("Sınav ipucu", "“0 = sıfırdan farklı sayı” satırı gördüğün an cevap “yazılamaz”dır; geri yerine koymaya gerek yok.", tur="ipucu"))
        return out

    # Son matris → denklemler
    pivot_satir = {p["column"]: p["row"] for p in res["pivots"]}
    denklemler = []
    for c, rr in sorted(pivot_satir.items()):
        terim = [(A[rr][j], lam[j]) for j in range(k)]
        denklemler.append(f"{_toplam(terim)} = {_f(b[rr])}")
    out.append(_madde("Son matrisi denkleme çevir",
                      "İndirgenmiş (RREF) matrisin her satırı bir denklemdir; çözüm doğrudan okunur:",
                      denklemler, "denklem"))

    c = _Fv(res.get("coefficients") or res.get("particular"))
    sonuc = arithmetic.linear_combination(vs, c)
    tamam = sonuc == _Fv(res["target"])
    out.append(_madde(
        "Kontrol: yerine koy",
        "Bulunan katsayılar gerçekten hedefi veriyor mu? (Kesin kesirlerle yeniden hesaplandı.)",
        [f"{_toplam([(c[i], _v(vs[i])) for i in range(k)])} = {_v(sonuc)}  {'✓' if tamam else '✗'}"],
        "kontrol"))

    if res["status"] == "unique":
        metin = (f"Her katsayı sütununda pivot var (rank = {r} = vektör sayısı) ⇒ {', '.join(adlar)} doğrusal "
                 f"BAĞIMSIZ ⇒ temsil TEKTİR; başka katsayı üçlüsü yoktur.")
        if r == m == k:
            metin += (f" Üstelik rank = {m} = boyut: bu {k} vektör {_R(m)}’ün bir BAZIDIR. Yani sadece bu hedef değil, "
                      f"{_R(m)}’teki her vektör tek biçimde yazılabilirdi. Bulunan sayılar hedefin bu bazdaki "
                      f"KOORDİNATLARIDIR: [w]_B = {_v(c)}.")
        out.append(_madde("Anlamı", metin))
        if any(x.denominator != 1 for x in c):
            out.append(_madde("Sınav ipucu", "Katsayıların kesirli çıkması normaldir; hata sanma. Emin olmak için her zaman yerine koyup kontrol et.", tur="ipucu"))
    else:
        serbest = [lam[f] for f in res["free_columns"]]
        yon = [_Fv(d) for d in res["directions"]]
        genel = "λ = " + _v(c) + "".join(f" + t{_alt(i + 1)}·{_v(d)}" for i, d in enumerate(yon))
        out.append(_madde(
            "Anlamı",
            f"rank = {r} < {k}: {', '.join(serbest)} serbest ⇒ SONSUZ çok temsil var. Gösterilen temsil serbest "
            "değişken(ler) 0 seçilerek bulundu; bu bir seçimdir, zorunluluk değildir. Genel çözüm:",
            [genel]))
        for d in yon:
            out.append(_madde(
                "Bonus: bağımlılık",
                "Yön vektörü, sıfırı veren sıfır olmayan bir birleşimdir; vektörler bağımlıdır:",
                [f"{_toplam([(d[i], adlar[i]) for i in range(k)])} = 0"], "kontrol"))
    return out


def _kosullar(res: Dict, soru: Dict) -> List[Dict]:
    vs = [_Fv(v) for v in res["vectors"]]
    k, m, r = len(vs), res["ambient_dim"], res["rank"]
    sem = res["symbols"]
    hedef = "(" + ", ".join(sem) + ")"
    out: List[Dict] = []

    if res["spans_ambient"]:
        out.append(_madde(
            "Son matrisi oku",
            f"Her satırda pivot var; tamamen sıfır olan katsayı satırı oluşmadı. Bu yüzden hedef {hedef} üzerinde "
            "HİÇBİR koşul yok: her hedef için sistem çözülebilir.",
            [f"son sağ taraf: {_v_metin(res['final_rhs'])}"], "denklem"))
        metin = f"rank = {r} = boyut ⇒ Span = {_R(m)}."
        if k == m:
            metin += f" {k} vektör ve rank {k}: aynı zamanda bağımsızlar ⇒ {_R(m)}’ün bir BAZI."
        out.append(_madde("Anlamı", metin))
        if soru.get("id") == "ex415":
            out.append(_madde(
                "Kaynak düzeltmesi",
                "Son satırın sağ tarafı (1/7)a + (3/7)b + c; 7 ile çarpınca a + 3b + 7c olur. PDF’teki “a − 3b − 7c” "
                "işaret hatasıdır, sonucu (rank 3) değiştirmez.", tur="ipucu"))
        out.append(_madde("Sınav ipucu",
                          f"“{_R(m)}’ü gerer mi?” sorusunda tek bir hedef denemek yetmez; GENEL hedef {hedef} ile çalış "
                          "ve sıfır satır çıkıp çıkmadığına bak (ya da rank = boyut mu kontrol et).", tur="ipucu"))
        return out

    kosullar, H = _normal_kosullar(res)
    out.append(_madde(
        "Sıfır satırlarını oku",
        "Katsayı kısmı tamamen sıfırlanan satırlarda sol taraf 0’dır; sağ taraf da 0 OLMAK ZORUNDA. "
        "Bu bir çelişki değil, üyelik KOŞULUDUR:",
        kosullar, "denklem"))

    kontrol = []
    for i, v in enumerate(vs):
        degerler = [sum(h[j] * v[j] for j in range(m)) for h in H]
        kontrol.append(f"v{_alt(i + 1)} = {_v(v)} → koşul(lar) = {', '.join(_f(d) for d in degerler)}  "
                       f"{'✓' if all(d == 0 for d in degerler) else '✗'}")
    disari = None
    for j in range(m):
        e = [Fraction(int(i == j)) for i in range(m)]
        if any(sum(h[t] * e[t] for t in range(m)) != 0 for h in H):
            disari = e
            break
    if disari is not None:
        kontrol.append(f"{_v(disari)} → koşul sağlanmaz ⇒ span DIŞINDA (o yüzden {_R(m)}’ü germez)")
    out.append(_madde("Kontrol",
                      "Gerilen uzaydaki her vektör koşulu sağlamalı; vektörlerin kendileri ile deneyelim:",
                      kontrol, "kontrol"))

    metin = (f"rank = {r} ⇒ Span, {_geometri(r, m)}. Boyut ile denklem sayısı toplanınca ortam boyutu çıkar: "
             f"{r} + {len(kosullar)} = {m}.")
    if r == 2 and m == 3 and len(H) == 1:
        metin += f" Düzlemin normal vektörü n = {_v(H[0])}: koşul, “(x, y, z) · n = 0” demektir."
    out.append(_madde("Geometrik anlamı", metin))

    if k > r:
        out.append(_madde(
            "Fazla vektör",
            f"{k} vektör var ama rank {r}: {k - r} tanesi diğerlerinin birleşimi (bağımlı). Aynı uzayı daha az vektörle "
            "germek mümkün:", _fazla_vektorler(vs), "kontrol"))
    out.append(_madde("Sınav ipucu",
                      "Koşulun bir katı da doğrudur (ör. −x − y + z = 0 ile x + y − z = 0 aynı denklemdir). Sembolik "
                      "sağ tarafı sıfır satırda “çelişki” sanma; o satır cevabın kendisidir.", tur="ipucu"))
    return out


def _v_metin(liste) -> str:
    return "(" + ", ".join(str(x).replace("-", MINUS) for x in liste) + ")"


def _polinom(katsayilar) -> str:
    parcalar = []
    for us, c in enumerate(katsayilar):
        c = Fraction(c)
        if c == 0:
            continue
        x = "" if us == 0 else ("x" if us == 1 else "x" + _ust(us))
        mag = abs(c)
        t = (_f(mag) if (mag != 1 or us == 0) else "") + x
        if not parcalar:
            parcalar.append((MINUS if c < 0 else "") + t)
        else:
            parcalar.append((f" {MINUS} " if c < 0 else " + ") + t)
    return "".join(parcalar) or "0"


def _bilinmeyen(res: Dict) -> List[Dict]:
    vs = [_Fv(v) for v in res["vectors"]]
    k, r = len(vs), res["rank"]
    adlar = [f"p{_alt(i + 1)}" for i in range(k)]
    out: List[Dict] = []
    cozum = res["solution"]
    out.append(_madde(
        "Sıfır satırları → bilinmeyenler",
        "Eliminasyon sonunda iki sıfır satır kaldı. Sağ tarafları sıfır olmak zorunda; bu da c ve d’yi belirler:",
        [_kosul_metni(c) for c in res["conditions"]] + [", ".join(f"{a} = {_f(v)}" for a, v in cozum.items())],
        "denklem"))
    temsil = res.get("representation")
    if temsil:
        c = _Fv(temsil.get("coefficients") or temsil.get("particular"))
        hedef = arithmetic.linear_combination(vs, c)
        out.append(_madde(
            "Kontrol: polinom olarak",
            "Katsayı vektörlerini geri polinoma çevirelim:",
            [f"{_toplam([(c[i], adlar[i]) for i in range(k)])} = {_polinom(hedef)}  "
             f"{'✓' if [str(x) for x in hedef[2:]] == [cozum.get('c'), cozum.get('d')] else ''}"],
            "kontrol"))
        if temsil.get("status") == "infinite":
            out[-1]["metin"] += (" Bu temsil TEK değildir (rank < polinom sayısı): serbest katsayılar 0 seçildi; "
                                 "örneğin 2·p₁ + 3·p₃ de aynı polinomu verir.")
    out.append(_madde(
        "Anlamı",
        f"Dört polinom P₃ (boyut 4) içinde yalnızca rank = {r} boyutlu bir alt uzay gerer. Bu yüzden hedefin "
        "son iki katsayısı serbest değildi: ilk ikisi (1, 1) seçilince c ve d ZORUNLU olarak belirlendi.",
        []))
    if k > r:
        out.append(_madde("Fazla polinomlar", f"{k - r} polinom diğerlerinin birleşimidir:",
                          [s.replace("v", "p") for s in _fazla_vektorler(vs)], "kontrol"))
    out.append(_madde("Sınav ipucu",
                      "Polinom, matris, fonksiyon… hepsinde yöntem aynı: önce KATSAYI VEKTÖRÜNE çevir (sıra: sabit, x, x², …), "
                      "sonra ℝⁿ’deki gibi Gauss eliminasyonu yap.", tur="ipucu"))
    return out


def _bagimlilik(res: Dict) -> List[Dict]:
    vs = [_Fv(v) for v in res["vectors"]]
    k, m, r = len(vs), res["ambient_dim"], res["rank"]
    adlar = [f"v{_alt(i + 1)}" for i in range(k)]
    out: List[Dict] = []
    if res["independent"]:
        out.append(_madde("Son matrisi oku",
                          f"Her sütunda pivot var (rank = {r} = {k}): homojen sistemin tek çözümü c = 0 ⇒ BAĞIMSIZ."))
        if r == m:
            out.append(_madde("Anlamı", f"{k} bağımsız vektör ve {k} = boyut ⇒ {_R(m)}’ün bir bazı."))
        return out

    c = _Fv(res["relation"])
    sifir = arithmetic.linear_combination(vs, c)
    out.append(_madde(
        "Bağıntıyı oku",
        "Serbest değişkene 1 verip pivot değişkenleri çözünce sıfır olmayan bir çözüm çıktı:",
        [f"c = {_v(c)}",
         f"{_toplam([(c[i], adlar[i]) for i in range(k)])} = {_v(sifir)}  {'✓' if all(x == 0 for x in sifir) else '✗'}"],
        "kontrol"))
    j = max(i for i in range(k) if c[i] != 0)
    ifade = _toplam([(-c[i] / c[j], adlar[i]) for i in range(k) if i != j])
    yorum = f"Bağıntıyı {adlar[j]} için çöz: {adlar[j]} diğerlerinin doğrusal birleşimidir, yani yeni bir yön katmaz."
    if k == 3 and c == [1, -2, 1]:
        yorum += " Burada v₂ = (v₁ + v₃)/2: ortadaki vektör, diğer ikisinin tam ORTALAMASI (ardışık sayılar eşit aralıklı)."
    out.append(_madde("Hangi vektör fazla?", yorum, [f"{adlar[j]} = {ifade}"], "denklem"))

    baz = res["basis_indices"]
    out.append(_madde(
        "Geometrik anlamı ve baz",
        f"rank = {r} ⇒ vektörlerin hepsi {_geometri(r, m)} üzerinde. Gerilen uzayın boyutu {r}; bir baz: "
        f"{{{', '.join(adlar[i] for i in baz)}}} (pivot sütunlarına karşılık gelen ORİJİNAL vektörler).",
        _fazla_vektorler(vs) if len(res["relations"]) > 1 else [], "anlam"))
    if k == m:
        out.append(_madde("Sınav ipucu",
                          f"{k} vektör, {_R(m)}’te: sayı boyuta EŞİT olduğu hâlde bağımlı çıktı. “Sayı yetiyor, o hâlde "
                          "bağımsız/baz” demek yanlıştır; karar her zaman rank (pivot sayısı) ile verilir. Kare matriste kısa yol: det = 0 ⇔ bağımlı.",
                          tur="ipucu"))
    elif k > m:
        out.append(_madde("Sınav ipucu",
                          f"{k} > {m} = boyut olduğundan bağımlılık önceden belliydi (rank ≤ {m} < {k}); ama HANGİ vektörlerin "
                          "fazla olduğunu ve bazı bulmak için eliminasyon gerekir.", tur="ipucu"))
    return out


def yorumla(soru: Dict, res: Dict) -> List[Dict]:
    tip = soru["type"]
    if tip == "combination":
        return _birlesim(res)
    if tip == "conditions":
        return _kosullar(res, soru)
    if tip == "target_unknowns":
        return _bilinmeyen(res)
    if tip in ("dependence", "basis"):
        return _bagimlilik(res)
    return []
