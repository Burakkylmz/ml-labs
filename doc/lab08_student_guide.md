# LAB08 Student Guide — Feature Engineering, Feature Selection & Explainability

Bu rehber, `ml-labs` projesindeki **LAB08: Feature Engineering, Feature Selection &
Explainability** çalışmasını kendi bilgisayarınızda Docker üzerinden nasıl çalıştıracağınızı
adım adım açıklar.

**Eğitim süresi:** 150 dakika (10 dakikalık mola dahil), artı isteğe bağlı Advanced Challenges

> Bu LAB, **LAB02-LAB07**'nin devamıdır. Bu LAB'ları tamamlamadıysanız önce
> [`doc/lab02_student_guide.md`](lab02_student_guide.md), [`doc/lab03_student_guide.md`](lab03_student_guide.md),
> [`doc/lab04_student_guide.md`](lab04_student_guide.md), [`doc/lab05_student_guide.md`](lab05_student_guide.md),
> [`doc/lab06_student_guide.md`](lab06_student_guide.md) ve [`doc/lab07_student_guide.md`](lab07_student_guide.md)
> rehberlerini takip edin.

---

## 1. LAB Overview

Bu LAB'da, **yeni bir veri kümesi** (DataCo SMART Supply Chain) üzerinde, bir siparişin
sevkiyatından önce gecikme riski taşıyıp taşımadığını tahmin eden bir classification problemini
ele alacaksınız. LAB sonunda şu konuları uygulamış olacaksınız:

- **Feature Engineering vs. Feature Selection vs. Feature Extraction**
- **Data Privacy & Target Leakage Audit** (bu LAB'ın en kritik bölümü)
- **Group-Aware Temporal Data Splitting**
- **Date-Time / Cyclical / Interaction Feature Engineering**
- **Filter / Wrapper / Embedded Feature Selection**
- **Comparative Feature Benchmarking** (Baseline vs. Engineered vs. Selected)
- **Model-Based Importance, Permutation Importance, SHAP** (Global & Local Explainability)

| Dataset | Kullanım Alanı |
|---|---|
| **DataCo SMART Supply Chain** (`data/dataco_supply_chain/DataCoSupplyChainDataset.csv`) | Bu LAB'ın tek veri kümesi — feature engineering, feature selection, explainability |

> **Önemli — Veri Gizliliği:** Bu veri kümesi gerçek müşteri bilgileri (isim, e-posta, adres vb.)
> içerir. Bu alanlar **hiçbir zaman belleğe yüklenmez** — `src/data_loading.py` içindeki
> `load_dataco_supply_chain()`, bu kolonları dosya okuma aşamasında (`usecols` ile) hariç tutar.

> **Önemli — Korunmuş Test Seti:** Bu LAB, veriyi group-aware kronolojik olarak train/validation/
> test olarak böler ve **test kümesine hiçbir zaman dokunmaz** — bu küme **LAB09**'un sonunda
> kullanılacak şekilde korunur.

---

## 2. Prerequisites

LAB'ı çalıştırmadan önce bilgisayarınızda şunların kurulu olması gerekir:

- **Docker Desktop** veya kurumunuz tarafından onaylanan eşdeğer bir Docker ortamı
- **Docker Compose V2**
- **Git**
- Bir **web browser** (Chrome, Edge, Firefox vb.)
- **Visual Studio Code** (önerilir, zorunlu değildir)

### Python, NumPy, Pandas, Scikit-learn, SHAP kurmanıza gerek yok

Tüm Python bağımlılıkları `uv` ile, **yalnızca Docker image'ı build edilirken** kurulur. LAB08,
`shap` ve `ipywidgets`'i proje bağımlılıklarına **yeni olarak** ekler — bu nedenle **Docker
image'ının bu LAB için yeniden build edilmesi gerekir** (Bölüm 6'daki `--build` bayrağı bunu
otomatik yapar).

---

## 3. Dataset Download Instructions

> **Not:** Veri dosyası bu proje tarafından otomatik olarak indirilmez.

### DataCo SMART Supply Chain

Bu, LAB02-LAB07'de kullanılan veri kümelerinden **farklı, yeni bir veri kümesidir**.

- **Kaggle bağlantısı:** [https://www.kaggle.com/datasets/shashwatwork/dataco-smart-supply-chain-for-big-data-analysis](https://www.kaggle.com/datasets/shashwatwork/dataco-smart-supply-chain-for-big-data-analysis)
- **Orijinal kaynak:** [Mendeley Data](https://data.mendeley.com/datasets/8gx2fvg2k6/5) (DOI `10.17632/8gx2fvg2k6.5`)
- **Beklenen hedef konum:** `data/dataco_supply_chain/DataCoSupplyChainDataset.csv`

**Adımlar:**

1. Yukarıdaki Kaggle bağlantısını tarayıcınızda açın.
2. Eğer dosya henüz görünmüyorsa Kaggle hesabınıza giriş yapın.
3. **Download** butonuna tıklayarak ZIP arşivini indirin.
4. İndirilen ZIP arşivini çıkarın (extract).
5. Arşivden çıkan ana CSV dosyasının adının `DataCoSupplyChainDataset.csv` olduğunu doğrulayın
   (varsa `DescriptionDataCoSupplyChain.csv` data dictionary dosyasını da aynı klasöre
   kopyalayabilirsiniz — opsiyoneldir, notebook tarafından kullanılmaz).
6. Bu dosyayı proje kök dizininde `data/dataco_supply_chain/` klasörünün içine kopyalayın
   (klasör yoksa oluşturun).

> **Teknik not:** Bu CSV dosyası **latin-1 encoding** ile kaydedilmiştir (UTF-8 değil). Notebook,
> bunu `src/data_loading.py` üzerinden doğru şekilde okur — dosyayı kendiniz bir metin
> düzenleyicide açarsanız, encoding'i doğru ayarlamadığınız takdirde bozuk karakterler
> görebilirsiniz.

> **Orijinal CSV içeriğini değiştirmeyin.** LAB08, bu dosyayı yalnızca okur.

---

## 4. Expected Directory Structure

```text
ml-labs/
├── data/
│   └── dataco_supply_chain/
│       ├── DataCoSupplyChainDataset.csv
│       └── DescriptionDataCoSupplyChain.csv   (opsiyonel)
├── labs/
│   ├── lab02/ ... lab07/
│   └── lab08/
│       ├── lab08_feature_engineering_explainability.ipynb
│       └── README.md
├── doc/
│   ├── lab02_student_guide.md ... lab07_student_guide.md
│   └── lab08_student_guide.md
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

> **LAB02-LAB07'den birini zaten tamamladıysanız**, bu adımı atlayabilirsiniz — `git pull` ile
> güncel dosyaları alıp Bölüm 6'ya geçin.

1. Bir terminal açın.
2. Projeyi klonlamak istediğiniz klasöre gidin.
3. Aşağıdaki komutu çalıştırın:

   ```bash
   git clone https://github.com/Burakkylmz/ml-labs.git
   ```

4. `cd ml-labs` ile klasöre girin.
5. Bölüm 3'teki dataset dosyasını `data/dataco_supply_chain/` içine yerleştirin.

---

## 6. Running the LAB with Docker

1. Bir terminal açın ve proje kök dizinine (`ml-labs/`) geçin.
2. **Docker Desktop'ın çalışır durumda olduğundan emin olun.**
3. Aşağıdaki komutu çalıştırın:

   ```bash
   docker compose up --build -d
   ```

   LAB08 için bu, `shap`/`ipywidgets` paketlerinin kurulmasını içeren bir **yeniden-build**
   tetikler (önceki LAB'lardan kalan image varsa) — biraz zaman alabilir.

4. Container durumunu kontrol edin:

   ```bash
   docker compose ps
   ```

5. JupyterLab erişim token'ını görmek için:

   ```bash
   docker compose logs ml-lab
   ```

   ```text
   http://127.0.0.1:8888/lab?token=<uzun-bir-token-degeri>
   ```

---

## 7. Accessing JupyterLab

1. Tarayıcınızı açın, adres çubuğuna `http://localhost:8888` yazın.
2. Gerekirse `docker compose logs ml-lab` çıktısından aldığınız **token**'ı girin.
3. Soldaki dosya gezgininde `labs` → `lab08` klasörüne girin.
4. `lab08_feature_engineering_explainability.ipynb` dosyasına çift tıklayın.

---

## 8. Working with Notebook Cells

- Bir Code Cell'i çalıştırmak için **`Shift + Enter`** kullanın.
- Değişiklikleri kaydetmek için **`Ctrl + S`**.

### Önemli — Bu notebook 164 hücreden oluşur ve sıkı bir sıralı bağımlılık zinciri içerir

- Section 2'de oluşturulan `train_df`/`validation_df`/`test_df` ve group-aware split, **bütün
  sonraki section'larda** yeniden kullanılır.
- Section 3'teki `create_datetime_features()`/`create_interaction_features()` fonksiyonları ve
  bunların ürettiği kolonlar, Section 4-7'nin feature matrislerinin temelidir.
- Section 4'teki `preprocessor`/`numerical_features`/`categorical_features`/
  `k_best_selector` nesneleri, Section 5-6'da **doğrudan** yeniden kullanılır.
- Section 5'teki `fitted_pipelines["E03"]`, Section 6'nın **tüm** explainability analizinin
  (model-based importance, permutation importance, SHAP) temelidir.

Hücreleri sırayla çalıştırmazsanız, sonraki hücrelerde `NameError` alırsınız — bu durumda
**Run → Run All Cells** en güvenli çözümdür. Notebook'un tam çalıştırılması (Advanced Challenges
dahil), donanımınıza bağlı olarak **birkaç dakika** sürebilir (SHAP hesaplamaları ve `RFE`/
`SelectFromModel` en yavaş hücrelerdir).

---

## 9. LAB Sections

1. **Feature Engineering Fundamentals & Dataset** (15 dk) — kavramsal farklar, güvenli veri
   yükleme, dataset genel yapısı.
2. **Data Audit, Privacy & Target Leakage** (20 dk) — 44 kolonluk Feature Audit, `Delivery
   Status` leakage demonstrasyonu (`INVALID — TARGET LEAKAGE`), group-aware kronolojik split.
3. **Feature Engineering Techniques** (20 dk) — baseline feature set, Date-Time/Cyclical/
   Interaction feature'lar, feature quality validation.
4. **Feature Selection Methods** (20 dk) — `VarianceThreshold`, correlation analizi,
   `SelectKBest`, Mutual Information, `SelectFromModel`. **Break (10 dk)** bu section'ın
   sonundadır.
5. **Comparative Feature Benchmarking** (25 dk) — E01 (Baseline)/E02 (Engineered)/E03 (Selected)
   karşılaştırması, 7 görselleştirme.
6. **Feature Importance & SHAP Explainability** (25 dk) — Model-Based Importance, Permutation
   Importance, SHAP (global bar/beeswarm, local waterfall).
7. **Final Workshop & Engineering Evaluation** (15 dk) — 3 senaryo, Feature Engineering &
   Explainability Report.

Notebook sonunda, deneyimli katılımcılar için beş **opsiyonel Advanced Challenge** (RFE, Embedded
Selection, Feature Ablation, Grouped Permutation Importance, SHAP Stability) bulunur.

---

## 10. Stopping the LAB

```bash
docker compose down
```

Bind mount sayesinde, notebook içinde kaydettiğiniz değişiklikler container durdurulsa/silinse
bile bilgisayarınızda kalıcı olarak saklanır.

---

## 11. Troubleshooting

| Problem | Çözüm |
|---|---|
| **Docker Desktop çalışmıyor** | Docker Desktop'ı başlatın, sistem tepsisindeki ikonun "running" olmasını bekleyin. |
| **Port 8888 kullanımda** | `docker compose down` ile önceki container'ı durdurun, tekrar deneyin. |
| **Dataset `FileNotFoundError`** | `data/dataco_supply_chain/DataCoSupplyChainDataset.csv` dosyasının Bölüm 3'teki adımlara göre doğru konumda olduğunu kontrol edin. |
| **`UnicodeDecodeError` (dataset'i kendiniz açarken)** | Dosya latin-1 encoding ile kaydedilmiştir, UTF-8 değil. Notebook bunu doğru okur; kendi başınıza açıyorsanız encoding'i `latin-1` olarak ayarlayın. |
| **SHAP hesaplama hücreleri uzun sürüyor** | Section 6'daki SHAP hücreleri (`shap_background_size=100`, `shap_sample_size=500`) birkaç saniye sürebilir — bu normaldir; tüm 180,519 satır üzerinde hesaplama yapılmaz. |
| **`TqdmWarning`/`ipywidgets` ile ilgili bir uyarı görüyorsanız** | Güncel `Dockerfile`/bağımlılıklar bu uyarıyı zaten önler (`ipywidgets` kurulu). `docker compose up --build -d` ile image'ı yeniden oluşturun. |
| **`NameError`** (örn. `train_df`, `preprocessor`, `fitted_pipelines` tanımlı değil) | Section 2-5'teki hücreler sırayla çalıştırılmadı. **Run → Run All Cells** kullanın. |
| **Yanlış Notebook Kernel** | **Kernel → Change Kernel** menüsünden `Python 3 (ipykernel)`'i seçin. |
| **Notebook değişiklikleri kaydedilemiyor** | Tarayıcı sekmesini yenileyin (F5) ve tekrar `Ctrl + S` deneyin; `docker compose logs ml-lab` ile container loglarını kontrol edin. |
