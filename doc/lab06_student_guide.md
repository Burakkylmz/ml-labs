# LAB06 Student Guide — Supervised Learning: Classification

Bu rehber, `ml-labs` projesindeki **LAB06: Supervised Learning — Classification** çalışmasını
kendi bilgisayarınızda Docker üzerinden nasıl çalıştıracağınızı adım adım açıklar.

**Eğitim süresi:** 150 dakika (10 dakikalık mola dahil)

> Bu LAB, **LAB02**, **LAB03**, **LAB04** ve **LAB05**'in devamıdır. Bu LAB'ları
> tamamlamadıysanız önce [`doc/lab02_student_guide.md`](lab02_student_guide.md),
> [`doc/lab03_student_guide.md`](lab03_student_guide.md),
> [`doc/lab04_student_guide.md`](lab04_student_guide.md) ve
> [`doc/lab05_student_guide.md`](lab05_student_guide.md) rehberlerini takip edin.

---

## 1. LAB Overview

Bu LAB'da, E-Commerce Shipping verisini kullanarak bir sevkiyatın **zamanında ulaşıp
ulaşmayacağını** tahmin eden Binary Classification modelleri geliştireceksiniz. LAB sonunda şu
konuları uygulamış olacaksınız:

- **Classification Fundamentals** (classification vs regression, binary classification)
- **Baseline Classification** (`DummyClassifier`)
- **Logistic Regression** (sigmoid, log-odds, `predict()` vs `predict_proba()`)
- **Decision Tree Classification** (Gini impurity, `max_depth`, overfitting)
- **Confusion Matrix & Classification Metrics** (Accuracy, Precision, Recall, F1)
- **ROC-AUC & Precision–Recall Analysis** (threshold-independent ranking metrikleri)
- **Class Imbalance & Decision Threshold** (Accuracy Paradox, threshold seçimi)
- **Model Comparison & Selection** (validation ile seçim, test ile tek seferlik doğrulama)

Bu LAB'da **tek bir veri kümesi** kullanılır — LAB02'deki Northwind veri kümesi burada
**kullanılmaz**:

| Dataset | Kullanım Alanı |
|---|---|
| **E-Commerce Shipping Data** (`data/ecommerce_shipping/Train.csv`) | Feature seçimi, baseline, Logistic Regression, Decision Tree, model karşılaştırması |

> **Bu LAB'da gerçek classification modelleri eğitilir ve karşılaştırılır.** LAB05'te Regression
> metodolojisini (baseline → model → değerlendirme → karşılaştırma → seçim → tek seferlik test)
> öğrenmiştiniz; bu LAB'da **aynı metodoloji** Classification problemleri için uygulanır.

> **Önemli varsayım — Prediction Time:** Notebook, modelin **sevkiyat gönderilmeden önce**
> tahmin yaptığını varsayar. Kullanılan feature'ların (`Warehouse_block`, `Mode_of_Shipment`,
> `Product_importance`, `Cost_of_the_Product`, `Prior_purchases`, `Discount_offered`,
> `Weight_in_gms`) bu zaman diliminde gerçek bir operasyonel sistemde erişilebilir olduğu
> **doğrulanmamıştır** — bu, bir eğitim varsayımıdır.

> **Önemli sınırlama:** Bu veri kümesi gerçek bir lojistik şirketinin verisi **değildir**. Bu
> LAB'daki modellerin gerçek operasyonel ortamlarda kullanılmaya hazır olduğu iddia
> edilmemektedir.

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
Scikit-learn kurmanıza gerek yoktur** — yalnızca Docker Desktop yeterlidir. LAB06, LAB02-LAB05 ile
**aynı Docker image'ını** kullanır; `scikit-learn` LAB04'ten beri zaten kurulu bir bağımlılıktır
— yeni bir bağımlılık eklenmemiştir.

---

## 3. Dataset Download Instructions

> **Not:** Veri dosyası bu proje tarafından otomatik olarak indirilmez.

### E-Commerce Shipping Data

LAB06, LAB02 ve LAB04'te kullandığınız **aynı** `data/ecommerce_shipping/Train.csv` dosyasını
kullanır.

- **Eğer LAB02 veya LAB04'ü zaten tamamladıysanız:** Bu dosya zaten doğru konumda olmalıdır —
  yeniden indirmenize gerek yoktur. Doğrudan [Bölüm 5](#5-cloning-the-repository-from-github)'e
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

> **Orijinal CSV içeriğini değiştirmeyin.** LAB06, bu dosyayı yalnızca okur; üzerinde herhangi bir
> değişiklik yapmaz.

> Northwind veri kümesi (`data/northwind/`) bu LAB için **gerekli değildir**. LAB02'den/LAB05'ten
> kalan dosyalar varsa, dokunmanıza gerek yoktur — silmeniz de gerekmez.

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
│   └── lab06/
│       ├── lab06_supervised_classification.ipynb
│       └── README.md
├── doc/
│   ├── lab02_student_guide.md
│   ├── lab03_student_guide.md
│   ├── lab04_student_guide.md
│   ├── lab05_student_guide.md
│   └── lab06_student_guide.md
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

> **LAB02, LAB03, LAB04 veya LAB05'i zaten tamamladıysanız** ve `ml-labs/` klasörünüz
> bilgisayarınızda halihazırda varsa, bu adımı atlayabilirsiniz — doğrudan bu klasörün içinde
> `git pull` çalıştırarak LAB06 dosyalarının (ve varsa diğer güncellemelerin) güncel sürümünü
> alabilirsiniz, ardından Bölüm 6'ya geçin.

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

   - Henüz oluşturulmamışsa, `Dockerfile`'a göre Docker image'ını **build** eder (bağımlılıkları
     `uv` ile kurar).
   - `ml-lab` adlı container'ı **başlatır**.
   - Container içinde **JupyterLab** servisini çalıştırır.
   - `-d` (detached) seçeneği, terminali kilitlemeden container'ı arka planda çalıştırır.

   > Eğer önceki LAB'lardan kalan bir image varsa, bu komut genellikle çok hızlı tamamlanır
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
   `labs` klasörüne, ardından `lab06` klasörüne girin.
5. `lab06_supervised_classification.ipynb` dosyasına çift tıklayarak notebook'u açın.

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
  altında görüntülenir (bu LAB'da target distribution, confusion matrix, ROC/PR curve, decision
  tree ve threshold grafikleri dahil).
- Yaptığınız değişiklikleri kaydetmek için **`Ctrl + S`** tuşlarına basın veya üst menüden
  **File → Save Notebook**'u seçin.

### Önemli

**Docker kullanılması, Jupyter Notebook'un hücre bazlı çalışma mantığını değiştirmez.** Yazdığınız
Python kodu, container içinde çalışan Jupyter **kernel**'i tarafından çalıştırılır; sonuçlar her
zaman ilgili hücrenin altında görüntülenir — bu davranış, Docker kullanılmasa da aynıdır.

**Hücre sırası bu LAB'da özellikle önemlidir.** Section 2'de oluşturulan `X_train`/`X_val`/`X_test`
değişkenleri ve Section 3'te oluşturulan `preprocessor`/`logreg_pipe` değişkenleri, Section 4'ten
Section 8'e kadar **tüm** model eğitimi, threshold seçimi ve değerlendirme hücrelerinde yeniden
kullanılır. Hücreleri sırayla çalıştırmazsanız (veya bir hücreyi atlarsanız), sonraki hücrelerde
`NameError` alabilirsiniz — bu durumda **Run → Run All Cells** ile notebook'u baştan sona
çalıştırmanız en güvenli çözümdür.

---

## 9. LAB Sections

Notebook, aşağıdaki sırayla ilerler:

1. **Classification Fundamentals & Dataset** — classification'ın tanımı, regression'dan farkı
   (LAB05 ile karşılaştırma), target dağılımı, feature seçim gerekçesi.
2. **Data Splitting & Baseline Models** — stratified %70/%15/%15 split,
   `DummyClassifier(most_frequent)` baseline'ı.
3. **Logistic Regression** — sigmoid/log-odds matematiği, bu LAB'ın şeması için yeniden kurulan
   preprocessing pipeline, `predict()` vs `predict_proba()`, katsayı yorumlama.
4. **Decision Tree Classification** — Gini impurity, farklı `max_depth` değerleriyle
   underfitting'den overfitting'e geçiş, küçük bir ağacın görselleştirilmesi.
5. **Confusion Matrix & Classification Metrics** — TP/TN/FP/FN, Accuracy/Precision/Recall/F1,
   False Positive/Negative'in iş bağlamında yorumlanması.
6. **ROC-AUC & Precision–Recall Analysis** — threshold'dan bağımsız sıralama metrikleri, Average
   Precision'ın class prevalence bağlamında yorumlanması.
7. **Class Imbalance & Decision Threshold** — gerçek (orta derecede dengesiz) dağılım ile açıkça
   etiketlenmiş bir synthetic (şiddetli dengesiz) örneğin karşılaştırılması; threshold
   karşılaştırması ve açık bir iş hedefine dayalı threshold seçimi.
8. **Model Comparison & Final Workshop** — model karşılaştırma tablosu, model + threshold seçimi,
   test verisinin **bir kez** kullanılması ve bir Classification Evaluation Summary.

Notebook sonunda, deneyimli katılımcılar için üç **opsiyonel Advanced Challenge** (class weight
karşılaştırması, `TunedThresholdClassifierCV` ile otomatik threshold tuning, depo/sevkiyat
yöntemi/ürün önemi bazında error segmentation) bulunur — bunlar ana 150 dakikalık süreye dahil
değildir ve tamamlanmamaları notebook'un çalışmasını etkilemez.

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
| **Dataset `FileNotFoundError`** | Notebook, `data/ecommerce_shipping/Train.csv` dosyasını bulamadığında bu hatayı fırlatır. Bölüm 3'teki adımlara göre dosyanın doğru konumda olduğunu kontrol edin (LAB02/LAB04'ü tamamladıysanız bu dosya zaten mevcut olmalıdır). |
| **Yanlış Notebook Kernel** | Bu container içinde tek bir Python ortamı (`Python 3 (ipykernel)`) bulunur. Notebook sağ üstte farklı bir kernel adı gösteriyorsa, **Kernel → Change Kernel** menüsünden `Python 3 (ipykernel)`'i seçin. |
| **Python `ModuleNotFoundError`** (örn. `sklearn` bulunamadı) | Tüm bağımlılıklar `Dockerfile` build aşamasında kurulur; bu hata genellikle image'ın güncel bağımlılıklarla yeniden build edilmediğini gösterir. `docker compose up --build -d` komutunu `--build` bayrağıyla tekrar çalıştırın. |
| **`NameError` (örn. `X_train`, `preprocessor` veya `logreg_pipe` tanımlı değil)** | Section 2/3'teki hücreler sırayla çalıştırılmadıysa bu hata oluşur. **Run → Run All Cells** ile notebook'u baştan sona çalıştırın. |
| **`ConvergenceWarning` (LogisticRegression)** | Bu LAB'da normalde bu uyarı oluşmaz. Oluşursa, yalnızca gizlemeyin — genellikle `max_iter` değerini artırmak veya feature'ların doğru ölçeklendiğini (pipeline'daki `StandardScaler`) kontrol etmek gerekir. |
| **`ValueError` (encoder, scaler veya pipeline hatası)** | Genellikle bir hücrenin atlanmış veya yanlış sırada çalıştırılmış olmasından kaynaklanır (örn. `transform()` çağrılmadan önce `fit()` çağrılmamış). **Kernel → Restart Kernel and Run All Cells** ile temiz bir çalıştırma yapın. |
| **Confusion Matrix'te beklenmeyen satır/sütun sırası** | `confusion_matrix(..., labels=[0, 1])` çağrısındaki `labels` parametresinin kaldırılmış veya değiştirilmiş olmasından kaynaklanabilir. Notebook'taki orijinal hücreyi referans alın; `0` = On Time, `1` = Late olmalıdır. |
| **Notebook değişiklikleri kaydedilemiyor** | Bölüm 10'da açıklanan bind mount sayesinde kaydetme normalde sorunsuz çalışır. Kaydetme başarısız oluyorsa, tarayıcı sekmesini yenileyin (F5) ve `Ctrl + S` ile tekrar deneyin; sorun sürerse `docker compose logs ml-lab` ile container loglarını kontrol edin. |
