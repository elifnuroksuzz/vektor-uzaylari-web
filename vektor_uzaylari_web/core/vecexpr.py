"""Küçük ve güvenli vektör/skaler ifade değerlendiricisi (kesin aritmetik).

Ders sahneleri ``"u+v"``, ``"(a+b)*v"``, ``"[r, 2*r]"``, ``"det(v1, v2)"``
gibi kısa ifadelerle yazılır; koordinatları bu modül ``Fraction`` ile hesaplar.
``eval``/``exec`` kullanılmaz: elle yazılmış bir ayrıştırıcıdır.

Dilbilgisi::

    ifade   := terim (('+' | '-') terim)*
    terim   := tekli (('*' | '/') tekli)*
    tekli   := '-' tekli | '+' tekli | sonek
    sonek   := birincil ('[' TAMSAYI ']')?          # 1 tabanlı bileşen
    birincil:= SAYI | AD | AD '(' ifade (',' ifade)* ')'
             | '(' ifade ')' | '[' ifade (',' ifade)* ']'

Değerler ya skaler (``Fraction``) ya da vektördür (``tuple`` of ``Fraction``).
"""

from __future__ import annotations

import re
from fractions import Fraction
from typing import Dict, List, Mapping, Tuple, Union

from .arithmetic import SayiHatasi, format_fraction

Deger = Union[Fraction, Tuple[Fraction, ...]]

MAX_IFADE = 200
MINUS = "−"

_TOKEN = re.compile(
    r"\s*(?:(?P<sayi>\d+(?:\.\d+)?)|(?P<ad>[A-Za-z_α-ωΑ-Ω][A-Za-z0-9_α-ω]*)|(?P<op>[-+*/()\[\],]))"
)


def _tokenize(metin: str) -> List[Tuple[str, str]]:
    if len(metin) > MAX_IFADE:
        raise SayiHatasi("İfade çok uzun.")
    konum = 0
    parcalar: List[Tuple[str, str]] = []
    metin = metin.replace("−", "-").replace("·", "*")
    while konum < len(metin):
        if metin[konum].isspace():
            konum += 1
            continue
        m = _TOKEN.match(metin, konum)
        if not m or m.end() == konum:
            raise SayiHatasi(f"İfade okunamadı: '{metin[konum:konum + 10]}'")
        tur = m.lastgroup
        parcalar.append((tur, m.group(tur)))
        konum = m.end()
    parcalar.append(("son", ""))
    return parcalar


def is_vector(x: Deger) -> bool:
    return isinstance(x, tuple)


def _topla(a: Deger, b: Deger, isaret: int) -> Deger:
    if is_vector(a) and is_vector(b):
        if len(a) != len(b):
            raise SayiHatasi("Farklı boyutlu vektörler toplanamaz.")
        return tuple(a[i] + isaret * b[i] for i in range(len(a)))
    if not is_vector(a) and not is_vector(b):
        return a + isaret * b
    raise SayiHatasi("Skaler ile vektör toplanamaz.")


def _carp(a: Deger, b: Deger) -> Deger:
    if is_vector(a) and is_vector(b):
        raise SayiHatasi("İki vektör çarpılamaz (skaler çarpım için dot(u, v) kullanın).")
    if is_vector(a):
        return tuple(b * x for x in a)
    if is_vector(b):
        return tuple(a * x for x in b)
    return a * b


def _bol(a: Deger, b: Deger) -> Deger:
    if is_vector(b):
        raise SayiHatasi("Vektöre bölünemez.")
    if b == 0:
        raise SayiHatasi("Sıfıra bölme.")
    if is_vector(a):
        return tuple(x / b for x in a)
    return a / b


def _det(u: Deger, v: Deger) -> Fraction:
    if not (is_vector(u) and is_vector(v) and len(u) == 2 and len(v) == 2):
        raise SayiHatasi("det(u, v) yalnızca iki 2B vektör için tanımlı.")
    return u[0] * v[1] - u[1] * v[0]


def _dot(u: Deger, v: Deger) -> Fraction:
    if not (is_vector(u) and is_vector(v) and len(u) == len(v)):
        raise SayiHatasi("dot(u, v) için aynı boyutlu iki vektör gerekir.")
    return sum((u[i] * v[i] for i in range(len(u))), Fraction(0))


def _abs(x: Deger) -> Fraction:
    if is_vector(x):
        raise SayiHatasi("abs yalnızca skaler için.")
    return abs(x)


_FONKSIYONLAR = {"det": (_det, 2), "dot": (_dot, 2), "abs": (_abs, 1)}


class _Ayristirici:
    def __init__(self, metin: str, ortam: Mapping[str, Deger]) -> None:
        self.p = _tokenize(metin)
        self.i = 0
        self.ortam = ortam

    def bak(self) -> Tuple[str, str]:
        return self.p[self.i]

    def al(self) -> Tuple[str, str]:
        t = self.p[self.i]
        self.i += 1
        return t

    def bekle(self, op: str) -> None:
        t = self.al()
        if t != ("op", op):
            raise SayiHatasi(f"İfadede '{op}' bekleniyordu.")

    def ifade(self) -> Deger:
        deger = self.terim()
        while self.bak() in (("op", "+"), ("op", "-")):
            op = self.al()[1]
            deger = _topla(deger, self.terim(), 1 if op == "+" else -1)
        return deger

    def terim(self) -> Deger:
        deger = self.tekli()
        while self.bak() in (("op", "*"), ("op", "/")):
            op = self.al()[1]
            sag = self.tekli()
            deger = _carp(deger, sag) if op == "*" else _bol(deger, sag)
        return deger

    def tekli(self) -> Deger:
        if self.bak() == ("op", "-"):
            self.al()
            return _carp(Fraction(-1), self.tekli())
        if self.bak() == ("op", "+"):
            self.al()
            return self.tekli()
        return self.sonek()

    def sonek(self) -> Deger:
        deger = self.birincil()
        if self.bak() == ("op", "["):
            self.al()
            tur, metin = self.al()
            if tur != "sayi" or "." in metin:
                raise SayiHatasi("Bileşen indeksi pozitif tam sayı olmalı.")
            self.bekle("]")
            k = int(metin)
            if not is_vector(deger) or not 1 <= k <= len(deger):
                raise SayiHatasi("Geçersiz bileşen indeksi.")
            deger = deger[k - 1]
        return deger

    def birincil(self) -> Deger:
        tur, metin = self.al()
        if tur == "sayi":
            return Fraction(metin)
        if tur == "ad":
            if self.bak() == ("op", "(") and metin in _FONKSIYONLAR:
                fonk, n = _FONKSIYONLAR[metin]
                self.al()
                argumanlar = [self.ifade()]
                while self.bak() == ("op", ","):
                    self.al()
                    argumanlar.append(self.ifade())
                self.bekle(")")
                if len(argumanlar) != n:
                    raise SayiHatasi(f"{metin} {n} argüman alır.")
                return fonk(*argumanlar)
            if metin not in self.ortam:
                raise SayiHatasi(f"Tanımsız ad: {metin}")
            return self.ortam[metin]
        if (tur, metin) == ("op", "("):
            deger = self.ifade()
            self.bekle(")")
            return deger
        if (tur, metin) == ("op", "["):
            bilesenler = [self.ifade()]
            while self.bak() == ("op", ","):
                self.al()
                bilesenler.append(self.ifade())
            self.bekle("]")
            for b in bilesenler:
                if is_vector(b):
                    raise SayiHatasi("Vektör bileşeni skaler olmalı.")
            return tuple(bilesenler)
        raise SayiHatasi("İfade beklenmedik biçimde bitti.")


def evaluate(metin: str, ortam: Mapping[str, Deger]) -> Deger:
    """İfadeyi verilen ortamda kesin olarak hesaplar."""

    a = _Ayristirici(str(metin), ortam)
    deger = a.ifade()
    if a.bak()[0] != "son":
        raise SayiHatasi("İfadenin sonunda fazladan karakter var.")
    return deger


# --- Biçimlendirme --------------------------------------------------------


def format_scalar_display(x: Fraction) -> str:
    """Ekran için: gerçek eksi işareti ile (ör. ``−7/3``)."""

    s = format_fraction(x)
    return s.replace("-", MINUS)


def format_display(x: Deger) -> str:
    if is_vector(x):
        return "(" + ", ".join(format_scalar_display(v) for v in x) + ")"
    return format_scalar_display(x)


def to_json(x: Deger):
    """Sahne koordinatları için JSON değeri (string kesirler)."""

    if is_vector(x):
        return [format_fraction(v) for v in x]
    return format_fraction(x)


_YER_TUTUCU = re.compile(r"\{\{(.+?)\}\}")


def fill_placeholders(metin: str, ortam: Mapping[str, Deger]) -> str:
    """``{{ifade}}`` yer tutucularını hesaplanmış değerle değiştirir."""

    if not metin or "{{" not in metin:
        return metin

    def degistir(m: "re.Match[str]") -> str:
        return format_display(evaluate(m.group(1), ortam))

    return _YER_TUTUCU.sub(degistir, metin)


def environment(base: Dict[str, Deger]) -> Dict[str, Deger]:
    """Ortama sıfır vektörü ``O``'yu (ilk vektörün boyutunda) ekler."""

    ortam = dict(base)
    boyut = 2
    for v in base.values():
        if is_vector(v):
            boyut = len(v)
            break
    ortam.setdefault("O", tuple(Fraction(0) for _ in range(boyut)))
    return ortam
