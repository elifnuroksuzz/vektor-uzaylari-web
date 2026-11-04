"""Vektör Uzayları — yerel öğretim web sunucusu (yalnızca standart kütüphane).

Çalıştırma:
    py -3 app.py              # ardından http://127.0.0.1:8000
    py -3 app.py --port 8001  # port doluysa

Sunucu sadece 127.0.0.1 üzerinde dinler; internet gerektirmez. Matematiksel
kararların tamamı :mod:`core` içindeki saf Python motorundan gelir. Tarayıcı
yalnızca kontrol, animasyon ve görüntüleme yapar.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import List

from core import analysis, arithmetic, guided_parameters, lessons, yorum
from core.arithmetic import SayiHatasi

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
DATA_DIR = BASE_DIR / "data"

MAX_BODY = 64 * 1024  # 64 KB
MAX_DIM = 8  # en çok 8×8
MAX_VECTORS = 8

CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml",
}


def _load_json(name: str) -> dict:
    with open(DATA_DIR / name, "r", encoding="utf-8") as f:
        return json.load(f)


AXIOMS = _load_json("axioms.json")
LESSONS = _load_json("lessons.json")
QUESTIONS = _load_json("questions.json")
QUESTION_BY_ID = {q["id"]: q for q in QUESTIONS["questions"]}


class ApiError(Exception):
    def __init__(self, message: str, status: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status = status


# --- İstek doğrulama yardımcıları ---------------------------------------


def _require_list(data: dict, key: str) -> list:
    v = data.get(key)
    if not isinstance(v, list):
        raise ApiError(f"'{key}' alanı liste olmalı.")
    return v


def _parse_vectors(raw) -> List[List[Fraction]]:
    if not isinstance(raw, list) or not raw:
        raise ApiError("En az bir vektör gerekli.")
    if len(raw) > MAX_VECTORS:
        raise ApiError(f"En çok {MAX_VECTORS} vektör desteklenir.")
    vectors = []
    for satir in raw:
        if not isinstance(satir, list):
            raise ApiError("Her vektör bir liste olmalı.")
        if len(satir) > MAX_DIM:
            raise ApiError(f"Vektör boyutu en çok {MAX_DIM} olabilir.")
        try:
            vectors.append(arithmetic.parse_vector(satir))
        except SayiHatasi as e:
            raise ApiError(str(e))
    return vectors


def _parse_target(raw) -> List[Fraction]:
    if not isinstance(raw, list):
        raise ApiError("Hedef bir liste olmalı.")
    if len(raw) > MAX_DIM:
        raise ApiError(f"Hedef boyutu en çok {MAX_DIM} olabilir.")
    try:
        return arithmetic.parse_vector(raw)
    except SayiHatasi as e:
        raise ApiError(str(e))


# --- API uçları ----------------------------------------------------------


def api_content(_data: dict) -> dict:
    return {
        "title": "Vektör Uzayları",
        "axioms": AXIOMS,
        "lessons": LESSONS,
        "questions": [
            {
                "id": q["id"],
                "number": q["number"],
                "tier": q["tier"],
                "title": q["title"],
                "prompt": q["prompt"],
                "asked": q["asked"],
                "type": q["type"],
                "matrix_view": q.get("matrix_view", False),
            }
            for q in QUESTIONS["questions"]
        ],
        "lesson_catalog": lessons.catalog(),
    }


def api_axiom(data: dict) -> dict:
    rule_id = data.get("rule_id")
    if rule_id not in {c["id"] for c in AXIOMS["cards"]}:
        raise ApiError("Geçersiz aksiyom numarası.")
    try:
        u = arithmetic.parse_vector(data.get("u", []))
        v = arithmetic.parse_vector(data.get("v", []))
        w = arithmetic.parse_vector(data.get("w", []))
        a = arithmetic.parse_fraction(data.get("a", "0"))
        b = arithmetic.parse_fraction(data.get("b", "0"))
        c = arithmetic.parse_fraction(data.get("c", "0"))
    except SayiHatasi as e:
        raise ApiError(str(e))
    if not (len(u) == len(v) == len(w)) or len(v) == 0:
        raise ApiError("u, v, w aynı ve sıfırdan büyük boyutta olmalı.")
    try:
        return analysis.evaluate_axiom(rule_id, u, v, w, a, b, c)
    except SayiHatasi as e:
        raise ApiError(str(e))


def api_combination(data: dict) -> dict:
    vectors = _parse_vectors(_require_list(data, "vectors"))
    try:
        coeffs = arithmetic.parse_vector(_require_list(data, "coeffs"))
    except SayiHatasi as e:
        raise ApiError(str(e))
    if len(coeffs) != len(vectors):
        raise ApiError("Katsayı sayısı vektör sayısına eşit olmalı.")
    boyut = len(vectors[0])
    # Ara vektörler ve çalışan toplam (animasyon için).
    ara = []
    toplam = [Fraction(0)] * boyut
    for vec, k in zip(vectors, coeffs):
        olcekli = arithmetic.scalar_mul(k, vec)
        toplam = arithmetic.vector_add(toplam, olcekli)
        ara.append(
            {
                "coeff": arithmetic.format_fraction(k),
                "scaled": arithmetic.format_vector(olcekli),
                "running_sum": arithmetic.format_vector(toplam),
            }
        )
    from core.elimination import Eliminator

    rank = Eliminator(arithmetic.columns_as_matrix(vectors)).ref().rank
    return {
        "vectors": [arithmetic.format_vector(v) for v in vectors],
        "coeffs": arithmetic.format_vector(coeffs),
        "steps": ara,
        "result": arithmetic.format_vector(toplam),
        "rank": rank,
        "ambient_dim": boyut,
    }


def api_span(data: dict) -> dict:
    vectors = _parse_vectors(_require_list(data, "vectors"))
    symbols = data.get("symbols")
    if not symbols:
        symbols = [chr(ord("a") + i) for i in range(len(vectors[0]))]
    target = None
    if data.get("target"):
        target = _parse_target(data["target"])
    try:
        return analysis.span_analysis(vectors, symbols, target)
    except SayiHatasi as e:
        raise ApiError(str(e))


def api_lesson(data: dict) -> dict:
    lesson_id = data.get("lesson_id")
    if not isinstance(lesson_id, str) or lesson_id not in lessons.LESSONS:
        raise ApiError("Geçersiz ders kimliği.")
    params = data.get("params")
    if params is not None and not isinstance(params, dict):
        raise ApiError("'params' alanı sözlük olmalı.")
    seed = data.get("seed")
    if seed is not None and (not isinstance(seed, int) or isinstance(seed, bool)):
        raise ApiError("'seed' tam sayı olmalı.")
    try:
        return lessons.build_lesson(
            lesson_id, params, randomize=bool(data.get("randomize")), seed=seed
        )
    except SayiHatasi as e:
        raise ApiError(str(e))


def api_dependence(data: dict) -> dict:
    vectors = _parse_vectors(_require_list(data, "vectors"))
    try:
        return analysis.dependence_analysis(vectors)
    except SayiHatasi as e:
        raise ApiError(str(e))


def _in_set(example_id: str, vec) -> bool:
    """Bir vektörün ilgili örnek kümesinde olup olmadığını kesin aritmetikle sınar."""

    x, y = vec[0], vec[1]
    if example_id == "y2x":
        return y == 2 * x
    if example_id == "y2x1":
        return y == 2 * x + 1
    if example_id == "pos":
        return x > 0 and y > 0
    if example_id == "xy":
        return x * y >= 0
    return False


def api_subspace(data: dict) -> dict:
    example_id = data.get("example_id")
    examples = {e["id"]: e for e in LESSONS["subspace"]["examples"]}
    if example_id not in examples:
        raise ApiError("Geçersiz alt uzay örneği.")
    ex = examples[example_id]
    check_id = data.get("check_id")
    if check_id not in {"zero", "add", "scalar"}:
        raise ApiError("Geçersiz kontrol türü.")

    kontrol = ex["checks"][check_id]
    sonuc = {"holds": kontrol["holds"], "reason": kontrol["reason"]}
    if "general" in kontrol:
        sonuc["general"] = kontrol["general"]

    orn = kontrol.get("example", {})
    ciz = {}
    try:
        if check_id == "zero":
            nokta = arithmetic.parse_vector(orn.get("point", ["0", "0"]))
            ciz = {
                "kind": "zero",
                "point": arithmetic.format_vector(nokta),
                "in_set": _in_set(example_id, nokta),
                "calc": "(0, 0)",
            }
        elif check_id == "add":
            u = arithmetic.parse_vector(orn["u"])
            v = arithmetic.parse_vector(orn["v"])
            toplam = arithmetic.vector_add(u, v)
            ciz = {
                "kind": "add",
                "u": arithmetic.format_vector(u),
                "v": arithmetic.format_vector(v),
                "sum": arithmetic.format_vector(toplam),
                "sum_in": _in_set(example_id, toplam),
                "u_in": _in_set(example_id, u),
                "v_in": _in_set(example_id, v),
            }
        else:  # scalar
            u = arithmetic.parse_vector(orn["u"])
            s = arithmetic.parse_fraction(orn["scalar"])
            olcekli = arithmetic.scalar_mul(s, u)
            ciz = {
                "kind": "scalar",
                "u": arithmetic.format_vector(u),
                "scalar": arithmetic.format_fraction(s),
                "scaled": arithmetic.format_vector(olcekli),
                "scaled_in": _in_set(example_id, olcekli),
                "u_in": _in_set(example_id, u),
            }
    except (SayiHatasi, KeyError) as e:
        raise ApiError("Örnek verisi eksik veya geçersiz: " + str(e))

    return {
        "example_id": example_id,
        "label": ex["label"],
        "is_subspace": ex["is_subspace"],
        "check_id": check_id,
        "result": sonuc,
        "draw": ciz,
    }


def api_solve(data: dict) -> dict:
    qid = data.get("question_id")
    q = QUESTION_BY_ID.get(qid)
    if q is None:
        raise ApiError("Geçersiz soru numarası.")
    tip = q["type"]
    try:
        if tip == "combination":
            vectors = arithmetic.parse_matrix(q["vectors"])
            target = arithmetic.parse_vector(q["target"])
            res = analysis.solve_combination(vectors, target)
        elif tip == "conditions":
            vectors = arithmetic.parse_matrix(q["vectors"])
            res = analysis.homogeneous_conditions(vectors, q["symbols"])
        elif tip == "target_unknowns":
            vectors = arithmetic.parse_matrix(q["vectors"])
            res = analysis.solve_target_unknowns(vectors, q["components"])
        elif tip in ("dependence", "basis"):
            vectors = arithmetic.parse_matrix(q["vectors"])
            res = analysis.dependence_analysis(vectors)
        elif tip == "guided_parameter":
            res = {"guided": guided_parameters.guided_derivation()}
            a = data.get("a")
            b = data.get("b")
            if a not in (None, "") and b not in (None, ""):
                res["evaluation"] = guided_parameters.evaluate_parameter(a, b)
        else:
            raise ApiError("Desteklenmeyen soru türü.")
    except SayiHatasi as e:
        raise ApiError(str(e))
    try:
        res["yorum"] = yorum.yorumla(q, res)
    except SayiHatasi:  # yorum üretilemezse çözüm yine gösterilsin
        res["yorum"] = []
    res["question"] = {
        "id": q["id"],
        "number": q["number"],
        "title": q["title"],
        "prompt": q["prompt"],
        "asked": q["asked"],
        "tier": q["tier"],
        "note": q.get("note"),
        "matrix_view": q.get("matrix_view", False),
        "type": tip,
    }
    return res


API_ROUTES = {
    "/api/content": api_content,
    "/api/axiom": api_axiom,
    "/api/combination": api_combination,
    "/api/span": api_span,
    "/api/subspace": api_subspace,
    "/api/solve": api_solve,
    "/api/lesson": api_lesson,
    "/api/dependence": api_dependence,
}


class Handler(BaseHTTPRequestHandler):
    server_version = "VektorUzaylari/1.0"

    def log_message(self, fmt, *args):  # sade sunucu günlüğü
        sys.stderr.write("[%s] %s\n" % (self.log_date_time_string(), fmt % args))

    # --- yardımcılar ----------------------------------------------------
    def _send_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def _send_error_json(self, message: str, status: int) -> None:
        self._send_json({"error": message}, status)

    def _resolve_static(self, url_path: str) -> Path | None:
        if url_path in ("/", ""):
            url_path = "/index.html"
        rel = url_path.lstrip("/")
        hedef = (STATIC_DIR / rel).resolve()
        try:
            hedef.relative_to(STATIC_DIR)
        except ValueError:
            return None  # dizin dışına çıkış denemesi
        if hedef.is_file():
            return hedef
        return None

    # --- HTTP metotları -------------------------------------------------
    def do_GET(self) -> None:
        from urllib.parse import urlparse

        yol = urlparse(self.path).path
        if yol == "/api/content":
            self._send_json(api_content({}))
            return
        if yol.startswith("/api/"):
            self._send_error_json("Bu uç yalnızca POST kabul eder.", 405)
            return
        dosya = self._resolve_static(yol)
        if dosya is None:
            self._send_error_json("Sayfa bulunamadı.", 404)
            return
        self._serve_file(dosya)

    def do_POST(self) -> None:
        from urllib.parse import urlparse

        yol = urlparse(self.path).path
        handler = API_ROUTES.get(yol)
        if handler is None:
            self._send_error_json("Uç bulunamadı.", 404)
            return
        if yol == "/api/content":
            self._send_error_json("Bu uç yalnızca GET kabul eder.", 405)
            return
        try:
            uzunluk = int(self.headers.get("Content-Length", 0))
        except (TypeError, ValueError):
            self._send_error_json("Geçersiz istek boyutu.", 400)
            return
        if uzunluk > MAX_BODY:
            self._send_error_json("İstek gövdesi çok büyük.", 413)
            return
        ham = self.rfile.read(uzunluk) if uzunluk > 0 else b""
        try:
            data = json.loads(ham.decode("utf-8")) if ham else {}
            if not isinstance(data, dict):
                raise ValueError
        except (ValueError, UnicodeDecodeError):
            self._send_error_json("Geçersiz JSON gövdesi.", 400)
            return
        try:
            self._send_json(handler(data))
        except ApiError as e:
            self._send_error_json(e.message, e.status)
        except Exception as e:  # motor hatası sunucuyu kapatmasın
            self.log_message("işlenmeyen hata: %s", repr(e))
            self._send_error_json("Sunucu içinde beklenmeyen bir hata oluştu.", 500)

    def _serve_file(self, dosya: Path) -> None:
        veri = dosya.read_bytes()
        self.send_response(200)
        self.send_header(
            "Content-Type", CONTENT_TYPES.get(dosya.suffix, "application/octet-stream")
        )
        self.send_header("Content-Length", str(len(veri)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(veri)


def main(argv=None) -> int:
    ayrıştırıcı = argparse.ArgumentParser(description="Vektör Uzayları yerel sunucu")
    ayrıştırıcı.add_argument("--port", type=int, default=8000, help="Dinlenecek port")
    ayrıştırıcı.add_argument("--host", default="127.0.0.1", help="Dinlenecek adres")
    args = ayrıştırıcı.parse_args(argv)

    try:
        httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    except OSError as e:
        print(
            f"Port {args.port} kullanılamıyor ({e}). "
            f"Farklı bir port deneyin: py -3 app.py --port {args.port + 1}",
            file=sys.stderr,
        )
        return 1

    print(f"Vektör Uzayları çalışıyor: http://{args.host}:{args.port}")
    print("Durdurmak için Ctrl+C.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nSunucu kapatılıyor.")
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
