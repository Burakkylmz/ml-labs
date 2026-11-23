# LAB12 — Stage 07 Ablation Study

## 1. Purpose

Yeni feature group'larinin (Composition, Value, Diversity, Transport Extensions) model
performansina **gercek katkisini**, kontrollu add-one-group ve drop-one-group
deneyleriyle olcmek.

## 2. Experimental Controls

Tum konfigurasyonlar: aynı frozen Stage 05 4-fold CV, aynı training-eligible observation'lar
(fold-training population icinde), aynı preprocessing (median+StandardScaler/rare-category
OneHot), aynı probe estimator hyperparameters (Stage 06'dan degismeden), aynı random seed
(42), aynı evaluation metrikleri (MAE/RMSE/Bias/WAPE/High-Cost MAE). **Difference Convention:**
Delta_MAE = MAE_candidate - MAE_reference (negatif = iyilesme).

## 3. Reference Feature Set

**F0 (Core, 6 feature):** `Line_Item_Qty_Sum`, `Line_Item_Value_Sum`, `Shipment_Mode`,
`INCO_Term`, `Country`, `Product_Group` -- Stage 06'nin aynen korunan core seti.

Pooled MAE: Ridge = 7974.86 USD, Random Forest = 6151.74 USD.

## 4. Add-One-Group Experiments

| Candidate | Raw Feature | Ridge Pooled MAE | Delta vs F0 | RF Pooled MAE | Delta vs F0 |
|---|---|---|---|---|---|
| F0_core | 6 | 7974.86 | -- | 6151.74 | -- |
| F1_composition | 9 | 7916.69 | **-58.17** | 6137.97 | **-13.78** |
| F2_value | 9 | 7944.26 | -30.60 | 6251.47 | +99.73 |
| F3_diversity | 7 | 7974.86 | 0.00 | 6151.18 | -0.57 |
| F4_combined | 15 | 7921.12 | -53.74 | 6239.42 | +87.68 |

**Bulgu:** F1 (Composition), HER IKI estimator icin de F0'dan daha iyi -- tutarli, pozitif
katki. F2 (Value) Ridge'i hafifce iyilestiriyor ama Random Forest'i kotulestiriyor --
model-bagimli. F3 (Diversity), beklenen gibi F0'dan ayirt edilemez (sanity check gecti).
F4 (hepsi birlikte), Ridge icin iyi ama Random Forest icin F0'dan daha kotu -- bu, F2/F4'un
RF'ye eklediği gurultunun F1'in kazancini gölgeleyebileceğini gösteriyor.

## 5. Drop-One-Group Experiments

Referans: F4_combined (Ridge=7921.12, RF=6239.42).

| Candidate (F4'ten cikarilan) | Ridge Pooled MAE | Delta vs F4 | RF Pooled MAE | Delta vs F4 |
|---|---|---|---|---|
| F4_minus_composition | 7950.97 | +29.85 | 6255.98 | +16.57 |
| F4_minus_value | 7921.85 | +0.73 | **6143.78** | **-95.64** |
| F4_minus_transport_ext | 7915.71 | -5.40 | 6233.76 | -5.66 |

**Bulgu:** Composition'i cikarmak her iki estimator icin de performansi kotulestiriyor
(pozitif delta) -- Composition grubunun F4 icindeki katkisi gercek. Value'yu cikarmak
Random Forest'i **iyilestiriyor** (-95.64 USD) -- Value grubu Random Forest icin
**redundant/potentially harmful** (Section 09'daki yuksek korelasyon bulgusuyla tutarli).
Transport extensions'i cikarmak pratik olarak notrdir (her iki estimator icin de kucuk
negatif delta) -- bu grubun katkisi **Inconclusive**.

## 6. Ridge Results (Ozet)

En iyi Ridge konfigurasyonu: F4_minus_transport_ext (7915.71) ve F1_composition (7916.69)
-- pratik olarak esdeger. En kotu: F0_core/F3_diversity (7974.86).

## 7. Random Forest Results (Ozet)

En iyi Random Forest konfigurasyonu: F4_minus_value (6143.78) -- Value grubu haric butun
digerlerini icerir. En kotu (ablation icinde): F2_value (6251.47).

## 8. Fold-Level Results

Fold-fold MAE dalgalanmasi (F0 vs F4, Section 16) Stage 06'daki ~%30'luk paterne
benzer sekilde devam ediyor -- 4 fold uzerinden kesin istatistiksel guven sinirlidir.

## 9. Pooled Metrics

Yukaridaki tablolar `(MAE * Validation_Count)` agirlikli pooled ortalamalardir (fold
boyutlarindaki farklar hesaba katilmistir).

## 10. Tail Error (High-Cost Segment)

High-cost segment (fold-training P90+) MAE, Random Forest icin tum konfigurasyonlarda
~18,500-18,700 USD araliginda tutarli kaldi; Ridge icin ~23,000-25,000 USD araliginda --
bu, Stage 06'daki genel high-cost-segment bulgusuyla tutarlidir (ayrintili sayilar
`stage07_cv_results.csv`'de).

## 11. Performance-Complexity Trade-Off

F0 (6 feature) -> F1 (9 feature): kucuk, tutarli iyilesme -- iyi trade-off.
F0 -> F4 (15 feature): Ridge icin iyilesme ama RF icin kotulesme -- feature count 2.5x
artarken net kazanc sorgulanmali.

## 12. Stability

Add-one-group ve drop-one-group bulgulari birbiriyle tutarli: Composition her iki
deneyde de pozitif katki gosterdi; Value her iki deneyde de Random Forest icin
zararli/redundant gorundu.

## 13. Conclusions

- **Composition grubu:** "Adds Consistent Value" -- her iki estimatorde de, her iki
  ablation yonteminde de tutarli pozitif katki.
- **Value grubu:** "Adds Model-Dependent Value" (Ridge icin hafif pozitif) ama "Potentially
  Harmful/Redundant" (Random Forest icin, muhtemelen Line_Item_Value_Sum ile redundancy).
- **Diversity grubu:** "Redundant" (zaten "Rejected" -- sifir varyans).
- **Transport Extensions grubu:** "Inconclusive" -- kucuk, belirsiz etki.

## 14. Limitations

Ablation sonuclari causal business effect olarak sunulmamalidir -- correlated features
(Section 09), feature interactions, estimator-specific davranislar ve sadece 4 fold'luk
orneklem bu sonuclarin genellenebilirligini sinirlar.
