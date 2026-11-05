# LAB02 Student Guide — Python for Machine Learning & Data Manipulation

Bu rehber, `ml-labs` projesindeki **LAB02: Python for Machine Learning & Data Manipulation** çalışmasını
kendi bilgisayarınızda Docker üzerinden nasıl çalıştıracağınızı adım adım açıklar.

**Eğitim süresi:** 150 dakika (10 dakikalık mola dahil)

---

## 1. LAB Overview

Bu LAB'da, Python'ın veri bilimi ekosistemini kullanarak iki farklı veri kümesi üzerinde çalışacaksınız.
LAB sonunda şu konuları uygulamış olacaksınız:

- **NumPy** array işlemleri
- **Pandas** `Series` ve `DataFrame` yapıları
- CSV dosyalarından **Data Loading**
- **Filtering** ve **Sorting**
- **GroupBy** ve **Aggregation**
- Birden fazla tabloyu **Merge** ve **Join** ile birleştirme
- **Matplotlib** ile temel veri görselleştirme
- Notebook içindeki kodu tekrar kullanılabilir bir Python modülüne ayırma (**code organization**)

Kullanılan iki veri kümesi birbirinden bağımsızdır ve birbirleriyle birleştirilmez:

| Dataset | Kullanım Alanı |
|---|---|
| **E-Commerce Shipping Data** | NumPy, Pandas, Filtering, Sorting, GroupBy, Aggregation, Visualization |
| **Northwind** | Relational Data, Merge, Join, Join Validation |

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
Scikit-learn kurmanıza gerek yoktur** — yalnızca Docker Desktop yeterlidir.

---

## 3. Dataset Download Instructions

> **Not:** Veri dosyaları bu proje tarafından otomatik olarak indirilmez. Her iki veri kümesini de
> Kaggle üzerinden manuel olarak indirip doğru klasöre yerleştirmeniz gerekir.

### Dataset 1 — E-Commerce Shipping Data

- **Kaggle bağlantısı:** [https://www.kaggle.com/datasets/prachi13/customer-analytics?resource=download](https://www.kaggle.com/datasets/prachi13/customer-analytics?resource=download)
- **Beklenen hedef konum:** `data/ecommerce_shipping/Train.csv`

**Adımlar:**

1. Yukarıdaki Kaggle bağlantısını tarayıcınızda açın.
2. Eğer dosya henüz görünmüyorsa Kaggle hesabınıza giriş yapın.
3. **Download** butonuna tıklayarak ZIP arşivini indirin.
4. İndirilen ZIP arşivini çıkarın (extract).
5. Arşivden çıkan dosyanın adının `Train.csv` olduğunu doğrulayın.
6. Bu dosyayı proje kök dizininde `data/ecommerce_shipping/` klasörünün içine kopyalayın (klasör yoksa
   oluşturun). Sonuçta dosya şu yolda olmalıdır: `data/ecommerce_shipping/Train.csv`.

### Dataset 2 — Northwind Traders Dataset

- **Kaggle bağlantısı:** [https://www.kaggle.com/datasets/matthuan/northwind-dataset](https://www.kaggle.com/datasets/matthuan/northwind-dataset)
- **Beklenen hedef konum:**

  ```text
  data/northwind/
  ├── customers.csv
  ├── orders.csv
  └── shippers.csv
  ```

> **Önemli uyarı:** Bu Kaggle arşivinin, yalnızca bu üç dosyayı içerdiği doğrulanmamıştır. Northwind,
> klasik olarak `Customers`, `Orders`, `Shippers` dışında `Categories`, `Employees`, `Products`,
> `Suppliers`, `Territories`, `Region`, `Order Details` gibi **çok daha fazla tabloyu** içeren bir
> veri kümesidir; bu Kaggle arşivi de muhtemelen bu tabloların **tamamını** ayrı CSV dosyaları olarak
> içerecektir. LAB02, bu tabloların yalnızca **üçünü** (`customers`, `orders`, `shippers`) kullanır.

**Adımlar:**

1. Yukarıdaki Kaggle bağlantısını tarayıcınızda açın.
2. Eğer dosya listesi görünmüyorsa Kaggle hesabınıza giriş yapın.
3. **Download** butonuna tıklayarak ZIP arşivini indirin.
4. İndirilen ZIP arşivini çıkarın (extract).
5. Çıkan klasördeki dosya listesini inceleyin. Dosya isimleri ve büyük/küçük harf kullanımı (örn.
   `Customers.csv` yerine `customers.csv`) arşiv sürümüne göre farklılık gösterebilir.
6. LAB02 için gereken üç tabloyu bulun — müşteri bilgilerini içeren tablo, sipariş bilgilerini içeren
   tablo ve kargo/taşıma şirketi bilgilerini içeren tablo.
7. Bu üç dosyayı, proje kök dizininde `data/northwind/` klasörünün içine kopyalayın (klasör yoksa
   oluşturun) ve gerekirse dosya isimlerini küçük harfle `customers.csv`, `orders.csv`, `shippers.csv`
   olacak şekilde yeniden adlandırın. Diğer tabloları (varsa) bu klasöre eklemeniz LAB02 için gerekli
   değildir; isterseniz silmeden bırakabilirsiniz.

> Her iki durumda da **orijinal CSV içeriğini değiştirmeyin** — yalnızca dosyaları doğru klasöre
> taşıyın/kopyalayın ve gerekirse yeniden adlandırın.

---

## 4. Expected Directory Structure

Her iki veri kümesini de yerleştirdikten sonra proje yapınız şu şekilde görünmelidir:

```text
ml-labs/
├── data/
│   ├── ecommerce_shipping/
│   │   └── Train.csv
│   └── northwind/
│       ├── customers.csv
│       ├── orders.csv
│       └── shippers.csv
├── labs/
│   └── lab02/
│       ├── lab02_python_data_manipulation.ipynb
│       └── README.md
├── doc/
│   └── lab02_student_guide.md
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

Projeyi kendi bilgisayarınıza almak için GitHub üzerinden clone edin.

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

5. Bölüm 3'te indirdiğiniz dataset dosyalarını, Bölüm 4'te gösterilen klasör yapısına göre bu klasörün
   içine yerleştirin (örn. `data/ecommerce_shipping/Train.csv`, `data/northwind/customers.csv` vb.).
6. Bu rehberin kalan adımlarını (Docker ile çalıştırma dahil) her zaman bu `ml-labs/` klasörünün içinden
   çalıştıracaksınız.

> Projeyi daha önce klonladıysanız ve güncellemeleri almak istiyorsanız, `ml-labs/` klasörü içinde
> `git pull` komutunu çalıştırabilirsiniz — tekrar `git clone` yapmanıza gerek yoktur.

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
   `labs` klasörüne, ardından `lab02` klasörüne girin.
5. `lab02_python_data_manipulation.ipynb` dosyasına çift tıklayarak notebook'u açın.

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

---

## 9. LAB Sections

Notebook, aşağıdaki sırayla ilerler:

1. **Python Data Science Ecosystem** — Kullanılan kütüphaneler, Jupyter kernel ve çalışma ortamı tanıtılır.
2. **NumPy Fundamentals** — Array oluşturma, indeksleme ve vectorized işlemler uygulanır.
3. **Pandas Series & DataFrame** — Temel Pandas veri yapıları tanıtılır.
4. **Data Loading & Inspection** — E-Commerce Shipping verisi okunur ve keşifsel olarak incelenir.
5. **Filtering & Sorting** — Satırlar koşullara göre filtrelenir ve sıralanır.
6. **GroupBy & Aggregation** — Veriler gruplanarak özet istatistikler hesaplanır.
7. **Northwind Merge & Join** — Northwind tabloları `merge` ve `join` ile birleştirilir, bütünlük
   kontrolleri yapılır.
8. **Matplotlib Visualization** — E-Commerce Shipping verisi üzerinde temel grafikler oluşturulur.
9. **Code Organization & Exit Challenge** — Notebook kodu ile `src/` altındaki yeniden kullanılabilir
   modül arasındaki fark gösterilir; bölüm bir kapanış alıştırmasıyla sona erer.

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
| **Port 8888 kullanımda** (`port is already allocated`) | Bilgisayarınızda 8888 portunu kullanan başka bir uygulama (örn. başka bir Jupyter örneği) çalışıyor olabilir. Bu uygulamayı durdurun veya `compose.yaml` dosyasındaki port eşlemesini güncelleyin (bu değişiklik bu rehberin kapsamı dışındadır — eğitmeninize danışın). |
| **JupyterLab açılmıyor / tarayıcıda yüklenmiyor** | `docker compose ps` ile container'ın `running` durumda olduğunu doğrulayın. `docker compose logs ml-lab` ile hata olup olmadığını kontrol edin. Gerekirse `docker compose down` ve ardından `docker compose up --build -d` ile yeniden başlatın. |
| **Dataset `FileNotFoundError`** | Notebook, ilgili CSV dosyasını bulamadığında bu hatayı fırlatır. `data/ecommerce_shipping/Train.csv` ve `data/northwind/{customers,orders,shippers}.csv` dosyalarının Bölüm 3'teki adımlara göre doğru konumda olduğunu kontrol edin. |
| **Yanlış Notebook Kernel** | Bu container içinde tek bir Python ortamı (`Python 3 (ipykernel)`) bulunur. Notebook sağ üstte farklı bir kernel adı gösteriyorsa, **Kernel → Change Kernel** menüsünden `Python 3 (ipykernel)`'i seçin. |
| **Python `ModuleNotFoundError`** | Tüm bağımlılıklar `Dockerfile` build aşamasında kurulur; bu hata genellikle image'ın güncel bağımlılıklarla yeniden build edilmediğini gösterir. `docker compose up --build -d` komutunu `--build` bayrağıyla tekrar çalıştırın. |
| **Notebook değişiklikleri kaydedilemiyor** | Bölüm 10'da açıklanan bind mount sayesinde kaydetme normalde sorunsuz çalışır. Kaydetme başarısız oluyorsa, tarayıcı sekmesini yenileyin (F5) ve `Ctrl + S` ile tekrar deneyin; sorun sürerse `docker compose logs ml-lab` ile container loglarını kontrol edin. |
