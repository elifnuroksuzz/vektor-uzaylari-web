# Vektör Uzayları — Adım Adım Ders Anlatım Rehberi

> Bu dosya, konuyu **sen anlatırken** takip edeceğin öğretmen notudur. Her
> bölüm uygulamadaki bir sekmeyle eşleşir: **Kurallar → Alt Uzaylar →
> Doğrusal Germe → Sorular**. Maddeleri sırayla anlat; _Tahtaya yaz_ ve
> _Sınıfa sor_ ipuçlarını istersen kullan.

**İçindekiler**

1. [Vektör uzayı nedir? (V1–V8)](#1-vektör-uzayı-nedir-v1v8)
2. [Alt uzaylar](#2-alt-uzaylar)
3. [Doğrusal germe (span)](#3-doğrusal-germe-span)
4. [Sorular — adım adım çözüm](#4-sorular--adım-adım-çözüm)
   - [Soru 17 — Doğrusal birleşim](#soru-17--doğrusal-birleşim)
   - [Soru 20 — Homojen sistem](#soru-20--homojen-sistem)
   - [Örnek 4.1.5 — Bütün ℝ³'ü germek](#örnek-415--bütün-ℝ³ü-germek)
   - [Soru 15 — Polinomlar da vektördür](#soru-15--polinomlar-da-vektördür)
5. [Kapanış — anahtar fikirler](#5-kapanış--anahtar-fikirler)

---

## 1. Vektör uzayı nedir? (V1–V8)

**Ana fikir (tek cümle):** Üzerinde *toplama* ve *sayıyla (skalerle) çarpma*
tanımlı olan, bu iki işlemin sekiz kuralı sağladığı kümeye **vektör uzayı**
denir.

**Önkoşul (tahtaya küçük not):** V boş olmayan bir küme, F bir cisimdir
(gerçek sayılar). Toplama iki vektörü yine bir vektöre, skalerle çarpma bir
sayı ile bir vektörü yine bir vektöre götürür. Yani küme bu işlemler altında
**kapalıdır** — bu, kuralların bir parçasıdır.

### Sekiz kural

| # | Ad | Formül |
|---|---|---|
| V1 | Toplamada birleşme | u+(v+w) = (u+v)+w |
| V2 | Sıfır vektörü | v+0 = 0+v = v |
| V3 | Toplamsal ters | v+(−v) = (−v)+v = 0 |
| V4 | Toplamada değişme | u+v = v+u |
| V5 | Vektör toplamına dağılma | c(u+v) = cu+cv |
| V6 | Skaler toplamına dağılma | (a+b)v = av+bv |
| V7 | Skaler çarpımının uyumu | (ab)v = a(bv) |
| V8 | Birim skaler | 1·v = v |

### Nasıl anlatılır (adım adım)

1. **Başla:** "Vektör dediğimiz şey sadece oklar değil; bu sekiz kuralı
   sağlayan her nesne vektördür. Birazdan polinomların bile vektör olduğunu
   göreceğiz."
2. **İki örnek seç** (uygulamadaki önayarlar):
   - Örnek 1: u=(1,2), v=(3,−1), w=(−2,1), a=2, b=−1, c=2.
   - Örnek 2: u=(−2,1), v=(1,3), w=(2,−2), a=−1, b=3, c=−2.
3. **Her kuralda iki tarafı ayrı ayrı hesapla**, sonra karşılaştır. Örnek:
   - **V4 (değişme):** u+v = (1,2)+(3,−1) = (4,1);  v+u = (3,−1)+(1,2) = (4,1).
     İki taraf eşit. ✓
   - **V3 (toplamsal ters):** v=(3,−1), −v=(−3,1); v+(−v) = (0,0). Grafikte
     `v` ve `−v` zıt yönde, eşit uzunlukta; uç uca eklenince orijine döner.
   - **V6 (dağılma):** a=2, b=−1, v=(3,−1). av=(6,−2), bv=(−3,1),
     av+bv=(3,−1); (a+b)v = 1·(3,−1) = (3,−1). Eşit. ✓
4. **Vurgula (çok önemli uyarı):** "Birkaç sayıda doğru çıkması **ispat
   değildir**. Örnek sadece fikri gösterir; genel ispat ‘her uygun vektör
   için’ cebirle yapılır."

> _Sınıfa sor:_ "V2'deki sıfır vektörü her vektör için **aynı** mı olmalı,
> yoksa her vektörün kendi sıfırı mı var?" (Yanıt: tek bir ortak sıfır vektörü.)

---

## 2. Alt uzaylar

**Ana fikir:** Büyük uzayın (ör. ℝ²) içinden seçtiğimiz bir alt küme, **aynı
işlemlerle** kendisi de vektör uzayıysa bir **alt uzaydır**.

### Üç kontrol (hepsi gerekli)

| Kontrol | Soru |
|---|---|
| 1. Sıfır vektörü | (0,0) kümede mi? |
| 2. Toplamaya kapalılık | İki vektörün toplamı yine kümede mi? |
| 3. Skalerle çarpmaya kapalılık | Bir vektörün her sayıyla çarpımı yine kümede mi? |

> **Kural:** Üçü de sağlanmalı. **Biri bile** bozulursa alt uzay değildir.
> Önce sıfır vektörüne bak: yoksa anında eleriz.

### Dört örnek (adım adım)

**a) y = 2x** → **alt uzaydır.**
- Sıfır: 0 = 2·0 ✓
- Toplama (genel): u=(r,2r), v=(s,2s) ⇒ u+v=(r+s, 2(r+s)) yine kümede ✓
- Skaler (genel): λ(r,2r) = (λr, 2λr) yine kümede ✓
- Üçü de sağlandı → **alt uzay.**

**b) y = 2x + 1** → **alt uzay DEĞİL.**
- Sıfır: 0 = 2·0+1 = 1 **yanlış** → (0,0) yok. Karar vermek için bu yeter.
- (Doğru orijinden geçmiyor; "görünüşü benziyor ama özellik kayboldu.")

**c) x > 0 ve y > 0** (birinci bölge) → **alt uzay DEĞİL.**
- Toplama: (1,2)+(3,1)=(4,3) hâlâ pozitif → bu koşul **sağlanır.**
- Skaler: −1·(5,2) = (−5,−2) **kümede değil** → skalerle çarpmaya kapalı
  değil. (Ayrıca (0,0) da yok.)
- **Ders:** "Yalnızca toplamaya kapalı olmak yetmez."

**d) xy ≥ 0** (1. ve 3. bölgeler) → **alt uzay DEĞİL.**
- Sıfır: 0·0 = 0 ≥ 0 ✓ (ama tek başına yetmez)
- Skaler (genel): (λx)(λy) = λ²·xy ≥ 0 → **sağlanır.**
- Toplama: u=(1,2), v=(−3,−1) (ikisi de kümede), ama u+v=(−2,1) ve
  (−2)·1 = −2 < 0 → **kümeden çıkar.** → alt uzay değil.
- **Ders:** "Sıfır var, skalere kapalı, ama toplamaya kapalı değil — yine olmaz."

### Karşılaştırma tablosu (kapanışta göster)

| Küme | Sıfır | Toplama | Skaler | Alt uzay? |
|---|:--:|:--:|:--:|:--:|
| y = 2x | ✓ | ✓ | ✓ | **Evet** |
| y = 2x+1 | ✗ | ✗ | ✗ | **Hayır** |
| x>0, y>0 | ✗ | ✓ | ✗ | **Hayır** |
| xy ≥ 0 | ✓ | ✗ | ✓ | **Hayır** |

> **Altın kural:** Bir **karşı örnek** koşulun bozulduğunu gösterir. Koşulun
> *sağlandığını* göstermek için **genel cebir** gerekir.

---

## 3. Doğrusal germe (span)

**Ana fikir:** Verilen vektörleri sayılarla çarpıp toplayarak elde
edebileceğimiz **bütün** vektörlerin kümesine **span** (gerilen uzay) denir.

- **w = α·v₁ + β·v₂** tek bir **doğrusal birleşimdir.**
- Bütün α, β değerleri için elde edilenlerin tamamı **span**'dir.

### Üç temel durum (grafikle)

1. **Bir doğru:** Tek bir yön, ör. (1,2). Katları `y = 2x` doğrusunu verir.
   Genelde (a,b) için `y = (b/a)·x`. → **rank 1.**
2. **Bütün düzlem:** İki bağımsız yön, ör. (1,0) ve (0,1). Her noktaya
   ulaşılır → span = ℝ². → **rank 2.**
3. **Yalnızca sıfır:** Sıfır vektörünün katları hep sıfır → span = {orijin}.
   → **rank 0.**

> **Anahtar ayrım:** "Şu an oluşturduğun **tek** vektör bir doğrusal
> birleşimdir. Oluşturabileceğin **bütün** vektörler ise span'i oluşturur."

**Rank = pivot sayısı.** Vektörler ℝᵐ'de ise, span'in ℝᵐ'nin tamamı olması için
rank = m olmalıdır.

---

## 4. Sorular — adım adım çözüm

**Ortak yöntem (hepsinde aynı):**
1. Vektörleri bir matrisin **sütunlarına** yerleştir.
2. Hedef (sayısal veya sembolik) sağ tarafa yazılır → **genişletilmiş matris.**
3. **Satır işlemleriyle** (Gauss eliminasyonu) basamak biçimine getir.
4. Son satırları yorumla: çözüm var mı, koşul ne, rank kaç?

> Not: Satır işlemi `Rᵢ ← Rᵢ − k·Rⱼ`, i. satırdan k katı j. satırı çıkarmaktır;
> aynı işlem sağ tarafa da uygulanır.

---

### Soru 17 — Doğrusal birleşim

**Soru:** (4, −2, 4) vektörü (1,0,1), (3,−4,1), (4,−6,−2) vektörlerinin
doğrusal birleşimi olarak yazılabilir mi?

**Ne isteniyor?** λ₁v₁ + λ₂v₂ + λ₃v₃ = (4,−2,4) yapan katsayılar var mı?

**Adım 1 — Sütunlara yerleştir, genişletilmiş matris (satırlar bileşenlerdir):**
```
[ 1   3   4 | 4 ]
[ 0  -4  -6 | -2 ]
[ 1   1  -2 | 4 ]
```

**Adım 2 — İlk sütunu temizle:**  R3 ← R3 − R1
```
[ 1   3   4 | 4 ]
[ 0  -4  -6 | -2 ]
[ 0  -2  -6 | 0 ]
```

**Adım 3 — İkinci sütunu temizle:**  R3 ← R3 − (1/2)·R2
```
[ 1   3   4 | 4 ]
[ 0  -4  -6 | -2 ]
[ 0   0  -3 | 1 ]
```

**Adım 4 — Geri yerine koyma:**
- Son satır: −3λ₃ = 1 ⇒ **λ₃ = −1/3**
- İkinci satır: −4λ₂ − 6λ₃ = −2 ⇒ −4λ₂ + 2 = −2 ⇒ **λ₂ = 1**
- Birinci satır: λ₁ + 3λ₂ + 4λ₃ = 4 ⇒ λ₁ + 3 − 4/3 = 4 ⇒ **λ₁ = 7/3**

**Sonuç:** Evet. Katsayılar **(7/3, 1, −1/3)**. Çelişki yok, **tek çözüm.**

> _Kontrol (sınıfa yaptır):_ (7/3)(1,0,1) + 1·(3,−4,1) − (1/3)(4,−6,−2) = (4,−2,4). ✓

---

### Soru 20 — Homojen sistem

**Soru:** Span{(1,−1,0), (0,1,1), (3,−5,−2)} uzayını homojen bir doğrusal
sistemin çözüm kümesi olarak ifade ediniz.

**Ne isteniyor?** Bu üç vektörün gerdiği uzaydaki (x,y,z) hangi denklemi sağlar?

**Fikir:** Sayısal hedef yerine **genel** hedef (x,y,z) kullanırız.

**Adım 1 — Genişletilmiş matris (sütunlar vektörler, sağ taraf sembolik):**
```
[ 1   0   3 | x ]
[ -1  1  -5 | y ]
[ 0   1  -2 | z ]
```

**Adım 2:**  R2 ← R2 + R1
```
[ 1   0   3 | x ]
[ 0   1  -2 | x + y ]
[ 0   1  -2 | z ]
```

**Adım 3:**  R3 ← R3 − R2
```
[ 1   0   3 | x ]
[ 0   1  -2 | x + y ]
[ 0   0   0 | z − x − y ]
```

**Adım 4 — Son satırı yorumla:** Sol taraf tamamen sıfır olduğundan sağ taraf
da sıfır olmalı:
$$ z − x − y = 0 \quad\Longleftrightarrow\quad \boxed{x + y − z = 0} $$

**Sonuç:** Span = { (x,y,z) : x + y − z = 0 }. **rank = 2** (iki pivot),
yani düzlemsel bir alt uzay.

> _Not:_ Bunu matris diliyle `[1  1  −1]·[x y z]ᵀ = 0` diye de yazabilirsin;
> bu **aynı** denklemdir, yeni bir işlem değildir.

---

### Örnek 4.1.5 — Bütün ℝ³'ü germek

**Soru:** {(1,2,−1), (−3,1,0), (2,−3,2)} kümesinin ℝ³'ü gerdiğini gösteriniz.

**Ne isteniyor?** Her (a,b,c) hedefine ulaşılabiliyor mu? (Yani rank = 3 mü?)

**Adım 1 — Genişletilmiş matris (genel hedef a,b,c):**
```
[ 1  -3   2 | a ]
[ 2   1  -3 | b ]
[ -1  0   2 | c ]
```

**Adım 2 — İlk sütun:**  R2 ← R2 − 2R1,  R3 ← R3 + R1
```
[ 1  -3   2 | a ]
[ 0   7  -7 | b − 2a ]
[ 0  -3   4 | c + a ]
```

**Adım 3 — İkinci sütun:**  R3 ← R3 + (3/7)·R2
```
[ 1  -3   2 | a ]
[ 0   7  -7 | b − 2a ]
[ 0   0   1 | a + 3b/7 + c ... ]   (tam sayıya ölçeklenirse → a + 3b + 7c)
```

**Adım 4 — Yorum:** Üç pivot var → **rank = 3.** Hiçbir satır tümüyle
sıfırlanmadı, yani **hiçbir koşul yok**: her (a,b,c) için çözüm bulunur.

**Sonuç:** Bu üç vektör **ℝ³'ün tamamını gerer.**

> **Kaynak düzeltmesi:** PDF s.117'de son satırın sağ tarafı hatalı
> basılmıştır. Katsayı satırı [0,0,7] olduğunda doğru sağ taraf
> **a + 3b + 7c**'dir (hatalı `a − 3b − 7c` değil). Sonucu değiştirmez; rank
> yine 3'tür.

> _Kıyasla:_ Soru 20'de rank 2 çıkıp **bir koşul** doğmuştu (germe yok).
> Burada rank 3, **koşul yok** (tam germe). Fark buradadır.

---

### Soru 15 — Polinomlar da vektördür

**Soru:** 1 + x + c·x² + d·x³ polinomu şu dört polinomun doğrusal birleşimi
ise c ve d'yi bulunuz:
- p₁ = −1 + 2x + 3x² + 4x³
- p₂ = 4 + x + 6x² + 11x³
- p₃ = 1 − x − x² − x³
- p₄ = 3 + x + 5x² + 9x³

**Fikir (bu sorunun kalbi):** Bir polinomu **katsayı vektörü** olarak yaz.
Sıra `[sabit, x, x², x³]`:
- p₁ = (−1, 2, 3, 4),  p₂ = (4, 1, 6, 11),  p₃ = (1, −1, −1, −1),  p₄ = (3, 1, 5, 9)
- Hedef = (1, 1, **c**, **d**) — ilk iki bileşen biliniyor, son ikisi aranıyor.

**Adım 1 — Span'in koşullarını bul** (genel hedef (w, x, y, z); yöntem Soru
20'deki ile aynı). Bu dört vektörün rank'ı 2'dir ve iki koşul doğar:
$$ y = w + 2x, \qquad z = 2w + 3x $$

**Adım 2 — Bilinen değerleri yerine koy** (w = 1, x = 1):
- c = y = 1 + 2·1 = **3**
- d = z = 2·1 + 3·1 = **5**

**Sonuç:** **c = 3, d = 5.**

**Adım 3 — Bir temsil göster (doğrulama):** 2·p₁ + 3·p₃
$$ 2(−1,2,3,4) + 3(1,−1,−1,−1) = (−2+3,\ 4−3,\ 6−3,\ 8−3) = (1, 1, 3, 5)\ ✓ $$
Yani polinom olarak: 2p₁ + 3p₃ = 1 + x + 3x² + 5x³.

> **Ders:** "Vektör illa ok değil. Polinomu katsayılarına açınca, aynı Gauss
> yöntemini aynen uyguladık. İşte 1. bölümdeki 'polinomlar da vektördür'
> sözünün kanıtı."

---

## 5. Kapanış — anahtar fikirler

1. **Vektör uzayı** = sekiz kuralı sağlayan toplama + skalerle çarpma.
   Örnekler ispat değildir; genel ispat cebirle yapılır.
2. **Alt uzay** = üç koşul (sıfır, toplama, skaler) birden. Biri bozulursa olmaz.
3. **Span** = bütün doğrusal birleşimler. Tek birleşim ≠ span.
4. **Rank = pivot sayısı.** ℝᵐ'de rank = m ise tam germe; değilse koşul(lar)
   doğar ve alt uzay elde edilir.
5. **Bir hedefe ulaşmak** (üyelik) ile **bütün uzayı germek** farklı
   sorulardır: (2,3,5)'e ulaşılır ama (2,3,6)'ya ulaşılmaz — ama ikisi de
   aynı span'i germe sorusu değildir.
6. **Yöntem hep aynı:** sütunlara yaz → genişletilmiş matris → satır işlemleri
   → son satırları yorumla. Sayı, polinom, matris… hepsinde bu çalışır.

> **Uygulamayla eşleştirme:** Kurallar sekmesinde V1–V8'i canlı hesaplat;
> Alt Uzaylar'da dört örneği kontrollerle göster; Doğrusal Germe'de sürgülerle
> span'i hissettir; Sorular'da yukarıdaki dört soruyu **İleri** düğmesiyle
> adım adım aç. "Kendi Vektörlerin" sekmesinde öğrencilerin kendi örneklerini
> denemesini sağla.
