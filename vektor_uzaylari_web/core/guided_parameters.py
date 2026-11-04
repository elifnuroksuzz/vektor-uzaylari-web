"""16. soru için rehberli parametre çözümü.

Katsayı matrisinde ``a`` parametresi vardır. Genel sembolik pivotlama yapmak
yerine doğrulanmış açık cebir adımlarını ve ``a = 1`` / ``a = -1`` / diğer
değerler dallarını sunarız. Sayısal ``a, b`` girildiğinde sonuç genel Fraction
motoruyla yeniden hesaplanır. ``a``'ya bağlı ifadeye bölmeden önce sıfır dalı
ayrılır.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Dict, Optional

from .analysis import solve_combination
from .arithmetic import SayiHatasi, format_fraction, parse_fraction

B_ESIK = Fraction(9, 4)  # a = -1 dalında içeride olma koşulu: b = 9/4.


def _vectors(a: Fraction):
    """``a`` parametresine göre dört vektörü üretir (sütun olarak kullanılacak)."""

    return [
        [Fraction(-1), Fraction(1), Fraction(-1), Fraction(1)],
        [Fraction(1), a, Fraction(1), Fraction(-1)],
        [Fraction(-2) * a, -a, Fraction(-2) * a + 1, Fraction(1) + 2 * a],
        [Fraction(-1), Fraction(3), a - 1, Fraction(2)],
    ]


def _target(b: Fraction):
    return [-b, Fraction(4), Fraction(0), 2 * b - 2]


def classify(a: Fraction, b: Fraction) -> Dict:
    """Kapalı-form sınıflandırma: hedef vektör alt uzayda mı (içeride mi)?

    İstenen DIŞARIDA koşulu: ``a = 1`` (her b) VEYA ``a = -1 ve b != 9/4``.
    """

    a = Fraction(a)
    b = Fraction(b)
    if a == 1:
        disarida = True
        dal = "a = 1"
        aciklama = "a = 1 dalında 0 = -2 çelişkisi doğar; her b için dışarıdadır."
    elif a == -1:
        disarida = b != B_ESIK
        dal = "a = -1"
        karsilastirma = "≠" if disarida else "="
        aciklama = (
            f"a = -1 dalında içeride olma koşulu b = {format_fraction(B_ESIK)}'tür; "
            f"b {karsilastirma} {format_fraction(B_ESIK)}."
        )
    else:
        disarida = False
        dal = "a ≠ ±1"
        aciklama = "a ≠ ±1 dalında sistem her b için çözülebilir; vektör içeridedir."
    return {
        "a": format_fraction(a),
        "b": format_fraction(b),
        "branch": dal,
        "is_outside": disarida,
        "is_inside": not disarida,
        "explanation": aciklama,
    }


def evaluate_parameter(a_text: str, b_text: str) -> Dict:
    """Sayısal a, b için sonucu hem kapalı-formla hem Fraction motoruyla hesaplar."""

    a = parse_fraction(a_text)
    b = parse_fraction(b_text)

    kapali = classify(a, b)

    vectors = _vectors(a)
    target = _target(b)
    cozum = solve_combination(vectors, target)
    motor_icerde = bool(cozum.get("member"))

    tutarli = motor_icerde == kapali["is_inside"]

    return {
        "a": format_fraction(a),
        "b": format_fraction(b),
        "closed_form": kapali,
        "engine": {
            "status": cozum["status"],
            "member": motor_icerde,
            "rank": cozum["rank"],
        },
        "is_inside": motor_icerde,
        "is_outside": not motor_icerde,
        "consistent": tutarli,
        "solve": cozum,
    }


def guided_derivation() -> Dict:
    """Tahtada gösterilecek doğrulanmış türetme ve dallar (statik veri değil,
    açıkça rehberli kapsam)."""

    return {
        "scope": "Rehberli parametre çözümü (genel sembolik pivotlama değildir).",
        "unknown_labels": ["λ1", "λ2", "λ3", "λ4"],
        "equations": [
            "−λ1 + λ2 − 2aλ3 − λ4 = −b",
            "λ1 + aλ2 − aλ3 + 3λ4 = 4",
            "−λ1 + λ2 + (1−2a)λ3 + (a−1)λ4 = 0",
            "λ1 − λ2 + (1+2a)λ3 + 2λ4 = 2b − 2",
        ],
        "derived": [
            "(a+1)λ2 − 3aλ3 + 2λ4 = 4 − b",
            "λ3 + aλ4 = b",
            "λ3 + λ4 = b − 2",
            "Fark: (1−a)λ4 = −2",
        ],
        "branches": [
            {
                "case": "a = 1",
                "result": "0 = −2 ÇELİŞKİSİ → her b için DIŞARIDA.",
            },
            {
                "case": "a ≠ ±1",
                "result": "λ4, λ3, λ2, λ1 sırayla bulunur → her b için İÇERİDE.",
            },
            {
                "case": "a = −1",
                "result": (
                    "λ4 = −1, λ3 = b−1; 3(b−1)−2 = 4−b → "
                    "içeride olma koşulu b = 9/4."
                ),
            },
        ],
        "answer": "DIŞARIDA: a = 1 (her b) VEYA a = −1 ve b ≠ 9/4.",
        "test_points": [
            {"a": "1", "b": "0", "expected": "outside"},
            {"a": "-1", "b": "9/4", "expected": "inside"},
            {"a": "-1", "b": "0", "expected": "outside"},
            {"a": "0", "b": "0", "expected": "inside"},
        ],
    }
