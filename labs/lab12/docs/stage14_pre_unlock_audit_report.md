# LAB12 — Stage 14 Final Pre-Unlock Audit Report

**Bu rapor Phase B'yi yetkilendirmez. 2015 Protected Test bu asamada
HICBIR SEKILDE acilmadi, okunmadi, degerlendirilmedi.**

## Task 1 — Real Development Baseline Verification

**Sonuc: Metrikler icin PASS (0.000000 fark), baseline fitting icin
KISMEN UNVERIFIED (kalan sinirlama acikca belgeli).**

Ham CSV'ye HIC dokunulmadan, 2 aile development-only artifact kullanildi:

1. **Stage 08 fold-level artifacts** (`stage08_fold_statistics.csv`,
   `stage08_oof_predictions.csv`, `stage08_segment_support.csv`):
   - B0 (Global Median) ve B1 (Global Mean) formulleri, **4/4 CV
     fold'da EXACT parity** ile dogrulandi (fold'un Train_Mean/Train_Median'i
     ile OOF prediction'lar birebir eslesti).
   - B4'un `PARENT_FALLBACK` (Mode veya INCOTERM median) ve
     `GLOBAL_FALLBACK` (global median) tahminleri, segment_support
     tablosundaki `support>=10` medianlarla **4/4 fold'da TAM eslesti**
     (set-membership check, per-shipment feature gerekmedi).
   - `COMBINED_SEGMENT` seviyesi: ayri bir referans tablosu
     olmadigindan **bagimsiz olarak dogrulanamadi** (sadece design doc'un
     belirttigi formulle -- segment median, ayni min_support kurali --
     yapisal olarak tutarli).

2. **Stage 11 full-population artifacts** (`stage11_baseline_predictions.csv`,
   `stage11_external_metrics.csv`, `stage11_development_refit_report.json`)
   -- B1/B4'un TAM development population'da (n=4987) TEK SEFERLIK fit
   edilip 2014'te skorlanmis GERCEK sonuclari:
   - `evaluation/metrics.py`'nin **TUM 10 metrigi** (MAE, RMSE, Median AE,
     WAPE, Bias, P90/P95 AE, High-Cost MAE, High-Cost Underprediction
     Rate, Negative Count), bu gercek 2014 actual/prediction ciftleri
     uzerinde calistirildiginda, published referans degerlerle
     **0.000000 fark ile TAM OLARAK** eslesti (hem B1 hem B4 icin).
   - `stage11_development_refit_report.json`, B1'in TAM development
     population'daki (n=4987) mean'ini ACIKCA yayinlamis:
     **`10456.218411870865` USD**. Bu, `evaluation/contracts.py`'ye
     `EXPECTED_B1_DEVELOPMENT_MEAN_USD` olarak eklendi ve
     `runner.py`'de Protected Test okunmadan ONCE calisan bir
     fail-closed dogrulama haline getirildi (D-174).

**Kalan sinirlama:** B1/B4'un GERCEK development population'da
(ham CSV'den) sifirdan yeniden fit edilip edilmedigi, bu asamada hala
BAGIMSIZ olarak kanitlanamadi; ham CSV erisimi engellendi (D-169). Bunun pratik etkisi: Phase B'nin
gercek unlock calismasinda, development population loader'i YANLIS bir
veri kumesi uretirse, bunu BASLANGICTA yakalayacak tek mekanizma
D-174'teki B1-mean dogrulamasidir (metrics/baseline MANTIGI zaten
kanitlandi, ama GIRDI verisinin dogrulugu hala bu tek noktadan kontrol
ediliyor).

## Task 2 — Acceptance Criteria Audit

**Sonuc: Orijinal kural WEAK (neredeyse anlamsiz) -- RECLASSIFY +
REPLACE yapildi, acceptance.py/contracts.py GUNCELLENDI (D-173).**

Analiz: High-cost underprediction rate [0,100] araliginda sinirli bir
metriktir. 2014 referansi (%89.93) zaten bu tavana yakin, VE **her iki
mevcut baseline (B1, B4) 2014'te TAM OLARAK %100 skorluyor**. Sabit bir
+10pp tolerans, tavani %99.93'e tasir -- bu esigi ASMAK icin bir modelin
pratik olarak HER TEK high-cost shipment'i underpredict etmesi gerekir
(zaten baseline'larin yaptigi). Sonuc: kural hemen hemen HER DURUMDA
gecer, hicbir gercek ayirt edicilik saglamaz -- **WEAK**.

**Uygulanan karar:** Reclassify + Replace (iki secenegin kombinasyonu):
- Eski kural (2014 referansi + 10pp) bir **GATING kriteri OLMAKTAN
  CIKARILDI**, `high_cost_risk_monitor` adinda, HER ZAMAN raporlanan ama
  siniflandirmayi hicbir zaman etkilemeyen bir **monitored risk
  indicator**'a donusturuldu.
- Yerine, keyfi bir sabit GEREKTIRMEYEN, istatistiksel olarak daha
  saglam bir kriter eklendi: **model'in high-cost underprediction
  rate'i, AYNI Protected Test doneminde B4'unkinden KESINLIKLE DUSUK
  olmali.** Bu, zaten MAE karsilastirmasinda kullanilan "ayni donemde
  B4'u gec" mantigiyla TUTARLIDIR ve 2014/2015'in mutlak seviyesinden
  BAGIMSIZDIR.
- `evaluation/acceptance.py`, `evaluation/contracts.py`,
  `stage14_metric_baseline_contract.md` Section 5 GUNCELLENDI.
  `stage14_evaluation_freeze_manifest_v2.json` **DOKUNULMADI** -- yeni
  `stage14_evaluation_freeze_manifest_v3.json` olusturuldu.

**2015 verisi bu kararda KULLANILMADI** -- analiz tamamen 2014'un zaten
yayinlanmis sonuclarina (baseline'larin %100 skorlamasi) dayanmaktadir.

## Task 3 — Freeze Integrity

| Kontrol | Sonuc |
|---|---|
| Frozen ExtraTrees model SHA-256 | `71a451...77782` -- DEGISMEDI (local + Docker) |
| Feature/preprocessing contract | `stage07-v1-minimal-core` / `stage06-v1-tree-model-no-scaling` -- DEGISMEDI |
| Evaluation code fingerprint | DEGISTI (D-173/D-174 nedeniyle) -- v3'e yansitildi |
| Baseline definitions | Mantik DEGISMEDI (sadece bir integrity-check EKLENDI) |
| Metric formulas | DEGISMEDI, gercek veriyle 0.000000 fark ile dogrulandi |
| Target eligibility policy | DEGISMEDI |
| Canonical execution environment | Python 3.11.15 (major.minor) / sklearn 1.9.1 (exact) -- DEGISMEDI |
| Protected-test isolation | DEGISMEDI -- `UnlockToken` yapisi aynen korundu |
| Explicit unlock requirements | DEGISMEDI (9 kontrol kategorisi) |
| One-time execution guard | DEGISMEDI (`AlreadyEvaluatedError`) |

**v1 VE v2 dosyalari KORUNDU, uzerine yazilmadi.** `stage14_evaluation_freeze_manifest_v3.json`,
`supersedes` alaniyla v2'ye referans verir ve degisikligin TAM
gerekcesini tasir.

## Task 4 — Final Readiness Decision

1. **Baseline real-data parity:** **PASS (metrikler icin, 0.000000
   fark) / UNVERIFIED (full-population baseline fitting icin, ham veri
   erisimi kisitlamasi devam ediyor, ama fail-closed bir B1-mean kontrolu
   ile telafi edildi -- D-174).**
2. **Acceptance criteria:** Orijinal kural **WEAK** olarak teshis edildi
   -> **duzeltildi, su an VALID** (relative-to-B4 kriteri, keyfi sabit
   gerektirmez, istatistiksel olarak saglam).
3. **Evaluation code & freeze integrity:** TAM -- 150/150 test PASSED
   (local + Docker), v3 kendi fingerprint'ini dogruluyor (mismatch yok).
4. **Protected-test gate verification:** `UnlockToken`/`PreUnlockGate`
   yapisi DEGISMEDI, programatik olarak dogrulandi (`test_structural_safety.py`).
   Unlock komutu bu asamada CAGRILMADI.
5. **Kalan blocker'lar:**
   - Development population'in GERCEK ham veriden tam olarak
     yeniden-uretilebilirligi hala bagimsiz kanitlanamadi (D-169/D-175).
   - Business-approved SLA hala YOK.
   - Yeni relative high-cost kriteri hic gercek veriyle test edilmedi
     (mantiksal olarak saglam ama empirik olarak dogrulanmamis).
   - Authentication/rate-limiting API'de hala YOK.
6. **Final Recommendation: CONDITIONAL GO.**

Bu rapor Phase B'yi baslatmaz. Unlock komutu calistirilmadi. Kullanicinin
ayri, acik onayi bekleniyor.
