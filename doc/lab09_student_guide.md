# LAB09 Student Guide — Model Selection, Hyperparameter Optimization & Reproducibility

Bu rehber, `ml-labs` projesindeki **LAB09: Model Selection, Hyperparameter Optimization &
Reproducibility** çalışmasını kendi bilgisayarınızda Docker üzerinden nasıl çalıştıracağınızı
adım adım açıklar.

**Eğitim süresi:** 150 dakika, artı isteğe bağlı Advanced Challenges

> Bu LAB, özellikle **LAB07** ve **LAB08**'in devamıdır. Bu LAB'ları tamamlamadıysanız önce
> [`doc/lab07_student_guide.md`](lab07_student_guide.md) ve
> [`doc/lab08_student_guide.md`](lab08_student_guide.md) rehberlerini takip edin.

---

## 1. LAB Overview

Bu LAB'da, LAB08'de seçtiğiniz feature strategy ve split'i **yeniden kurup doğrulayarak**,
`GridSearchCV`/`RandomizedSearchCV` ile kontrollü bir hyperparameter optimization süreci
geliştirecek, MLflow kullanmadan (yalnızca Python/Pandas/JSON/CSV ile) bir Experiment Tracking
mekanizması inşa edecek ve **korunmuş test setini** açık bir execution gate arkasında, bilinçli
bir şekilde, **bir kez** değerlendireceksiniz.

LAB sonunda şu konuları uygulamış olacaksınız:

- **Model Parameters vs. Hyperparameters**
- **Group-Aware Temporal Cross-Validation** (custom fold generator)
- **GridSearchCV & RandomizedSearchCV**
- **Computational Budget Management**
- **Experiment Tracking & Reproducibility** (MLflow'suz)
- **Gated Final Test Evaluation**

| Dataset | Kullanım Alanı |
|---|---|
| **DataCo SMART Supply Chain** (LAB08 ile aynı) | Hyperparameter optimization, experiment tracking, final test evaluation |

> **Önemli — Korunmuş Test Seti:** LAB08'in `test_df`'i bu LAB'a kadar **hiç** kullanılmadı. Bu
> LAB'da da, `RUN_FINAL_TEST_EVALUATION` adlı bir flag **varsayılan olarak `False`**'tur — yani
> notebook'u normal şekilde (**Run → Run All**) çalıştırdığınızda test seti **otomatik olarak
> değerlendirilmez**. Bu flag'i bilinçli olarak `True` yapmadığınız sürece, test sonuçları
> "Not Evaluated" olarak görünür — bu bir hata değildir.

---

## 2. Prerequisites

- **Docker Desktop**, **Docker Compose V2**, **Git**, bir **web browser**.
- **Visual Studio Code** (önerilir).

### Yeni bir bağımlılık eklenmedi

LAB09, mevcut teknoloji stack'ini (LAB08'den kalan `shap`/`xgboost`/`lightgbm` dahil) kullanır —
**yeni bir Python paketi eklenmedi**. Eğer LAB08'i zaten Docker ile çalıştırdıysanız, image'ı
**yeniden build etmenize gerek yoktur** (ama `docker compose up --build -d` çalıştırmak her
zaman güvenlidir — değişiklik yoksa hızlıca tamamlanır).

---

## 3. Dataset Download Instructions

> **LAB08'i zaten tamamladıysanız**, bu adımı atlayabilirsiniz — aynı dosya
> (`data/dataco_supply_chain/DataCoSupplyChainDataset.csv`) kullanılır.

Eğer bu dosya henüz yoksa, [`doc/lab08_student_guide.md`](lab08_student_guide.md) Bölüm 3'teki
adımları izleyin (Kaggle: `shashwatwork/dataco-smart-supply-chain-for-big-data-analysis`).

> **Orijinal CSV içeriğini değiştirmeyin.**

---

## 4. Expected Directory Structure

```text
ml-labs/
├── data/
│   └── dataco_supply_chain/
│       └── DataCoSupplyChainDataset.csv
├── labs/
│   ├── lab02/ ... lab08/
│   └── lab09/
│       ├── lab09_model_selection_optimization.ipynb
│       ├── README.md
│       └── artifacts/              (notebook çalıştırıldığında otomatik dolar)
│           ├── .gitignore
│           ├── experiment_registry.csv
│           ├── experiment_metadata.json
│           ├── grid_search_results.csv
│           ├── randomized_search_results.csv
│           ├── model_comparison.csv
│           ├── fold_summary.csv
│           ├── selected_model_config.json
│           └── final_evaluation.json      (yalnızca gate açılırsa oluşur)
├── doc/
│   └── lab09_student_guide.md
├── config/settings.yaml
├── pyproject.toml / uv.lock
├── Dockerfile / compose.yaml
```

> `labs/lab09/artifacts/` içindeki CSV/JSON dosyaları **notebook'un kendisi tarafından üretilir**
> — bunları manuel oluşturmanıza gerek yoktur. Bu dosyalar `.gitignore` ile korunur, git'e
> commit edilmez.

---

## 5. Cloning the Repository from GitHub

> **LAB02-LAB08'den birini zaten tamamladıysanız**, `git pull` ile güncel dosyaları alıp
> Bölüm 6'ya geçin.

1. `git clone https://github.com/Burakkylmz/ml-labs.git`
2. `cd ml-labs`
3. Bölüm 3'teki dataset dosyasını yerleştirin (zaten yoksa).

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
2. `labs` → `lab09` klasörüne girin.
3. `lab09_model_selection_optimization.ipynb` dosyasını açın.

---

## 8. Working with Notebook Cells

- **`Shift + Enter`** ile hücre çalıştırın, **`Ctrl + S`** ile kaydedin.

### Önemli — Bu notebook 142 hücreden oluşur ve uzun süren arama hücreleri içerir

- Section 2'deki `train_df_cv`, `cv_folds`, `create_group_temporal_folds()` fonksiyonu, **bütün
  sonraki section'ların** temelidir.
- Section 3'teki `build_model_pipeline()`, `grid_search` nesnesi; Section 4'teki `random_search`
  nesnesi, Section 5-7'de **doğrudan yeniden kullanılır** (tekrar fit edilmez).
- **`GridSearchCV`/`RandomizedSearchCV` hücreleri her biri ~25-40 saniye sürebilir** (donanımınıza
  bağlı) — bu normaldir, search 24+1 veya 24+1 fit işlemi gerçekleştirir.
- Section 6'daki `RUN_ID`/`dataset_hash` gibi değerler, Section 7'nin `selected_model_config.json`
  ve (gate açıksa) `final_evaluation.json` dosyalarında kullanılır.

Hücreleri sırayla çalıştırmazsanız `NameError` alırsınız — **Run → Run All Cells** en güvenli
çözümdür. Notebook'un tam çalıştırılması (Advanced Challenges dahil), arama hücreleri nedeniyle
**birkaç dakika** sürebilir.

### Final Test Evaluation Gate — Nasıl Çalışır?

Section 7'de `RUN_FINAL_TEST_EVALUATION = config["lab09"]["evaluation"]["run_final_test"]`
satırını göreceksiniz. `config/settings.yaml`'da bu değer **`false`**'tur. Bunun anlamı:

- **Run All** yaptığınızda, final test evaluation hücreleri **otomatik olarak atlanır** (ekranda
  "Test set NOT accessed" mesajı görürsünüz) ve `final_evaluation.json` **oluşturulmaz**.
- Test setini **bilinçli olarak** değerlendirmek isterseniz, `config/settings.yaml`'daki
  `lab09.evaluation.run_final_test` değerini `true` yapıp notebook'u yeniden çalıştırmanız
  gerekir. **Bu, gerçek bir güvenlik mekanizması değildir** — sadece eğitim amaçlı bir execution
  guard'dır; amacı, test setinin yanlışlıkla/düşünmeden tekrar tekrar değerlendirilmesini
  önlemektir.
- Eğer `final_evaluation.json` zaten mevcutsa, notebook bunu tespit eder ve mevcut sonuçları
  gösterir — tekrar otomatik olarak yeniden değerlendirme yapmaz.

---

## 9. LAB Sections

1. **Model Optimization Fundamentals** (10 dk) — Parameters vs Hyperparameters.
2. **Cross-Validation Strategies** (25 dk) — LAB08 split review, Test Set Integrity, KFold
   ailesinin tanıtımı, **group-aware temporal CV fold generator**, Fold Summary + 3
   görselleştirme, Nested CV (kavramsal).
3. **GridSearchCV** (20 dk) — search cost formülü, 8 aday, sonuç analizi, heatmap.
4. **RandomizedSearchCV** (25 dk) — 4,800'lük bir uzaydan 8 örnek, search budget karşılaştırması.
5. **Model Comparison & Optimization Analysis** (20 dk) — E01-E07 karşılaştırması, 7
   görselleştirme.
6. **Experiment Tracking & Reproducibility** (20 dk) — Experiment Registry, dataset/split
   fingerprinting, environment metadata, reproducibility deneyi, artifact dosyaları.
7. **Final Test Evaluation & Workshop** (20 dk) — Model Freeze, Test Access Gate, Final
   Workshop, Model Selection & Optimization Report.

Notebook sonunda, deneyimli katılımcılar için beş **opsiyonel Advanced Challenge** (Random
Forest/LightGBM optimizasyonu, Nested CV, Successive Halving, Search Budget Sensitivity)
bulunur — bunlar test seti **kullanmaz**.

---

## 10. Stopping the LAB

```bash
docker compose down
```

`labs/lab09/artifacts/` içindeki dosyalar (bind mount sayesinde) bilgisayarınızda kalıcı olarak
saklanır.

---

## 11. Troubleshooting

| Problem | Çözüm |
|---|---|
| **Docker Desktop çalışmıyor / çöktü** | Docker Desktop'ı yeniden başlatın, sistem tepsisindeki ikonun "running" olmasını bekleyin (bazen 1-2 dakika sürebilir). Ardından `docker compose up -d` tekrar deneyin. |
| **`NameError`** (örn. `cv_folds`, `grid_search`, `random_search` tanımlı değil) | Section 2-4'teki hücreler sırayla çalıştırılmadı. **Run → Run All Cells** kullanın. |
| **`GridSearchCV`/`RandomizedSearchCV` hücresi "uzun sürüyor" gibi görünüyor** | Bu hücreler gerçekten 25-40 saniye sürebilir (24-25 ayrı model fit işlemi) — donmuş değildir. Jupyter'in sol kenarındaki `[*]` işareti hâlâ çalıştığını gösterir. |
| **`final_evaluation.json` oluşmuyor** | Bu **beklenen davranıştır** eğer `config/settings.yaml`'daki `lab09.evaluation.run_final_test` hâlâ `false` ise. Bölüm 8'deki "Final Test Evaluation Gate" açıklamasına bakın. |
| **Test sonuçları "Not Evaluated" görünüyor** | Aynı şekilde beklenen davranış — final evaluation gate'i henüz açmadınız. Bu bir hata/başarısızlık değildir. |
| **`HalvingRandomSearchCV` ile ilgili bir `ImportError`** | Bu API hâlâ "experimental" durumdadır (Advanced Challenge 4). Notebook, `from sklearn.experimental import enable_halving_search_cv` satırını zaten doğru şekilde içerir — eksikse notebook'u baştan çalıştırın. |
| **`git` komutları ile ilgili bir hata/uyarı görüyorsanız (Section 6, environment metadata)** | Bu, bazı makinelerde (özellikle Windows'ta) bilinen bir "dubious ownership" git sorunudur. Notebook bunu **doğru şekilde tespit eder ve raporlar** ("Not available: ...") — uydurma bir commit SHA üretmez. Bu bir notebook hatası değildir. |
| **Yanlış Notebook Kernel** | **Kernel → Change Kernel** menüsünden `Python 3 (ipykernel)`'i seçin. |
| **Notebook değişiklikleri kaydedilemiyor** | Tarayıcı sekmesini yenileyin (F5), `Ctrl + S` ile tekrar deneyin; `docker compose logs ml-lab` ile container loglarını kontrol edin. |
