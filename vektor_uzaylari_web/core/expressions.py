"""Sembolik sağ taraf için basit doğrusal ifade sınıfı.

Hazır bir CAS yazmak yerine yalnızca ``sabit + Σ katsayı·sembol`` biçiminde
doğrusal ifadeleri destekleriz. İki sembolik ifadeyi çarpmak gerekmez; sadece
toplama, çıkarma ve rasyonel sayıyla çarpma vardır. Bu, 19/20/21 gibi sembolik
sağ taraflı sorularda satır işlemlerini sembolik olarak yürütmeye yeter.
"""

from __future__ import annotations

from fractions import Fraction
from math import gcd
from typing import Dict, List, Mapping, Sequence

from .arithmetic import SayiHatasi, format_fraction


class LinearExpr:
    """``const`` (Fraction) + ``terms`` (sembol -> Fraction)."""

    __slots__ = ("const", "terms")

    def __init__(
        self, const: object = 0, terms: Mapping[str, Fraction] | None = None
    ) -> None:
        self.const = Fraction(const)
        self.terms: Dict[str, Fraction] = {}
        if terms:
            for sembol, kat in terms.items():
                kat = Fraction(kat)
                if kat != 0:
                    self.terms[sembol] = kat

    # --- kurucular -------------------------------------------------------
    @classmethod
    def symbol(cls, name: str) -> "LinearExpr":
        return cls(0, {name: Fraction(1)})

    @classmethod
    def constant(cls, value: object) -> "LinearExpr":
        return cls(value, None)

    @classmethod
    def coerce(cls, value: object) -> "LinearExpr":
        if isinstance(value, LinearExpr):
            return value
        return cls.constant(Fraction(value))

    # --- aritmetik -------------------------------------------------------
    def __add__(self, other: object) -> "LinearExpr":
        o = LinearExpr.coerce(other)
        yeni = dict(self.terms)
        for s, k in o.terms.items():
            yeni[s] = yeni.get(s, Fraction(0)) + k
        return LinearExpr(self.const + o.const, yeni)

    __radd__ = __add__

    def __sub__(self, other: object) -> "LinearExpr":
        return self + (LinearExpr.coerce(other) * Fraction(-1))

    def __rsub__(self, other: object) -> "LinearExpr":
        return LinearExpr.coerce(other) - self

    def __mul__(self, scalar: object) -> "LinearExpr":
        if isinstance(scalar, LinearExpr):
            if scalar.terms:
                raise SayiHatasi("İki sembolik ifade çarpılamaz.")
            scalar = scalar.const
        k = Fraction(scalar)
        return LinearExpr(
            self.const * k, {s: v * k for s, v in self.terms.items()}
        )

    __rmul__ = __mul__

    def __neg__(self) -> "LinearExpr":
        return self * Fraction(-1)

    # --- yardımcılar -----------------------------------------------------
    def is_zero(self) -> bool:
        return self.const == 0 and not self.terms

    def substitute(self, values: Mapping[str, object]) -> Fraction:
        toplam = self.const
        for s, k in self.terms.items():
            if s not in values:
                raise SayiHatasi(f"'{s}' için değer verilmedi.")
            toplam += k * Fraction(values[s])
        return toplam

    def coefficients(self, symbols: Sequence[str]) -> List[Fraction]:
        """Verilen sembol sırasına göre katsayı vektörü (sabit hariç)."""

        return [self.terms.get(s, Fraction(0)) for s in symbols]

    def clear_denominators(self) -> "LinearExpr":
        """İfadeyi, katsayıları tam sayı olacak şekilde ölçekler.

        Koşul ``ifade = 0`` olduğundan sabitle ölçek değişmez; yalnızca
        eşdeğer bir temsil üretilir. Böylece ``z - x/4 + 7y/4`` yerine
        ``-x + 7y + 4z`` gösterilir.
        """

        paydalar = [self.const.denominator] + [
            k.denominator for k in self.terms.values()
        ]
        lcm = 1
        for d in paydalar:
            lcm = lcm * d // gcd(lcm, d)
        if lcm == 1:
            return LinearExpr(self.const, dict(self.terms))
        olcek = Fraction(lcm)
        return self * olcek

    def format(self, symbols: Sequence[str] | None = None) -> str:
        """İnsan tarafından okunabilir string (ör. ``-x + 7y + 4z``)."""

        parcalar: List[str] = []
        sirali = symbols if symbols is not None else sorted(self.terms)
        for s in sirali:
            k = self.terms.get(s, Fraction(0))
            if k == 0:
                continue
            parcalar.append(_terim_yaz(k, s, not parcalar))
        if self.const != 0 or not parcalar:
            parcalar.append(_sabit_yaz(self.const, not parcalar))
        return "".join(parcalar) if parcalar else "0"

    def to_json(self, symbols: Sequence[str] | None = None) -> dict:
        sirali = symbols if symbols is not None else sorted(self.terms)
        return {
            "const": format_fraction(self.const),
            "terms": {s: format_fraction(self.terms[s]) for s in sirali if s in self.terms},
            "text": self.format(symbols),
        }

    def __repr__(self) -> str:  # pragma: no cover - sadece hata ayıklama
        return f"LinearExpr({self.format()})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LinearExpr):
            return NotImplemented
        return self.const == other.const and self.terms == other.terms


def _terim_yaz(k: Fraction, sembol: str, ilk: bool) -> str:
    isaret = "-" if k < 0 else ("" if ilk else "+")
    mutlak = abs(k)
    if mutlak == 1:
        govde = sembol
    else:
        govde = f"{format_fraction(mutlak)}{sembol}"
    return f"{isaret}{govde}" if ilk else f" {isaret} {govde}"


def _sabit_yaz(c: Fraction, ilk: bool) -> str:
    if ilk:
        return format_fraction(c)
    isaret = "-" if c < 0 else "+"
    return f" {isaret} {format_fraction(abs(c))}"
