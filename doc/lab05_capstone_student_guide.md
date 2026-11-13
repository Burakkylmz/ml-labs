# LAB05 Capstone Student Guide — Multiple Linear Regression

Bu rehber, `ml-labs` projesindeki **LAB05 Capstone: Multiple Linear Regression** çalışmasını
kendi bilgisayarınızda Docker üzerinden nasıl çalıştıracağınızı adım adım açıklar.

**Eğitim süresi:** 6 oturum × 150 dakika ≈ 15 saat

> Bu Capstone, **LAB02-LAB06**'yı tamamlamış katılımcılar için tasarlanmıştır ve mevcut
> **LAB05**'in (`lab05_supervised_regression.ipynb`, Northwind verisi) **yerine geçmez** —
> tamamen ayrı, bağımsız bir çalışmadır. Önceki LAB'ları tamamlamadıysanız önce
> [`doc/lab02_student_guide.md`](lab02_student_guide.md) ile başlayın.

---

## 1. LAB Overview

Bu Capstone'da, King County (Seattle bölgesi) konut satış verisini kullanarak **Ordinary Least
Squares (OLS) Multiple Linear Regression** ile bir **Historical Property Valuation** modeli
geliştireceksiniz. Bu, sıradan bir regression tutorial'ı değildir — veri kalitesi
değerlendirmesinden, kapsamlı EDA'ya, feature engineering'e, **multicollinearity analizine**,
OLS istatistiksel çıkarımına (hypothesis testing, residual diagnostics, influence analizi) ve
nihai model seçimine kadar **tam bir uygulamalı regresyon analizi iş akışı**dır.

- **Dataset:** King County House Sales (`data/king_county_house_sales/kc_house_data.csv`)
- **Target:** `price`
- **Yöntem:** `statsmodels` ile OLS (hem tahmin hem istatistiksel çıkarım için)

> **Önemli sınırlama:** Bu çalışma gerçek zamanlı bir production valuation sistemi değildir;
> 2014-2015 King County verisine özgüdür.

### Oturum Planı

| Oturum | İçerik | Section'lar |
|---|---|---|
| 1 | Problem Definition & Data Quality | 01–05 |
| 2 | Univariate EDA & Distribution Analysis | 06–09 |
| 3 | Bivariate & Multivariate EDA | 10–14 |
| 4 | Feature Engineering & Multicollinearity | 15–19 |
| 5 | OLS Regression & Statistical Diagnostics | 20–24 |
| 6 | Model Refinement & Final Evaluation | 25–30 |

---

## 2. Prerequisites

LAB'ı çalıştırmadan önce bilgisayarınızda şunların kurulu olması gerekir:

- **Docker Desktop** veya kurumunuz tarafından onaylanan eşdeğer bir Docker ortamı
- **Docker Compose V2**
- **Git**
- Bir **web browser**
- **Visual Studio Code** (önerilir, zorunlu değildir)

### Python, NumPy, Pandas, Scikit-learn, Statsmodels, Seaborn kurmanıza gerek yok

Bu projede tüm Python bağımlılıkları `uv` ile yönetilir ve yalnızca Docker image'ı build
edilirken kurulur. Bu Capstone için **iki yeni bağımlılık** (`seaborn`, `statsmodels`) projeye
eklenmiştir — bunlar da diğer bağımlılıklar gibi otomatik olarak Docker image'ına kurulacaktır;
sizin ayrıca bir şey yüklemeniz gerekmez.

---

## 3. Dataset Download Instructions

> **Not:** Veri dosyası bu proje tarafından otomatik olarak indirilmez ve repository'ye commit
> edilmez.

### King County House Sales

- **Kaggle bağlantısı:** [https://www.kaggle.com/datasets/harlfoxem/housesalesprediction](https://www.kaggle.com/datasets/harlfoxem/housesalesprediction)
- **Beklenen hedef konum:** `data/king_county_house_sales/kc_house_data.csv`

**Adımlar:**

1. Yukarıdaki Kaggle bağlantısını tarayıcınızda açın.
2. Eğer dosya henüz görünmüyorsa Kaggle hesabınıza giriş yapın.
3. **Download** butonuna tıklayarak ZIP arşivini indirin.
4. İndirilen ZIP arşivini çıkarın (extract).
5. Arşivden çıkan dosyanın adının `kc_house_data.csv` olduğunu doğrulayın.
6. Bu dosyayı proje kök dizininde `data/king_county_house_sales/` klasörünün içine kopyalayın
   (klasör yoksa oluşturun). Sonuçta dosya şu yolda olmalıdır:
   `data/king_county_house_sales/kc_house_data.csv`.

> **Orijinal CSV içeriğini değiştirmeyin.** Notebook bu dosyayı yalnızca okur.

> Diğer LAB'lardan kalan dataset klasörleri (`data/ecommerce_shipping/`, `data/northwind/`) bu
> Capstone için **gerekli değildir**. Dokunmanıza gerek yoktur — silmeniz de gerekmez.

---

## 4. Expected Directory Structure

```text
ml-labs/
├── data/
│   └── king_county_house_sales/
│       └── kc_house_data.csv
├── labs/
│   ├── lab02/ ... lab06/
│   └── lab05_capstone/
│       ├── lab05_capstone_multiple_linear_regression.ipynb
│       └── README.md
├── doc/
│   ├── lab02_student_guide.md ... lab06_student_guide.md
│   └── lab05_capstone_student_guide.md
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

> **Önceki LAB'ları zaten tamamladıysanız** ve `ml-labs/` klasörünüz bilgisayarınızda
> halihazırda varsa, bu adımı atlayabilirsiniz — doğrudan bu klasörün içinde `git pull`
> çalıştırarak Capstone dosyalarının güncel sürümünü alabilirsiniz, ardından Bölüm 6'ya geçin.

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

5. Bölüm 3'te indirdiğiniz dataset dosyasını, Bölüm 4'te gösterilen klasör yapısına göre bu
   klasörün içine yerleştirin (`data/king_county_house_sales/kc_house_data.csv`).
6. Bu rehberin kalan adımlarını (Docker ile çalıştırma dahil) her zaman bu `ml-labs/` klasörünün
   içinden çalıştıracaksınız.

---

## 6. Running the LAB with Docker

1. Bir terminal açın ve proje kök dizinine (`ml-labs/`) geçin.
2. **Docker Desktop'ın çalışır durumda olduğundan emin olun.**
3. Aşağıdaki komutu çalıştırın:

   ```bash
   docker compose up --build -d
   ```

   Bu Capstone, `pyproject.toml`/`uv.lock`'a `seaborn` ve `statsmodels` eklediği için, **ilk
   çalıştırmada** image'ın yeniden build edilmesi önceki LAB'lara göre biraz daha uzun
   sürebilir (yeni paketlerin indirilmesi nedeniyle). Sonraki çalıştırmalar, Docker'ın katman
   önbelleğinden yararlanarak hızlı olacaktır.

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

---

## 7. Accessing JupyterLab

1. Tarayıcınızı açın.
2. Adres çubuğuna şunu yazın:

   ```text
   http://localhost:8888
   ```

3. Karşınıza bir giriş ekranı gelirse, loglardan aldığınız **token** değerini girin.
4. JupyterLab açıldığında, `labs` klasörüne, ardından `lab05_capstone` klasörüne girin.
5. `lab05_capstone_multiple_linear_regression.ipynb` dosyasına çift tıklayarak notebook'u açın.

---

## 8. Working with Notebook Cells

### Temel kullanım

- Bir Code Cell'i çalıştırmak için hücreye tıklayın ve **`Shift + Enter`** tuşlarına basın.
- Hücre çalıştırıldıktan sonra, çıktısı **hücrenin hemen altında** görüntülenir.
- Grafikler (histogram, scatter, correlation heatmap, pairplot, spatial map, residual
  diagnostics, Cook's Distance vb.) hücrenin altında görsel olarak gösterilir.
- Değişiklikleri kaydetmek için **`Ctrl + S`**.

### Önemli — Bu Notebook Çok Uzun ve Sıralıdır

Bu Capstone **313 hücre, 30 section, 6 oturum** içerir ve **tamamen sıralı bir bağımlılık
zincirine** sahiptir: Section 04'teki `train_model_df`/`val_model_df`/`test_model_df`, Section
19'daki `GRADE_MEAN`/`AGE_MEAN`/`final_numeric_features`, Section 20'deki `initial_ols_model`
ve `base_ols_terms`, Section 25'teki `train_without_point` — bunların hepsi **sonraki
section'larda tekrar kullanılır**. Bir hücreyi atlarsanız veya sırayı bozarsanız, çok daha
sonraki bir section'da `NameError` alabilirsiniz.

**Bu nedenle bu Capstone'u birkaç oturuma yayarken (örn. her gün bir oturum), her oturumun
başında notebook'u `Run → Run All Cells` ile baştan çalıştırmanız önerilir** — Docker'ın bind
mount yapısı sayesinde kaydedilmiş çıktılar korunur, ama kernel'i her yeni oturumda yeniden
başlatmak (`Kernel → Restart Kernel`) ve tüm hücreleri yeniden çalıştırmak en güvenli
yaklaşımdır.

---

## 9. LAB Sections

### Session 1 — Problem Definition & Data Quality (Section 01-05)

İş problemi tanımı, dataset şema doğrulaması, veri kalitesi/anomali değerlendirmesi (otomatik
silme yok), gün-sınırına hizalı kronolojik split, leakage & integrity checkpoint.

### Session 2 — Univariate EDA & Distribution Analysis (Section 06-09)

`price` dağılım analizi (log transform karşılaştırması dahil), 13 sayısal feature için tekrar
kullanılabilir fonksiyonlarla özet istatistik/grafik, kategorik/ordinal analiz, bağımsız EDA
workshop'u.

### Session 3 — Bivariate & Multivariate EDA (Section 10-14)

Feature-target scatter + LOWESS, Pearson/Spearman korelasyon (ve korelasyonun sınırlamaları),
pairplot/spatial analiz, gerçek bir confounding örneği (`condition`/`grade`), hypothesis
register.

### Session 4 — Feature Engineering & Multicollinearity (Section 15-19)

Sekiz domain-based feature, log transformation, dummy variable trap canlı demosu, **zorunlu
Multicollinearity bölümü** (perfect/high multicollinearity, VIF, Condition Number), üç katmanlı
feature selection.

### Session 5 — OLS Regression & Statistical Diagnostics (Section 20-24)

Baseline + Initial OLS, `statsmodels` summary'nin tam yorumu, hypothesis testing (t-test, joint
F-test), dört formal varsayım testi (Breusch-Pagan, Jarque-Bera, Durbin-Watson, Ramsey RESET),
OLS Diagnostic Report.

### Session 6 — Model Refinement & Final Evaluation (Section 25-30)

Influence diagnostics (Cook's Distance, sensitivity analysis), HC3 robust standard errors, altı
alternatif specification karşılaştırması (log-target dahil, retransformation bias düzeltmesiyle),
model seçimi, **tek seferlik** final test değerlendirmesi, Final Capstone Report.

---

## 10. Stopping the LAB

```bash
docker compose down
```

Proje kök dizini bind-mount edildiği için, kaydettiğiniz tüm değişiklikler container
durdurulsa/silinse bile bilgisayarınızda kalıcı olarak saklanır.

---

## 11. Troubleshooting

| Problem | Çözüm |
|---|---|
| **Docker Desktop çalışmıyor** | Docker Desktop'ı başlatın ve "running" durumunu bekleyin. |
| **Dataset `FileNotFoundError`** | Bölüm 3'teki adımlara göre `data/king_county_house_sales/kc_house_data.csv` dosyasının doğru konumda olduğunu kontrol edin. |
| **Python `ModuleNotFoundError: statsmodels` veya `seaborn`** | `docker compose up --build -d` komutunu `--build` bayrağıyla tekrar çalıştırın — image'ın güncel `pyproject.toml`/`uv.lock` ile yeniden build edildiğinden emin olun. |
| **`NameError` (örn. `train_model_df`, `GRADE_MEAN`, `initial_ols_model` tanımlı değil)** | Bu notebook'ta hücreler **son derece sıralıdır** (bkz. Bölüm 8). **Kernel → Restart Kernel and Run All Cells** ile baştan çalıştırın. |
| **`SingularMatrixWarning` (Ramsey RESET testi, Section 23)** | Bu **beklenen** bir uyarıdır — notebook içinde bu uyarının neden oluştuğu (ölçek-hassasiyeti, gerçek bir rank sorunu değil) ve test sonucunun geçerli olduğu ayrıca doğrulanmıştır. Hata değildir, atlamayın — açıklamasını okuyun. |
| **Notebook çok uzun sürüyor (`Run All Cells`)** | Bu normaldir — pairplot, LOWESS ve çoklu OLS fit'leri nedeniyle tam çalıştırma birkaç dakika sürebilir. Hücreleri tek tek çalıştırırken sabırlı olun. |
| **`ValueError` / encoding veya pipeline hatası** | Genellikle bir hücrenin atlanmış olmasından kaynaklanır. **Kernel → Restart Kernel and Run All Cells** ile temiz bir çalıştırma yapın. |
| **Notebook değişiklikleri kaydedilemiyor** | Bind mount sayesinde kaydetme normalde sorunsuz çalışır. Sorun sürerse `docker compose logs ml-lab` ile container loglarını kontrol edin. |
