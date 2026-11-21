# LAB12 — Stage 05 Split Strategy

## 1. Business Problem

Pre-Shipment Freight Cost Prediction — geçmiş sevkiyatların maliyetlerinden öğrenip gelecekteki
sevkiyatlar için tahmin üretmek. Geçmiş/gelecek yönü, evaluation protokolü boyunca korunmalıdır.

## 2. Dataset Contract

SCMS Delivery History, SHA-256 doğrulandı (Stage 01-03 ile birebir eşleşti). Shipment Data
Contract (Stage 03.5) esas alınmıştır — yeni bir aggregation mantığı uydurulmamıştır.

## 3. Observation Unit

Shipment. Primary key: `ASN/DN #` (0 eksik, 0 contract violation, %100 reference resolution).

## 4. Temporal Field

`Scheduled Delivery Date` — 0 parse hatası, 2006-05-02 → 2015-12-31 kapsama, %99.86 shipment-içi
tutarlılık (7030'un 10'u tutarsız, Stage 03.5'ten taşındı).

## 5. Temporal Validity Limitations

Bu alanın cost estimation anında bilindiği, planlama sırasında güncellenip güncellenmediği, ve
gerçek label finalization tarihinin bundan önce mi sonra mı olduğu **doğrulanamamaktadır**
(D-007, Conditional). Bu alan yalnızca **chronological bir proxy** olarak kullanılmıştır.

## 6. EDA Isolation Compatibility

Stage 04 EDA cutoff'u (**2013-12-31**) ile Stage 05'in Train sınırı **birebir aynıdır** (notebook
içinde `assert` ile doğrulandı) — Stage 04'ün tüm target-dependent analizi (Population B/C)
Training dönemi içinde kalır.

## 7. Candidate Splitting Strategies

Random shuffle split (reddedildi — temporal/group leakage riski, yalnızca eğitsel karşı-örnek
olarak gösterildi) vs Chronological + Group-Aware split (kabul edildi).

## 8. Final Split Boundaries

| Split | Aralık | Shipment Sayısı |
|---|---|---:|
| Training | < 2014-01-01 | 5551 |
| Validation | 2014-01-01 → 2014-12-31 | 910 |
| Protected Test | ≥ 2015-01-01 (gerçek max: 2015-12-31) | 569 |

Toplam: 7030 (canonical popülasyonla tam örtüşür).

## 9. Group Integrity

0 ASN/DN overlap across splits; 0 cross-shipment cost-anchor dependency (Stage 03.5); 0 CV fold
group overlap.

## 10. Target Eligibility

Split membership **önce** complete shipment population üzerinde (target-free) belirlendi;
target eligibility filtreleri **yalnızca** Training popülasyonu içinde (CV feasibility için)
uygulandı. Validation/Test membership'i target eligibility ile **değiştirilmedi.**

## 11. Sample Counts

Training eligible: 4987/5551. Validation eligible: 819/910 (bu notebook'ta **incelenmedi**).
Protected Test eligible: 392/569 (bu notebook'ta **incelenmedi**).

## 12. Partial-Year Risk

2015, dataset'in `...20150929` toplanma tarihiyle tutarlı biçimde Eylül sonrası keskin bir
düşüş gösteriyor — tam yıl **varsayılmamıştır.**

## 13. Selection Bias Considerations

Stage 03.5/04'ün INCOTERM-temelli selection bias bulgusu, split tasarımını **etkilememiştir**
(split target-free belirlendi) — ama bu risk Stage 06+ model evaluation'a taşınmalıdır.

## 14. Statistical Limitations

Gerçek bir label settlement timestamp'i bulunmadığından, point-in-time correctness **kesin
olarak kanıtlanamaz.** 0-day gap'in leakage-free olduğu garanti edilmez.

## 15. Accepted Decision

Önerilen 2006-2013 (Train) / 2014 (Validation) / 2015-partial (Protected Test) protokolü
**Accept** edilmiştir — gerçek bir structural blocker bulunmamıştır.

## 16. Open Risks

D-007 (temporal validity) Conditional kalmaya devam ediyor; Line Item Quantity/Value
aggregation (D-010) hâlâ Pending.
