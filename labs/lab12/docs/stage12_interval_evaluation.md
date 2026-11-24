# LAB12 — Stage 12 Interval Evaluation

## 1. Calibration Population

4 outer fold, calibration N = [664, 780, 776, 861] (years 2009, 2010, 2011,
2012 respectively) -- her biri kendi outer fold'unun inner training
history'sinin son calendar year'i.

## 2. Outer Evaluation Population

Evaluation N = [780, 776, 861, 835] (years 2010, 2011, 2012, 2013) --
Stage 05'in frozen CV_Validation rolleri, degistirilmeden.

## 3. Calibration Sample Counts

Tum fold'lar `minimum_calibration_samples=30` esigini acikca astigi icin
hicbir fold "insufficient calibration" olarak isaretlenmedi.

## 4. Empirical Coverage

| Nominal | Empirical | Gap | Sample Count |
|---|---:|---:|---:|
| 80% | 73.0% | **-7.0%** | 3,252 |
| 90% | 83.1% | **-6.9%** | 3,252 |

Her iki seviyede de **sistematik undercoverage** gozlemlendi.

## 5. Mean Interval Width

80% nominal: 14,227 USD (median 13,727, P90 16,223). 90% nominal: 23,689 USD
(median 23,825, P90 27,339).

## 6. Coverage–Width Trade-Off

Daha yuksek nominal coverage (90%) daha genis interval (23,689 vs 14,227
USD) gerektirdi ama yine de ~7 puan undercoverage gosterdi -- genislik artisi
undercoverage'i TAM OLARAK cozmedi.

## 7. Fold-Level Coverage

`stage12_temporal_coverage.csv` -- undercoverage **4 fold'un hepsinde**
tutarli olarak gozlemlendi (tek bir anormal fold'a izole edilemedi).

## 8. Conditional Coverage

92 (segment x nominal_coverage) satirindan **30'u** (`Shipment_Mode`,
`INCO_Term`, `Country` kesisimlerinde) minimum segment support (n<20) esigini
gecemedi ve `INSUFFICIENT_SUPPORT` olarak flaglendi -- bu segmentler icin
coverage degeri raporlandi ama guvenilir kabul edilmedi.

## 9. High-Cost Coverage (En Kritik Bulgu)

| Fold | Eval Year | High-Cost N | Coverage (90%) | Upper-Bound Miss Rate |
|---|---|---:|---:|---:|
| 1 | 2010 | 64 | 34.4% | 57.8% |
| 2 | 2011 | 123 | 48.0% | 48.8% |
| 3 | 2012 | 184 | 45.1% | 53.3% |
| 4 | 2013 | 194 | 46.9% | 50.0% |

**Ortalama high-cost coverage (90% nominal) = %43.6** -- overall %83.1'in
COK ALTINDA. Bu, Stage 11'in %89.9 high-cost underprediction bulgusuyla
dogrudan tutarlidir ve interval-seviyesinde ayni riski teyit eder.

## 10. Temporal Stability

Undercoverage'in 4 fold boyunca tutarli kalmasi, bunun tek bir yilin
anomalisi degil, **sistematik bir yapisal sinirlama** oldugunu gosterir
(kesin mekanizma -- distribution shift, residual heteroscedasticity, veya
baska bir faktor -- bu veriyle AYRISTIRILAMAZ).

## 11. Undercoverage Cases

En yuksek undercoverage high-cost segmentte (bkz Section 9) -- genel
populasyonda da (~7 puan) var ama daha az siddetli.

## 12. Statistical Limitations

(1) 4 outer fold -- coverage tahmininin kendisi kucuk orneklem belirsizligine
sahip. (2) Marginal conformal guarantee segment-seviyesinde garanti SAGLAMAZ
-- gozlemlenen conditional/high-cost undercoverage bu nedenle "beklenen"
bir sinirlamadir, hesaplama hatasi degildir. (3) Temporal exchangeability
muhtemelen ihlal edilmistir (bkz calibration design doc).

## 13. Operational Interpretation

Bu interval'lar **arastirma amacli** kalmalidir -- hicbir production
quotation sistemine dogrudan baglanmamalidir (bkz
`stage12_model_risk_decisions.md`).

## 14. Conclusions

Genel coverage nominal'in ~7 puan altinda; high-cost segment coverage
kritik derecede yetersiz (%43.6 vs %90). Bu bulgular **"Production Interval
Not Approved"** kararina dogrudan temel olusturmustur.
