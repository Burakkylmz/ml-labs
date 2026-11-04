# LAB03 Student Guide — Statistics & Exploratory Data Analysis

Bu rehber, `ml-labs` projesindeki **LAB03: Statistics & Exploratory Data Analysis** çalışmasını kendi
bilgisayarınızda Docker üzerinden nasıl çalıştıracağınızı adım adım açıklar.

**Eğitim süresi:** 150 dakika (10 dakikalık mola dahil)

> Bu LAB, **LAB02**'nin devamıdır. LAB02'yi tamamlamadıysanız önce
> [`doc/lab02_student_guide.md`](lab02_student_guide.md) rehberini takip edin.

---

## 1. LAB Overview

Bu LAB'da, LAB02'de öğrendiğiniz NumPy/Pandas becerilerini kullanarak bir veri kümesini bir Machine
Learning modeline vermeden önce **istatistiksel olarak incelemeyi (EDA)** öğreneceksiniz. LAB sonunda şu
konuları uygulamış olacaksınız:

- **Descriptive Statistics** (mean, median, mode)
- **Dispersion** (variance, standard deviation, IQR)
- **Outlier Detection** (IQR yöntemi)
- **Distribution Shape & Skewness** (histogram, çarpıklık)
- **Data Quality Assessment** (missing values, duplicates, range/categorical checks)
- **Correlation** (Pearson correlation matrix) ve **Group Comparisons**
- **Matplotlib** ile EDA'ya özgü grafikler (histogram, boxplot, bar chart, scatter plot)

Bu LAB'da **tek bir veri kümesi** kullanılır — LAB02'deki Northwind veri kümesi burada **kullanılmaz**:

| Dataset | Kullanım Alanı |
|---|---|
| **E-Commerce Shipping Data** | Descriptive Statistics, Dispersion, Outliers, Distributions, Data Quality, Correlation, Group Comparisons, Visualization |

---

## 2. Prerequisites

LAB'ı çalıştırmadan önce bilgisayarınızda şunların kurulu olması gerekir:

- **Docker Desktop** veya kurumunuz tarafından onaylanan eşdeğer bir Docker ortamı
- **Docker Compose V2** (güncel Docker Desktop sürümleriyle birlikte gelir)
- **Git**
- Bir **web browser** (Chrome, Edge, Firefox vb.)
- **Visual Studio Code** (önerilir, zorunlu değildir)

### Python, NumPy, Pandas kurmanıza gerek yok

Bu projede tüm Python bağımlılıkları (`numpy`, `pandas`, `matplotlib`, `pyyaml`, `jupyterlab` vb.)
`uv` ile yönetilir, ancak `uv` **yalnızca Docker image'ı build edilirken** çalışır:

- `Dockerfile` içinde `uv sync --locked` komutu, `pyproject.toml` ve `uv.lock` dosyalarına göre tüm
  bağımlılıkları container içindeki `/opt/venv` sanal ortamına kurar.
- JupyterLab bu sanal ortam üzerinden çalışır.

Bu nedenle, LAB'ı Docker ile çalıştırmak için **kendi bilgisayarınıza Python, uv, NumPy, Pandas veya
Scikit-learn kurmanıza gerek yoktur** — yalnızca Docker Desktop yeterlidir. LAB03, LAB02 ile **aynı
Docker image'ını** kullanır; yeni bir bağımlılık eklenmemiştir.

---

## 3. Dataset Download Instructions

> **Not:** Veri dosyası bu proje tarafından otomatik olarak indirilmez.

### E-Commerce Shipping Data

LAB03, LAB02'de kullandığınız **aynı** `data/ecommerce_shipping/Train.csv` dosyasını kullanır.

- **Eğer LAB02'yi zaten tamamladıysanız:** Bu dosya zaten doğru konumda olmalıdır — yeniden indirmenize
  gerek yoktur.
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

> **Orijinal CSV içeriğini değiştirmeyin.** LAB03, bu dosyayı yalnızca okur; üzerinde herhangi bir
> değişiklik yapmaz.

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
│   └── lab03/
│       ├── lab03_statistics_eda.ipynb
│       └── README.md
├── doc/
│   ├── lab02_student_guide.md
│   └── lab03_student_guide.md
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

## 5. Running the LAB with Docker

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

   > Eğer LAB02'den kalan bir image varsa, bu komut genellikle çok hızlı tamamlanır (önceki build
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

## 6. Accessing JupyterLab

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
   `labs` klasörüne, ardından `lab03` klasörüne girin.
5. `lab03_statistics_eda.ipynb` dosyasına çift tıklayarak notebook'u açın.

> Container'ın çalışma dizini (`WORKDIR`) `/app`'tir ve proje kök dizininiz bu yola bağlanır (bind
> mount). Bu nedenle JupyterLab'daki klasör yapısı, kendi bilgisayarınızdaki `ml-labs/` klasör yapısıyla
> birebir aynıdır.

---

## 7. Working with Notebook Cells

Bir Jupyter notebook (`.ipynb`), iki tür hücreden oluşur:

- **Markdown Cell**: Açıklama metni içerir (bu rehber gibi); çalıştırıldığında kod üretmez, yalnızca
  biçimlendirilmiş metni gösterir. Bu LAB'da Markdown hücreleri, LaTeX formülleri (örn. varyans, IQR,
  Pearson correlation) içerir — bunlar JupyterLab tarafından otomatik olarak biçimlendirilmiş şekilde
  görüntülenir.
- **Code Cell**: Çalıştırılabilir Python kodu içerir.

### Temel kullanım

- Bir Code Cell'i çalıştırmak için hücreye tıklayın ve **`Shift + Enter`** tuşlarına basın. Bu, hücreyi
  çalıştırır ve bir sonraki hücreye geçer.
- Hücre çalıştırıldıktan sonra, çıktısı (varsa) **hücrenin hemen altında** görüntülenir.
- Bir Pandas `DataFrame`'i döndüren bir hücre çalıştırıldığında, DataFrame tablo olarak hücrenin altında
  gösterilir.
- Bir Matplotlib grafiği (histogram, boxplot, bar chart, scatter plot) oluşturan bir hücre
  çalıştırıldığında, grafik görsel olarak hücrenin altında görüntülenir.
- Yaptığınız değişiklikleri kaydetmek için **`Ctrl + S`** tuşlarına basın veya üst menüden **File → Save
  Notebook**'u seçin.

### Önemli

**Docker kullanılması, Jupyter Notebook'un hücre bazlı çalışma mantığını değiştirmez.** Yazdığınız Python
kodu, container içinde çalışan Jupyter **kernel**'i tarafından çalıştırılır; sonuçlar her zaman ilgili
hücrenin altında görüntülenir — bu davranış, Docker kullanılmasa da aynıdır.

---

## 8. LAB Sections

Notebook, aşağıdaki sırayla ilerler:

1. **LAB02 Review & EDA Introduction** — EDA'nın ne olduğu, dataset'in hızlı hatırlatması ve target
   dağılımı incelenir.
2. **Descriptive Statistics** — Mean, median ve mode hesaplanır ve ne zaman farklı davrandıkları
   yorumlanır.
3. **Dispersion, Quantiles & Outliers** — Variance, standard deviation, IQR hesaplanır; IQR yöntemiyle
   potansiyel outlier'lar belirlenir.
4. **Data Distributions & Skewness** — Histogram ve skewness ile dağılım şekli değerlendirilir.
5. **Data Quality Assessment** — Missing values, duplicate kayıtlar ve geçerlilik kontrolleri yapılarak
   bir Data Quality Report oluşturulur.
6. **Correlation & Group Comparisons** — Pearson correlation matrix oluşturulur ve kategorik gruplar
   arasında istatistiksel karşılaştırmalar yapılır.
7. **EDA Visualization with Matplotlib** — Histogram, boxplot, bar chart ve scatter plot oluşturulur.
8. **EDA Workshop & Findings** — Kısa bir öğrenci değerlendirmesi ve notebook sonunda gerçek
   hesaplamalara dayanan bir EDA Findings özeti bulunur.

Notebook sonunda, deneyimli katılımcılar için üç **opsiyonel Advanced Challenge** (bootstrap confidence
interval, çoklu grup karşılaştırması, istatistiksel yorum tartışması) bulunur — bunlar ana 150 dakikalık
süreye dahil değildir ve tamamlanmamaları notebook'un çalışmasını etkilemez.

---

## 9. Stopping the LAB

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

## 10. Troubleshooting

| Problem | Çözüm |
|---|---|
| **Docker Desktop çalışmıyor** | Docker Desktop uygulamasını başlatın ve sistem tepsisindeki ikonun "running" durumuna geçmesini bekleyin. Ardından komutu tekrar çalıştırın. |
| **Docker Engine bağlantı hatası** (`error during connect`, `pipe not found` vb.) | Bu hata genellikle Docker Desktop'ın henüz tamamen başlamadığını gösterir. Docker Desktop'ın tamamen açıldığından emin olun ve birkaç saniye bekleyip komutu tekrar deneyin. |
| **Port 8888 kullanımda** (`port is already allocated`) | Bilgisayarınızda 8888 portunu kullanan başka bir uygulama (örn. LAB02'den kapatılmamış bir container) çalışıyor olabilir. `docker compose down` ile önceki container'ı durdurun, ardından tekrar deneyin. |
| **JupyterLab açılmıyor / tarayıcıda yüklenmiyor** | `docker compose ps` ile container'ın `running` durumda olduğunu doğrulayın. `docker compose logs ml-lab` ile hata olup olmadığını kontrol edin. Gerekirse `docker compose down` ve ardından `docker compose up --build -d` ile yeniden başlatın. |
| **Dataset `FileNotFoundError`** | Notebook, `data/ecommerce_shipping/Train.csv` dosyasını bulamadığında bu hatayı fırlatır. Bölüm 3'teki adımlara göre dosyanın doğru konumda olduğunu kontrol edin (LAB02'yi tamamladıysanız bu dosya zaten mevcut olmalıdır). |
| **Yanlış Notebook Kernel** | Bu container içinde tek bir Python ortamı (`Python 3 (ipykernel)`) bulunur. Notebook sağ üstte farklı bir kernel adı gösteriyorsa, **Kernel → Change Kernel** menüsünden `Python 3 (ipykernel)`'i seçin. |
| **Python `ModuleNotFoundError`** | Tüm bağımlılıklar `Dockerfile` build aşamasında kurulur; bu hata genellikle image'ın güncel bağımlılıklarla yeniden build edilmediğini gösterir. `docker compose up --build -d` komutunu `--build` bayrağıyla tekrar çalıştırın. |
| **LaTeX formülleri (Markdown hücrelerinde) düzgün görünmüyor** | Sayfayı yenileyin (F5) ve notebook'un tamamen yüklenmesini bekleyin; JupyterLab, MathJax kütüphanesini ilk açılışta yüklediği için formüllerin render edilmesi birkaç saniye sürebilir. |
| **Notebook değişiklikleri kaydedilemiyor** | Bölüm 9'da açıklanan bind mount sayesinde kaydetme normalde sorunsuz çalışır. Kaydetme başarısız oluyorsa, tarayıcı sekmesini yenileyin (F5) ve `Ctrl + S` ile tekrar deneyin; sorun sürerse `docker compose logs ml-lab` ile container loglarını kontrol edin. |
