"""Vektör Uzayları matematik motoru.

Bu paket saf standart kütüphane ile yazılmıştır. Hazır bir matris çözücüsü
(NumPy, SymPy vb.) kullanılmaz; bütün satır işlemleri ve çözümler elle
yazılmış döngülerle, kesin aritmetik için ``fractions.Fraction`` ile yapılır.
"""

from . import arithmetic, elimination, expressions, analysis, guided_parameters

__all__ = [
    "arithmetic",
    "elimination",
    "expressions",
    "analysis",
    "guided_parameters",
]
