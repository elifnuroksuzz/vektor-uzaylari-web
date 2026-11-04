"""Kesin sayısal aritmetik ve biçimlendirme.

Girdiler her zaman string olarak gelir ve ``Fraction`` ile kesin sayıya
çevrilir; JavaScript floating point'inden geçirilmez. Vektör/matris/polinom
işlemleri burada elle yazılmış döngülerle yapılır.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Iterable, List, Sequence

# Girdi başına güvenli karakter sınırı (API tarafında da kontrol edilir).
MAX_INPUT_CHARS = 80


class SayiHatasi(ValueError):
    """Kullanıcı girdisi geçersiz bir sayı olduğunda fırlatılır (Türkçe mesaj)."""


def parse_fraction(text: object) -> Fraction:
    """Bir string'i kesin ``Fraction``'a çevirir.

    Kabul edilenler: tam sayı (``4``), kesir (``-2/3``), sonlu ondalık
    (``0.25``). Boş hücre, sıfır payda, NaN/Infinity ve anlamsız metin için
    Türkçe :class:`SayiHatasi` fırlatır.
    """

    if isinstance(text, Fraction):
        return text
    if isinstance(text, bool):  # bool, int'in alt tipidir; kazara kabul etmeyelim.
        raise SayiHatasi("Sayı yerine mantıksal değer verildi.")
    if isinstance(text, int):
        return Fraction(text)
    if isinstance(text, float):
        raise SayiHatasi(
            "Sayılar metin olarak gönderilmelidir; float kesinliği kabul edilmez."
        )
    if not isinstance(text, str):
        raise SayiHatasi("Geçersiz sayı türü.")

    ham = text.strip()
    if ham == "":
        raise SayiHatasi("Boş hücre var; lütfen bir sayı girin.")
    if len(ham) > MAX_INPUT_CHARS:
        raise SayiHatasi("Sayı girdisi çok uzun.")

    dusuk = ham.lower()
    if dusuk in {"nan", "inf", "+inf", "-inf", "infinity", "-infinity"}:
        raise SayiHatasi("NaN veya sonsuz değer kabul edilmez.")

    try:
        if "/" in ham:
            pay_str, _, payda_str = ham.partition("/")
            pay = Fraction(pay_str.strip())
            payda = Fraction(payda_str.strip())
            if payda == 0:
                raise SayiHatasi("Payda sıfır olamaz.")
            return pay / payda
        return Fraction(ham)
    except SayiHatasi:
        raise
    except ZeroDivisionError:
        raise SayiHatasi("Payda sıfır olamaz.")
    except (ValueError, ArithmeticError):
        raise SayiHatasi(f"'{ham}' geçerli bir sayı değil.")


def parse_vector(values: Iterable[object]) -> List[Fraction]:
    """Bir dizilimi kesin kesir vektörüne çevirir."""

    return [parse_fraction(v) for v in values]


def parse_matrix(rows: Iterable[Iterable[object]]) -> List[List[Fraction]]:
    satirlar = [parse_vector(r) for r in rows]
    if satirlar:
        genislik = len(satirlar[0])
        for r in satirlar:
            if len(r) != genislik:
                raise SayiHatasi("Matris satırları eşit uzunlukta olmalıdır.")
    return satirlar


def format_fraction(value: Fraction) -> str:
    """Kesiri ``7/3`` ya da ``-1`` biçiminde string'e çevirir."""

    value = Fraction(value)
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def format_vector(vec: Sequence[Fraction]) -> List[str]:
    return [format_fraction(v) for v in vec]


# --- Elle yazılmış vektör/matris işlemleri -------------------------------


def vector_add(a: Sequence[Fraction], b: Sequence[Fraction]) -> List[Fraction]:
    if len(a) != len(b):
        raise SayiHatasi("Vektör boyutları eşit değil; toplanamaz.")
    sonuc: List[Fraction] = []
    for i in range(len(a)):
        sonuc.append(a[i] + b[i])
    return sonuc


def vector_sub(a: Sequence[Fraction], b: Sequence[Fraction]) -> List[Fraction]:
    if len(a) != len(b):
        raise SayiHatasi("Vektör boyutları eşit değil; çıkarılamaz.")
    return [a[i] - b[i] for i in range(len(a))]


def scalar_mul(scalar: Fraction, vec: Sequence[Fraction]) -> List[Fraction]:
    return [scalar * v for v in vec]


def linear_combination(
    vectors: Sequence[Sequence[Fraction]], coeffs: Sequence[Fraction]
) -> List[Fraction]:
    if len(vectors) != len(coeffs):
        raise SayiHatasi("Katsayı sayısı vektör sayısına eşit olmalı.")
    if not vectors:
        return []
    boyut = len(vectors[0])
    sonuc = [Fraction(0) for _ in range(boyut)]
    for vec, k in zip(vectors, coeffs):
        if len(vec) != boyut:
            raise SayiHatasi("Vektör boyutları eşit değil.")
        for i in range(boyut):
            sonuc[i] += k * vec[i]
    return sonuc


def transpose(matrix: Sequence[Sequence[Fraction]]) -> List[List[Fraction]]:
    if not matrix:
        return []
    satir = len(matrix)
    sutun = len(matrix[0])
    return [[matrix[r][c] for r in range(satir)] for c in range(sutun)]


def matrix_mul(
    a: Sequence[Sequence[Fraction]], b: Sequence[Sequence[Fraction]]
) -> List[List[Fraction]]:
    if not a or not b:
        return []
    if len(a[0]) != len(b):
        raise SayiHatasi("Matris boyutları çarpıma uygun değil.")
    ic = len(b)
    sonuc = [[Fraction(0) for _ in range(len(b[0]))] for _ in range(len(a))]
    for i in range(len(a)):
        for j in range(len(b[0])):
            toplam = Fraction(0)
            for k in range(ic):
                toplam += a[i][k] * b[k][j]
            sonuc[i][j] = toplam
    return sonuc


def columns_as_matrix(
    vectors: Sequence[Sequence[Fraction]],
) -> List[List[Fraction]]:
    """Vektörleri sütun kabul edip bileşen-denklemi satırlarına yerleştirir.

    Örneğin v1, v2 R³'te ise sonuç 3×2 matristir; i. satır her vektörün i.
    bileşenidir. Span/üyelik analizinin temel kuruluşu budur.
    """

    if not vectors:
        return []
    boyut = len(vectors[0])
    for v in vectors:
        if len(v) != boyut:
            raise SayiHatasi("Vektör boyutları eşit olmalı.")
    return [[vectors[j][i] for j in range(len(vectors))] for i in range(boyut)]
