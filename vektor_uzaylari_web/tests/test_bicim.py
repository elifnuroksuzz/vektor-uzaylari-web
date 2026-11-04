"""Gösterim biçimi ve rastgele ders üretimi testleri."""

import os
import sys
import unittest
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import lessons  # noqa: E402
from core.elimination import _op_combine_text  # noqa: E402
from core.expressions import _terim_yaz  # noqa: E402
from core.vecexpr import format_line_through_origin  # noqa: E402


def v(*xs):
    return tuple(F(x) for x in xs)


class DogruDenklemi(unittest.TestCase):
    def test_sade_bicim(self):
        self.assertEqual(format_line_through_origin(v(1, 2)), "2x − y = 0")
        self.assertEqual(format_line_through_origin(v(-1, 1)), "x + y = 0")
        self.assertEqual(format_line_through_origin(v(0, 3)), "x = 0")
        self.assertEqual(format_line_through_origin(v(3, 0)), "y = 0")
        self.assertEqual(format_line_through_origin(v(F(1, 2), 3)), "3x − (1/2)y = 0")

    def test_denklem_vektoru_saglar(self):
        # qx − py = 0, (p, q) noktasında sağlanmalı
        for p in range(-3, 4):
            for q in range(-3, 4):
                if p == 0 and q == 0:
                    continue
                metin = format_line_through_origin(v(p, q))
                self.assertNotIn("1x", metin.replace("−1", "").replace("(", ""))
                self.assertNotIn("0x", metin)

    def test_sifir_vektor_hata(self):
        with self.assertRaises(Exception):
            format_line_through_origin(v(0, 0))


class KesirliKatsayi(unittest.TestCase):
    def test_terim_parantezli(self):
        self.assertEqual(_terim_yaz(F(1, 7), "a", True), "(1/7)a")
        self.assertEqual(_terim_yaz(F(-3, 7), "b", False), " - (3/7)b")
        self.assertEqual(_terim_yaz(F(2), "c", False), " + 2c")

    def test_satir_islemi_parantezli(self):
        self.assertEqual(_op_combine_text(2, 1, F(-3, 7)), "R3 ← R3 + (3/7)R2")
        self.assertEqual(_op_combine_text(1, 0, F(2)), "R2 ← R2 − 2R1")


class RastgeleDersler(unittest.TestCase):
    def test_her_ders_rastgele_kurulur(self):
        for c in lessons.catalog():
            for seed in range(200):
                with self.subTest(ders=c["id"], seed=seed):
                    ders = lessons.build_lesson(c["id"], None, randomize=True, seed=seed)
                    metin = " ".join(
                        (s.get("text") or "") + " ".join(s.get("math") or []) + (s.get("caption") or "")
                        for s in ders["steps"]
                    )
                    self.assertNotIn("{{", metin)


if __name__ == "__main__":
    unittest.main()
