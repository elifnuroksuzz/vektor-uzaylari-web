"""Yüksek seviyeli analizler: doğrusal birleşim, span üyeliği, homojen koşullar,
aksiyom hesapları ve alt uzay örnekleri.

Bütün kararlar :mod:`core.elimination` üzerinden kesin aritmetikle verilir.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Dict, List, Optional, Sequence

from . import arithmetic
from .arithmetic import SayiHatasi, format_fraction, format_vector
from .elimination import Eliminator, fmt_entry
from .expressions import LinearExpr


# --- Doğrusal birleşim / üyelik (sayısal) --------------------------------


def solve_combination(
    vectors: Sequence[Sequence[Fraction]], target: Sequence[Fraction]
) -> Dict:
    """Ax = hedef'i çözer (A sütunları = vektörler).

    ``status`` alanı: ``unique`` | ``infinite`` | ``inconsistent``.
    """

    if not vectors:
        raise SayiHatasi("En az bir vektör gerekli.")
    m = len(target)
    for v in vectors:
        if len(v) != m:
            raise SayiHatasi("Hedef ve vektör boyutları eşit olmalı.")

    A = arithmetic.columns_as_matrix(vectors)
    rhs = [Fraction(t) for t in target]
    elim = Eliminator(A, rhs).rref()

    k = len(vectors)
    tutarsiz = False
    for r in range(elim.m):
        if all(elim.A[r][c] == 0 for c in range(elim.n)) and elim.rhs[r] != 0:
            tutarsiz = True
            break

    sonuc: Dict[str, object] = {
        "vectors": [format_vector(v) for v in vectors],
        "target": format_vector(target),
        "rank": elim.rank,
        "num_vectors": k,
        "ambient_dim": m,
        "steps": elim.steps,
        "pivots": elim.pivots,
        "final_matrix": [[format_fraction(v) for v in row] for row in elim.A],
        "final_rhs": [format_fraction(v) for v in elim.rhs],
    }

    if tutarsiz:
        sonuc["status"] = "inconsistent"
        sonuc["member"] = False
        return sonuc

    pivot_cols = elim.pivot_columns()
    free_cols = elim.free_columns()
    pivot_row_of = {p["column"]: p["row"] for p in elim.pivots}

    # Özel çözüm (serbest değişkenler = 0)
    ozel = [Fraction(0)] * k
    for c in pivot_cols:
        ozel[c] = elim.rhs[pivot_row_of[c]]

    sonuc["member"] = True
    if not free_cols:
        sonuc["status"] = "unique"
        sonuc["coefficients"] = format_vector(ozel)
    else:
        sonuc["status"] = "infinite"
        sonuc["particular"] = format_vector(ozel)
        yonler = []
        for f in free_cols:
            d = [Fraction(0)] * k
            d[f] = Fraction(1)
            for c in pivot_cols:
                d[c] = -elim.A[pivot_row_of[c]][f]
            yonler.append(format_vector(d))
        sonuc["free_columns"] = free_cols
        sonuc["directions"] = yonler
        sonuc["note"] = (
            "Serbest katsayı(lar) sıfır olmak zorunda değildir; tek bir temsil "
            "göstermek için seçilmiştir."
        )
    return sonuc


# --- Homojen koşullar (sembolik sağ taraf) -------------------------------


def homogeneous_conditions(
    vectors: Sequence[Sequence[Fraction]], symbols: Sequence[str]
) -> Dict:
    """Span(vektörler) için hedef (sembolik) üzerindeki koşulları bulur.

    ``Col(A) = ker(H)``. HA = 0 ve rank(H) = m - rank(A) kontrol edilir.
    """

    if not vectors:
        raise SayiHatasi("En az bir vektör gerekli.")
    m = len(symbols)
    for v in vectors:
        if len(v) != m:
            raise SayiHatasi("Sembol sayısı vektör boyutuna eşit olmalı.")

    A = arithmetic.columns_as_matrix(vectors)
    rhs = [LinearExpr.symbol(s) for s in symbols]
    elim = Eliminator(A, rhs, symbols=symbols).ref()

    kosullar: List[LinearExpr] = []
    for r in range(elim.m):
        if all(elim.A[r][c] == 0 for c in range(elim.n)):
            ifade = elim.rhs[r]
            if isinstance(ifade, LinearExpr) and not ifade.is_zero():
                kosullar.append(ifade.clear_denominators())

    H = [k.coefficients(symbols) for k in kosullar]
    dogrulama = _verify_conditions(H, A, elim.rank, m)

    return {
        "vectors": [format_vector(v) for v in vectors],
        "symbols": list(symbols),
        "rank": elim.rank,
        "ambient_dim": m,
        "num_vectors": len(vectors),
        "spans_ambient": elim.rank == m,
        "steps": elim.steps,
        "pivots": elim.pivots,
        "conditions": [k.format(symbols) + " = 0" for k in kosullar],
        "condition_exprs": [k.to_json(symbols) for k in kosullar],
        "H": [[format_fraction(v) for v in row] for row in H],
        "verification": dogrulama,
        "final_rhs": [fmt_entry(v, symbols) for v in elim.rhs],
    }


def _verify_conditions(H, A, rankA, m) -> Dict:
    """HA = 0 ve rank(H) = m - rank(A) doğrulamasını yapar."""

    HA_sifir = True
    if H:
        HA = arithmetic.matrix_mul(H, A)
        for row in HA:
            for v in row:
                if v != 0:
                    HA_sifir = False
    rankH = 0
    if H:
        rankH = Eliminator(H).ref().rank
    beklenen = m - rankA
    return {
        "HA_is_zero": HA_sifir,
        "rank_H": rankH,
        "expected_rank_H": beklenen,
        "rank_matches": rankH == beklenen,
        "ok": HA_sifir and rankH == beklenen,
    }


def solve_target_unknowns(
    vectors: Sequence[Sequence[Fraction]], components: Sequence[str]
) -> Dict:
    """Hedef vektörün bazı bileşenleri bilinmeyen olduğunda onları bulur.

    ``components`` listesinde her eleman ya sayı stringidir (sabit bileşen) ya
    da tek harfli bir bilinmeyendir (ör. ``c``, ``d``). Vektörler sütun kabul
    edilip sembolik sağ tarafla indirgenir; sıfır katsayı satırlarının verdiği
    koşullar bilinmeyenler için çözülür. 15. soru bu yolla çözülür.
    """

    unknowns: List[str] = []
    rhs: List[LinearExpr] = []
    for parca in components:
        try:
            deger = arithmetic.parse_fraction(parca)
            rhs.append(LinearExpr.constant(deger))
        except SayiHatasi:
            ad = str(parca).strip()
            rhs.append(LinearExpr.symbol(ad))
            if ad not in unknowns:
                unknowns.append(ad)

    m = len(components)
    for v in vectors:
        if len(v) != m:
            raise SayiHatasi("Bileşen sayısı vektör boyutuna eşit olmalı.")

    A = arithmetic.columns_as_matrix(vectors)
    elim = Eliminator(A, rhs, symbols=unknowns).ref()

    kosullar: List[LinearExpr] = []
    for r in range(elim.m):
        if all(elim.A[r][c] == 0 for c in range(elim.n)):
            ifade = elim.rhs[r]
            if isinstance(ifade, LinearExpr) and not ifade.is_zero():
                kosullar.append(ifade)

    # Koşulları bilinmeyenler için çöz: katsayı·unknown = -sabit
    coeff = [[k.terms.get(s, Fraction(0)) for s in unknowns] for k in kosullar]
    sab = [-k.const for k in kosullar]
    cozum_degerleri: Dict[str, str] = {}
    temsil = None
    if coeff and unknowns:
        coz = Eliminator(coeff, sab).rref()
        tutarsiz = any(
            all(coz.A[r][c] == 0 for c in range(coz.n)) and coz.rhs[r] != 0
            for r in range(coz.m)
        )
        if not tutarsiz and not coz.free_columns():
            prow = {p["column"]: p["row"] for p in coz.pivots}
            degerler = {}
            for c in range(len(unknowns)):
                degerler[unknowns[c]] = coz.rhs[prow[c]]
            cozum_degerleri = {s: format_fraction(v) for s, v in degerler.items()}
            # Bir temsil: bilinen hedefi kurup katsayıları bul.
            hedef = []
            for parca in components:
                try:
                    hedef.append(arithmetic.parse_fraction(parca))
                except SayiHatasi:
                    hedef.append(degerler[str(parca).strip()])
            temsil = solve_combination(vectors, hedef)

    return {
        "vectors": [format_vector(v) for v in vectors],
        "components": list(components),
        "unknowns": unknowns,
        "rank": elim.rank,
        "steps": elim.steps,
        "pivots": elim.pivots,
        "conditions": [k.format(unknowns) + " = 0" for k in kosullar],
        "solution": cozum_degerleri,
        "representation": temsil,
    }


def span_analysis(
    vectors: Sequence[Sequence[Fraction]],
    symbols: Sequence[str],
    target: Optional[Sequence[Fraction]] = None,
) -> Dict:
    """Hem homojen koşulları hem (hedef verilirse) sayısal üyeliği döndürür."""

    sonuc = {"homogeneous_conditions": homogeneous_conditions(vectors, symbols)}
    sonuc["ambient_span"] = sonuc["homogeneous_conditions"]["spans_ambient"]
    if target is not None:
        sonuc["membership"] = solve_combination(vectors, target)
    return sonuc


# --- Aksiyom hesapları (V1-V8) -------------------------------------------

_AXIOM_TANIM = {
    "V1": ("u+(v+w)", "(u+v)+w"),
    "V2": ("v+0", "v"),
    "V3": ("v+(-v)", "0"),
    "V4": ("u+v", "v+u"),
    "V5": ("c(u+v)", "cu+cv"),
    "V6": ("(a+b)v", "av+bv"),
    "V7": ("(ab)v", "a(bv)"),
    "V8": ("1v", "v"),
}


def evaluate_axiom(
    rule_id: str,
    u: Sequence[Fraction],
    v: Sequence[Fraction],
    w: Sequence[Fraction],
    a: Fraction,
    b: Fraction,
    c: Fraction,
) -> Dict:
    add = arithmetic.vector_add
    mul = arithmetic.scalar_mul
    boyut = len(v)
    sifir = [Fraction(0)] * boyut

    if rule_id == "V1":
        sol, sag = add(u, add(v, w)), add(add(u, v), w)
    elif rule_id == "V2":
        sol, sag = add(v, sifir), v
    elif rule_id == "V3":
        sol, sag = add(v, mul(Fraction(-1), v)), sifir
    elif rule_id == "V4":
        sol, sag = add(u, v), add(v, u)
    elif rule_id == "V5":
        sol, sag = mul(c, add(u, v)), add(mul(c, u), mul(c, v))
    elif rule_id == "V6":
        sol, sag = mul(a + b, v), add(mul(a, v), mul(b, v))
    elif rule_id == "V7":
        sol, sag = mul(a * b, v), mul(a, mul(b, v))
    elif rule_id == "V8":
        sol, sag = mul(Fraction(1), v), v
    else:
        raise SayiHatasi(f"Bilinmeyen aksiyom: {rule_id}")

    sol_str = _AXIOM_TANIM[rule_id][0]
    sag_str = _AXIOM_TANIM[rule_id][1]
    return {
        "rule_id": rule_id,
        "left_label": sol_str,
        "right_label": sag_str,
        "left": format_vector(sol),
        "right": format_vector(sag),
        "equal": sol == sag,
        "diagram": _axiom_diagram(rule_id, u, v, w, a, b, c, sol),
    }


def _axiom_diagram(rule_id, u, v, w, a, b, c, left):
    """Her aksiyom için çizilecek 2B vektörleri (sunucu hesaplı) döndürür.

    ``coords`` okun ucudur; ``from`` verilirse ok oradan başlar (uç-uca
    kurulum). Girişler önce, sonuç en sonda gelir (arayüz sırayla belirtir).
    Böylece toplama/dağılma gibi aksiyomlarda sonucun parçalardan nasıl
    kurulduğu görülür.
    """

    if len(v) != 2:
        return []  # yalnızca iki boyutlu girişlerde çiz

    add = arithmetic.vector_add
    mul = arithmetic.scalar_mul

    def D(tip, label, kind, base=None, offset=False):
        d = {"coords": format_vector(tip), "label": label, "kind": kind}
        if base is not None:
            d["from"] = format_vector(base)
        if offset:
            d["offset"] = True
        return d

    neg = [-x for x in v]

    if rule_id == "V1":
        uv = add(u, v)
        return [
            D(u, "u", "giris"),
            D(uv, "v", "ara", base=u),            # u'nun ucundan v
            D(left, "w", "ara", base=uv),          # (u+v)'nin ucundan w
            D(left, "u+(v+w)", "sonuc"),
        ]
    if rule_id == "V2":
        return [D(v, "v", "giris"), D(left, "v+0", "sonuc")]  # 0 eklemek değiştirmez
    if rule_id == "V3":
        return [D(v, "v", "giris"), D(neg, "-v", "ara"),
                D(left, "v+(-v)=0", "sonuc")]
    if rule_id == "V4":
        return [
            D(u, "u", "giris"),
            D(left, "v", "ara", base=u),           # u'nun ucundan v → u+v
            D(left, "u+v", "sonuc"),
        ]
    if rule_id == "V5":
        cu = mul(c, u)
        return [
            D(cu, "cu", "giris"),
            D(left, "cv", "ara", base=cu),         # cu'nun ucundan cv → cu+cv
            D(left, "c(u+v)", "sonuc"),
        ]
    if rule_id == "V6":
        av = mul(a, v)
        # av, bv, (a+b)v hepsi v'nin katı (kolineer); bv kurulumunu paralel
        # kaydırarak görünür kıl.
        return [
            D(av, "av", "giris"),
            D(left, "bv", "ara", base=av, offset=True),
            D(left, "(a+b)v", "sonuc"),
        ]
    if rule_id == "V7":
        bv = mul(b, v)
        return [D(v, "v", "giris"), D(bv, "bv", "ara"),
                D(left, "(ab)v", "sonuc")]
    if rule_id == "V8":
        return [D(v, "v", "giris"), D(left, "1v", "sonuc")]
    return []


# --- Doğrusal bağımlılık / bağımsızlık / baz (4.2) -----------------------


def _integerize(vec: Sequence[Fraction]) -> List[Fraction]:
    """Bir yön vektörünü en sade tam sayılı biçime getirir (ilk sıfırdan farklı > 0)."""

    from math import gcd

    payda = 1
    for x in vec:
        payda = payda * x.denominator // gcd(payda, x.denominator)
    tam = [x * payda for x in vec]
    ortak = 0
    for x in tam:
        ortak = gcd(ortak, int(abs(x)))
    if ortak > 1:
        tam = [x / ortak for x in tam]
    for x in tam:
        if x != 0:
            if x < 0:
                tam = [-y for y in tam]
            break
    return [Fraction(x) for x in tam]


def null_space(vectors: Sequence[Sequence[Fraction]]) -> Dict:
    """c₁v₁ + … + cₖvₖ = 0 denkleminin çözüm uzayının bir bazını bulur.

    Vektörler sütun olarak yerleştirilir; RREF'te her serbest sütun bir temel
    çözüm verir. Bağımsızlık ⇔ serbest sütun yok ⇔ rank = vektör sayısı.
    """

    if not vectors:
        raise SayiHatasi("En az bir vektör gerekli.")
    A = arithmetic.columns_as_matrix(vectors)
    elim = Eliminator(A, [Fraction(0)] * len(A)).rref()
    pivot_row_of = {p["column"]: p["row"] for p in elim.pivots}
    temel = []
    for f in elim.free_columns():
        d = [Fraction(0)] * elim.n
        d[f] = Fraction(1)
        for c in elim.pivot_columns():
            d[c] = -elim.A[pivot_row_of[c]][f]
        temel.append(_integerize(d))
    return {"elim": elim, "basis": temel}


def dependence_analysis(vectors: Sequence[Sequence[Fraction]]) -> Dict:
    """Bağımlılık kararı, sıfır olmayan bir bağıntı ve gerilen uzay için baz.

    Baz, indirgenmiş matrisin değil, pivot indekslerine karşılık gelen
    ORİJİNAL vektörlerden seçilir.
    """

    sonuc = null_space(vectors)
    elim = sonuc["elim"]
    temel = sonuc["basis"]
    k = len(vectors)
    pivotlar = elim.pivot_columns()
    bagimsiz = not temel
    iliskiler = []
    for d in temel:
        kontrol = arithmetic.linear_combination(vectors, d)
        if any(x != 0 for x in kontrol):  # pragma: no cover - motor güvencesi
            raise SayiHatasi("İç hata: bulunan bağıntı sıfır vermedi.")
        iliskiler.append(format_vector(d))
    return {
        "vectors": [format_vector(v) for v in vectors],
        "num_vectors": k,
        "ambient_dim": len(vectors[0]),
        "rank": elim.rank,
        "independent": bagimsiz,
        "relations": iliskiler,
        "relation": iliskiler[0] if iliskiler else None,
        "pivot_columns": pivotlar,
        "basis_indices": pivotlar,
        "basis": [format_vector(vectors[c]) for c in pivotlar],
        "spans_ambient": elim.rank == len(vectors[0]),
        "is_basis_of_ambient": bagimsiz and elim.rank == len(vectors[0]),
        "steps": elim.steps,
        "pivots": elim.pivots,
        "reason": (
            "Her katsayı sütununda pivot var: c₁v₁+…+cₖvₖ = 0 yalnızca sıfır "
            "katsayılarla sağlanır."
            if bagimsiz
            else f"rank = {elim.rank} < {k} = vektör sayısı: serbest değişken var, "
            "sıfır olmayan katsayılarla sıfır elde edilir."
        ),
    }
