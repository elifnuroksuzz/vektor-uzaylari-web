"""API/sunucu testleri: uçlar, hata yönetimi ve sunucunun ayakta kalması."""

import json
import os
import sys
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app  # noqa: E402


class SunucuTestTemel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
        cls.port = cls.httpd.server_address[1]
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def _url(self, yol):
        return f"http://127.0.0.1:{self.port}{yol}"

    def get(self, yol):
        with urllib.request.urlopen(self._url(yol)) as r:
            return r.status, json.loads(r.read().decode("utf-8"))

    def post(self, yol, govde):
        veri = json.dumps(govde).encode("utf-8")
        istek = urllib.request.Request(
            self._url(yol), data=veri, headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(istek) as r:
                return r.status, json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read().decode("utf-8"))

    def post_raw(self, yol, ham_bytes):
        istek = urllib.request.Request(
            self._url(yol), data=ham_bytes, headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(istek) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            return e.code, e.read()


class TestUclar(SunucuTestTemel):
    def test_content(self):
        st, veri = self.get("/api/content")
        self.assertEqual(st, 200)
        self.assertEqual(veri["title"], "Vektör Uzayları")
        self.assertEqual(len(veri["axioms"]["cards"]), 8)
        # 17, 20, Örnek 4.1.5, 15 + 4.2 soruları (bağımlılık, baz seçimi).
        self.assertEqual([q["id"] for q in veri["questions"]], ["q17", "q20", "ex415", "q15", "q_dep", "q_baz"])
        self.assertTrue(any(d["id"] == "B_kuvvet" for d in veri["lesson_catalog"]))

    def test_statik_index(self):
        st, govde = self._get_raw("/")
        self.assertEqual(st, 200)
        self.assertIn(b"Vekt", govde)

    def _get_raw(self, yol):
        try:
            with urllib.request.urlopen(self._url(yol)) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            return e.code, e.read()

    def test_tum_sorular_cozulur(self):
        _, veri = self.get("/api/content")
        for q in veri["questions"]:
            st, sonuc = self.post("/api/solve", {"question_id": q["id"]})
            self.assertEqual(st, 200, q["id"])
            self.assertIn("question", sonuc)

    def test_axiom_ucu(self):
        st, veri = self.post(
            "/api/axiom",
            {"rule_id": "V5", "u": ["1", "2"], "v": ["3", "-1"], "w": ["0", "0"],
             "a": "2", "b": "-1", "c": "2"},
        )
        self.assertEqual(st, 200)
        self.assertTrue(veri["equal"])

    def test_combination_ucu(self):
        st, veri = self.post(
            "/api/combination", {"vectors": [["1", "0"], ["0", "1"]], "coeffs": ["2", "3"]}
        )
        self.assertEqual(st, 200)
        self.assertEqual(veri["result"], ["2", "3"])
        self.assertEqual(veri["rank"], 2)

    def test_span_uyelik(self):
        st, veri = self.post(
            "/api/span",
            {"vectors": [["1", "0"], ["0", "1"]], "target": ["2", "5"], "symbols": ["x", "y"]},
        )
        self.assertEqual(st, 200)
        self.assertEqual(veri["membership"]["status"], "unique")

    def test_subspace_ucu(self):
        st, veri = self.post("/api/subspace", {"example_id": "xy", "check_id": "add"})
        self.assertEqual(st, 200)
        self.assertFalse(veri["result"]["holds"])
        # xy>=0: u=(1,2), v=(-3,-1) → toplam (-2,1) kümenin dışında
        self.assertEqual(veri["draw"]["sum"], ["-2", "1"])
        self.assertFalse(veri["draw"]["sum_in"])

    def test_subspace_zero_ve_scalar(self):
        st, veri = self.post("/api/subspace", {"example_id": "pos", "check_id": "zero"})
        self.assertEqual(st, 200)
        self.assertFalse(veri["draw"]["in_set"])  # (0,0) x>0,y>0 kümesinde değil
        st, veri = self.post("/api/subspace", {"example_id": "pos", "check_id": "scalar"})
        self.assertEqual(st, 200)
        self.assertEqual(veri["draw"]["scaled"], ["-5", "-2"])
        self.assertFalse(veri["draw"]["scaled_in"])


    def test_lesson_ucu(self):
        st, veri = self.post("/api/lesson", {"lesson_id": "V4"})
        self.assertEqual(st, 200)
        self.assertEqual(veri["id"], "V4")
        self.assertTrue(veri["steps"][0]["scene"]["vectors"])
        st, veri = self.post("/api/lesson", {"lesson_id": "V4", "randomize": True, "seed": 7})
        self.assertEqual(st, 200)
        st, veri = self.post("/api/lesson", {"lesson_id": "V4", "params": {"u": ["2", "-1/2"]}})
        self.assertEqual(st, 200)
        self.assertEqual(veri["params"][0]["value"], ["2", "-1/2"])

    def test_lesson_hatalari(self):
        self.assertEqual(self.post("/api/lesson", {"lesson_id": "yok"})[0], 400)
        self.assertEqual(self.post("/api/lesson", {"lesson_id": "V4", "params": []})[0], 400)
        self.assertEqual(self.post("/api/lesson", {"lesson_id": "V4", "seed": "x"})[0], 400)
        st, veri = self.post("/api/lesson", {"lesson_id": "B_baz", "params": {"b1": ["1", "1"], "b2": ["2", "2"]}})
        self.assertEqual(st, 400)
        self.assertIn("baz değil", veri["error"])

    def test_dependence_ucu(self):
        st, veri = self.post("/api/dependence", {"vectors": [["1", "2"], ["2", "4"], ["0", "1"]]})
        self.assertEqual(st, 200)
        self.assertFalse(veri["independent"])
        self.assertEqual(veri["basis"], [["1", "2"], ["0", "1"]])
        self.assertEqual(self.post("/api/dependence", {"vectors": [["1"], ["1", "2"]]})[0], 400)


class TestHatalar(SunucuTestTemel):
    def test_gecersiz_json(self):
        st, _ = self.post_raw("/api/solve", b"{bozuk json")
        self.assertEqual(st, 400)

    def test_eksik_alan(self):
        st, veri = self.post("/api/combination", {"vectors": [["1"]]})
        self.assertEqual(st, 400)
        self.assertIn("error", veri)

    def test_kotu_sayi(self):
        st, veri = self.post(
            "/api/combination", {"vectors": [["abc"]], "coeffs": ["1"]}
        )
        self.assertEqual(st, 400)

    def test_404(self):
        st, _ = self.post("/api/yok", {})
        self.assertEqual(st, 404)

    def test_405(self):
        # /api/content yalnızca GET
        st, _ = self.post("/api/content", {})
        self.assertEqual(st, 405)

    def test_gecersiz_soru(self):
        st, _ = self.post("/api/solve", {"question_id": "yok"})
        self.assertEqual(st, 400)

    def test_sunucu_ayakta_kaliyor(self):
        # Kötü istekten sonra sunucu hâlâ yanıt vermeli.
        self.post("/api/solve", {"question_id": "yok"})
        st, _ = self.get("/api/content")
        self.assertEqual(st, 200)


if __name__ == "__main__":
    unittest.main()
