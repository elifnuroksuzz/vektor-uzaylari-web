"""Elle yazılmış satır indirgeme (REF / RREF) ve çözüm.

Katsayı matrisi ``A`` (Fraction girdileri) ile sağ taraf ``rhs`` birlikte
indirgenir. Sağ taraf ya sayısal (Fraction) ya da sembolik (:class:`LinearExpr`)
olabilir; her satır işlemi her ikisine birlikte uygulanır. Genişletilmiş
matriste sağ taraf ayrı tutulur, böylece pivot sayımına katılmaz.

Her işlem yapılandırılmış bir adım nesnesi üretir: önceki/sonraki matris, sağ
taraf, kullanılan satırlar, işlem metni, kısa gerekçe ve hücre hesapları.
"""

from __future__ import annotations

import copy
from fractions import Fraction
from typing import List, Optional, Sequence

from .arithmetic import SayiHatasi, format_fraction
from .expressions import LinearExpr

MINUS = "−"  # gerçek eksi işareti (okunur çıktı için)


def fmt_entry(x, symbols: Optional[Sequence[str]] = None) -> str:
    if isinstance(x, LinearExpr):
        return x.format(symbols)
    return format_fraction(x)


def _snapshot(matrix, symbols):
    return [[format_fraction(v) for v in row] for row in matrix]


def _rhs_snapshot(rhs, symbols):
    if rhs is None:
        return None
    return [fmt_entry(v, symbols) for v in rhs]


def _op_combine_text(i: int, j: int, factor: Fraction) -> str:
    if factor >= 0:
        isaret = MINUS
        mag = factor
    else:
        isaret = "+"
        mag = -factor
    magstr = "" if mag == 1 else f"{format_fraction(mag)}"
    return f"R{i + 1} ← R{i + 1} {isaret} {magstr}R{j + 1}"


def _op_scale_text(i: int, factor: Fraction) -> str:
    return f"R{i + 1} ← {format_fraction(factor)}·R{i + 1}"


def _op_swap_text(i: int, j: int) -> str:
    return f"R{i + 1} ↔ R{j + 1}"


class Eliminator:
    """Bir matris + sağ taraf üzerinde satır işlemlerini yürütür ve kaydeder."""

    def __init__(
        self,
        matrix: Sequence[Sequence[Fraction]],
        rhs: Optional[Sequence[object]] = None,
        symbols: Optional[Sequence[str]] = None,
    ) -> None:
        self.A: List[List[Fraction]] = [list(r) for r in copy.deepcopy([list(x) for x in matrix])]
        self.m = len(self.A)
        self.n = len(self.A[0]) if self.A else 0
        for row in self.A:
            if len(row) != self.n:
                raise SayiHatasi("Matris satırları eşit uzunlukta olmalı.")
        if rhs is None:
            self.rhs: Optional[List[object]] = None
        else:
            if len(rhs) != self.m:
                raise SayiHatasi("Sağ taraf uzunluğu satır sayısına eşit olmalı.")
            self.rhs = list(rhs)
        self.symbols = list(symbols) if symbols else None
        self.steps: List[dict] = []
        self.pivots: List[dict] = []

    # --- temel satır işlemleri ------------------------------------------
    def _record(self, step_type, target, source, factor, text, reason, cell_calcs, pivot):
        self.steps.append(
            {
                "index": len(self.steps),
                "type": step_type,
                "target_row": target,
                "source_row": source,
                "factor": format_fraction(factor) if factor is not None else None,
                "operation_text": text,
                "reason": reason,
                "before": self._before_A,
                "after": _snapshot(self.A, self.symbols),
                "rhs_before": self._before_rhs,
                "rhs_after": _rhs_snapshot(self.rhs, self.symbols),
                "cell_calculations": cell_calcs,
                "pivot": pivot,
            }
        )

    def _begin(self):
        self._before_A = _snapshot(self.A, self.symbols)
        self._before_rhs = _rhs_snapshot(self.rhs, self.symbols)

    def swap(self, i: int, j: int, reason: str, pivot=None):
        if i == j:
            return
        self._begin()
        self.A[i], self.A[j] = self.A[j], self.A[i]
        if self.rhs is not None:
            self.rhs[i], self.rhs[j] = self.rhs[j], self.rhs[i]
        self._record("swap", i, j, None, _op_swap_text(i, j), reason, [], pivot)

    def scale(self, i: int, factor: Fraction, reason: str, pivot=None):
        self._begin()
        onceki = list(self.A[i])
        self.A[i] = [factor * v for v in self.A[i]]
        hesaplar = []
        for c in range(self.n):
            if onceki[c] != 0:
                hesaplar.append(
                    {
                        "column": c,
                        "text": f"{format_fraction(factor)}·({format_fraction(onceki[c])}) = {format_fraction(self.A[i][c])}",
                    }
                )
        rhs_hesap = None
        if self.rhs is not None:
            onceki_rhs = self.rhs[i]
            self.rhs[i] = factor * onceki_rhs
            rhs_hesap = f"{format_fraction(factor)}·({fmt_entry(onceki_rhs, self.symbols)}) = {fmt_entry(self.rhs[i], self.symbols)}"
        if rhs_hesap:
            hesaplar.append({"column": "rhs", "text": rhs_hesap})
        self._record("scale", i, i, factor, _op_scale_text(i, factor), reason, hesaplar, pivot)

    def combine(self, i: int, j: int, factor: Fraction, reason: str, pivot=None):
        """R_i <- R_i - factor * R_j (hem A hem sağ tarafa)."""

        self._begin()
        onceki = list(self.A[i])
        kaynak = list(self.A[j])
        self.A[i] = [onceki[c] - factor * kaynak[c] for c in range(self.n)]
        hesaplar = []
        for c in range(self.n):
            if factor != 0 and kaynak[c] != 0:
                hesaplar.append(
                    {
                        "column": c,
                        "text": (
                            f"{format_fraction(onceki[c])} {MINUS if factor >= 0 else '+'} "
                            f"{format_fraction(abs(factor))}·({format_fraction(kaynak[c])}) = "
                            f"{format_fraction(self.A[i][c])}"
                        ),
                    }
                )
        rhs_hesap = None
        if self.rhs is not None:
            onceki_rhs = self.rhs[i]
            kaynak_rhs = self.rhs[j]
            self.rhs[i] = onceki_rhs - factor * kaynak_rhs
            rhs_hesap = (
                f"{fmt_entry(onceki_rhs, self.symbols)} {MINUS if factor >= 0 else '+'} "
                f"{format_fraction(abs(factor))}·({fmt_entry(kaynak_rhs, self.symbols)}) = "
                f"{fmt_entry(self.rhs[i], self.symbols)}"
            )
        if rhs_hesap:
            hesaplar.append({"column": "rhs", "text": rhs_hesap})
        self._record(
            "row_add", i, j, factor, _op_combine_text(i, j, factor), reason, hesaplar, pivot
        )

    # --- pivot seçimi ----------------------------------------------------
    def _pick_pivot(self, start_row: int, col: int) -> Optional[int]:
        tercih = None
        ilk = None
        for r in range(start_row, self.m):
            if self.A[r][col] != 0:
                if ilk is None:
                    ilk = r
                if abs(self.A[r][col]) == 1:
                    tercih = r
                    break
        return tercih if tercih is not None else ilk

    # --- REF / RREF ------------------------------------------------------
    def ref(self) -> "Eliminator":
        pivot_row = 0
        for col in range(self.n):
            if pivot_row >= self.m:
                break
            sec = self._pick_pivot(pivot_row, col)
            if sec is None:
                continue
            if sec != pivot_row:
                self.swap(
                    pivot_row,
                    sec,
                    f"{col + 1}. sütunda pivot için satırları değiştiriyoruz.",
                    pivot={"row": pivot_row, "column": col},
                )
            p = self.A[pivot_row][col]
            for r in range(pivot_row + 1, self.m):
                e = self.A[r][col]
                if e == 0:
                    continue
                factor = e / p
                self.combine(
                    r,
                    pivot_row,
                    factor,
                    f"{col + 1}. sütundaki {format_fraction(e)} değerini sıfırlıyoruz.",
                    pivot={"row": pivot_row, "column": col},
                )
            self.pivots.append({"row": pivot_row, "column": col})
            pivot_row += 1
        return self

    def rref(self) -> "Eliminator":
        self.ref()
        for p in reversed(self.pivots):
            r, c = p["row"], p["column"]
            pivot_val = self.A[r][c]
            if pivot_val != 1:
                self.scale(
                    r,
                    Fraction(1) / pivot_val,
                    f"{c + 1}. sütundaki pivotu 1 yapıyoruz.",
                    pivot=p,
                )
            for ust in range(r):
                e = self.A[ust][c]
                if e == 0:
                    continue
                self.combine(
                    ust,
                    r,
                    e,
                    f"{c + 1}. sütunda pivotun üstünü sıfırlıyoruz.",
                    pivot=p,
                )
        return self

    # --- sonuç yardımcıları ---------------------------------------------
    @property
    def rank(self) -> int:
        return len(self.pivots)

    def pivot_columns(self) -> List[int]:
        return [p["column"] for p in self.pivots]

    def free_columns(self) -> List[int]:
        pc = set(self.pivot_columns())
        return [c for c in range(self.n) if c not in pc]
