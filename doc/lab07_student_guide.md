# LAB07 Student Guide — Advanced Machine Learning & Ensemble Methods

Bu rehber, `ml-labs` projesindeki **LAB07: Advanced Machine Learning & Ensemble Methods**
çalışmasını kendi bilgisayarınızda Docker üzerinden nasıl çalıştıracağınızı adım adım açıklar.

**Eğitim süresi:** 150 dakika (10 dakikalık mola dahil), artı isteğe bağlı Advanced Challenges

> Bu LAB, **LAB02**, **LAB03**, **LAB04**, **LAB05** ve **LAB06**'nın devamıdır. Bu LAB'ları
> tamamlamadıysanız önce [`doc/lab02_student_guide.md`](lab02_student_guide.md),
> [`doc/lab03_student_guide.md`](lab03_student_guide.md),
> [`doc/lab04_student_guide.md`](lab04_student_guide.md),
> [`doc/lab05_student_guide.md`](lab05_student_guide.md) ve
> [`doc/lab06_student_guide.md`](lab06_student_guide.md) rehberlerini takip edin.

---

## 1. LAB Overview

Bu LAB'da, LAB06'da tanımladığınız **aynı** Shipment Delay Classification problemini, tekil
modeller yerine **Ensemble Learning** yöntemleriyle ele alacak ve sekiz farklı modeli **aynı
protokolle** karşılaştıracaksınız. LAB sonunda şu konuları uygulamış olacaksınız:

- **Ensemble Learning Fundamentals** (Bagging vs Boosting, weak/strong learner, model diversity)
- **Bootstrap Sampling** (sampling with replacement)
- **Bagging & Random Forest** (`BaggingClassifier`, `RandomForestClassifier`, OOB evaluation,
  feature importance)
- **AdaBoost** (adaptive sample weighting — küçük bir sentetik örnekle)
- **Gradient Boosting** (additive model, negative gradient fitting, boosting-stage log loss)
- **XGBoost & LightGBM** (regularized objective, histogram tabanlı inşa, leaf-wise büyüme)
- **Comparative Model Benchmarking** (8 modelin aynı protokolle: metrikler, generalization gap,
  training time, inference latency)
- **Model Selection Workshop** (iş önceliğine göre farklı senaryolarda farklı model seçimi)

Bu LAB'da **tek bir veri kümesi** kullanılır — LAB06 ile **birebir aynı**:

| Dataset | Kullanım Alanı |
|---|---|
| **E-Commerce Shipping Data** (`data/ecommerce_shipping/Train.csv`) | 8 modelin eğitimi, benchmarking, model seçim workshop'u |

> **Bu LAB'ın amacı en yüksek accuracy'yi elde etmek değildir.** Amaç, sistematik model
> karşılaştırması, deney tasarımı, genelleme performansı ve hesaplama maliyeti analizi
> öğrenmektir.

> **Önemli — Test Set Integrity:** Bu LAB'ın train/validation/test split'i, LAB06'dakiyle
> **index seviyesinde aynıdır** (notebook içinde bu doğrulanır). LAB06, bu test kümesini Section
> 8'de zaten bir kez kullanmıştı. Bu yüzden LAB07'de **bütün model seçim kararları yalnızca
> validation verisi üzerinden** verilir; bağımsız bir "nihai test evaluation" yapılmaz. Bu, bir
> notebook hatası değil, kasıtlı bir metodolojik karardır.

---

## 2. Prerequisites

LAB'ı çalıştırmadan önce bilgisayarınızda şunların kurulu olması gerekir:

- **Docker Desktop** veya kurumunuz tarafından onaylanan eşdeğer bir Docker ortamı
- **Docker Compose V2** (güncel Docker Desktop sürümleriyle birlikte gelir)
- **Git**
- Bir **web browser** (Chrome, Edge, Firefox vb.)
- **Visual Studio Code** (önerilir, zorunlu değildir)

### Python, NumPy, Pandas, Scikit-learn, XGBoost, LightGBM kurmanıza gerek yok

Bu projede tüm Python bağımlılıkları `uv` ile yönetilir ve **yalnızca Docker image'ı build
edilirken** kurulur. LAB07, `xgboost` ve `lightgbm`'i proje bağımlılıklarına **yeni olarak**
ekler — bu nedenle **Docker image'ının bu LAB için yeniden build edilmesi gerekir** (aşağıdaki
Bölüm 6'daki `--build` bayrağı bunu otomatik yapar).

> **Teknik not:** LightGBM'in Python wheel'i, Linux üzerinde `libgomp` (OpenMP runtime) kütüphanesine
> ihtiyaç duyar. Bu proje `python:3.11-slim` tabanlı bir image kullandığından, `Dockerfile`'a bu
> paketi (`libgomp1`) ekleyen bir adım eklenmiştir — bu sizin için otomatik olarak gerçekleşir, ek
> bir işlem yapmanız gerekmez.

---

## 3. Dataset Download Instructions

> **Not:** Veri dosyası bu proje tarafından otomatik olarak indirilmez.

### E-Commerce Shipping Data

LAB07, LAB02/LAB04/LAB06'da kullandığınız **aynı** `data/ecommerce_shipping/Train.csv` dosyasını
kullanır.

- **Eğer LAB02, LAB04 veya LAB06'yı zaten tamamladıysanız:** Bu dosya zaten doğru konumda olmalıdır
  — yeniden indirmenize gerek yoktur. Doğrudan [Bölüm 5](#5-cloning-the-repository-from-github)'e
  geçebilirsiniz.
- **Eğer bu dosya henüz yoksa**, aşağıdaki adımları izleyin:

  - **Kaggle bağlantısı:** [https://www.kaggle.com/datasets/prachi13/customer-analytics?resource=download](https://www.kaggle.com/datasets/prachi13/customer-analytics?resource=download)
  - **Beklenen hedef konum:** `data/ecommerce_shipping/Train.csv`

  **Adımlar:**

  1. Yukarıdaki Kaggle bağlantısını tarayıcınızda açın.
  2. Eğer dosya henüz görünmüyorsa Kaggle hesabınıza giriş yapın.
  3. **Download** butonuna tıklayarak ZIP arşivini indirin.
  4. İndirilen ZIP arşivini çıkarın (extract).
  5. Arşivden çıkan dosyanın adının `Train.csv` olduğunu doğrulayın.
  6. Bu dosyayı proje kök dizininde `data/ecommerce_shipping/` klasörünün içine kopyalayın (klasör
     yoksa oluşturun). Sonuçta dosya şu yolda olmalıdır: `data/ecommerce_shipping/Train.csv`.

> **Orijinal CSV içeriğini değiştirmeyin.** LAB07, bu dosyayı yalnızca okur; üzerinde herhangi bir
> değişiklik yapmaz.

> Northwind ve King County House Sales veri kümeleri bu LAB için **gerekli değildir**. Önceki
> LAB'lardan kalan dosyalar varsa, dokunmanıza gerek yoktur — silmeniz de gerekmez.

---

## 4. Expected Directory Structure

Dataset doğru konumda olduğunda proje yapınız şu şekilde görünmelidir:

```text
ml-labs/
├── data/
│   └── ecommerce_shipping/
│       └── Train.csv
├── labs/
│   ├── lab02/
│   │   └── ...
│   ├── lab03/
│   │   └── ...
│   ├── lab04/
│   │   └── ...
│   ├── lab05/
│   │   └── ...
│   ├── lab05_capstone/
│   │   └── ...
│   ├── lab06/
│   │   └── ...
│   └── lab07/
│       ├── lab07_advanced_ml_ensemble_methods.ipynb
│       └── README.md
├── doc/
│   ├── lab02_student_guide.md
│   ├── lab03_student_guide.md
│   ├── lab04_student_guide.md
│   ├── lab05_student_guide.md
│   ├── lab05_capstone_student_guide.md
│   ├── lab06_student_guide.md
│   └── lab07_student_guide.md
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

> **LAB02-LAB06'dan birini zaten tamamladıysanız** ve `ml-labs/` klasörünüz bilgisayarınızda
> halihazırda varsa, bu adımı atlayabilirsiniz — doğrudan bu klasörün içinde `git pull`
> çalıştırarak LAB07 dosyalarının (ve varsa diğer güncellemelerin) güncel sürümünü alabilirsiniz,
> ardından Bölüm 6'ya geçin.

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
   yapısına göre bu klasörün içine yerleştirin (`data/ecommerce_shipping/Train.csv`).
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

   - `Dockerfile`'a göre Docker image'ını **build** eder — LAB07 için bu, `xgboost`/`lightgbm`
     paketlerinin ve `libgomp1` sistem paketinin kurulmasını içerir. **Önceki bir LAB'dan kalan
     image varsa, LAB07'yi ilk kez çalıştırdığınızda `--build` bayrağı bu yeni bağımlılıkları
     içeren bir yeniden-build tetikler** — bu normal bir durumdur ve biraz zaman alabilir.
   - `ml-lab` adlı container'ı **başlatır**.
   - Container içinde **JupyterLab** servisini çalıştırır.
   - `-d` (detached) seçeneği, terminali kilitlemeden container'ı arka planda çalıştırır.

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
   `labs` klasörüne, ardından `lab07` klasörüne girin.
5. `lab07_advanced_ml_ensemble_methods.ipynb` dosyasına çift tıklayarak notebook'u açın.

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
  altında görüntülenir (bu LAB'da n_estimators/max_depth deneyleri, boosting log loss, ve
  Section 6'nın 6 benchmark grafiği dahil).
- Yaptığınız değişiklikleri kaydetmek için **`Ctrl + S`** tuşlarına basın veya üst menüden
  **File → Save Notebook**'u seçin.

### Önemli — Bu notebook 112 hücreden oluşur ve sıkı bir sıralı bağımlılık zinciri içerir

**Docker kullanılması, Jupyter Notebook'un hücre bazlı çalışma mantığını değiştirmez** — ancak bu
LAB'daki hücreler arası bağımlılık, önceki LAB'lardan daha derindir:

- Section 2'de oluşturulan `X_train`/`X_val`/`X_test`, `preprocessor`, `config` değişkenleri,
  **bütün sonraki section'larda** yeniden kullanılır.
- Section 3-5'te oluşturulan `rf_cfg`, `ada_cfg`, `gb_cfg`, `xgb_cfg`, `lgbm_cfg` ve ilgili fit
  edilmiş pipeline'lar (`random_forest_model`, `xgboost_model`, vb.), Section 6'nın
  `build_pipeline()` fonksiyonu ve Section 7/Advanced Challenges tarafından **doğrudan** kullanılır.
- Section 6'da oluşturulan `benchmark_df`, Section 7'nin **bütün** Student Questions ve Model
  Selection Cases hücrelerinin temelidir.
- Section 5'te oluşturulan `X_train_for_es`/`X_val_for_es` (Early Stopping için ayrı,
  train-only fit edilmiş preprocessor çıktısı), Advanced Challenge 3'te **tekrar kullanılır**.

Hücreleri sırayla çalıştırmazsanız (veya bir hücreyi atlarsanız), sonraki hücrelerde `NameError`
alırsınız — bu durumda **Run → Run All Cells** ile notebook'u baştan sona çalıştırmanız en güvenli
çözümdür. Bu notebook'un tam çalıştırılması (Advanced Challenges dahil), donanımınıza bağlı olarak
**birkaç dakika** sürebilir (`GradientBoostingClassifier` ve geniş `n_estimators` sweep'leri en
yavaş hücrelerdir).

---

## 9. LAB Sections

Notebook, aşağıdaki sırayla ilerler:

1. **LAB06 Review & Ensemble Fundamentals** (10 dk) — Single Learner vs Ensemble, Bagging vs
   Boosting kavramsal çerçevesi, Educational Question.
2. **Baseline Models, Bootstrap & Bagging** (15 dk) — LAB06 ile aynı split'in yeniden kurulması
   ve **Test Set Integrity** doğrulaması, baseline modeller, derin bir Decision Tree ile
   overfitting demonstrasyonu, Bootstrap Sampling (NumPy), `BaggingClassifier` demonstrasyonu.
3. **Random Forest** (20 dk) — mimari açıklaması, `n_estimators`/`max_depth` deneyleri (2
   görselleştirme), OOB evaluation, feature importance.
4. **AdaBoost & Gradient Boosting** (30 dk) — AdaBoost'un sample-weight güncellemesi
   (`[SYNTHETIC]` etiketli küçük bir örnek), Gradient Boosting matematiği, learning rate deneyi,
   boosting-stage log loss grafiği. **Break (10 dk)** bu section'ın sonundadır.
5. **XGBoost & LightGBM** (25 dk) — regularized objective, her iki kütüphane için hands-on,
   `num_leaves`/`max_depth` ilişkisi, isteğe bağlı bir Early Stopping örneği.
6. **Comparative Model Benchmarking** (25 dk) — **LAB'ın en önemli bölümü.** 8 modelin aynı
   protokolle (metrikler, generalization gap, training time, inference latency) karşılaştırılması
   ve 6 görselleştirme.
7. **Model Selection & Final Workshop** (15 dk) — Student Questions, 3 Model Selection Case,
   Evaluation Integrity notu, Markdown tabanlı Benchmark Findings raporu.

Notebook sonunda, deneyimli katılımcılar için dört **opsiyonel Advanced Challenge** (Ensemble Size
& Diminishing Returns, Equal Computational Budget, Early Stopping Expanded, Voting Classifier)
bulunur — bunlar ana 150 dakikalık süreye dahil değildir ve tamamlanmamaları notebook'un
çalışmasını etkilemez.

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
| **`ImportError`/`OSError: libgomp.so.1: cannot open shared object file`** (LightGBM) | Bu, image'ın LAB07 öncesi (eski) bir sürümüyle çalıştığınızı gösterir — güncel `Dockerfile`, `libgomp1` sistem paketini zaten içerir. `docker compose up --build -d` komutunu **`--build`** bayrağıyla tekrar çalıştırarak image'ı yeniden oluşturun. |
| **JupyterLab açılmıyor / tarayıcıda yüklenmiyor** | `docker compose ps` ile container'ın `running` durumda olduğunu doğrulayın. `docker compose logs ml-lab` ile hata olup olmadığını kontrol edin. Gerekirse `docker compose down` ve ardından `docker compose up --build -d` ile yeniden başlatın. |
| **Dataset `FileNotFoundError`** | Notebook, `data/ecommerce_shipping/Train.csv` dosyasını bulamadığında bu hatayı fırlatır. Bölüm 3'teki adımlara göre dosyanın doğru konumda olduğunu kontrol edin (LAB02/LAB04/LAB06'yı tamamladıysanız bu dosya zaten mevcut olmalıdır). |
| **Yanlış Notebook Kernel** | Bu container içinde tek bir Python ortamı (`Python 3 (ipykernel)`) bulunur. Notebook sağ üstte farklı bir kernel adı gösteriyorsa, **Kernel → Change Kernel** menüsünden `Python 3 (ipykernel)`'i seçin. |
| **`NameError`** (örn. `benchmark_df`, `preprocessor`, `rf_cfg` veya `random_forest_model` tanımlı değil) | Section 2-6'daki hücreler sırayla çalıştırılmadıysa bu hata oluşur (Bölüm 8'deki bağımlılık zincirine bakın). **Run → Run All Cells** ile notebook'u baştan sona çalıştırın. |
| **Training Time / Inference Latency sayıları her çalıştırmada biraz farklı** | Bu **beklenen bir durumdur, hata değildir.** Accuracy/F1/ROC-AUC gibi metrikler sabit random seed sayesinde her zaman aynıdır; ancak zamanlama ölçümleri işletim sistemi zamanlaması ve arka plan süreçlerinden etkilenir. Notebook, bu nedenle kesin sayılar yerine göreli sıralamayı (örn. "GradientBoosting her zaman en yavaş eğitilen model") vurgular. |
| **Section 6 (benchmark) hücresi uzun sürüyor** | 8 modelin her biri 3 kez eğitiliyor (median training time için) ve 10+2 kez tahmin yapıyor (median inference latency için) — bu, tek seferlik bir `fit()`'ten daha uzun sürer. Donanımınıza bağlı olarak bu hücre tek başına 5-15 saniye sürebilir; bu normaldir. |
| **`LGBMDeprecationWarning` (`eval_set` argümanı)** | Bu notebook, LightGBM'in Early Stopping örneklerinde (Section 5, Challenge 3) güncel `eval_X`/`eval_y` argümanlarını kullanır — bu uyarıyı görmemelisiniz. Görüyorsanız, kurulu `lightgbm` sürümünüzün `uv.lock`'taki sürümle (4.7.0) eşleştiğini `docker compose up --build -d` ile doğrulayın. |
| **`ValueError` (encoder, scaler veya pipeline hatası)** | Genellikle bir hücrenin atlanmış veya yanlış sırada çalıştırılmış olmasından kaynaklanır (örn. `transform()` çağrılmadan önce `fit()` çağrılmamış). **Kernel → Restart Kernel and Run All Cells** ile temiz bir çalıştırma yapın. |
| **Notebook değişiklikleri kaydedilemiyor** | Bölüm 10'da açıklanan bind mount sayesinde kaydetme normalde sorunsuz çalışır. Kaydetme başarısız oluyorsa, tarayıcı sekmesini yenileyin (F5) ve `Ctrl + S` ile tekrar deneyin; sorun sürerse `docker compose logs ml-lab` ile container loglarını kontrol edin. |
