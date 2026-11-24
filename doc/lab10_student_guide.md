# LAB10 Student Guide — Time Series Fundamentals & Forecasting Baselines

Bu rehber, `ml-labs` projesindeki **LAB10: Time Series Fundamentals & Forecasting Baselines**
çalışmasını kendi bilgisayarınızda Docker üzerinden nasıl çalıştıracağınızı adım adım açıklar.

**Eğitim süresi:** 150 dakika, artı isteğe bağlı Advanced Challenges

> Bu LAB, LAB02-LAB09'dan **farklı bir alana** geçiştir: klasik tabular Machine Learning'den
> **Time Series Forecasting**'e. LAB08/LAB09'daki dataset'i (DataCo Supply Chain) kullanmaz —
> yeni bir dataset (Bike Sharing) ile çalışacaksınız.

---

## 1. LAB Overview

Bu LAB'da, günlük bisiklet kiralama verisi üzerinde zaman serisi kavramlarını (trend,
seasonality, autocorrelation), leakage-safe bir chronological evaluation protokolü, ve üç basit
ama güçlü **baseline forecasting yöntemini** (Naive, Seasonal Naive, Moving Average)
geliştireceksiniz. LAB sonunda şu konuları uygulamış olacaksınız:

- **Time Series vs Tabular Data**, **Forecast Origin / Forecast Horizon**
- **Chronological Train/Validation/Protected-Test Split**
- **Naive, Seasonal Naive, Moving Average Forecasting**
- **MAE, RMSE, WAPE, MASE**
- **Rolling-Origin Evaluation (Backtesting)**

| Dataset | Kullanım Alanı |
|---|---|
| **Bike Sharing — day.csv** (Washington D.C.) | Ana LAB: trend/seasonality analizi, baseline forecasting, rolling-origin evaluation |
| **Bike Sharing — hour.csv** | Yalnızca Advanced Challenge 4 (opsiyonel, saatlik keşif) |

> **Önemli — Korunmuş Test Seti:** `2012-11-01` - `2012-12-31` dönemi (**Protected Test
> Period**) bu LAB boyunca **hiçbir analizde kullanılmaz** — ne grafikte, ne metrikte, ne de
> baseline seçiminde. LAB09'daki gibi bir "gate" mekanizması burada yoktur çünkü bu LAB'da test
> seti üzerinde **hiçbir evaluation zaten yapılmamaktadır** — korunma, kodun test period'a hiç
> erişmemesiyle sağlanır. Bu dönem LAB12 için saklanmaktadır.

---

## 2. Prerequisites

- **Docker Desktop**, **Docker Compose V2**, **Git**, bir **web browser**.
- **Visual Studio Code** (önerilir).

### Yeni bir bağımlılık eklenmedi

LAB10, mevcut teknoloji stack'ini (pandas, numpy, matplotlib, pyyaml) kullanır — **yeni bir
Python paketi eklenmedi**. XGBoost/LightGBM/SHAP (önceki LAB'lardan) bu LAB'da **kullanılmaz**.
Eğer önceki bir LAB'ı zaten Docker ile çalıştırdıysanız, image'ı yeniden build etmenize gerek
yoktur (ama `docker compose up --build -d` çalıştırmak her zaman güvenlidir).

---

## 3. Dataset Download Instructions

1. Kaggle'dan [marklvl/bike-sharing-dataset](https://www.kaggle.com/datasets/marklvl/bike-sharing-dataset)
   sayfasına gidin (veya orijinal kaynak: [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/275/bike-sharing-dataset)).
2. Dataset'i indirin, zip'i açın.
3. `day.csv` ve `hour.csv` dosyalarını `data/bike_sharing/` klasörüne yerleştirin:

```text
data/bike_sharing/
├── day.csv
└── hour.csv
```

> **Orijinal CSV içeriğini değiştirmeyin.** Dataset otomatik indirilmez — bu klasörü manuel
> hazırlamanız gerekir. `day.csv` eksikse notebook, Section 2'de anlaşılır bir
> `FileNotFoundError` ile durur (sessizce devam etmez).

---

## 4. Expected Directory Structure

```text
ml-labs/
├── data/
│   └── bike_sharing/
│       ├── day.csv
│       └── hour.csv
├── labs/
│   ├── lab02/ ... lab09/
│   └── lab10/
│       ├── lab10_time_series_fundamentals.ipynb
│       ├── README.md
│       └── artifacts/              (notebook çalıştırıldığında otomatik dolar)
│           ├── .gitignore
│           ├── forecasting_metadata.json
│           ├── split_metadata.json
│           ├── baseline_results.csv
│           └── validation_forecasts.csv
├── doc/
│   └── lab10_student_guide.md
├── config/settings.yaml
├── pyproject.toml / uv.lock
├── Dockerfile / compose.yaml
```

> `labs/lab10/artifacts/` içindeki dosyalar **notebook'un kendisi tarafından üretilir** — manuel
> oluşturmanıza gerek yoktur. Bu klasör `.gitignore` ile korunur, git'e commit edilmez.

---

## 5. Cloning the Repository from GitHub

> **LAB02-LAB09'dan birini zaten tamamladıysanız**, `git pull` ile güncel dosyaları alıp
> Bölüm 6'ya geçin.

1. `git clone https://github.com/Burakkylmz/ml-labs.git`
2. `cd ml-labs`
3. Bölüm 3'teki dataset dosyalarını yerleştirin (zaten yoksa).

---

## 6. Running the LAB with Docker

```bash
docker compose up --build -d
docker compose ps
docker compose logs ml-lab
```

Loglardaki token ile `http://localhost:8888` adresine giriş yapacaksınız.

---

## 7. Accessing JupyterLab

1. `http://localhost:8888` adresini açın, token'ı girin.
2. `labs` → `lab10` klasörüne girin.
3. `lab10_time_series_fundamentals.ipynb` dosyasını açın.

---

## 8. Working with Notebook Cells

- **`Shift + Enter`** ile hücre çalıştırın, **`Ctrl + S`** ile kaydedin.

### Önemli — Bu notebook 92 hücreden oluşur ve kümülatif bir bağımlılık zinciri içerir

- Section 2'deki `daily_series` (tarih-indeksli Pandas Series), **bütün sonraki section'ların**
  temelidir.
- Section 4'teki `train_series` / `validation_series` / `test_series` ve `split_result`,
  Section 5-7'de doğrudan yeniden kullanılır.
- Section 5'teki `naive_forecast()`, `seasonal_naive_forecast()`, `moving_average_forecast()`
  fonksiyonları; Section 6'daki `evaluate_forecast()` ve sabit `MASE_DENOMINATOR`; Section 7'deki
  `evaluate_baselines()` — bunların hepsi birbirine bağımlıdır ve **tanımlandıkları sıradan önce
  çağrılamaz**.
- Section 7'nin sonunda `labs/lab10/artifacts/` altındaki 4 dosya **gerçek çalıştırma sonucunda**
  üretilir (`forecasting_metadata.json`, `split_metadata.json`, `baseline_results.csv`,
  `validation_forecasts.csv`).

Hücreleri sırayla çalıştırmazsanız `NameError` alırsınız — **Run → Run All Cells** en güvenli
çözümdür. Bu LAB'daki hiçbir hücre uzun sürmez (rastgele arama/model eğitimi yoktur) — tüm
notebook, Advanced Challenges dahil, genellikle **1 dakikanın altında** tamamlanır.

### Beklenen (Hata Değil) İki Bulgu

- **Validation döneminin son 5 günü (2012-10-27 → 2012-10-31) Rolling-Origin Evaluation'a dahil
  değildir.** Section 7'de bu açıkça raporlanır — sabit 14 günlük, 4 origin'lik protokolün
  tasarım sonucu budur, bir hata değildir.
- **Seasonal Naive, yüksek haftalık autocorrelation'a (Section 3) rağmen genel olarak en iyi
  baseline çıkmaz** — Naive baseline daha düşük Mean Fold MAE elde eder. Section 7'deki "Key,
  Honest Finding" bu sonucu ve nedenini (validation döneminin düşüş trendinde olması) açıklar.
  Bu, notebook'un bilinçli olarak gösterdiği gerçek bir sonuçtur, düzeltilmesi gereken bir hata
  değildir.

---

## 9. LAB Sections

1. **Time Series & Forecasting Fundamentals** (15 dk) — kavramlar, sentetik demo, forecast
   origin/horizon.
2. **Dataset Audit & Time Index Preparation** (20 dk) — yükleme, kalite kontrolleri, tarih
   parse, `daily_series`, time index validation, protected period farkındalığı.
3. **Trend, Seasonality & Autocorrelation** (25 dk) — sadece Training Period üzerinde: rolling
   mean, haftalık/aylık pattern, lag 1/7/14/28 autocorrelation (5 görselleştirme).
4. **Forecasting Problem & Temporal Splitting** (20 dk) — split doğrulama, leakage discussion,
   split timeline grafiği.
5. **Naive & Seasonal Naive Forecasting** (25 dk) — üç baseline fonksiyonu, ilk forecast demo'su
   ve karşılaştırma grafiği.
6. **Forecasting Metrics & Error Analysis** (20 dk) — MAE/RMSE/WAPE/MASE fonksiyonları, sabit
   MASE denominator, demo pencere karşılaştırması.
7. **Rolling-Origin Evaluation & Workshop** (15 dk) — 4 origin üzerinde backtesting, fold-level
   + aggregate metrikler (Mean Fold vs Pooled), 6 görselleştirme, workshop soruları, artifact
   dosyalarının yazılması.

Notebook sonunda, deneyimli katılımcılar için dört **opsiyonel Advanced Challenge** (Forecast
Horizon Sensitivity, Seasonal Period Sensitivity, Rolling vs Expanding Window, Hourly Demand
Exploration) bulunur — hiçbiri test seti **kullanmaz**.

---

## 10. Stopping the LAB

```bash
docker compose down
```

`labs/lab10/artifacts/` içindeki dosyalar (bind mount sayesinde) bilgisayarınızda kalıcı olarak
saklanır.

---

## 11. Troubleshooting

| Problem | Çözüm |
|---|---|
| **Docker Desktop çalışmıyor / çöktü** | Docker Desktop'ı yeniden başlatın, sistem tepsisindeki ikonun "running" olmasını bekleyin (bazen 1-2 dakika sürebilir). Ardından `docker compose up -d` tekrar deneyin. |
| **`FileNotFoundError: Required dataset file not found`** | `data/bike_sharing/day.csv` (ve/veya `hour.csv` Advanced Challenge 4 için) yerleştirilmemiş. Bölüm 3'teki adımları tekrar kontrol edin. |
| **`NameError`** (örn. `daily_series`, `train_series`, `evaluate_forecast` tanımlı değil) | Section 2-6'daki hücreler sırayla çalıştırılmadı. **Run → Run All Cells** kullanın. |
| **`ModuleNotFoundError: No module named 'data_loading'`** | Notebook'un ilk kod hücresi `PROJECT_ROOT`'u `pyproject.toml` dosyasını yukarı doğru arayarak bulur; bu hücre atlanmış veya değiştirilmiş olabilir. Notebook'u baştan çalıştırın. |
| **Validation'ın son 5 günü sonuçlarda görünmüyor** | Bu **beklenen davranıştır** — Bölüm 8'deki "Beklenen (Hata Değil) İki Bulgu" kısmına bakın. |
| **Seasonal Naive, Naive'den daha kötü sonuç veriyor** | Bu da **beklenen, gerçek bir bulgudur** — aynı bölüme bakın; Section 7'nin "Key, Honest Finding" kısmı nedenini açıklar. |
| **Yanlış Notebook Kernel** | **Kernel → Change Kernel** menüsünden `Python 3 (ipykernel)`'i seçin. |
| **Notebook değişiklikleri kaydedilemiyor** | Tarayıcı sekmesini yenileyin (F5), `Ctrl + S` ile tekrar deneyin; `docker compose logs ml-lab` ile container loglarını kontrol edin. |
