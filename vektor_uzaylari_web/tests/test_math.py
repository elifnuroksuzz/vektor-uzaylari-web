"""Matematik motoru kabul testleri (standart unittest).

Bu testler sonuçları sabit göstermenin değil, bağımsız doğrulamanın
kaynağıdır: değerler motor tarafından yeniden hesaplanır ve beklenen cebirsel
niteliklerle karşılaştırılır.
"""

import os
import sys
import unittest
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import analysis, arithmetic, guided_parameters  # noqa: E402
from core.arithmetic import SayiHatasi, parse_fraction  # noqa: E402
from core.elimination import Eliminator  # noqa: E402


def V(rows):
    return [[Fraction(x) for x in r] for r in rows]


def F(x):
    return Fraction(x)


class TestKombinasyon(unittest.TestCase):
    def test_q17_tam_esitlik(self):
        vs = V([[1, 0, 1], [3, -4, 1], [4, -6, -2]])
        t = [F(4), F(-2), F(4)]
        r = analysis.solve_combination(vs, t)
        self.assertEqual(r["status"], "unique")
        self.assertEqual(r["coefficients"], ["7/3", "1", "-1/3"])
        # Aλ = hedef tam eşitliği
        coeff = [parse_fraction(c) for c in r["coefficients"]]
        self.assertEqual(arithmetic.linear_combination(vs, coeff), t)

    def test_q18_genel_cozum(self):
        vs = V([[3, -1, 1, 1], [4, 3, 2, 1], [1, 4, 1, 0]])
        t = [F(6), F(11), F(4), F(1)]
        r = analysis.solve_combination(vs, t)
        self.assertEqual(r["status"], "infinite")
        self.assertEqual(r["rank"], 2)
        part = [parse_fraction(c) for c in r["particular"]]
        dirs = [[parse_fraction(c) for c in d] for d in r["directions"]]
        for ti in (0, 1, 2):
            lam = [part[i] + F(ti) * dirs[0][i] for i in range(len(part))]
            self.assertEqual(arithmetic.linear_combination(vs, lam), t)


class TestKosullar(unittest.TestCase):
    def _verify(self, vs, symbols):
        r = analysis.homogeneous_conditions(vs, symbols)
        self.assertTrue(r["verification"]["HA_is_zero"])
        self.assertTrue(r["verification"]["rank_matches"])
        self.assertTrue(r["verification"]["ok"])
        return r

    def test_q19(self):
        self._verify(V([[1, -1, 0], [0, 1, 1], [3, -2, 1]]), ["a", "b", "c"])

    def test_q20(self):
        r = self._verify(V([[1, -1, 0], [0, 1, 1], [3, -5, -2]]), ["x", "y", "z"])
        self.assertEqual(r["rank"], 2)

    def test_q21(self):
        r = self._verify(
            V([[1, -1, 2, 4], [3, 1, -1, 1], [-2, -2, 3, 3]]), ["x", "y", "z", "t"]
        )
        self.assertEqual(r["rank"], 2)
        self.assertEqual(len(r["conditions"]), 2)

    def test_ex414(self):
        r = self._verify(V([[3, -4, 1, 0], [0, 6, 1, -3]]), ["a", "b", "c", "d"])
        self.assertFalse(r["spans_ambient"])

    def test_ex416(self):
        self._verify(
            V([[1, -3, 2, 1], [7, 3, 2, -1], [3, 15, -6, -5]]), ["a", "b", "c", "d"]
        )

    def test_ex415_rank3_ve_isaret(self):
        vs = V([[1, 2, -1], [-3, 1, 0], [2, -3, 2]])
        r = analysis.homogeneous_conditions(vs, ["a", "b", "c"])
        self.assertEqual(r["rank"], 3)
        self.assertTrue(r["spans_ambient"])
        self.assertEqual(r["conditions"], [])
        # Hatalı a-3b-7c yerine her hedef için çözüm olmalı (örn. a+3b+7c dalı).
        r2 = analysis.solve_combination(vs, [F(1), F(0), F(0)])
        self.assertEqual(r2["status"], "unique")


class TestPolinom(unittest.TestCase):
    def test_q15(self):
        vs = V([[-1, 2, 3, 4], [4, 1, 6, 11], [1, -1, -1, -1], [3, 1, 5, 9]])
        r = analysis.solve_target_unknowns(vs, ["1", "1", "c", "d"])
        self.assertEqual(r["solution"], {"c": "3", "d": "5"})
        # Bir temsil gerçekten [1,1,3,5]'i vermeli.
        rep = r["representation"]
        coeff = [parse_fraction(c) for c in (rep.get("coefficients") or rep["particular"])]
        self.assertEqual(
            arithmetic.linear_combination(vs, coeff), [F(1), F(1), F(3), F(5)]
        )
        # 2*p1 + 3*p3 de geçerli bir temsildir.
        self.assertEqual(
            arithmetic.linear_combination(vs, [F(2), F(0), F(3), F(0)]),
            [F(1), F(1), F(3), F(5)],
        )


class TestParametre(unittest.TestCase):
    def test_q16_test_noktalari(self):
        beklenen = [("1", "0", True), ("-1", "9/4", False), ("-1", "0", True), ("0", "0", False)]
        for a, b, disarida in beklenen:
            e = guided_parameters.evaluate_parameter(a, b)
            self.assertEqual(e["is_outside"], disarida, f"a={a}, b={b}")
            self.assertTrue(e["consistent"], f"motor/cebir tutarsız a={a}, b={b}")

    def test_q16_sifira_bolme_yok(self):
        # a = ±1 dallarında sıfıra bölme olmamalı; farklı a'larda da çalışmalı.
        for a, b in [("1", "5"), ("-1", "9/4"), ("2", "0"), ("1/2", "-3")]:
            e = guided_parameters.evaluate_parameter(a, b)
            self.assertIn(e["engine"]["status"], {"unique", "infinite", "inconsistent"})


class TestKenarDurumlar(unittest.TestCase):
    def test_tutarsiz_sistem(self):
        vs = V([[1, 2], [1, 2]])  # sütunlar (1,1) ve (2,2)
        r = analysis.solve_combination(vs, [F(1), F(3)])
        self.assertEqual(r["status"], "inconsistent")
        self.assertFalse(r["member"])

    def test_sifir_matris(self):
        vs = V([[0, 0], [0, 0]])
        self.assertEqual(analysis.solve_combination(vs, [F(0), F(0)])["status"], "infinite")
        self.assertEqual(
            analysis.solve_combination(vs, [F(1), F(0)])["status"], "inconsistent"
        )

    def test_satir_degisimi(self):
        # İlk pivot sıfır → satır değişimi gerekir.
        vs = V([[0, 1], [1, 0]])
        r = analysis.solve_combination(vs, [F(2), F(3)])
        self.assertEqual(r["status"], "unique")
        coeff = [parse_fraction(c) for c in r["coefficients"]]
        self.assertEqual(arithmetic.linear_combination(vs, coeff), [F(2), F(3)])

    def test_dikdortgen_ve_kesir(self):
        vs = V([["1/2", "1/3", 0], [1, 0, 1]])  # R³'te 2 kesirli vektör
        r = analysis.homogeneous_conditions(vs, ["a", "b", "c"])
        self.assertTrue(r["verification"]["ok"])

    def test_tek_ve_yinelenen_vektor(self):
        self.assertEqual(
            analysis.homogeneous_conditions(V([[1, 2]]), ["a", "b"])["rank"], 1
        )
        r = analysis.homogeneous_conditions(V([[1, 2], [1, 2]]), ["a", "b"])
        self.assertEqual(r["rank"], 1)
        self.assertTrue(r["verification"]["ok"])

    def test_gecersiz_girdi(self):
        for kotu in ["", "abc", "1/0", "nan", "inf"]:
            with self.assertRaises(SayiHatasi):
                parse_fraction(kotu)


class TestAdimYenidenUygula(unittest.TestCase):
    """Her kaydedilen işlem, 'before'a uygulanınca tam olarak 'after' vermeli."""

    def _reapply(self, before, step):
        M = [[parse_fraction(x) for x in row] for row in before]
        tp, i, j = step["type"], step["target_row"], step["source_row"]
        if tp == "swap":
            M[i], M[j] = M[j], M[i]
        elif tp == "scale":
            k = parse_fraction(step["factor"])
            M[i] = [k * x for x in M[i]]
        elif tp == "row_add":
            k = parse_fraction(step["factor"])
            M[i] = [M[i][c] - k * M[j][c] for c in range(len(M[i]))]
        return [[arithmetic.format_fraction(x) for x in row] for row in M]

    def test_combination_adimlari(self):
        vs = V([[1, 0, 1], [3, -4, 1], [4, -6, -2]])
        r = analysis.solve_combination(vs, [F(4), F(-2), F(4)])
        for s in r["steps"]:
            self.assertEqual(self._reapply(s["before"], s), s["after"])

    def test_rhs_ayni_islem(self):
        # Sağ taraf da aynı işleme tabi olmalı.
        A = V([[0, 1], [1, 0]])
        e = Eliminator(A, [F(2), F(3)]).ref()
        for s in e.steps:
            self.assertIsNotNone(s["rhs_after"])


class TestAksiyomlar(unittest.TestCase):
    PRESETLER = [
        dict(u=[F(1), F(2)], v=[F(3), F(-1)], w=[F(-2), F(1)], a=F(2), b=F(-1), c=F(2)),
        dict(u=[F(-2), F(1)], v=[F(1), F(3)], w=[F(2), F(-2)], a=F(-1), b=F(3), c=F(-2)),
    ]

    def test_v1_v8_iki_taraf_esit(self):
        for p in self.PRESETLER:
            for rid in [f"V{i}" for i in range(1, 9)]:
                r = analysis.evaluate_axiom(rid, **p)
                self.assertTrue(r["equal"], f"{rid} eşit değil: {r}")

    def test_kart_sirasi(self):
        import json
        import os

        yol = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data",
            "axioms.json",
        )
        with open(yol, encoding="utf-8") as f:
            ax = json.load(f)
        self.assertEqual([c["id"] for c in ax["cards"]], [f"V{i}" for i in range(1, 9)])


if __name__ == "__main__":
    unittest.main()
