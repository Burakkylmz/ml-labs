# LAB12 — Stage 07 Feature Selection Evidence

## 1. Research Questions

Filter, Embedded ve Limited Wrapper feature selection yontemleri, F4 (Combined Eligible,
15 raw feature, encoded ~57-60 kolon) uzerinde, Stage 05'in dondurulmus 4-fold CV
protokolunde nasil karsilastirilir?

## 2. Candidate Feature Sets

Tum selection deneyleri **F4_combined** (`Line_Item_Qty_Sum`, `Line_Item_Value_Sum`,
`Line_Item_Count`, `Distinct_Item_Description_Count`, `Distinct_Molecule_Count`,
`Line_Item_Value_Mean`, `Line_Item_Value_Max`, `Value_Dispersion`; `Shipment_Mode`,
`INCO_Term`, `Country`, `Product_Group`, `Managed_By`, `Fulfill_Via`,
`First_Line_Designation`) uzerinde calisir.

## 3. Frozen CV Protocol

Stage 05 protokol fingerprint'i (`b87ca0fd...8935e`) notebook icinde yeniden hesaplanip
dogrulandi. Preprocessing (median imputation + StandardScaler numeric; constant-fill +
rare-category OneHot categorical) tum selection karsilastirmalarinda **sabit** tutuldu.

## 4. Filter Methods

`SelectKBest(mutual_info_regression, k)`, k ∈ {5, 10, 15}, fold-training'de fit edildi.

| k | Ridge Pooled MAE | Random Forest Pooled MAE |
|---|---|---|
| 5 | 8214.42 | 6883.24 |
| 10 | 8150.68 | 6683.63 |
| 15 | 8155.77 | 6421.88 |
| No_Selection (15 raw -> ~57 encoded) | 7921.12 | 6239.42 |

k arttikca Random Forest icin MAE iyilesiyor (6883->6421), ama No_Selection'a hala
ulasamiyor -- MI-tabanli filter, tum encoded alanin tasidigi bilgiyi kucuk k'larda tam
yakalayamiyor. Ridge icin k'nin etkisi kucuk ve tutarsiz.

## 5. Embedded Methods

`SelectFromModel(Lasso(alpha=50.0))`, sabit (optimize edilmemis) alpha. Fold basina
secilen encoded feature sayisi: 21-24 (4 fold ortalamasi ~22.75).

| Yontem | Ridge Pooled MAE | Random Forest Pooled MAE |
|---|---|---|
| Embedded (Lasso SelectFromModel) | 8065.87 | 6332.24 |
| No_Selection | 7921.12 | 6239.42 |

Embedded, No_Selection'dan hafifce daha kotu -- ~23 encoded feature, ~57'nin tasidigi
bilginin kucuk bir kismini feda ediyor olabilir.

## 6. Wrapper Methods (Limited)

`RFE(estimator=Ridge, n_features_to_select=8, step=2)` -- **sinirli** (exhaustive degil).

| Yontem | Ridge Pooled MAE | Random Forest Pooled MAE |
|---|---|---|
| Wrapper (RFE, n=8) | 8645.20 | 7438.38 |
| No_Selection | 7921.12 | 6239.42 |

Wrapper, test edilen 3 yontem arasinda **en kotu** performansi verdi -- hem Ridge hem
Random Forest icin No_Selection'dan acikca daha yuksek MAE. 8 encoded feature'a
sikistirma, bu veri setinde asiri agresif bir azaltma gibi gorunuyor.

## 7. Selection Stability

Filter (k=10) secilen encoded feature index'lerinin 4 fold arasindaki mean pairwise
Jaccard similarity: **0.483**. Fold'lar bagimsiz olmadigindan (expanding window, birbirinin
alt kumesi) bu deger rastgele CV'den daha yuksek cikma egilimindedir -- tam bagimsiz bir
stabilite kaniti olarak yorumlanmamalidir.

## 8. Model-Dependent Results

Her uc yontem de Random Forest icin **daha fazla** MAE kaybina yol aciyor (Filter k=5:
+643.82 USD, Embedded: +92.82 USD, Wrapper: +1198.96 USD vs No_Selection) -- Random
Forest, encoded feature uzayinin tamamindan daha fazla fayda sagliyor (olasi nedeni:
tree-based split'lerin fazladan feature'lari "gormezden gelme" kapasitesi, yani ekstra
feature'lar fazla zarar vermiyor, ama cikarilmalari bilgi kaybina yol aciyor).

## 9. Feature Count Trade-Off

| Yontem | Secilen (Encoded) Feature | Pooled MAE (RF) |
|---|---|---|
| Wrapper (n=8) | 8 | 7438.38 (en kotu) |
| Filter (k=5) | 5 | 6883.24 |
| Filter (k=10) | 10 | 6683.63 |
| Embedded (Lasso) | ~22.75 | 6332.24 |
| Filter (k=15) | 15 | 6421.88 |
| No_Selection | ~57 | 6239.42 (en iyi) |

Bu veri setinde **daha fazla encoded feature, tutarli olarak daha iyi Random Forest
performansi** ile iliskili -- agresif feature selection'in acik bir faydasi olculmedi.

## 10. Statistical Uncertainty

Sonuclar 4 (kismen ortusen) fold uzerinden hesaplandi -- formal p-value/confidence
interval hesaplanmadi. Yon tutarliligi (tum k/alpha/n degerlerinde No_Selection'in daha
iyi veya esdeger kalmasi) pratik kanit olarak kullanildi.

## 11. Risks and Limitations

- Sadece 3 sabit k degeri, 1 sabit Lasso alpha, 1 sabit RFE n_features denendi --
  exhaustive degil.
- Mutual information, kucuk fold-training orneklerinde (Fold 1: n=1735) gurultulu
  olabilir.
- Encoded-feature-level secim, raw-feature-level yorumla birebir eslenmeyebilir (bir
  categorical feature'in sadece bazi dummy kolonlari secilebilir).

## 12. Recommended Candidates

- **No Selection (F4, full encoded space):** Preferred -- en iyi olculen performans,
  ek selection katmani karmasikligi gerektirmiyor.
- **Filter (k=10-15):** Acceptable Alternative -- daha az feature, orta performans kaybi.
- **Embedded (Lasso):** Acceptable Alternative -- benzer profil.
- **Wrapper (RFE, n=8):** Rejected (bu konfigurasyonla) -- performans kaybi digerlerinden
  acikca daha yuksek.
