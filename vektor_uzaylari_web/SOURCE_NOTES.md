# Kaynak Notları

Kaynak: **VEKTÖR UZAYLARI**, basılı sayfalar 107–117. PDF çalışma sırasında
bağımlılık değildir; doğrulanmış Türkçe içerik `data/*.json` dosyalarına
aktarılmıştır. Bu uygulama kaynak dosyaları okumuş gibi davranmaz; aşağıdaki
kurallar ve soru verileri doğrudan görev tanımından alınmış ve motor tarafından
bağımsızca doğrulanmıştır.

## Alınan içerik

- **Tanım 4.1.1 (s.107–108):** V₁–V₈ aksiyomları. Sıra değiştirilmemiştir
  (`data/axioms.json`). V boş olmayan küme, F cisim; toplama ve skaler çarpma
  kapalılığı işlem tanımlarının parçasıdır (ayrı aksiyom kartı eklenmedi, kısa
  önkoşul notu gösterildi).
- **Teorem 4.1.1 (s.108–109):** c·0 = 0·v = 0; (−1)v = −v; (−c)v = c(−v) = −(cv).
  İleri bilgi; ana akışta zorunlu değil.
- **Vektör türleri (s.109–112):** matrisler, Fⁿ, fonksiyonlar, polinomlar.
  Pₙ: derecesi EN FAZLA n olan polinomlar ve sıfır polinomu.
- **Tanımlar 4.1.2–4.1.3 (s.112–115):** boş olmama, toplama ve skaler çarpmaya
  kapalılık. Pratikte önce sıfır vektörü kontrol edilir; sıfır içermek tek
  başına yeterli değildir.
- **Tanım 4.1.4 (s.115–116):** doğrusal birleşim; tüm SONLU birleşimlerin
  kümesi Span(S); Span(∅) = {0}.
- **Teorem 4.1.3 (s.117):** Span(S) bir alt uzaydır.

## Düzeltmeler

- **Örnek 4.1.5 (s.117):** PDF'de son satırın sağ tarafı hatalı basılmıştır.
  Katsayı satırı `[0, 0, 7]` olduğunda doğru sağ taraf **a + 3b + 7c**'dir;
  hatalı `a − 3b − 7c` kopyalanmamıştır. Motor bu kümenin ℝ³'ü gerdiğini
  (rank = 3, ek koşul yok) bağımsızca doğrular; dolayısıyla işaret hatası
  sonucu değiştirmez.

## Referans konsol kodundan dönüşüm

Referans `lineer_cebir_egitmeni.py` yaklaşımından alınan fikir: vektörleri
sütunlara yerleştirip her satır işlemini kaydetmek. Düzeltilenler:

- `input`/`print`/`os.system('cls')` ve Enter ile duraklama motorda yoktur; her
  fonksiyon yapılandırılmış veri döndürür.
- Float'tan paydası ≤100 yaklaşık kesir araması kullanılmaz; girdi ilk andan
  itibaren string üzerinden `Fraction`'dır.
- Genişletilmiş matriste sağ taraf pivot sayımına katılmaz (ayrı tutulur).
- Bağımsızlık/germe kararları rank ölçütüne dayanır; "sıfır sütunu yok, o yüzden
  bağımsız" veya "fazla/eksik vektör" genellemeleri kullanılmaz.
- Homojen koşullar sembolik sağ tarafın sıfır katsayı satırlarından türetilir;
  `HA = 0` ve `rank(H) = m − rank(A)` kontrol edilir. Eşdeğer koşul sistemleri
  (aynı çözüm kümesi) kabul edilir; string eşitliğiyle test yapılmaz.

## Sembolik ve parametrik kapsam

- Sembolik sağ taraf yalnızca doğrusal ifadelerle (`sabit + Σ katsayı·sembol`)
  taşınır. Bir sıfır katsayı satırındaki ifade otomatik "çelişki" sayılmaz; bu
  bir üyelik koşuludur. Doğrusal birleşim katsayıları λ₁, λ₂, … olarak
  adlandırılır; hedefin bileşen adlarıyla (a, b, c, …) karıştırılmaz.
- **16. soru** rehberli parametre çözümüdür: `a = 1`, `a = −1`, `a ≠ ±1` dalları
  açıkça ayrılır; `a`'ya bağlı ifadeye bölmeden önce sıfır dalı ayrılır.
  `b = 2.25` tam olarak `9/4` kabul edilir. Sayısal `a, b` girişinde sonuç genel
  Fraction motoruyla yeniden hesaplanır (kapalı-form ile tutarlılık test edilir).

Görsel ve sonlu-sayısal örnekler bir aksiyomun genel ispatı değildir; genel
sonuçlar cebirsel gerekçeyle verilir.
