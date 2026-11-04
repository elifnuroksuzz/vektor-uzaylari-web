# Vektör Uzayları

Ders anlatımında kullanılabilen, öğrencinin de deney yapabildiği sade bir
Türkçe web uygulaması. Üçüncü taraf bağımlılık yoktur: yalnızca Python 3.11+
standart kütüphanesi (sunucu için `http.server`, kesin aritmetik için
`fractions.Fraction`). Matematiksel kararların tümünü Python üretir; tarayıcı
yalnızca kontrol, animasyon ve görüntüleme yapar. İnternet gerekmez; sunucu
sadece `127.0.0.1` üzerinde dinler.

## Çalıştırma (Windows)

```powershell
cd vektor_uzaylari_web
py -3 app.py
```

`py` yoksa:

```powershell
python app.py
```

Ardından tarayıcıda **http://127.0.0.1:8000** adresini açın. Durdurmak için
terminalde **Ctrl+C**.

Port doluysa anlaşılır bir hata verilir; farklı port:

```powershell
py -3 app.py --port 8001
```

`pip install` veya Node derleme adımı **gerekmez**.

## Testler

```powershell
py -3 -m unittest discover -s tests -v
```

## Bölümler

Her konu sekmesi aynı düzendedir: **kısa konu anlatımı → ders seçici → ders
oynatıcısı**. Oynatıcıda anlatım (solda, adım adım açılır) ve grafik (sağda,
her adımda canlanır) aynı yerdedir. **Grafiğe tıklamak**, *İleri* düğmesi ya da
**→** tuşu sonraki adıma geçer; **←** geri, *Oynat* otomatik ilerler, *Tahta
modu* projeksiyon için tam ekran açar (Esc ile çıkılır).

- **4.1 Vektör Uzayları** — V1–V8’in her biri için bileşen bileşen **genel
  ispat** (her satırın gerekçesiyle), Teorem 4.1.1 (0·v = 0, (−1)v = −v,
  c·0 = 0) için yalnızca aksiyomlardan ispat, V8’in neden gerekli olduğu ve
  vektör uzayı OLMAYAN bir yapı (karşı örnek).
- **4.1.1 Alt Uzaylar** — y = 2x (genel ispat), y = 2x + 1, x > 0 ∧ y > 0,
  xy ≥ 0; tek adım alt uzay testi; Span(S) alt uzaydır; mühendislik: Ax = 0
  ve Ax = b, “özel + homojen çözüm”, süperpozisyon.
- **4.1.2 Doğrusal Germe** — birleşimi adım adım kurma, tek vektörün span’i,
  det ≠ 0 ⇒ ℝ²’yi germe (Cramer ile genel ispat + eğik ızgara), çakışık
  vektörler. Sürgülü laboratuvar ve **fazör / süperpozisyon laboratuvarı**
  (y″ + y = 0 çözümleri = Span{cos t, sin t}).
- **4.2 Bağımsızlık ve Baz** — bağımsızlık tanımı ve ispatı, ℝ²’de üç vektör
  her zaman bağımlı (kapanan çokgen; katsayıları motor bulur), bağımlı ⇔
  det = 0, baz ve koordinatların tekliği, mühendislik: iki kabloyla asılı yük
  (statik denge = baz koordinatları).
- **Kendi Vektörlerin** — ℝᵐ’de gerilen uzay, hedef üyeliği, **bağımsızlık
  testi ve baz seçimi** (orijinal pivot sütunları).
- **Sorular** — 17, 20, Örnek 4.1.5, 15 ve 4.2 soruları (bağımlılık, geren
  kümeden baz seçimi); her satır işlemi ayrı adım, değişen satır vurgulanır.

### “Örnek ≠ ispat” ilkesi

İspat satırları genel (keyfi u, v, λ …) yazılır; grafik yalnızca bir örnek
görüntüdür. Parametreler düzenlenebilir ya da **🎲 Başka sayılarla dene** ile
rastgele seçilebilir: sunucu sahneyi yeniden hesaplar, ispat satırları aynı
kalır. “Sağlanmıyor” sonuçları tek bir karşı örnekle gösterilir ve bunun
mantığı (¬∀ ⇔ ∃¬) açıkça yazılır.

### Ders içeriğini düzenlemek

Dersler `data/dersler.json` içindedir. Her adımda `text`, `math`, `why`
(gerekçe) ve `scene` (oklar, noktalar, doğrular, çokgenler, taramalar) vardır.
Sahne koordinatları `"u+v"`, `"(a+b)*v"`, `"[r, 2*r]"`, `"det(v1, v2)"` gibi
ifadelerle yazılır; `core/vecexpr.py` bunları `eval` kullanmadan, kesin
kesirlerle hesaplar. Metinde `{{ifade}}` hesaplanan değerle değiştirilir.

## Dizin

```
vektor_uzaylari_web/
  app.py              Yerel HTTP sunucusu + API
  core/               Saf Python matematik motoru
    arithmetic.py       Fraction ayrıştırma, vektör/matris işlemleri
    elimination.py      Elle yazılmış REF/RREF, adım kaydı
    expressions.py      Doğrusal ifade (sembolik sağ taraf)
    analysis.py         Birleşim, üyelik, homojen koşullar, aksiyomlar
    guided_parameters.py 16. soru rehberli çözümü
    vecexpr.py          Güvenli vektör/skaler ifade değerlendirici
    lessons.py          Ders adımları + sahne koordinatları
  data/               axioms.json, lessons.json, questions.json, dersler.json
  static/             index.html, styles.css, ortak.js, diagrams.js (sahne
                      motoru), player.js (ders oynatıcısı), app.js
  tests/              test_math.py, test_api.py, test_lessons.py
```

## API (özet)

| Uç | Yöntem | Açıklama |
|----|--------|----------|
| `/api/content` | GET | Aksiyomlar, konu başlıkları, soru listesi |
| `/api/axiom` | POST | rule_id + vektör/skalerler → iki tarafın hesabı |
| `/api/combination` | POST | vektörler + katsayılar → ara ve sonuç vektörleri |
| `/api/span` | POST | vektörler (+hedef) → üyelik ve homojen koşullar |
| `/api/subspace` | POST | örnek + kontrol → sonuç ve sayısal doğrulama |
| `/api/solve` | POST | question_id → adımlar ve sonuç |
| `/api/lesson` | POST | lesson_id (+params / randomize) → adımlar ve sahneler |
| `/api/dependence` | POST | vektörler → bağımsızlık, bağıntı, baz |

Rasyonel sayılar JSON'da string taşınır (float kesinliğinden geçmez). İstek
gövdesi en çok 64 KB, matris en çok 8×8, sayı girdisi en çok 80 karakter.
Hatalı JSON/eksik alan Türkçe mesajla 400 döner; 404/405 düzgün yanıtlanır.

## Kapsam ve sınırlar

- **Kaynak:** VEKTÖR UZAYLARI, basılı sayfa 107–117 (Tanım 4.1.1–4.1.4, Teorem
  4.1.1/4.1.3, örnekler 4.1.1, 4.1.4–4.1.6). Ayrıntılı kaynak/düzeltme notları
  için [SOURCE_NOTES.md](SOURCE_NOTES.md).
- **Kesin aritmetik:** tam sayı, kesir (`-2/3`) ve sonlu ondalık (`0.25`,
  `2.25 = 9/4`) girdileri `Fraction` ile işlenir.
- **Sembolik kapsam:** sağ taraf doğrusal ifadelerle (`sabit + Σ katsayı·sembol`)
  taşınır; genel bir CAS değildir. İki sembolik ifade çarpılmaz.
- **16. soru:** genel sembolik pivotlama değil, doğrulanmış *rehberli parametre
  çözümü*dür; sayısal `a, b` girişinde sonuç genel Fraction motoruyla yeniden
  hesaplanır ve cebirsel dalla tutarlılığı kontrol edilir.
- Görsel/sayısal örnekler bir aksiyomun **genel ispatı değildir**; arayüz bu
  ayrımı açıkça belirtir.
