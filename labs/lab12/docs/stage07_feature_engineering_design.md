# LAB12 — Stage 07 Feature Engineering Design

## 1. Overview

Bu belge, Stage 07'de uretilen yeni shipment-level feature'larin tasarim gerekcesini,
veri kaynagini ve kabul/red kararlarini belgeler. **Final model feature set'i bu belgede
kesinlesmez** -- bkz `stage07_feature_contract.md`.

## 2. Business Objective

Pre-Shipment Freight Cost Estimation (Freight Cost (USD), shipment-level).

## 3. Dataset Contract

SCMS Delivery History Dataset, `ASN/DN #` shipment grouping (Stage 03.5 Shipment Data
Contract). Dataset SHA-256 ve Stage 05 protokol fingerprint'i notebook icinde yeniden
dogrulanmistir (degismeden).

## 4. Feature Eligibility

Mandatory exclusions: `Freight Cost (USD)`, `ID`, `PQ #`, `PO / SO #`, `ASN/DN #`,
`Delivered to Client Date`, `Delivered Recorded Date`. Stage 06 core feature schema
(`Line_Item_Qty_Sum`, `Line_Item_Value_Sum`, `Shipment_Mode`, `INCO_Term`, `Country`,
`Product_Group`) **degistirilmeden** korunmustur.

## 5. Feature Lineage

14 aday feature (`stage07_feature_lineage.csv`), her biri Source_Columns, Transformation,
Aggregation, Business_Justification, Prediction_Time_Requirement, Data_Quality_Risk ve
Leakage_Risk alanlariyla izlenebilir kilinmistir.

## 6. Shipment Composition (Group A)

`Line_Item_Count`, `Distinct_Item_Description_Count`, `Distinct_Molecule_Count` --
**Accepted for Experimentation**. Ablation sonucu: F1 (Core+Composition), hem Ridge
(7916.69 USD) hem Random Forest (6137.97 USD) icin F0'dan (Ridge 7974.86, RF 6151.74)
**daha iyi** pooled MAE verdi -- bu grup olcumsel olarak kucuk ama tutarli bir katki
sagliyor.

## 7. Shipment Value (Group B)

`Line_Item_Value_Mean`, `Line_Item_Value_Max`, `Value_Dispersion` -- **Conditional**.
Leakage riski: veri setinin %13.97'si (1442/10324 satir) "Freight Included in Commodity
Cost" kategorisinde -- bu, bazi vendor/rota kombinasyonlarinda `Line Item Value`'nun
navlun maliyetini icerebilecegini gosteriyor. Numeric-target shipment'lar bu kategoriden
DOGRUDAN etkilenmiyor, ama pricing politikasi kismen gecerli olabilecegi icin risk tam
olarak elenmemistir.

**Ablation bulgusu:** Value grubunu F4'ten cikarmak (`F4_minus_value`) Random Forest'i
**iyilestirdi** (6143.78 vs F4'un 6239.42 USD) ve Ridge'i pratik olarak degistirmedi
(7921.85 vs 7921.12). Bu, Value grubunun mevcut `Line_Item_Value_Sum` (core feature) ile
**redundant** oldugunu gosteriyor -- Section 9'daki yuksek korelasyon bulgusuyla tutarli.

## 8. Product Diversity (Group C)

**REJECTED.** `Product_Group_Diversity`, bu veri setinde **TUM 7030 shipment icin tam
olarak 1** (sifir varyans) -- her shipment tek bir Product Group icerir. Bu veri kumesinde shipment basina birden fazla Product Group gozlenmemistir. Ablation sanity-check'i (F3 vs F0) bu bulguyu dogruladi: Ridge icin
fark TAM SIFIR, Random Forest icin fark numeric noise seviyesinde (-0.57 USD).

## 9. Contract and Transport Features (Group D)

`Managed_By`, `Fulfill_Via`, `First_Line_Designation` -- **Accepted for Experimentation**
(hepsi %0 missing, PO/planlama asamasinda bilinir). Ablation (`F4_minus_transport_ext`):
Random Forest pratik olarak degismedi (6233.76 vs 6239.42), Ridge hafifce iyilesti
(7915.71 vs 7921.12) -- bu grubun katkisi **kucuk ve belirsiz** (Inconclusive'e yakin).

## 10. Calendar Features (Group E)

`Scheduled_Month`, `Scheduled_Quarter` -- **Conditional/Sensitivity-Only (D-007)**.
`Scheduled_Year` -- **Excluded** (temporal-trend overfitting riski: split boundary ile
dolayli iliskili olabilir). Sensitivity sonucu (Section 15): Calendar eklenmesi her iki
estimator icin de performansi hafifce **kotulestirdi** (RF 6283.24 vs 6239.42, Ridge
7959.89 vs 7921.12) -- D-007 kararini degistirmez.

## 11. Weight Sensitivity (Group F)

`Weight_KG` -- **D-006 Sensitivity-Only, production setine DAHIL DEGIL.** Sensitivity
sonucu carpici: Random Forest icin -542.09 USD pooled MAE iyilesmesi (5697.32 vs F4'un
6239.42), Ridge icin ihmal edilebilir fark (-0.41 USD). Bu buyuk, model-bagimli etki,
Weight'in gercek bir predictive sinyal tasidigini gosteriyor -- ANCAK D-006 (prediction-
time availability Unknown) karari bu sonuctan **BAGIMSIZ** olarak korunmaktadir.

## 12. Aggregation Semantics

Stage 03.5'in kabul ettigi semantics korunmustur: numeric -> `sum()`/`mean()`/`max()`/
`count()`/`nunique()` (duruma gore), categorical -> `first()`. Hicbir kolon icin repeated
shipment-level degerler yanlislikla toplanmadi (sum() sadece gercekten line-item-duzeyinde
degisken kolonlara uygulandi).

## 13. Data Quality

`stage07_feature_quality_report.csv`: yeni numeric feature'larin hicbirinde (Composition,
Value) missing value yok; categorical extension'larin (Managed_By, Fulfill_Via,
First_Line_Designation) hicbirinde missing value yok. Weight_KG (sensitivity-only) %9.36
missing tasir (Stage 06'dan bilinen).

## 14. Leakage Risks

- Line_Item_Value tabanli feature'lar: %13.97 bundling riski (Section 7).
- Scheduled_Year: dolayli temporal-split iliskisi riski nedeniyle excluded.
- Diger tum yeni feature'lar icin dogrudan leakage riski **None** olarak degerlendirildi
  (target'tan turetilmemis, post-shipment bilgi icermiyor).

## 15. Reproducibility

Tum feature engineering stateless ve deterministiktir (random state'e bagli degil, gelecek
shipment istatistiklerini kullanmaz). Reproducibility check: referans pipeline (F4, Ridge)
iki kez fit edildi, tahminler `np.allclose` ile birebir eslesti.

## 16. Engineering Conclusions

- **Accepted (production-eligible aday):** Shipment Composition (Group A), Transport/
  Contract extensions (Group D, kucuk katki).
- **Conditional:** Shipment Value (Group B, bundling riski + redundancy), Calendar
  (Group E, D-007).
- **Rejected:** Product Diversity (Group C, sifir varyans).
- **Sensitivity-Only:** Weight (Group F, D-006 -- buyuk olcumsel fayda olsa da production
  karari degismez).
