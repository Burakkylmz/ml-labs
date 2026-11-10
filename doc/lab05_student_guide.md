# LAB05 Student Guide — Supervised Learning: Regression

Bu rehber, `ml-labs` projesindeki **LAB05: Supervised Learning — Regression** çalışmasını kendi
bilgisayarınızda Docker üzerinden nasıl çalıştıracağınızı adım adım açıklar.

**Eğitim süresi:** 150 dakika (10 dakikalık mola dahil)

> Bu LAB, **LAB02**, **LAB03** ve **LAB04**'ün devamıdır. Bu LAB'ları tamamlamadıysanız önce
> [`doc/lab02_student_guide.md`](lab02_student_guide.md), [`doc/lab03_student_guide.md`](lab03_student_guide.md)
> ve [`doc/lab04_student_guide.md`](lab04_student_guide.md) rehberlerini takip edin.

---

## 1. LAB Overview

Bu LAB'da, Northwind sipariş verisini kullanarak bir siparişin **taşıma ücretini (`Freight`)**
tahmin eden regression modelleri geliştireceksiniz. LAB sonunda şu konuları uygulamış olacaksınız:

- **Regression Fundamentals** (regression vs classification, numerical target)
- **Baseline Regression** (`DummyRegressor` — mean/median strateji)
- **Linear & Multiple Linear Regression** (katsayı yorumlama)
- **Ridge & Lasso Regularization** (L1/L2, `alpha` hiperparametresi, coefficient shrinkage)
- **Decision Tree Regression** (`max_depth`, underfitting/overfitting)
- **Regression Evaluation Metrics** (MAE, MSE, RMSE, R²)
- **Residual Analysis** (actual vs predicted, residual plots, error segmentation)
- **Model Comparison & Selection** (validation ile seçim, test ile tek seferlik doğrulama)

Bu LAB'da **tek bir veri kümesi** kullanılır:

| Dataset | Kullanım Alanı |
|---|---|
| **Northwind Orders** (`data/northwind/orders.csv`) | Feature engineering, baseline, Linear/Ridge/Lasso/Decision Tree Regression, model karşılaştırması |

> **Bu LAB'da gerçek regression modelleri eğitilir ve karşılaştırılır.** LAB04'te sadece
> preprocessing yapılmıştı; bu LAB'da preprocessing pipeline'ın üzerine bir estimator eklenir.

> **Önemli varsayım:** `Freight`'ın gerçek bir kurumsal sistemde ne zaman hesaplandığı bu veri
> kümesinden kesin olarak çıkarılamaz. Notebook, "model taşıma yöntemi/sevkiyat bilgileri
> belirlendikten sonra, `Freight` henüz bilinmiyorken tahmin yapar" varsayımını kullanır ve bu
> LAB'ın sonuçlarını gerçek taşıma fiyatlandırması için doğrulanmış sonuçlar olarak sunmaz.

---

## 2. Prerequisites

LAB'ı çalıştırmadan önce bilgisayarınızda şunların kurulu olması gerekir:

- **Docker Desktop** veya kurumunuz tarafından onaylanan eşdeğer bir Docker ortamı
- **Docker Compose V2** (güncel Docker Desktop sürümleriyle birlikte gelir)
- **Git**
- Bir **web browser** (Chrome, Edge, Firefox vb.)
- **Visual Studio Code** (önerilir, zorunlu değildir)

### Python, NumPy, Pandas, Scikit-learn kurmanıza gerek yok

Bu projede tüm Python bağımlılıkları `uv` ile yönetilir, ancak `uv` **yalnızca Docker image'ı build
edilirken** çalışır — `Dockerfile` içindeki `uv sync --locked` komutu, bağımlılıkları container
içindeki `/opt/venv` sanal ortamına kurar ve JupyterLab bu ortam üzerinden çalışır.

Bu nedenle, LAB'ı Docker ile çalıştırmak için **kendi bilgisayarınıza Python, uv, NumPy, Pandas veya
Scikit-learn kurmanıza gerek yoktur** — yalnızca Docker Desktop yeterlidir. LAB05, LAB02/LAB03/LAB04
ile **aynı Docker image'ını** kullanır; `scikit-learn` LAB04'ten beri zaten kurulu bir bağımlılıktır
— yeni bir bağımlılık eklenmemiştir.

---

## 3. Dataset Download Instructions

> **Not:** Veri dosyası bu proje tarafından otomatik olarak indirilmez.

### Northwind Orders

LAB05, `data/northwind/orders.csv` dosyasını kullanır. Bu dosya, **LAB02** için indirdiğiniz
Northwind Traders veri kümesinin bir parçasıdır (`customers.csv`, `orders.csv`, `shippers.csv`
üçlüsünden biri).

- **Eğer LAB02'yi zaten tamamladıysanız:** `data/northwind/orders.csv` dosyası zaten doğru
  konumda olmalıdır — yeniden indirmenize gerek yoktur. Doğrudan [Bölüm 5](#5-cloning-the-repository-from-github)'e
  geçebilirsiniz.
- **Eğer bu dosya henüz yoksa**, [`doc/lab02_student_guide.md`](lab02_student_guide.md) rehberinin
  **Bölüm 3 — Dataset 2 — Northwind Traders Dataset** adımlarını izleyerek üç dosyayı
  (`customers.csv`, `orders.csv`, `shippers.csv`) indirip `data/northwind/` klasörüne yerleştirin.
  LAB05 yalnızca `orders.csv`'yi kullanır, ancak diğer iki dosyanın da klasörde bulunması
  (LAB02'de zaten edinilmiş olmaları nedeniyle) sorun oluşturmaz.

> **Orijinal CSV içeriğini değiştirmeyin.** LAB05, bu dosyayı yalnızca okur; üzerinde herhangi bir
> değişiklik yapmaz.

> E-Commerce Shipping veri kümesi (`data/ecommerce_shipping/`) bu LAB için **gerekli değildir**.
> LAB03/LAB04'ten kalan dosyalar varsa, dokunmanıza gerek yoktur — silmeniz de gerekmez.

---

## 4. Expected Directory Structure

Dataset doğru konumda olduğunda proje yapınız şu şekilde görünmelidir:

```text
ml-labs/
├── data/
│   └── northwind/
│       ├── customers.csv
│       ├── orders.csv
│       └── shippers.csv
├── labs/
│   ├── lab02/
│   │   └── ...
│   ├── lab03/
│   │   └── ...
│   ├── lab04/
│   │   └── ...
│   └── lab05/
│       ├── lab05_supervised_regression.ipynb
│       └── README.md
├── doc/
│   ├── lab02_student_guide.md
│   ├── lab03_student_guide.md
│   ├── lab04_student_guide.md
│   └── lab05_student_guide.md
├── src/
│   └── data_loading.py
├── config/
│   └── settings.yaml
├── pyproject.toml
├── uv.lock
├── Dockerfile
└── compose.yaml
```

---

## 5. Cloning the Repository from GitHub

> **LAB02, LAB03 veya LAB04'ü zaten tamamladıysanız** ve `ml-labs/` klasörünüz bilgisayarınızda
> halihazırda varsa, bu adımı atlayabilirsiniz — doğrudan bu klasörün içinde `git pull` çalıştırarak
> LAB05 dosyalarının (ve varsa diğer güncellemelerin) güncel sürümünü alabilirsiniz, ardından
> Bölüm 6'ya geçin.

Projeyi ilk kez kendi bilgisayarınıza alıyorsanız, GitHub üzerinden clone edin.

1. Bir terminal açın.
2. Projeyi klonlamak istediğiniz klasöre gidin (örn. `cd Documents`).
3. Aşağıdaki komutu çalıştırın:

   ```bash
   git clone https://github.com/Burakkylmz/ml-labs.git
   ```

4. Oluşan `ml-labs` klasörüne girin:

   ```bash
   cd ml-labs
   ```

5. Bölüm 3'te kontrol ettiğiniz/indirdiğiniz dataset dosyasını, Bölüm 4'te gösterilen klasör
   yapısına göre bu klasörün içine yerleştirin (`data/northwind/orders.csv`).
6. Bu rehberin kalan adımlarını (Docker ile çalıştırma dahil) her zaman bu `ml-labs/` klasörünün
   içinden çalıştıracaksınız.

---

## 6. Running the LAB with Docker

1. Bir terminal açın ve proje kök dizinine (`ml-labs/`) geçin.
2. **Docker Desktop'ın çalışır durumda olduğundan emin olun** (sistem tepsisindeki Docker ikonu
   "running" göstermelidir). Docker Desktop çalışmıyorsa aşağıdaki komutlar bağlantı hatası verir.
3. Aşağıdaki komutu çalıştırın:

   ```bash
   docker compose up --build -d
   ```

   Bu komut şunları yapar:

   - Henüz oluşturulmamışsa, `Dockerfile`'a göre Docker image'ını **build** eder (bağımlılıkları
     `uv` ile kurar).
   - `ml-lab` adlı container'ı **başlatır**.
   - Container içinde **JupyterLab** servisini çalıştırır.
   - `-d` (detached) seçeneği, terminali kilitlemeden container'ı arka planda çalıştırır.

   > Eğer LAB02/LAB03/LAB04'ten kalan bir image varsa, bu komut genellikle çok hızlı tamamlanır
   > (önceki build katmanları yeniden kullanılır, çünkü bağımlılıklar değişmemiştir).

4. Container'ın çalışıp çalışmadığını kontrol etmek için:

   ```bash
   docker compose ps
   ```

5. Container loglarını (ve JupyterLab erişim token'ını) görmek için:

   ```bash
   docker compose logs ml-lab
   ```

   Loglarda şuna benzer bir satır göreceksiniz:

   ```text
   http://127.0.0.1:8888/lab?token=<uzun-bir-token-degeri>
   ```

   Bu satırdaki `token=` sonrasındaki değer, JupyterLab'a giriş yapmak için kullanacağınız
   **authentication token**'dır. Bu proje token authentication'ı **açık** tutar; token'ı kapatan bir
   ayar yoktur.

---

## 7. Accessing JupyterLab

Bu projede JupyterLab, `127.0.0.1:8888` portu üzerinden **yalnızca kendi bilgisayarınızdan
(localhost)** erişilebilir şekilde yapılandırılmıştır.

1. Tarayıcınızı açın.
2. Adres çubuğuna şunu yazın:

   ```text
   http://localhost:8888
   ```

3. Karşınıza bir giriş (login) ekranı gelirse, `docker compose logs ml-lab` çıktısından aldığınız
   **token** değerini ilgili alana yapıştırın. (Loglardaki tam URL'yi — `token=...` dahil —
   doğrudan tarayıcıya yapıştırmanız da yeterlidir.)
4. JupyterLab açıldığında, soldaki dosya gezgininde (file browser) proje kök dizinini göreceksiniz.
   `labs` klasörüne, ardından `lab05` klasörüne girin.
5. `lab05_supervised_regression.ipynb` dosyasına çift tıklayarak notebook'u açın.

> Container'ın çalışma dizini (`WORKDIR`) `/app`'tir ve proje kök dizininiz bu yola bağlanır (bind
> mount). Bu nedenle JupyterLab'daki klasör yapısı, kendi bilgisayarınızdaki `ml-labs/` klasör
> yapısıyla birebir aynıdır.

---

## 8. Working with Notebook Cells

Bir Jupyter notebook (`.ipynb`), iki tür hücreden oluşur:

- **Markdown Cell**: Açıklama metni içerir (bu rehber gibi); çalıştırıldığında kod üretmez, yalnızca
  biçimlendirilmiş metni gösterir.
- **Code Cell**: Çalıştırılabilir Python kodu içerir.

### Temel kullanım

- Bir Code Cell'i çalıştırmak için hücreye tıklayın ve **`Shift + Enter`** tuşlarına basın. Bu,
  hücreyi çalıştırır ve bir sonraki hücreye geçer.
- Hücre çalıştırıldıktan sonra, çıktısı (varsa) **hücrenin hemen altında** görüntülenir.
- Bir Pandas `DataFrame`'i döndüren bir hücre çalıştırıldığında, DataFrame tablo olarak hücrenin
  altında gösterilir.
- Bir Matplotlib grafiği oluşturan bir hücre çalıştırıldığında, grafik görsel olarak hücrenin
  altında görüntülenir (bu LAB'da histogram, scatter, residual ve decision tree grafikleri dahil).
- Yaptığınız değişiklikleri kaydetmek için **`Ctrl + S`** tuşlarına basın veya üst menüden
  **File → Save Notebook**'u seçin.

### Önemli

**Docker kullanılması, Jupyter Notebook'un hücre bazlı çalışma mantığını değiştirmez.** Yazdığınız
Python kodu, container içinde çalışan Jupyter **kernel**'i tarafından çalıştırılır; sonuçlar her
zaman ilgili hücrenin altında görüntülenir — bu davranış, Docker kullanılmasa da aynıdır.

**Hücre sırası bu LAB'da özellikle önemlidir.** Section 2'de oluşturulan `X_train`/`X_val`/`X_test`
ve `preprocessor` değişkenleri, Section 3'ten Section 8'e kadar **tüm** model eğitimi ve
değerlendirme hücrelerinde yeniden kullanılır. Hücreleri sırayla çalıştırmazsanız (veya bir hücreyi
atlarsanız), sonraki hücrelerde `NameError` alabilirsiniz — bu durumda **Run → Run All Cells** ile
notebook'u baştan sona çalıştırmanız en güvenli çözümdür.

---

## 9. LAB Sections

Notebook, aşağıdaki sırayla ilerler:

1. **Regression Fundamentals & Dataset** — regression'ın tanımı, classification'dan farkı,
   `Freight` hedef değişkeninin dağılımı.
2. **Data Splitting & Baseline Models** — feature seçim gerekçesi, `OrderDate`'e göre kronolojik
   %70/%15/%15 split, `DummyRegressor` (mean/median) baseline'ları.
3. **Linear & Multiple Linear Regression** — Simple Linear Regression matematiğini gösteren,
   açıkça etiketlenmiş bir synthetic örnek; ardından gerçek Northwind verisiyle Multiple Linear
   Regression ve katsayı yorumlama.
4. **Ridge & Lasso Regularization** — L2 (Ridge) ve L1 (Lasso) regularization, farklı `alpha`
   değerlerinin katsayılar üzerindeki küçültme/sıfırlama etkisi.
5. **Decision Tree Regression** — farklı `max_depth` değerleriyle underfitting'den overfitting'e
   geçişin gözlemlenmesi, küçük bir ağacın görselleştirilmesi.
6. **Regression Evaluation Metrics** — MAE, MSE, RMSE, R² formülleri ve tüm modellerin tek bir
   karşılaştırma tablosunda özetlenmesi.
7. **Residual Analysis & Model Comparison** — actual vs predicted ve residual grafikleri, ülke
   bazlı hata segmentasyonu (küçük örneklem uyarısıyla).
8. **Final Workshop & Evaluation** — model seçimi, test verisinin **bir kez** kullanılması ve bir
   Model Evaluation Summary.

Notebook sonunda, deneyimli katılımcılar için üç **opsiyonel Advanced Challenge**
(regularization path, target transformation, `ShipVia` bazlı error segmentation) bulunur — bunlar
ana 150 dakikalık süreye dahil değildir ve tamamlanmamaları notebook'un çalışmasını etkilemez.

---

## 10. Stopping the LAB

Çalışmanız bittiğinde container'ları durdurmak için:

```bash
docker compose down
```

### Değişiklikleriniz korunuyor mu?

Proje kök dizini (`ml-labs/`), `compose.yaml` içinde bir **bind mount** ile container'ın `/app`
klasörüne bağlanır. Bu, notebook içindeki tüm klasörlerin (`labs/`, `data/`, `src/`, `config/`
dahil) doğrudan kendi bilgisayarınızdaki dosyalar olduğu anlamına gelir.

- Notebook içinde yaptığınız ve **kaydettiğiniz** (`Ctrl + S`) değişiklikler, container durdurulsa,
  silinse veya yeniden build edilse bile **kendi bilgisayarınızda kalıcı olarak saklanır**.
- `docker compose down` komutu yalnızca container'ı ve network'ü kaldırır; bind mount edilen proje
  dosyalarına **dokunmaz**.
- Kaydetmediğiniz (unsaved) değişiklikler, tarayıcı sekmesini kapatırsanız veya kernel çökerse
  kaybolabilir — bu, Docker'dan bağımsız, standart Jupyter davranışıdır.

---

## 11. Troubleshooting

| Problem | Çözüm |
|---|---|
| **Docker Desktop çalışmıyor** | Docker Desktop uygulamasını başlatın ve sistem tepsisindeki ikonun "running" durumuna geçmesini bekleyin. Ardından komutu tekrar çalıştırın. |
| **Docker Engine bağlantı hatası** (`error during connect`, `pipe not found` vb.) | Bu hata genellikle Docker Desktop'ın henüz tamamen başlamadığını gösterir. Docker Desktop'ın tamamen açıldığından emin olun ve birkaç saniye bekleyip komutu tekrar deneyin. |
| **Port 8888 kullanımda** (`port is already allocated`) | Bilgisayarınızda 8888 portunu kullanan başka bir uygulama (örn. önceki LAB'dan kapatılmamış bir container) çalışıyor olabilir. `docker compose down` ile önceki container'ı durdurun, ardından tekrar deneyin. |
| **JupyterLab açılmıyor / tarayıcıda yüklenmiyor** | `docker compose ps` ile container'ın `running` durumda olduğunu doğrulayın. `docker compose logs ml-lab` ile hata olup olmadığını kontrol edin. Gerekirse `docker compose down` ve ardından `docker compose up --build -d` ile yeniden başlatın. |
| **Dataset `FileNotFoundError`** | Notebook, `data/northwind/orders.csv` dosyasını bulamadığında bu hatayı fırlatır. Bölüm 3'teki adımlara göre dosyanın doğru konumda olduğunu kontrol edin (LAB02'yi tamamladıysanız bu dosya zaten mevcut olmalıdır). |
| **Yanlış Notebook Kernel** | Bu container içinde tek bir Python ortamı (`Python 3 (ipykernel)`) bulunur. Notebook sağ üstte farklı bir kernel adı gösteriyorsa, **Kernel → Change Kernel** menüsünden `Python 3 (ipykernel)`'i seçin. |
| **Python `ModuleNotFoundError`** (örn. `sklearn` bulunamadı) | Tüm bağımlılıklar `Dockerfile` build aşamasında kurulur; bu hata genellikle image'ın güncel bağımlılıklarla yeniden build edilmediğini gösterir. `docker compose up --build -d` komutunu `--build` bayrağıyla tekrar çalıştırın. |
| **`NameError` (örn. `X_train`, `preprocessor` veya `linear_pipe` tanımlı değil)** | Section 2/3'teki hücreler sırayla çalıştırılmadıysa bu hata oluşur. **Run → Run All Cells** ile notebook'u baştan sona çalıştırın. |
| **`ConvergenceWarning` (Lasso)** | Bu LAB'da kullanılan `alpha` değerleriyle normalde bu uyarı oluşmaz. Oluşursa, yalnızca gizlemeyin — genellikle `max_iter` değerini artırmak veya feature'ların doğru ölçeklendiğini (pipeline'daki `StandardScaler`) kontrol etmek gerekir. |
| **`ValueError` (encoder, scaler veya pipeline hatası)** | Genellikle bir hücrenin atlanmış veya yanlış sırada çalıştırılmış olmasından kaynaklanır (örn. `transform()` çağrılmadan önce `fit()` çağrılmamış). **Kernel → Restart Kernel and Run All Cells** ile temiz bir çalıştırma yapın. |
| **Notebook değişiklikleri kaydedilemiyor** | Bölüm 10'da açıklanan bind mount sayesinde kaydetme normalde sorunsuz çalışır. Kaydetme başarısız oluyorsa, tarayıcı sekmesini yenileyin (F5) ve `Ctrl + S` ile tekrar deneyin; sorun sürerse `docker compose logs ml-lab` ile container loglarını kontrol edin. |
