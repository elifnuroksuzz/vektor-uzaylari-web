# Codex görevi: Python ile Vektör Uzayları web uygulaması

## 0. Bu dosyayı alan Codex'e doğrudan talimat

Bu belgedeki uygulamayı çalışan kod olarak geliştir. Sadece plan veya örnek ekran üretme. Dosyaları oluştur, matematik motorunu doğrula, web arayüzünü çalıştır ve kullanım talimatını yaz. Kullanıcı Windows'ta Visual Studio / VS Code üzerinden çalışacak. Ana başlık tam olarak **Vektör Uzayları** olsun. Bütün kullanıcı metinleri Türkçe olsun.

Bu belge bir uygulama geliştirme görevidir; mevcut çalışan uygulama değildir. Kullanıcı bu dosyayı Codex'e verecektir.

Kaynak dosyalar, varsa aynı proje klasöründe:
- `VEKTÖR UZAYLARI(1).pdf`: temel matematik kaynağı.
- `lineer_cebir_egitmeni.py`: mevcut konsol uygulaması, algoritmik yaklaşım referansı.

Kaynakların aslını değiştirme. Yeni uygulamayı `vektor_uzaylari_web/` klasöründe oluştur. PDF çalışma sırasında gerekli bir bağımlılık olmasın: doğrulanmış Türkçe içeriği veri dosyalarına aktar. Kaynaklar yoksa bu belgedeki açık kurallar ve soru verileriyle devam et; kaynak dosyaları okumuş gibi davranma.

## 1. Amaç ve kapsam

Ders anlatırken projeksiyonda kullanılabilen, öğrencinin de deney yapabildiği sade bir uygulama:
1. 4.1 Vektör Uzayları: PDF'deki V1–V8 aksiyomları.
2. 4.1.1 Alt Uzaylar: boş olmama / sıfır vektörü ve kapalılık testleri.
3. 4.1.2 Doğrusal Germe: doğrusal birleşim, span, üyelik ve homojen denklemle tanımlama.
4. Sorular: aşağıda verilen 10 soru/örnek ve tek tek satır işlemleri.

Bağımlılık, bağımsızlık, baz ve boyut ana dersin odağı olmasın. Mevcut kodun bu işlevleri korunacaksa “İleri bilgiler” adlı kapalı bölümde göster. İlk açılışta yalnızca ana başlık, kısa tanım ve 8 kural kartı görünsün. Sayfayı uzun teori, istatistik panelleri, rozetler veya birden çok grafikle doldurma.

## 2. Teknoloji: üçüncü taraf bağımlılık olmadan

- Python 3.11+ standart kütüphane.
- Yerel web sunucusu: `http.server.ThreadingHTTPServer` ve özel handler.
- Hesap: kendi yazdığın liste, döngü ve satır işlemleri. Kesin aritmetik için standart `fractions.Fraction` kullanılabilir. Bu hazır bir matris çözücüsü değildir.
- Yardımcı standart modüller: `json`, `pathlib`, `argparse`, `urllib.parse`, `math`, `unittest`.
- Arayüz: normal HTML, CSS, vanilla JavaScript, SVG veya Canvas.
- NumPy, SymPy, SciPy, pandas, Matplotlib, Plotly, Streamlit, Dash, React, Vue, Bootstrap, Tailwind, CDN, harici font ve matematik render servisi kullanma.
- Matematiksel kararları Python üretsin. JavaScript kontroller, animasyon ve görüntüleme yapsın.
- Formüller MathML veya güvenli DOM elemanlarıyla gösterilebilir; kesirleri pay/payda düzeninde, matrisleri HTML tablo/grid ile çiz. Ham LaTeX komutları kullanıcı ekranında kalmasın.
- İnternetsiz çalışsın. Sunucu yalnızca `127.0.0.1` üzerinde dinlesin. Bu ders amaçlı yerel sunucu; üretim hosting sistemi tasarlama.
- `python app.py` sonrası kullanıcı tarayıcıda `http://127.0.0.1:8000` adresini açabilsin. Terminal ders arayüzü değil, sadece sunucu günlüğü olsun.

## 3. Referans Python kodunu nasıl dönüştüreceksin?

Gönderilen kodda `vektor_sutun_matris_yap`, `eselon_forma_getir`, `rref_getir`, adım listeleri, vektör/polinom girişi ve baz analizi var. Sütunlara vektör yerleştirme ve her işlemi kaydetme fikrini koru.

Şu noktaları düzelt:
- `input`, `print`, `os.system('cls')` ve Enter ile duraklama, hesap motorunda bulunmasın.
- Her hesap fonksiyonu yapılandırılmış veri döndürsün; web ekranı bunu çizsin.
- Float'tan paydası en çok 100 olan yaklaşık kesir arama yaklaşımını kullanma. Girdiyi ilk andan itibaren string üzerinden `Fraction` yap.
- “Sıfır sütunu yok, o yüzden bağımsız” açıklaması doğru bir ölçüt değildir. İleri bölüm varsa “her katsayı sütununda pivot var” de.
- “Bağımlı çünkü fazla vektör var / germiyor çünkü eksik vektör var” genellemesini kullanma. Doğru ölçüt ranktır; aynı sayıda vektör bağımlı olabilir.
- Baz çıkarırken indirgenmiş matrisin sütunlarını değil, pivot indekslerine karşılık gelen ORİJİNAL sütunları seç.
- Sıfır uzayının bazı boş kümedir; “baz bulunamadı” hatası verme.
- Genişletilmiş matriste sağ tarafı katsayı sütunu gibi pivot sayımına katma. `coefficient_columns` açık parametre olsun.

## 4. Arayüz ve öğretim akışı

Üst gezinme: **Kurallar | Alt Uzaylar | Doğrusal Germe | Sorular**.

### 4.1 Ana ekran: Kurallar

- Başlık: Vektör Uzayları.
- Tek kısa açıklama: “Toplama ve skalerle çarpmanın kurallarını keşfet.”
- Masaüstünde 4×2, tablette 2 sütun, telefonda 1 sütun kural kartı.
- Kartta sadece V numarası, kısa başlık, formül ve “Keşfet” düğmesi.
- Kart açılınca tek bir detay alanı aç. Diğer detaylar kapansın; aynı anda 8 grafik gösterme.
- Detayda 1 cümle açıklama, “Örnek 1 / Örnek 2”, düzenlenebilir küçük vektör alanları, “Oynat / Sıfırla”.
- Ekrana giriş ve vektör hareketleri 200–600 ms aralığında yumuşak olsun. Kullanıcı istemeden sürekli hareket etmesin.
- Grafikte eksen, orijin, vektör adları ve gerektiği kadar sayı. Sonuç okunu farklı renkle göster. Renk dışında etiket de kullan.
- Matematik sonucu sunucudan gelsin; animasyon adımları bu sonuçların sunumudur.

### 4.2 Alt Uzaylar

Tek deney alanı, üstünde örnek seçici:
1. `y = 2x`: alt uzay.
2. `y = 2x + 1`: sıfır vektörü yok; alt uzay değil (ek öğretici örnek).
3. `x > 0 ve y > 0`: toplama kapalı, skaler çarpma kapalı değil; PDF Örnek 4.1.1(a).
4. `xy >= 0`: skaler çarpma kapalı, toplama kapalı değil; PDF Örnek 4.1.1(b).

Üç küçük kontrol: “Sıfır vektörü”, “Toplamaya kapalılık”, “Skalerle çarpmaya kapalılık”. Bir kontrol seçilince sadece ilgili hesap ve gerekçe açılsın.

Örnek 4 için karşı örnek: u=(1,2), v=(-3,-1), u+v=(-2,1), bileşen çarpımı -2 < 0. Skaler çarpma ispatı: (λx)(λy)=λ²xy>=0.
Örnek 3 için λ=-1, u=(5,2), sonuç (-5,-2) küme dışında. Sıfır skaler de strict pozitiflik kümesinden çıkarır.

Pozitif sonuçlar genel cebirsel gerekçeye dayansın; birkaç sayısal deneme ile “ispatlandı” deme. Sayısal örnekte “Bu örnekte doğrulandı”, genel açıklamada “Her uygun vektör için...” ayrımını koru. Serbest metinle verilen her küme için genel alt uzay karar vericisi yapmaya çalışma; desteklenen örneklerle sınırlı tut.

### 4.3 Doğrusal Germe

Bir grafik ve küçük kontrol alanı:
- Varsayılan v1=(1,0), v2=(0,1); α ve β sürgüleri.
- w=αv1+βv2; ara vektörler ve sonuç Python'dan hesaplanır.
- Örnekler: bağımsız iki yön; v1=(1,2), v2=(2,4); tek sıfır vektörü.
- Sürgüler [-3,3] adım 0.25; API'ye ondalık string gönder. Girdiler ayrıca yazılabilsin.
- Örneklenen noktalar “seçili katsayı aralığı” olarak etiketlensin. Sınırlı tarama bütün sonsuz span gibi gösterilmesin.
- Rank 2 ise bütün R²'nin gerildiğini, rank 1 ise orijinden geçen doğruyu, rank 0 ise sadece orijini doğru göster.
- Sıfır vektörü ve çakışan vektörler grafiği bozmasın. Eksen ölçekleri eşit olsun.
- 4 boyutlu vektörleri fiziksel 2B oklarla birebir temsil etmeye çalışma; R⁴ sorularında matris görünümünü kullan.
- “Hedef vektör” alanıyla sayısal span üyeliği denensin; evet ise bir temsil, hayır ise çelişki satırı gösterilsin.

### 4.4 Sorular

Varsayılan liste: 17 ve 20 “Tahtada anlatım”, 18,19,21 ek alıştırma; 15 polinom; 16 ileri parametre; örnekler 4.1.4–4.1.6.

Bir soru açılınca:
1. Türkçe tam soru.
2. “Ne isteniyor?” tek cümle.
3. Genel doğrusal birleşim.
4. Bileşen denklemleri.
5. Başlangıç matrisi.
6. Her satır işlemi ayrı adım.
7. Son satırların denklem karşılığı.
8. Gerekli sonuç ve isteğe bağlı kontrol.

Kontroller: Geri, İleri, Oynat, Duraklat, Başa dön, Sonucu göster; “Neden bu işlem?” açılır açıklaması. Sonuç başlangıçta kapalı olsun. Önceki adımlara dönüşte matrisler aynen korunsun. Kullanıcı bir adımdayken örnek/girdi değişirse mevcut işlem iptal edilip yeni dizi baştan başlasın; eski API cevabı yeni sorunun üstüne yazılmasın.

Her işlemde:
- önceki ve sonraki matris,
- kullanılan satırlar,
- işlem formülü,
- hedef hücrenin hesabı,
- sağ tarafın hesabı,
- kısa gerekçe bulunsun.

`R3 <- 4R3 + 7R2` öğretim modunda iki ayrı adıma bölünsün: önce `R3 <- 4R3`, sonra `R3 <- R3 + 7R2`. Kaynak satır ikinci işlem sırasında güncel durumdan alınsın. Pivotun 1 olması REF için zorunluymuş gibi anlatma; REF ve RREF ayrımını koru.

Tahta modu: büyük yazılar, mevcut adım, matris ve tek gerekçe. Gezinti dışında paneller gizlensin. Tam ekran düğmesi ve sol/sağ ok kısayolu olsun; input içinde yazarken kısayol tetiklenmesin. Mobilde matris yatay kaydırılabilsin, sayfanın tamamı taşmasın.

## 5. PDF'den alınan kurallar: sıra değişmeyecek

Kaynak: basılı sayfa 107–108, Tanım 4.1.1. PDF'nin ilk fiziksel sayfası basılı 107'dir. V boş olmayan küme, F cisimdir. Toplama V×V→V, skaler çarpma F×V→V olarak tanımlıdır; kapalılık bu işlem tanımlarının parçasıdır. Ayrı iki ek aksiyom kartı ekleme; kısa önkoşul notu göster.

| ID | Türkçe başlık | Formül |
|---|---|---|
| V1 | Toplamada birleşme | u+(v+w)=(u+v)+w |
| V2 | Sıfır vektörü | v+0=0+v=v |
| V3 | Toplamsal ters | v+(-v)=(-v)+v=0 |
| V4 | Toplamada değişme | u+v=v+u |
| V5 | Vektör toplamına dağılma | c(u+v)=cu+cv |
| V6 | Skaler toplamına dağılma | (a+b)v=av+bv |
| V7 | Skaler çarpımının uyumu | (ab)v=a(bv) |
| V8 | Birim skaler | 1v=v |

V2: bütün vektörler için çalışan tek bir sıfır vektörü vardır. V3: her vektörün bir toplamsal tersi vardır. Diğer eşitlikler tüm uygun vektör/skalerler için geçerlidir.

Aksiyom deneyleri için iki preset:
- Örnek 1: u=(1,2), v=(3,-1), w=(-2,1), a=2, b=-1, c=2.
- Örnek 2: u=(-2,1), v=(1,3), w=(2,-2), a=-1, b=3, c=-2.

Formüllerin iki tarafını motor ayrı ayrı hesaplasın; sonuçları sabit yazı olarak koyma. V1'de gruplama, V4'te toplama sırası, V3'te zıt ok, V5–V6'da iki farklı hesap yolu animasyonla gösterilsin. Standart işlemlerde eşitlik geçerlidir; sonlu örnekler aksiyomun genel ispatı değildir.

Kapalı ek bilgiler:
- Teorem 4.1.1, s.108–109: c0=0v=0; (-1)v=-v; (-c)v=c(-v)=-(cv).
- Vektör türleri, s.109–112: matrisler, Fⁿ, F'nin kendisi, fonksiyonlar, polinomlar. P_n: derecesi EN FAZLA n olan polinomlar ve sıfır polinomu.
- Tanımlar 4.1.2–4.1.3, s.112–115: boş olmama, toplama ve skaler çarpmaya kapalılık. Pratikte sıfır vektörünü kontrol etmekle başla; sıfır içermek tek başına yeterli değil.
- Tanım 4.1.4, s.115–116: doğrusal birleşim; tüm SONLU doğrusal birleşimlerin kümesi Span(S); Span(∅)={0}; Span(S)=V ise S, V'yi gerer.
- Teorem 4.1.3, s.117: Span(S) bir alt uzaydır. Genel kapalılık ispatını açılır bölümde göster.
- Kaynak sayfa/başlık etiketleri kısa olsun; tüm PDF metnini ana sayfaya dökme. OCR hatalarını (Ö, !, bozuk eksi ve eşitsizlikler) formüllere taşıma.

## 6. Matematik motoru tasarımı

### 6.1 Kesin sayısal hesap

İzin verilen sayı girdileri: tam sayı, `-2/3` gibi kesir, `0.25` gibi sonlu ondalık string. Bunları `Fraction(string)` ile dönüştür. Sıfır payda, boş hücre, NaN, Infinity, anlamsız metin ve farklı vektör uzunluklarında anlaşılır Türkçe hata dön. Sayıları JS floating point üzerinden dolaştırma; JSON'da string olarak taşı.

Vektör/matris/polinom toplama, skaler çarpma, transpose, matris çarpma, sütun matrisi kurma kendi döngülerinle yazılsın. Polinom katsayı sırası `[a0,a1,a2,...]`. 2×2 matris düzleştirme sırası `[a,b,c,d]` (satır öncelikli) olsun ve ekranda gösterilsin.

### 6.2 REF, RREF, çözüm

`ref(A, rhs=None, pivot_policy='simple')` katsayı kısmında pivot arar, satır işlemlerini A ve sağ tarafa birlikte uygular. Önce ±1 tercih edilebilir. `rref` ayrı fonksiyon olsun.

- Tutarsızlık: A tarafı sıfır, sayısal RHS sıfır değil.
- Tutarlı ve pivot sayısı n ise tek çözüm.
- Tutarlı ve pivot sayısı n'den küçükse serbest değişkenler; genel çözüm `p + Σ ti*di`.
- “Bir temsil” istenirse serbest katsayıları 0 seçmek serbesttir; bunun bulunan zorunlu değer değil bir seçim olduğunu belirt.
- `span_membership` Ax=b çözer; `spans_ambient` rank(A)=satır sayısı kontrol eder. Bunlar ayrı sonuç alanlarıdır.
- Sıfır sütunu bulunmaması bağımsızlık kanıtı değildir.
- Bütün matrisler/adımlar deep-copy olmalı, daha sonraki işlemler geçmişi değiştirmemeli.

### 6.3 Sembolik sağ taraf: hazır CAS kullanmadan

19,20,21 ve matris örneklerinde A sabit, sağ taraf semboliktir. Genel CAS yazmak yerine doğrusal ifade sınıfı oluştur:
`LinearExpr = sabit Fraction + {sembol: Fraction}`.
Destek: toplama, çıkarma, rasyonel sayıyla çarpma, sadeleştirme, biçimleme ve sayısal yerine koyma. İki sembolik ifadeyi çarpma gerekmiyor.

Daha basit eşdeğer yöntem: A'yı indirgerken E=I üzerinde aynı satır işlemlerini uygula. A'nın sıfır satırlarına karşılık gelen E satırları, genel hedef y için `h·y=0` koşullarını verir. Bunları H matrisinde topla. `Col(A)=ker(H)`; HA=0 ve rank(H)=m-rank(A) kontrol edilsin. Hiç koşul yoksa tüm R^m, sıfır A için H=I. Aynı çözüm kümesini veren eşdeğer denklem sistemleri kabul edilsin, string eşitliğiyle test yapılmasın.

Sembolik RHS varken sıfır katsayı satırındaki ifadeyi otomatik “çelişki” sayma; bu bir üyelik KOŞULUDUR. “0=c-a-b” içindeki c ile doğrusal birleşim katsayısını karıştırmamak için katsayıları λ1,λ2,... olarak adlandır.

### 6.4 Parametreli 16. soru

Katsayı matrisinde a parametresi vardır. Genel sembolik pivotlama varmış gibi davranma; bu soru için açık, doğrulanmış cebir adımları ve a=1, a=-1, diğer değerler dalları oluştur. “Rehberli parametre çözümü” olarak göster. a'ya bağlı bir ifadeye bölmeden önce sıfır olduğu dalı ayır. Sayısal a,b girişinde genel Fraction motoruyla sonucu tekrar hesapla. b=2.25 tam olarak 9/4 kabul edilsin.

## 7. Soru bankası: tam veriler ve doğrulama sonuçları

Aşağıdakiler sonuçları sabit göstermenin gerekçesi değil, bağımsız test beklentileridir. Sayısal sorular ve sembolik RHS sorularının adımları motor tarafından üretilsin. Rehberli 16. sorunun özel durumu yukarıda tanımlıdır.

### Soru 17 — Doğrusal birleşim [ana]
Soru: (4,-2,4), (1,0,1), (3,-4,1), (4,-6,-2) vektörlerinin doğrusal birleşimi olarak yazılabilir mi?
Vektör listesi: `[[1,0,1],[3,-4,1],[4,-6,-2]]`; hedef `[4,-2,4]`.
Beklenti: evet, katsayılar `[7/3,1,-1/3]`, tek çözüm.
İşlem yolu: başlangıç satırları [1,3,4|4], [0,-4,-6|-2], [1,1,-2|4]. R3←R3−R1, R3←R3−(1/2)R2; son satır [0,0,-3|1]. Geriye yerine koymayı da ayrı adımlarla göster.

### Soru 18 — Span üyeliği [ek]
Soru: (6,11,4,1), Span{(3,-1,1,1),(4,3,2,1),(1,4,1,0)} içinde midir?
Vektör listesi `[[3,-1,1,1],[4,3,2,1],[1,4,1,0]]`; hedef `[6,11,4,1]`.
Beklenti: rank=2; evet, sonsuz temsil. Katsayılar `(t-2,3-t,t)`; t=0 ile `(-2,3,0)`. “Neden 0 seçtik?” paneli: serbest katsayı 0 olmak zorunda değildir, tek temsil göstermek için seçilmiştir.

### Soru 19 — Üyelik koşulu [ek]
Soru: (a,b,c), (1,-1,0),(0,1,1),(3,-2,1) vektörlerinin gerdiği alt uzaydaysa a,b,c hangi bağıntıyı sağlar?
Vektörler `[[1,-1,0],[0,1,1],[3,-2,1]]`; sembolik hedef `[a,b,c]`.
Beklenti: `a+b-c=0`. Eşelon sonunda `0=c-a-b` satırını açıkça yorumla. Bileşen c'yi sıfır seçme; ifadenin tamamı sıfır olmalıdır.

### Soru 20 — Homojen sistem [ana]
Soru: Span{(1,-1,0),(0,1,1),(3,-5,-2)} uzayını homojen doğrusal bir sistemin çözüm kümesi olarak ifade ediniz.
Vektörler `[[1,-1,0],[0,1,1],[3,-5,-2]]`; sembolik hedef `[x,y,z]`.
Beklenti: `x+y-z=0`, rank=2, H=[1,1,-1]. Soru 19 ile üçüncü vektör farklıdır; verileri karıştırma.
İşlemler: R2←R2+R1; R3←R3−R2. Son satır [0,0,0|z−x−y].
Sonuçtan sonra göster: [1 1 -1][x y z]^T=0 aynı denklemin matris yazımıdır; yeni bir işlem değildir.

### Soru 21 — R⁴'te homojen sistem [ek]
Soru: (1,-1,2,4), (3,1,-1,1), (-2,-2,3,3) vektörlerinin gerdiği uzayı homojen bir sistemin çözüm kümesi olarak ifade ediniz.
Vektörler `[[1,-1,2,4],[3,1,-1,1],[-2,-2,3,3]]`; hedef `[x,y,z,t]`.
Beklenti:
- `-x+7y+4z=0`
- `-5x+11y+4t=0`
Rank=2. Eşdeğer iki bağımsız koşul da kabul edilir.
Tahta için özel işlem dizisi (her satır ayrı olay):
1. R2←R2+R1.
2. R3←R3−2R1.
3. R4←R4−4R1.
4. R3←4R3.
5. R3←R3+7R2.
6. R4←4R4.
7. R4←R4+11R2.
Son iki RHS sırasıyla −x+7y+4z ve −5x+11y+4t olmalı. Her olay ortak satır işlem motorunda yürütülsün; matris ekranları elle yazılmış fotoğraflar olmasın.

### Soru 15 — Polinomlar [farklı vektör türü]
Soru: 1+x+cx²+dx³ polinomu aşağıdaki polinomların doğrusal birleşimi ise c ve d'yi bulunuz:
- −1+2x+3x²+4x³
- 4+x+6x²+11x³
- 1−x−x²−x³
- 3+x+5x²+9x³
Katsayı vektörleri `[[-1,2,3,4],[4,1,6,11],[1,-1,-1,-1],[3,1,5,9]]`; hedef `[1,1,c,d]`.
Beklenti: c=3, d=5. Bir temsil 2*p1+3*p3. Çözüm koşullarını sadeleştirip önce c sonra d bulunmalı; hazır “3,5” yazıp adımları atlama. Grafik zorunlu değil, katsayı tablosu esas.

### Soru 16 — Alt uzayda bulunmama [ileri]
Soru: (-b,4,0,2b−2) aşağıdaki vektörlerin gerdiği alt uzayda BULUNMUYORSA a ve b hangi koşulları sağlamalıdır?
- (-1,1,-1,1)
- (1,a,1,-1)
- (-2a,-a,-2a+1,1+2a)
- (-1,3,a-1,2)
Katsayıları λ1,λ2,λ3,λ4 olarak adlandır.
Denklemler:
- −λ1+λ2−2aλ3−λ4=−b
- λ1+aλ2−aλ3+3λ4=4
- −λ1+λ2+(1−2a)λ3+(a−1)λ4=0
- λ1−λ2+(1+2a)λ3+2λ4=2b−2
İlk satırı kullanarak aşağıdakileri türet:
- (a+1)λ2−3aλ3+2λ4=4−b
- λ3+aλ4=b
- λ3+λ4=b−2
Son iki denklemin farkı: (1−a)λ4=−2.
Dallar:
- a=1: 0=−2, her b için dışarıda.
- a≠±1: λ4,λ3,λ2,λ1 sırasıyla bulunur, her b için içeride.
- a=−1: λ4=−1, λ3=b−1; ilk kalan denklem 3(b−1)−2=4−b, dolayısıyla içeride olma koşulu b=9/4.
İstenen DIŞARIDA koşulu: `a=1 (her b)` VEYA `a=-1 ve b!=9/4`.
Test noktaları: (1,0) dışarıda; (-1,9/4) içeride; (-1,0) dışarıda; (0,0) içeride.

### Örnek 4.1.4 — R⁴'ün tamamını germez
Soru: S={(3,-4,1,0),(0,6,1,-3)} için (a,b,c,d)'nin Span(S)'de bulunma koşullarını bulunuz ve S'nin R⁴'ü gerip germediğini belirleyiniz.
Vektörler `[[3,-4,1,0],[0,6,1,-3]]`.
Beklenti: `a−3c−d=0` ve `3b+12c+10d=0`. Rank=2; R⁴'ü germez. (1,0,0,0) koşulları sağlamaz.

### Örnek 4.1.5 — Bütün R³'ü germek
Soru: {(1,2,-1),(-3,1,0),(2,-3,2)} kümesinin R³'ü gerdiğini gösteriniz.
Vektörler `[[1,2,-1],[-3,1,0],[2,-3,2]]`, genel hedef `[a,b,c]`.
Beklenti: rank=3; her hedef için çözüm, hiçbir üyelik kısıtı yok.
Kaynak düzeltmesi: PDF s.117'de son satır sağ tarafı hatalı basılmıştır. Katsayı satırı [0,0,7] olduğunda doğru RHS `a+3b+7c` olur. Bunu test et; hatalı `a−3b−7c` ifadesini kopyalama. Kaynak notunda kısa düzeltme kaydı tut.

### Örnek 4.1.6 — Matrisler de vektördür
Soru: A1=[[1,-3],[2,1]], A2=[[7,3],[2,-1]], A3=[[3,15],[-6,-5]] matrislerinin gerdiği uzayı homojen sistemle tanımlayınız.
Genel hedef [[a,b],[c,d]]. Satır öncelikli düzleştirme:
`[1,-3,2,1]`, `[7,3,2,-1]`, `[3,15,-6,-5]`; hedef `[a,b,c,d]`.
Beklenti: `−a+2c−3d=0` ve `b+3d=0`, rank=2. Önce 2×2 matrisleri, sonra dört bileşenli sütuna geçişi göster.

## 8. Önerilen proje dosyaları

```text
vektor_uzaylari_web/
  app.py
  core/
    __init__.py
    arithmetic.py
    elimination.py
    expressions.py
    analysis.py
    guided_parameters.py
  data/
    axioms.json
    lessons.json
    questions.json
  static/
    index.html
    styles.css
    app.js
    diagrams.js
  tests/
    test_math.py
    test_api.py
  README.md
  SOURCE_NOTES.md
  .vscode/launch.json
```

Bu ayrım gereksiz çatılar kurmak için değil, matematiği UI'dan ayırmak içindir. Sorular veriyle tanımlansın, sayısal çözüm fonksiyonlarını her soru için kopyalama.

## 9. API ve adım sözleşmesi

Örnek uçlar:
- GET /api/content → aksiyomlar, konu başlıkları, soru listesi.
- POST /api/axiom → rule_id, vektörler, skalerler; iki tarafın hesapları.
- POST /api/combination → vektörler, katsayılar; ara ve sonuç vektörleri.
- POST /api/solve → question_id veya desteklenen kullanıcı vektörleri/hedefi; adımlar ve sonuç.
- POST /api/subspace → desteklenen örnek kimliği ve deney girdileri.

Örnek adım nesnesi:
```json
{
  "index": 2,
  "type": "row_add",
  "target_row": 2,
  "source_row": 0,
  "factor": "-2",
  "operation_text": "R3 ← R3 − 2R1",
  "reason": "Birinci sütundaki 2 değerini sıfırlıyoruz.",
  "before": [],
  "after": [],
  "rhs_before": [],
  "rhs_after": [],
  "cell_calculations": [],
  "pivot": {"row": 0, "column": 0}
}
```

İndeksler API'de sıfır tabanlı, ekranda bir tabanlı. Rasyoneller JSON string; sembolik ifadeler sabit ve katsayı sözlüğü ile taşınsın. Hücre hesaplarının değerleri motorun yaptığı işlemlerden türetilsin.

Sonuçlar en az şu ayrımı taşısın: `unique`, `infinite`, `inconsistent`, `symbolic_conditions`, `parameter_cases`. Hedefi olmayan span analizi `ambient_span` ve `homogeneous_conditions` alanlarını döndürsün.

İstek boyutu ve matris boyutu sınırlı olsun (örneğin en çok 8×8, girdi başına 80 karakter, istek 64 KB). Yanlış JSON/eksik alan 400 ve Türkçe hata mesajı üretsin. Kullanıcı metinlerini `eval`/`exec` ile çalıştırma; `innerHTML` içine ham girdi basma. Sunucu static klasörü dışına yol geçişine izin vermesin. 404/405 durumları düzgün dönsün.

## 10. Doğrulama ve kabul ölçütleri

Matematik testleri standart `unittest` ile:
1. Soru 17: bulunan katsayılarla Aλ=hedef tam eşitliği.
2. Soru 18: genel çözüm için t=0,1,2 değerlerinde eşitlik; rank=2.
3. Soru 19–21 ve örnekler 4.1.4/4.1.6: HA=0 ve rank(H)=m−rank(A).
4. Soru 15: c=3,d=5 ve 2*p1+3*p3 kontrolü.
5. Soru 16: dört test noktası ve cebir dallarında sıfıra bölme olmaması.
6. Örnek 4.1.5: rank=3 ve işaret düzeltmesi.
7. Tutarsız sistem: A=[[1,1],[2,2]], b=[1,3].
8. Sıfır matris: sıfır hedef tutarlı; sıfır olmayan hedef tutarsız.
9. Satır değişimi gereken matris; dikdörtgen matris; kesirli girdiler; tek vektör; yinelenen vektör.
10. Her kaydedilen işlemde yeniden uygulama tam olarak `after` sonucunu üretmeli; sağ taraf da aynı işleme tabi olmalı.
11. V1–V8'de iki preset için iki taraf eşit; 8 kart numarası PDF sırasıyla aynı.
12. Kötü girdi ve API hataları sunucuyu kapatmamalı.

Arayüz kontrolleri:
- Ana sayfada 8 kart, büyük Vektör Uzayları başlığı ve sade gezinme.
- Her Keşfet butonu gerçekten farklı ilgili örneği açıyor.
- Dört sekme, soru seçimi, ileri/geri, oynatma/duraklatma, tahta modu ve hedef değişikliği çalışıyor.
- Çözüm adımı bir ileri bir geri yapıldığında aynı matris dönüyor.
- Sembolik formüllerde bozuk `+ -`, ham LaTeX, kaçış karakterleri yok.
- 1366×768 ve mobil genişlikte ana elemanlar taşmıyor; büyük matris sadece kendi alanında kayıyor.
- `prefers-reduced-motion` destekli; klavye erişimi, görünür odak, düğme etiketleri var.
- Ağ isteği sürerken durum gösteriliyor; hata olursa kullanıcı tekrar deneyebiliyor.

Sadece ekran görüntüsü veya statik cevap kartları üretmek kabul edilmez. Kaynak değerleri değiştirince yeni sonuç motor tarafından hesaplanmalıdır. Parametreli özel rehberin kapsamı açıkça belirtilmelidir.

## 11. Çalıştırma ve teslim

README'de Windows için:
```powershell
cd vektor_uzaylari_web
py -3 app.py
```
Python komutu `python` ise alternatifini de yaz. Adres `http://127.0.0.1:8000`. Port doluysa anlaşılır hata ve `--port 8001` seçeneği. Kapatma Ctrl+C. `pip install` veya Node build adımı gerekmemeli.

Test:
```powershell
py -3 -m unittest discover -s tests -v
```

`.vscode/launch.json` doğrudan app.py'yi çalıştırmalı. README'de kaynak PDF'nin hangi basılı sayfalarından içerik alındığını, sayı aritmetiği ve sembolik kapsam sınırlarını belirt. Görsel örneklerin genel ispat olmadığı açıklansın.

Teslim mesajında oluşturulan dosyaları, çalıştırma komutunu, geçen testleri ve varsa somut eksikleri yaz. Test etmediğin arayüz davranışını test edilmiş gibi raporlama. TODO düğmesi, boş panel, çalışmayan örnek veya sahte başarı bildirimi bırakma.
