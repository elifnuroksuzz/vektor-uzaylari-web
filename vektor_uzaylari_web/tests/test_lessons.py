"""Ders oynatıcısı, ifade değerlendirici ve 4.2 (bağımlılık/baz) testleri."""

import os
import sys
import unittest
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import analysis, lessons  # noqa: E402
from core.arithmetic import SayiHatasi, linear_combination  # noqa: E402
from core.vecexpr import evaluate, fill_placeholders  # noqa: E402


def V(*xs):
    return tuple(F(x) for x in xs)


class TestIfade(unittest.TestCase):
    ortam = {"u": V(1, 2), "v": V(3, -1), "a": F(2), "b": F(-1, 2)}

    def test_temel_islemler(self):
        self.assertEqual(evaluate("u+v", self.ortam), V(4, 1))
        self.assertEqual(evaluate("(a+b)*v", self.ortam), V("9/2", "-3/2"))
        self.assertEqual(evaluate("a*(b*v)", self.ortam), evaluate("(a*b)*v", self.ortam))
        self.assertEqual(evaluate("-u", self.ortam), V(-1, -2))
        self.assertEqual(evaluate("v/a", self.ortam), V("3/2", "-1/2"))

    def test_literal_indeks_fonksiyon(self):
        self.assertEqual(evaluate("[a, 2*a]", self.ortam), V(2, 4))
        self.assertEqual(evaluate("v[2]", self.ortam), F(-1))
        self.assertEqual(evaluate("(u+v)[1]", self.ortam), F(4))
        self.assertEqual(evaluate("det(u, v)", self.ortam), F(-7))
        self.assertEqual(evaluate("dot(u, v)", self.ortam), F(1))
        self.assertEqual(evaluate("abs(-3/4)", self.ortam), F(3, 4))

    def test_hatalar(self):
        for kotu in ["u+a", "u*v", "1/0", "x", "u[3]", "__import__('os')", "u +", "(u", "det(u)"]:
            with self.assertRaises(SayiHatasi, msg=kotu):
                evaluate(kotu, self.ortam)

    def test_yer_tutucu(self):
        self.assertEqual(fill_placeholders("w = {{u+v}}, k = {{b}}", self.ortam), "w = (4, 1), k = −1/2")
        self.assertEqual(fill_placeholders("Span{v}", self.ortam), "Span{v}")


class TestDersler(unittest.TestCase):
    def test_her_ders_varsayilan_ve_rastgele_kurulur(self):
        for lid in lessons.LESSONS:
            d = lessons.build_lesson(lid)
            self.assertTrue(d["steps"], lid)
            self.assertGreaterEqual(d["range"], 3)
            for adim in d["steps"]:
                for alan in ("title", "text", "caption", "why"):
                    self.assertNotIn("{{", adim[alan], f"{lid}: {alan}")
                for m in adim["math"]:
                    self.assertNotIn("{{", m, lid)
            for seed in range(12):
                lessons.build_lesson(lid, randomize=True, seed=seed)

    def test_katalog(self):
        sekmeler = {d["tab"] for d in lessons.catalog()}
        self.assertEqual(sekmeler, {"kurallar", "altuzaylar", "germe", "bagimsizlik"})
        kural = [d["id"] for d in lessons.catalog() if d["group"] == "Aksiyomlar"]
        self.assertEqual(kural, ["V1", "V2", "V3", "V4", "V5", "V6", "V7", "V8"])

    def _sahne(self, lid, adim, **kw):
        return lessons.build_lesson(lid, **kw)["steps"][adim]["scene"]

    def test_aksiyom_iki_yol_ayni_uca_cikar(self):
        # V1: sol taraf oku ile sağ yolun ucu aynı nokta (rastgele parametrelerle de)
        for seed in range(10):
            sc = self._sahne("V1", 3, randomize=True, seed=seed)
            sol = next(v for v in sc["vectors"] if v["id"] == "sol")
            w = next(v for v in sc["vectors"] if v["id"] == "w")
            self.assertEqual(sol["to"], w["to"])
            self.assertEqual(sc["points"][0]["at"], sol["to"])

    def test_altuzay_uyelik_renkleri(self):
        sc = self._sahne("S_xy", 3)
        s = next(v for v in sc["vectors"] if v["id"] == "s")
        self.assertEqual((s["to"], s["kind"]), (["-2", "1"], "disarda"))
        self.assertIn("∉ W", s["label"])
        for seed in range(10):  # y = 2x: toplam ve katlar her zaman doğruda
            sc = self._sahne("S_y2x", 5, randomize=True, seed=seed)
            for v in sc["vectors"]:
                if v["id"] in ("s", "lu"):
                    self.assertEqual(v["kind"], "icerde")

    def test_kapanan_cokgen(self):
        for seed in range(15):
            d = lessons.build_lesson("B_cokgen", randomize=True, seed=seed)
            son = d["steps"][5]["scene"]
            c = next(v for v in son["vectors"] if v["id"] == "c")
            self.assertEqual(c["to"], ["0", "0"])

    def test_kuvvet_dengesi(self):
        d = lessons.build_lesson("B_kuvvet")
        self.assertIn("k₁ = 4,   k₂ = 2", d["steps"][2]["math"][1])
        self.assertEqual(d["steps"][3]["math"][0], "T₁ + T₂ + G = (0, 0)")

    def test_cramer_formulu_hedefe_ulasir(self):
        for seed in range(15):
            d = lessons.build_lesson("G_cramer", randomize=True, seed=seed)
            sc = d["steps"][5]["scene"]
            r = next(v for v in sc["vectors"] if v["id"] == "r")
            self.assertEqual(r["to"], sc["points"][0]["at"])

    def test_baz_koordinatlari(self):
        d = lessons.build_lesson("B_baz")
        self.assertIn("[w]_B = (2, −1)", d["steps"][2]["math"][1])

    def test_kosul_mesajlari(self):
        with self.assertRaises(SayiHatasi) as cm:
            lessons.build_lesson("G_cramer", {"v1": ["1", "2"], "v2": ["2", "4"]})
        self.assertIn("aynı doğru", str(cm.exception))
        with self.assertRaises(SayiHatasi):
            lessons.build_lesson("S_xy", {"u": ["1", "-2"]})
        with self.assertRaises(SayiHatasi):
            lessons.build_lesson("V1", {"u": ["1"]})
        with self.assertRaises(SayiHatasi):
            lessons.build_lesson("V1", {"u": ["a", "b"]})
        with self.assertRaises(SayiHatasi):
            lessons.build_lesson("yok")

    def test_kullanici_parametresi_kesirli(self):
        d = lessons.build_lesson("V4", {"u": ["1/2", "0.25"], "v": ["-1", "3"]})
        self.assertEqual(d["params"][0]["value"], ["1/2", "1/4"])
        sc = d["steps"][1]["scene"]
        self.assertEqual(next(v for v in sc["vectors"] if v["id"] == "s")["to"], ["-1/2", "13/4"])


class TestBagimlilik(unittest.TestCase):
    def test_bagimli_r3(self):
        vs = [[F(1), F(2), F(3)], [F(4), F(5), F(6)], [F(7), F(8), F(9)]]
        r = analysis.dependence_analysis(vs)
        self.assertFalse(r["independent"])
        self.assertEqual(r["rank"], 2)
        c = [F(x) for x in r["relation"]]
        self.assertEqual(linear_combination(vs, c), [0, 0, 0])
        self.assertTrue(any(x != 0 for x in c))
        self.assertEqual(r["relation"], ["1", "-2", "1"])

    def test_bagimsiz(self):
        r = analysis.dependence_analysis([[F(1), F(0)], [F(1), F(1)]])
        self.assertTrue(r["independent"])
        self.assertTrue(r["is_basis_of_ambient"])
        self.assertIsNone(r["relation"])

    def test_baz_orijinal_vektorlerden(self):
        vs = [[F(1), F(2), F(1)], [F(2), F(4), F(2)], [F(0), F(1), F(1)], [F(1), F(3), F(2)]]
        r = analysis.dependence_analysis(vs)
        self.assertEqual(r["basis_indices"], [0, 2])
        self.assertEqual(r["basis"], [["1", "2", "1"], ["0", "1", "1"]])
        self.assertEqual(len(r["relations"]), 2)
        for rel in r["relations"]:
            self.assertEqual(linear_combination(vs, [F(x) for x in rel]), [0, 0, 0])

    def test_esit_sayida_ama_bagimli(self):
        r = analysis.dependence_analysis([[F(1), F(2)], [F(2), F(4)]])
        self.assertFalse(r["independent"])
        self.assertEqual(r["rank"], 1)

    def test_sifir_vektor_bagimli(self):
        r = analysis.dependence_analysis([[F(0), F(0)]])
        self.assertFalse(r["independent"])
        self.assertEqual(r["basis"], [])  # sıfır uzayının bazı boş küme


if __name__ == "__main__":
    unittest.main()


class TestYorum(unittest.TestCase):
    def setUp(self):
        import app
        self.app = app

    def test_her_soruda_yorum_ve_kontroller_dogru(self):
        for q in self.app.QUESTIONS["questions"]:
            yorum = self.app.api_solve({"question_id": q["id"]})["yorum"]
            self.assertTrue(yorum, q["id"])
            for m in yorum:
                self.assertTrue(m["baslik"])
                for satir in m["mat"]:
                    self.assertNotIn("✗", satir, q["id"])  # her kontrol gerçekten tutmalı
                    self.assertNotIn("+ −", satir)
                    self.assertNotIn("− +", satir)

    def test_q20_kosul_ve_normal(self):
        yorum = self.app.api_solve({"question_id": "q20"})["yorum"]
        self.assertIn("x + y − z = 0", yorum[0]["mat"])
        self.assertIn("v₃ = 3·v₁ − 2·v₂", yorum[3]["mat"])

    def test_q17_baz_koordinatlari(self):
        yorum = self.app.api_solve({"question_id": "q17"})["yorum"]
        self.assertIn("✓", yorum[1]["mat"][0])
        self.assertIn("BAZI", yorum[2]["metin"])

    def test_q_baz_fazla_vektorler(self):
        yorum = self.app.api_solve({"question_id": "q_baz"})["yorum"]
        hepsi = [x for m in yorum for x in m["mat"]]
        self.assertIn("v₂ = 2·v₁", hepsi)
        self.assertIn("v₄ = v₁ + v₃", hepsi)
