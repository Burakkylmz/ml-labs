# LAB12 — Stage 08 Baseline Acceptance

## 1. Acceptance Objective

Stage 09 modellerinin hangi baseline'lari asmasi gerektigini, gercek CV evidence ile
belirlemek.

## 2. Statistical Baseline Selection

**B1 (Global Mean)** -- B0/B1 arasinda en dusuk pooled MAE (9106.34 USD). Secim, gercek
CV sonucuna dayanir; bu, median'in teorik MAE-optimalligine ragmen bu ozel CV'de mean'in
daha iyi performans gostermesinin bir sonucudur (temporal shift-sensitive bulgu).

## 3. Business Baseline Selection

**B4 (Hierarchical Segment Median)** -- B2/B3/B4 arasinda en dusuk pooled MAE (8694.56
USD). B2'ye (Shipment Mode Median) kiyasla kazanc kucuk (-96.99 USD) ama 4 fold'un
hepsinde tutarli yonde.

## 4. Fallback Baseline

**B4** -- yapisal olarak en tam fallback hiyerarsisine sahip (combined -> mode ->
incoterm -> global), unseen/missing/low-support durumlarini guvenli sekilde ele alir
(%4.1 fallback rate, hicbir crash/NaN/infinite prediction).

## 5. Comparison Criteria

Pooled MAE, RMSE, high-cost segment MAE, bias, fold-level stabilite, fallback
robustness, prediction-time availability, inference basitligi, maintenance cost,
reproducibility -- hepsi birlikte degerlendirildi (tek bir metrige indirgenmedi).

## 6. Business Impact Considerations

Shipment volume, cost magnitude, operational decision cost, error tolerance hakkinda
**onaylanmis bir business veri seti yoktur**. Bu nedenle business impact degerlendirmesi
Section 7'deki provisional threshold'la sinirlidir.

## 7. Provisional Improvement Thresholds

**%5 MAE improvement** (business reference baseline'a gore) -- bu **keyfi, provisional
bir engineering threshold'dur**, is birimi tarafindan onaylanmis bir KPI/SLA degildir.
Provisional Stage 09 hedefi: **8259.83 USD** (B4'un 8694.56 USD'sinin %5 altinda).

## 8. Limitations

- Sadece 4 (kismen bagimli) CV fold -- istatistiksel guven sinirli.
- B4'un B2'ye kazanci kucuk -- ek complexity'nin kesin gerekcesi guclu degil.
- INCOTERM'in target availability ile olasi iliskisi, deployment semantics acisindan
  ayri incelenmelidir.
- Tum baseline'lar high-cost segmentte %100 underpredict ediyor -- bu, basit
  baseline'larin yapisal bir sinirlamasidir, bir "basarisizlik" degil.

## 9. Remaining Risks

- Business-approved bir SLA/KPI threshold'u **yoktur**.
- Stage 06-07 Ridge/RF probe sonuclari, farkli feature/preprocessing policy'leri
  nedeniyle bu baseline'larla **dogrudan karsilastirilamaz** (bkz
  `stage09_benchmark_contract.md` Section 10).
- D-007 (label availability) kosullu kalmaya devam ediyor.

## 10. Final Decision

**Statistical Reference Baseline:** B1 (Global Mean), Pooled MAE=9106.34 USD.
**Business Reference Baseline:** B4 (Hierarchical Segment Median), Pooled MAE=8694.56
USD. **Robust Fallback Baseline:** B4. **Stage 09 Readiness: CONDITIONAL GO** -- referans
baseline'lar ve degerlendirme protokolu hazir; business-approved SLA hala eksik,
bu Stage 09 oncesi is birimiyle netlestirilmelidir (zorunlu degil, risk olarak tasinir).
