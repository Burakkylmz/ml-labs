# LAB04 Student Guide — Data Preparation & Preprocessing Pipelines

Bu rehber, `ml-labs` projesindeki **LAB04: Data Preparation & Preprocessing Pipelines** çalışmasını
kendi bilgisayarınızda Docker üzerinden nasıl çalıştıracağınızı adım adım açıklar.

**Eğitim süresi:** 150 dakika (10 dakikalık mola dahil)

> Bu LAB, **LAB02** ve **LAB03**'ün devamıdır. Bu LAB'ları tamamlamadıysanız önce
> [`doc/lab02_student_guide.md`](lab02_student_guide.md) ve
> [`doc/lab03_student_guide.md`](lab03_student_guide.md) rehberlerini takip edin.

---

## 1. LAB Overview

Bu LAB'da, LAB03'te tespit ettiğiniz veri kalitesi ve veri yapısı sorunlarının, bir Machine Learning
modeline vermeden önce **nasıl ele alınacağını (Data Preparation)** öğreneceksiniz. LAB sonunda şu
konuları uygulamış olacaksınız:

- **Data Quality Validation** (completeness, validity, data quality summary)
- **Missing Value Handling** (`SimpleImputer` stratejileri: mean, median, most_frequent, constant)
- **Duplicate & Outlier Handling** (IQR yöntemi, clipping)
- **Categorical Encoding** (`OneHotEncoder`, ordinal/nominal ayrımı)
- **Feature Scaling** (`StandardScaler`, `MinMaxScaler`)
- **Train / Validation / Test Split** (stratified split)
- **Data Leakage Prevention** (leakage'ı tanıma ve önleme)
- Scikit-learn **`Pipeline`** ve **`ColumnTransformer`** ile tekrar kullanılabilir bir preprocessing
  workflow'u

Bu LAB'da **tek bir veri kümesi** kullanılır — LAB02'deki Northwind veri kümesi burada
**kullanılmaz**:

| Dataset | Kullanım Alanı |
|---|---|
| **E-Commerce Shipping Data** | Data Quality, Missing Values, Outliers, Encoding, Scaling, Train/Val/Test Split, Pipeline/ColumnTransformer |

> **Bu LAB'da model eğitimi yapılmaz.** Amaç yalnızca, bir sonraki LAB'larda (LAB05, LAB06) model
> eğitimiyle birlikte kullanılacak bir preprocessing pipeline'ı inşa etmektir.

---

## 2. Prerequisites

LAB'ı çalıştırmadan önce bilgisayarınızda şunların kurulu olması gerekir:

- **Docker Desktop** veya kurumunuz tarafından onaylanan eşdeğer bir Docker ortamı
- **Docker Compose V2** (güncel Docker Desktop sürümleriyle birlikte gelir)
- **Git**
- Bir **web browser** (Chrome, Edge, Firefox vb.)
- **Visual Studio Code** (önerilir, zorunlu değildir)

### Python, NumPy, Pandas, Scikit-learn kurmanıza gerek yok

Bu projede tüm Python bağımlılıkları (`numpy`, `pandas`, `matplotlib`, `scikit-learn`, `pyyaml`,
`jupyterlab` vb.) `uv` ile yönetilir, ancak `uv` **yalnızca Docker image'ı build edilirken** çalışır:

- `Dockerfile` içinde `uv sync --locked` komutu, `pyproject.toml` ve `uv.lock` dosyalarına göre tüm
  bağımlılıkları container içindeki `/opt/venv` sanal ortamına kurar.
- JupyterLab bu sanal ortam üzerinden çalışır.

Bu nedenle, LAB'ı Docker ile çalıştırmak için **kendi bilgisayarınıza Python, uv, NumPy, Pandas veya
Scikit-learn kurmanıza gerek yoktur** — yalnızca Docker Desktop yeterlidir. LAB04, LAB02/LAB03 ile
**aynı Docker image'ını** kullanır; `scikit-learn` bu LAB'da ilk kez kullanılır ama proje başından beri
zaten kurulu bir bağımlılıktır — yeni bir bağımlılık eklenmemiştir.

---

## 3. Dataset Download Instructions

> **Not:** Veri dosyası bu proje tarafından otomatik olarak indirilmez.

### E-Commerce Shipping Data

LAB04, LAB02 ve LAB03'te kullandığınız **aynı** `data/ecommerce_shipping/Train.csv` dosyasını kullanır.

- **Eğer LAB02/LAB03'ü zaten tamamladıysanız:** Bu dosya zaten doğru konumda olmalıdır — yeniden
  indirmenize gerek yoktur.
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

> **Orijinal CSV içeriğini değiştirmeyin.** LAB04, bu dosyayı yalnızca okur; üzerinde herhangi bir
> değişiklik yapmaz. Notebook içindeki eksik değer/duplicate gösterimleri, bu dosyanın **bellekteki bir
> kopyası** üzerinde yapılır — orijinal dosyayı etkilemez.

> Northwind veri kümesi (`data/northwind/`) bu LAB için **gerekli değildir**. LAB02'den kalan dosyalar
> varsa, dokunmanıza gerek yoktur — silmeniz de gerekmez.

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
│   └── lab04/
│       ├── lab04_data_preparation.ipynb
│       └── README.md
├── doc/
│   ├── lab02_student_guide.md
│   ├── lab03_student_guide.md
│   └── lab04_student_guide.md
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

> **LAB02 veya LAB03'ü zaten tamamladıysanız** ve `ml-labs/` klasörünüz bilgisayarınızda halihazırda
> varsa, bu adımı atlayabilirsiniz — doğrudan bu klasörün içinde `git pull` çalıştırarak LAB04
> dosyalarının (ve varsa diğer güncellemelerin) güncel sürümünü alabilirsiniz, ardından Bölüm 6'ya
> geçin.

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

5. Bölüm 3'te indirdiğiniz dataset dosyasını, Bölüm 4'te gösterilen klasör yapısına göre bu klasörün
   içine yerleştirin (`data/ecommerce_shipping/Train.csv`).
6. Bu rehberin kalan adımlarını (Docker ile çalıştırma dahil) her zaman bu `ml-labs/` klasörünün içinden
   çalıştıracaksınız.

---

## 6. Running the LAB with Docker

1. Bir terminal açın ve proje kök dizinine (`ml-labs/`) geçin.
2. **Docker Desktop'ın çalışır durumda olduğundan emin olun** (sistem tepsisindeki Docker ikonu "running"
   göstermelidir). Docker Desktop çalışmıyorsa aşağıdaki komutlar bağlantı hatası verir.
3. Aşağıdaki komutu çalıştırın:

   ```bash
   docker compose up --build -d
   ```

   Bu komut şunları yapar:

   - Henüz oluşturulmamışsa, `Dockerfile`'a göre Docker image'ını **build** eder (bağımlılıkları `uv`
     ile kurar).
   - `ml-lab` adlı container'ı **başlatır**.
   - Container içinde **JupyterLab** servisini çalıştırır.
   - `-d` (detached) seçeneği, terminali kilitlemeden container'ı arka planda çalıştırır.

   > Eğer LAB02/LAB03'ten kalan bir image varsa, bu komut genellikle çok hızlı tamamlanır (önceki build
   > katmanları yeniden kullanılır, çünkü bağımlılıklar değişmemiştir).

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

Bu projede JupyterLab, `127.0.0.1:8888` portu üzerinden **yalnızca kendi bilgisayarınızdan (localhost)**
erişilebilir şekilde yapılandırılmıştır.

1. Tarayıcınızı açın.
2. Adres çubuğuna şunu yazın:

   ```text
   http://localhost:8888
   ```

3. Karşınıza bir giriş (login) ekranı gelirse, `docker compose logs ml-lab` çıktısından aldığınız
   **token** değerini ilgili alana yapıştırın. (Loglardaki tam URL'yi — `token=...` dahil — doğrudan
   tarayıcıya yapıştırmanız da yeterlidir.)
4. JupyterLab açıldığında, soldaki dosya gezgininde (file browser) proje kök dizinini göreceksiniz.
   `labs` klasörüne, ardından `lab04` klasörüne girin.
5. `lab04_data_preparation.ipynb` dosyasına çift tıklayarak notebook'u açın.

> Container'ın çalışma dizini (`WORKDIR`) `/app`'tir ve proje kök dizininiz bu yola bağlanır (bind
> mount). Bu nedenle JupyterLab'daki klasör yapısı, kendi bilgisayarınızdaki `ml-labs/` klasör yapısıyla
> birebir aynıdır.

---

## 8. Working with Notebook Cells

Bir Jupyter notebook (`.ipynb`), iki tür hücreden oluşur:

- **Markdown Cell**: Açıklama metni içerir (bu rehber gibi); çalıştırıldığında kod üretmez, yalnızca
  biçimlendirilmiş metni gösterir.
- **Code Cell**: Çalıştırılabilir Python kodu içerir.

### Temel kullanım

- Bir Code Cell'i çalıştırmak için hücreye tıklayın ve **`Shift + Enter`** tuşlarına basın. Bu, hücreyi
  çalıştırır ve bir sonraki hücreye geçer.
- Hücre çalıştırıldıktan sonra, çıktısı (varsa) **hücrenin hemen altında** görüntülenir.
- Bir Pandas `DataFrame`'i döndüren bir hücre çalıştırıldığında, DataFrame tablo olarak hücrenin altında
  gösterilir.
- Bir Matplotlib grafiği oluşturan bir hücre çalıştırıldığında, grafik görsel olarak hücrenin altında
  görüntülenir.
- Yaptığınız değişiklikleri kaydetmek için **`Ctrl + S`** tuşlarına basın veya üst menüden **File → Save
  Notebook**'u seçin.

### Önemli

**Docker kullanılması, Jupyter Notebook'un hücre bazlı çalışma mantığını değiştirmez.** Yazdığınız Python
kodu, container içinde çalışan Jupyter **kernel**'i tarafından çalıştırılır; sonuçlar her zaman ilgili
hücrenin altında görüntülenir — bu davranış, Docker kullanılmasa da aynıdır.

**Hücre sırası bu LAB'da özellikle önemlidir.** Section 6'da oluşturulan `X_train`/`X_val`/`X_test`
değişkenleri, Section 7'deki preprocessing pipeline hücrelerinde kullanılır. Hücreleri sırayla
çalıştırmazsanız (veya bir hücreyi atlarsanız), sonraki hücrelerde `NameError` alabilirsiniz — bu
durumda **Run → Run All Cells** ile notebook'u baştan çalıştırmanız en güvenli çözümdür.

---

## 9. LAB Sections

Notebook, aşağıdaki sırayla ilerler:

1. **LAB03 Review & Preprocessing Workflow** — EDA ile Data Preparation arasındaki fark ve dataset'in
   hızlı hatırlatması.
2. **Data Quality & Validation** — completeness/validity kontrolleri ve bir Data Quality Summary.
3. **Missing Values & Duplicate Handling** — `SimpleImputer` stratejileri (mean, median, most_frequent,
   constant) ve duplicate tespiti; gösterimler dataset'in bellekteki bir kopyasında yapılır.
4. **Outlier Detection & Treatment** — IQR yöntemi ve bir kopya üzerinde clipping gösterimi.
5. **Categorical Encoding & Feature Scaling** — `OneHotEncoder`, `handle_unknown="ignore"`,
   `StandardScaler` ve `MinMaxScaler` karşılaştırması.
6. **Train / Validation / Test Split & Data Leakage** — stratified %70/%15/%15 split ve leakage
   kavramının somut bir örnekle gösterimi.
7. **Scikit-learn Pipeline & ColumnTransformer** — bu LAB'ın en önemli bölümü: numerical ve categorical
   feature'ları birleştiren, yalnızca training verisinden öğrenen tek bir preprocessing pipeline'ı.
8. **Preprocessing Validation & Workshop** — kısa bir öğrenci değerlendirmesi ve iki kritik tartışma
   sorusu (bilinmeyen kategori, farklı scaler fit etme).

Notebook sonunda, deneyimli katılımcılar için üç **opsiyonel Advanced Challenge** (custom transformer,
scaler karşılaştırması, leakage investigation) bulunur — bunlar ana 150 dakikalık süreye dahil değildir
ve tamamlanmamaları notebook'un çalışmasını etkilemez.

---

## 10. Stopping the LAB

Çalışmanız bittiğinde container'ları durdurmak için:

```bash
docker compose down
```

### Değişiklikleriniz korunuyor mu?

Proje kök dizini (`ml-labs/`), `compose.yaml` içinde bir **bind mount** ile container'ın `/app`
klasörüne bağlanır. Bu, notebook içindeki tüm klasörlerin (`labs/`, `data/`, `src/`, `config/` dahil)
doğrudan kendi bilgisayarınızdaki dosyalar olduğu anlamına gelir.

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
| **Port 8888 kullanımda** (`port is already allocated`) | Bilgisayarınızda 8888 portunu kullanan başka bir uygulama (örn. LAB02/LAB03'ten kapatılmamış bir container) çalışıyor olabilir. `docker compose down` ile önceki container'ı durdurun, ardından tekrar deneyin. |
| **JupyterLab açılmıyor / tarayıcıda yüklenmiyor** | `docker compose ps` ile container'ın `running` durumda olduğunu doğrulayın. `docker compose logs ml-lab` ile hata olup olmadığını kontrol edin. Gerekirse `docker compose down` ve ardından `docker compose up --build -d` ile yeniden başlatın. |
| **Dataset `FileNotFoundError`** | Notebook, `data/ecommerce_shipping/Train.csv` dosyasını bulamadığında bu hatayı fırlatır. Bölüm 3'teki adımlara göre dosyanın doğru konumda olduğunu kontrol edin (LAB02/LAB03'ü tamamladıysanız bu dosya zaten mevcut olmalıdır). |
| **Yanlış Notebook Kernel** | Bu container içinde tek bir Python ortamı (`Python 3 (ipykernel)`) bulunur. Notebook sağ üstte farklı bir kernel adı gösteriyorsa, **Kernel → Change Kernel** menüsünden `Python 3 (ipykernel)`'i seçin. |
| **Python `ModuleNotFoundError`** (örn. `sklearn` bulunamadı) | Tüm bağımlılıklar `Dockerfile` build aşamasında kurulur; bu hata genellikle image'ın güncel bağımlılıklarla yeniden build edilmediğini gösterir. `docker compose up --build -d` komutunu `--build` bayrağıyla tekrar çalıştırın. |
| **`NameError` (örn. `X_train` tanımlı değil)** | Section 6/7'deki hücreler sırayla çalıştırılmadıysa bu hata oluşur. **Run → Run All Cells** ile notebook'u baştan sona çalıştırın. |
| **`ValueError` / encoder veya scaler hatası** | Genellikle bir hücrenin atlanmış veya yanlış sırada çalıştırılmış olmasından kaynaklanır (örn. `transform()` çağrılmadan önce `fit()` çağrılmamış). **Kernel → Restart Kernel and Run All Cells** ile temiz bir çalıştırma yapın. |
| **Notebook değişiklikleri kaydedilemiyor** | Bölüm 10'da açıklanan bind mount sayesinde kaydetme normalde sorunsuz çalışır. Kaydetme başarısız oluyorsa, tarayıcı sekmesini yenileyin (F5) ve `Ctrl + S` ile tekrar deneyin; sorun sürerse `docker compose logs ml-lab` ile container loglarını kontrol edin. |
