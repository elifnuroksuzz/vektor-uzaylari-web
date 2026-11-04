"""Ders oynatıcısı için adım + sahne üretimi.

Ders metinleri ``data/dersler.json`` içindedir. Her adımın sahnesi (oklar,
noktalar, doğrular, çokgenler, taramalar) kısa ifadelerle tarif edilir ve
koordinatlar burada :mod:`core.vecexpr` ile KESİN olarak hesaplanır. Tarayıcı
yalnızca bu hazır koordinatları canlandırır.

Parametreler (u, v, λ, …) kullanıcı tarafından değiştirilebilir ya da rastgele
seçilebilir; ispat metni genel kaldığı için adımlar aynı kalır, yalnızca
örnek görüntü değişir. Bu, "örnek ≠ ispat" fikrini somutlaştırır.
"""

from __future__ import annotations

import json
import math
import random
from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Optional

from . import analysis, arithmetic
from .arithmetic import SayiHatasi
from .vecexpr import (
    Deger,
    environment,
    evaluate,
    fill_placeholders,
    is_vector,
    to_json,
)

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "dersler.json"

MAX_SWEEP = 500
_SKALER_SECENEK = ["-2", "-1", "-1/2", "1/2", "2", "3"]


def _load() -> Dict[str, dict]:
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        veri = json.load(f)
    return {d["id"]: d for d in veri["lessons"]}


LESSONS = _load()


def catalog() -> List[dict]:
    """İçerik ucu için ders listesi (metinsiz özet)."""

    return [
        {
            "id": d["id"],
            "tab": d["tab"],
            "title": d["title"],
            "short": d.get("short", d["title"]),
            "badge": d.get("badge", ""),
            "summary": d.get("summary", ""),
            "group": d.get("group", ""),
        }
        for d in LESSONS.values()
    ]


# --- Parametreler ---------------------------------------------------------


def _parse_param(spec: dict, deger) -> Deger:
    if spec["type"] == "vec":
        if not isinstance(deger, list) or len(deger) != len(spec["value"]):
            raise SayiHatasi(f"{spec['label']} {len(spec['value'])} bileşenli olmalı.")
        return tuple(arithmetic.parse_vector(deger))
    if isinstance(deger, list):
        raise SayiHatasi(f"{spec['label']} bir sayı olmalı.")
    return arithmetic.parse_fraction(deger)


def _random_param(spec: dict, rng: random.Random) -> Deger:
    if spec["type"] == "vec":
        n = len(spec["value"])
        while True:
            v = tuple(Fraction(rng.randint(-3, 3)) for _ in range(n))
            if any(x != 0 for x in v):
                return v
    secenek = spec.get("choices", _SKALER_SECENEK)
    return Fraction(rng.choice(secenek))


def _check_requirements(
    ders: dict,
    ortam: Dict[str, Deger],
    randomizing: bool = False,
    partial: bool = False,
) -> Optional[str]:
    for kosul in ders.get("require", []):
        if kosul.get("random_only") and not randomizing:
            continue  # yalnızca rastgele seçimde "güzel görüntü" koşulu
        try:
            deger = evaluate(kosul["expr"], ortam)
        except SayiHatasi as e:
            if partial and str(e).startswith("Tanımsız ad"):
                continue  # türetilmiş değerler henüz yok; sonra kontrol edilir
            raise
        if is_vector(deger):
            raise SayiHatasi("Koşul ifadesi skaler olmalı.")
        hedef = Fraction(kosul.get("value", "0"))
        op = kosul["op"]
        tamam = {
            "!=": deger != hedef,
            "==": deger == hedef,
            ">": deger > hedef,
            "<": deger < hedef,
            ">=": deger >= hedef,
            "<=": deger <= hedef,
        }[op]
        if not tamam:
            return kosul["message"]
    return None


def _build_env(ders: dict, params: Dict[str, Deger]) -> Dict[str, Deger]:
    ortam = environment(params)
    for ad, ifade in ders.get("defs", []):
        ortam[ad] = evaluate(ifade, ortam)
    for tur in ders.get("derive", []):
        if tur["type"] == "nullspace":
            vektorler = [list(ortam[n]) for n in tur["vectors"]]
            temel = analysis.null_space(vektorler)["basis"]
            ilk = temel[0] if temel else [Fraction(0)] * len(vektorler)
            for ad, x in zip(tur["names"], ilk):
                ortam[ad] = x
        else:  # pragma: no cover - veri hatası
            raise SayiHatasi("Bilinmeyen türetme.")
    return ortam


def resolve_params(
    ders: dict,
    overrides: Optional[dict] = None,
    randomize: bool = False,
    seed: Optional[int] = None,
) -> Dict[str, Deger]:
    specs = ders.get("params", [])
    varsayilan = {s["name"]: _parse_param(s, s["value"]) for s in specs}

    if randomize:
        rng = random.Random(seed)
        for _ in range(400):
            aday = dict(varsayilan)
            for s in specs:
                if s.get("random", True):
                    aday[s["name"]] = _random_param(s, rng)
            try:
                ortam = _build_env(ders, aday)
                if _check_requirements(ders, ortam, randomizing=True) is None:
                    return aday
            except SayiHatasi:
                continue
        return varsayilan

    params = dict(varsayilan)
    if overrides:
        if not isinstance(overrides, dict):
            raise SayiHatasi("Parametreler sözlük olmalı.")
        for s in specs:
            if s["name"] in overrides:
                params[s["name"]] = _parse_param(s, overrides[s["name"]])
    return params


# --- Sahne ----------------------------------------------------------------


def _in_set(kume: Optional[dict], p) -> Optional[bool]:
    if not kume or not is_vector(p) or len(p) != 2:
        return None
    x, y = p
    if kume["type"] == "line":
        return y == Fraction(kume["m"]) * x + Fraction(kume.get("b", "0"))
    bolge = kume.get("region")
    if bolge == "q1":
        return x > 0 and y > 0
    if bolge == "q13":
        return x * y >= 0
    if bolge == "all":
        return True
    return None


def _vec(ifade: str, ortam) -> tuple:
    d = evaluate(ifade, ortam)
    if not is_vector(d):
        raise SayiHatasi(f"'{ifade}' bir vektör olmalı.")
    return d


def _auto_kind(kume, p, label):
    icinde = _in_set(kume, p)
    if icinde is None:
        return "sonuc", label
    if label:
        label = label + (" ∈ W" if icinde else " ∉ W")
    return ("icerde" if icinde else "disarda"), label


def _frange(spec):
    lo, hi, adim = (Fraction(x) for x in spec)
    if adim <= 0:
        raise SayiHatasi("Tarama adımı pozitif olmalı.")
    degerler = []
    x = lo
    while x <= hi and len(degerler) < 200:
        degerler.append(x)
        x += adim
    return degerler


def eval_scene(sahne: dict, ortam: Dict[str, Deger]) -> dict:
    cikti: dict = {}
    kume = sahne.get("set")
    if kume:
        cikti["set"] = dict(kume)
    if sahne.get("plane"):
        cikti["plane"] = True
    if sahne.get("lines"):
        cikti["lines"] = [
            {
                "id": l["id"],
                "m": l["m"],
                "b": l.get("b", "0"),
                "label": fill_placeholders(l.get("label", ""), ortam),
                "kind": l.get("kind", "ek"),
            }
            for l in sahne["lines"]
        ]

    span = []
    for s in sahne.get("spanLines", []):
        d = _vec(s["dir"], ortam)
        if any(x != 0 for x in d):
            span.append({"id": s["id"], "dir": to_json(d), "label": fill_placeholders(s.get("label", ""), ortam)})
    if span:
        cikti["spanLines"] = span

    if sahne.get("grid"):
        b1 = _vec(sahne["grid"]["b1"], ortam)
        b2 = _vec(sahne["grid"]["b2"], ortam)
        if b1[0] * b2[1] - b1[1] * b2[0] != 0:
            cikti["grid"] = {"b1": to_json(b1), "b2": to_json(b2)}

    vektorler = []
    for v in sahne.get("vectors", []):
        uc = _vec(v["to"], ortam)
        bas = _vec(v["from"], ortam) if v.get("from") else None
        label = fill_placeholders(v.get("label", ""), ortam)
        kind = v.get("kind", "giris")
        if kind == "auto":
            kind, label = _auto_kind(kume, uc, label)
        o = {"id": v["id"], "to": to_json(uc), "label": label, "kind": kind}
        if bas is not None:
            o["from"] = to_json(bas)
        if v.get("offset"):
            o["offset"] = True
        vektorler.append(o)
    if vektorler:
        cikti["vectors"] = vektorler

    noktalar = []
    for p in sahne.get("points", []):
        at = _vec(p["at"], ortam)
        label = fill_placeholders(p.get("label", ""), ortam)
        kind = p.get("kind", "nokta")
        if kind == "auto":
            kind, label = _auto_kind(kume, at, label)
        noktalar.append({"id": p["id"], "at": to_json(at), "label": label, "kind": kind})
    if noktalar:
        cikti["points"] = noktalar

    cokgenler = []
    for pg in sahne.get("polygons", []):
        cokgenler.append(
            {
                "id": pg["id"],
                "pts": [to_json(_vec(e, ortam)) for e in pg["pts"]],
                "kind": pg.get("kind", "alan"),
                "label": fill_placeholders(pg.get("label", ""), ortam),
            }
        )
    if cokgenler:
        cikti["polygons"] = cokgenler

    if sahne.get("sweep"):
        sw = sahne["sweep"]
        adlar = list(sw["vars"].keys())
        araliklar = [_frange(sw["vars"][a]) for a in adlar]
        noktalar_sw = []
        yerel = dict(ortam)

        def tara(i):
            if len(noktalar_sw) >= MAX_SWEEP:
                return
            if i == len(adlar):
                noktalar_sw.append(to_json(_vec(sw["expr"], yerel)))
                return
            for x in araliklar[i]:
                yerel[adlar[i]] = x
                tara(i + 1)

        tara(0)
        cikti["sweep"] = {
            "id": sw.get("id", "tarama"),
            "points": noktalar_sw,
            "label": fill_placeholders(sw.get("label", ""), ortam),
        }

    if sahne.get("focus"):
        cikti["focus"] = list(sahne["focus"])
    return cikti


def _scene_extent(sahne: dict) -> float:
    m = 0.0

    def gor(p):
        nonlocal m
        for x in p:
            m = max(m, abs(float(Fraction(x))))

    for v in sahne.get("vectors", []):
        gor(v["to"])
        if "from" in v:
            gor(v["from"])
    for p in sahne.get("points", []):
        gor(p["at"])
    for pg in sahne.get("polygons", []):
        for p in pg["pts"]:
            gor(p)
    if "grid" in sahne:
        gor(sahne["grid"]["b1"])
        gor(sahne["grid"]["b2"])
    return m


# --- Ders kurma -----------------------------------------------------------


def build_lesson(
    lesson_id: str,
    overrides: Optional[dict] = None,
    randomize: bool = False,
    seed: Optional[int] = None,
) -> dict:
    ders = LESSONS.get(lesson_id)
    if ders is None:
        raise SayiHatasi("Geçersiz ders kimliği.")

    params = resolve_params(ders, overrides, randomize, seed)
    # Önce yalnızca parametrelerle kontrol: ör. D = 0 iken bölme yapmadan
    # anlaşılır mesaj verilsin.
    hata = _check_requirements(ders, environment(params), partial=True)
    if hata:
        raise SayiHatasi(hata)
    ortam = _build_env(ders, params)
    hata = _check_requirements(ders, ortam)
    if hata:
        raise SayiHatasi(hata)

    temel = ders.get("base_scene", {})
    adimlar = []
    kapsam = 0.0
    for adim in ders["steps"]:
        sahne_tarif = dict(temel)
        sahne_tarif.update(adim.get("scene", {}))
        sahne = eval_scene(sahne_tarif, ortam)
        kapsam = max(kapsam, _scene_extent(sahne))
        adimlar.append(
            {
                "kind": adim.get("kind", "ispat"),
                "title": fill_placeholders(adim.get("title", ""), ortam),
                "text": fill_placeholders(adim.get("text", ""), ortam),
                "math": [fill_placeholders(m, ortam) for m in adim.get("math", [])],
                "why": fill_placeholders(adim.get("why", ""), ortam),
                "caption": fill_placeholders(adim.get("caption", ""), ortam),
                "scene": sahne,
            }
        )

    aralik = max(3, min(12, math.ceil(kapsam + 0.75)))
    return {
        "id": ders["id"],
        "tab": ders["tab"],
        "title": ders["title"],
        "badge": ders.get("badge", ""),
        "summary": fill_placeholders(ders.get("summary", ""), ortam),
        "claim": fill_placeholders(ders.get("claim", ""), ortam),
        "param_note": ders.get("param_note", ""),
        "params": [
            {
                "name": s["name"],
                "label": s["label"],
                "type": s["type"],
                "value": to_json(params[s["name"]]),
                "random": s.get("random", True),
            }
            for s in ders.get("params", [])
        ],
        "randomizable": any(s.get("random", True) for s in ders.get("params", [])),
        "range": aralik,
        "steps": adimlar,
    }
