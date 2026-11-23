# LAB12 — Engineering Decision Registry

Bu belge, Stage 01-03 boyunca alınan (ve henüz alınmayan) kararları, gerçek kanıtlarla birlikte
kaydeder. Her karar ilgili notebook section'ı ve artifact ile ilişkilidir. Kullanılabilir kanıt
olmadan `Accepted` durumuna geçilmemiştir.

| Decision_ID | Question | Decision | Status | Confidence |
|---|---|---|---|---|
| D-001 | Business prediction time nedir? | Pre-Shipment Cost Estimation | Conditional | Medium |
| D-002 | Freight Cost (USD) ne temsil ediyor? | Shipment-level toplam navlun maliyeti (line-item değil) | Accepted | High |
| D-003 | Hangi Freight Cost satırları target-eligible? | Yalnızca Numeric Positive satırlar (~%60) | Accepted | High |
| D-004 | Her satır bağımsız bir shipment mı? | Hayır — `ASN/DN #` shipment-grouping anahtarıdır | Accepted | High |
| D-005 | Line-item mi, shipment-level mi modelleme birimi olmalı? | **[Stage 03.5]** Shipment-Level Modeling | **Accepted** | High |
| D-006 | Weight (Kilograms) model feature'ı olarak uygun mu? | Aday feature, prediction-time availability `Unknown`; **[Stage 03.5]** default-safe policy: ana feature set'inden çıkarılmıştır | **Partially Resolved** | Medium |
| D-007 | Chronological split mümkün mü? | Evet, `Scheduled Delivery Date` ile; **[Stage 03.5]** 2015 partial-year + 10 shipment'ta grup-içi tutarsızlık bulundu | **Conditional (düşürüldü)** | Medium |
| D-008 | Dataset Stage 04'e geçebilir mi? | **CONDITIONAL GO** (Stage 03.5 sonrası da değişmedi, ama koşullar artık somut) | Conditional | Medium-High |

*(Not: Bu özet tablo Stage 03.5 sonrası güncellenmiştir. D-005/D-006/D-007 için orijinal
Stage 01-03 muhakemesi aşağıda **değiştirilmeden** korunmuştur; güncellemeler "Stage 03.5
Update" bölümünde ayrıca belgelenmiştir — tarihsel audit trail silinmemiştir.)*

## D-001 — Business Prediction Time

- **Hypothesis:** Pre-Shipment Cost Estimation — sevkiyat planlaması sırasında, gerçek taşıma
  maliyeti henüz kesinleşmemişken tahmin üretmek.
- **Evidence:** Stage 1.3 feature availability tablosu; `Scheduled Delivery Date` %100 parse
  oranı (Stage 2.5).
- **Alternatives:** Post-shipment cost reconciliation (reddedildi — planlama için faydasız).
- **Limitations:** `Scheduled Delivery Date`'in freight booking'den önce mi belirlendiği veri
  setinden doğrulanamıyor.
- **Next Action:** Stage 04'te iş birimi/domain owner ile doğrulanmalı.

## D-002 — Target Definition

- **Hypothesis:** Freight Cost (USD), numeric olduğunda shipment-level bir toplamdır.
- **Evidence:** Stage 2.4 — multi-row ASN/DN gruplarının **hiçbirinde** 1'den fazla numeric
  Freight Cost satırı yok (1241 grupta tam 1, 209 grupta 0); sibling satırlar bu tek numeric
  satıra `"See ASN/DN-xxxx (ID#:yyyy)"` ile açıkça referans veriyor.
- **Alternatives:** Per-line-item paylaştırılmış maliyet (reddedildi — hiçbir kanıt yok).
- **Limitations:** Gerçekleşmiş/quoted ayrımı doğrulanamıyor.
- **Next Action:** Stage 04 feature/target tasarımına taşınacak.

## D-003 — Target Eligibility Rules

- **Hypothesis:** Yalnızca "Numeric Positive" satırlar regression target için uygundur;
  "Commodity Included"/"Invoiced Separately" **yapısal olarak farklı bir popülasyondur**,
  eksik veri değildir.
- **Evidence:** Stage 3.3 — 6198 Numeric Positive / 1442 Commodity-Included / 239 Invoiced
  Separately / 2445 Reference = tam olarak 10324.
- **Alternatives:** Commodity-Included/Invoiced-Separately'i sıfır olarak kodlamak (açıkça
  yasaklandı — iş anlamını yanlış temsil eder).
- **Limitations:** PoC kapsamı, navlunun ayrı faturalandırıldığı sevkiyatlarla (~%60) sınırlanır.
- **Next Action:** Stage 04'te modelleme popülasyonu olarak formalize edilmeli.

## D-004 — Observation Granularity

- **Hypothesis:** Her satır bağımsız bir shipment değildir; `ASN/DN #` fiziksel shipment'ı
  tanımlar.
- **Evidence:** Stage 2.4 — 7030 benzersiz `ASN/DN #` / 10324 satır; bir grupta en fazla 54
  satır.
- **Alternatives:** Her satırı bağımsız kabul etmek (reddedildi — gelecekteki bir split'te aynı
  shipment'ın satırlarının farklı fold'lara dağılması riskini oluşturur).
- **Limitations:** 209 grupta (1058 satır) hiçbir numeric anchor yok.
- **Next Action:** Gelecekteki herhangi bir split'te (Stage 05) `ASN/DN #` group key olarak
  kullanılmalı.

## D-005 — Shipment Grouping Strategy

- **Hypothesis:** Henüz karar verilmedi — line-item düzeyi (daha fazla satır, ama target
  tekrarı/leakage riski) ile shipment düzeyi (dedup, ama line-item feature'ları kaybı) arasında
  bir seçim gerekiyor.
- **Evidence:** D-004'ün bulgusu.
- **Status:** **Pending** — Stage 04'te, herhangi bir feature engineering'den önce çözülmeli.

## D-006 — Weight Feature Eligibility

- **Hypothesis:** Weight (Kilograms), Freight Cost ile anlamlı bir ilişki taşıyabilir, ama
  prediction-time availability'si doğrulanamıyor.
- **Evidence:** Stage 3.5 — log-log korelasyon ~0.73 (linear ~0.23); Weight'in missingness
  deseni Target'inkiyle benzer (aynı INCO Term mekanizmasına bağlı olabilir).
- **Alternatives:** Weight'i tamamen hariç tutmak (aşırı tutucu, gerçek sinyali atar); hiç
  şüphe duymadan dahil etmek (doğrulanamayan bir availability varsayımı riski taşır).
- **Status:** **Under Investigation** — Stage 06 feature finalizasyonundan önce domain-expert
  teyidi aranmalı.

## D-007 — Temporal Split Feasibility

- **Hypothesis:** `Scheduled Delivery Date` güvenilir bir chronological split field'ıdır.
- **Evidence:** Stage 2.6 — %100 parse oranı, 2006-2015 tam kapsama, aynı ASN/DN grubunun
  satırları arasında 0 tarih tutarsızlığı (gerçek veride ölçüldü).
- **Alternatives:** `PO Sent to Vendor Date` (birincil olarak reddedildi — 5732 sentinel/
  parse-edilemeyen satır).
- **Limitations:** 2015 muhtemelen kısmi yıl (dataset `..._20150929` tarihli) — test/held-out
  yılı olarak kullanılması sayıyı düşük gösterebilir.
- **Next Action:** Stage 05'te gerçek split tasarlanırken 2015 için caveat uygulanmalı.

## D-008 — Dataset Qualification

- **Decision:** **CONDITIONAL GO** (tam gerekçe `dataset_qualification.md`'de).
- **Status:** Conditional — Stage 04'e geçiş, 5 koşulun belgelenmesine bağlıdır.

---

## Stage 03.5 Update

Aşağıdaki kararlar, Stage 03.5'teki yeni kanıtlara dayanarak **güncellenmiştir** (yukarıdaki
Stage 01-03 muhakemesi değiştirilmemiş, yalnızca ek bilgiyle genişletilmiştir).

### D-005 — Shipment-Level Modeling Strategy (RESOLVED)

- **Previous Status:** Pending
- **New Status:** **Accepted — Shipment-Level Modeling**
- **New Evidence:** Stage 03.5 Section 04/07 — hiçbir shipment grubunda 1'den fazla numeric
  Freight Cost anchor yok (anomali sıfır); `Shipment Mode` ve `Vendor INCO Term` shipment içinde
  **%100 tek değerli** (Section 08); Reference Resolution Rate **%100** (Section 05).
- **Decision Rationale:** Target zaten shipment-level bir büyüklük (D-002); gözlemlenen hiçbir
  grouping/katmanlama çelişkisi yok; bu üç kanıt birlikte Candidate B'yi (shipment-level)
  net biçimde destekliyor.
- **Related Artifacts:** `shipment_group_profile.csv`, `reference_resolution_summary.csv`
- **Next Action:** Line Item Quantity/Value aggregation kuralı (D-010) çözülmeden
  training-ready bir feature matrix üretilmemelidir.

### D-006 — Weight Feature Eligibility (PARTIALLY RESOLVED)

- **Previous Status:** Under Investigation
- **New Status:** **Partially Resolved** (durum aynı kalıyor ama politika artık açık)
- **New Evidence:** Stage 03.5 Section 10 — korelasyon yeniden doğrulandı (linear 0.232,
  log-log 0.732, birebir Stage 03 ile aynı); satır-seviyesi weight coverage (%61.72) vs
  shipment-seviyesi (%90.64); weight missingness deseni target missingness deseniyle güçlü
  örtüşüyor (muhtemelen aynı INCO Term mekanizması).
- **Decision Rationale:** Correlation yüksekliği prediction-time availability kanıtı değildir
  (Mandatory Rule). Domain confirmation hâlâ yok.
- **Recommended Policy:** Weight ana production feature set'inden **çıkarılmıştır**; ayrı bir
  "Weight Included vs Excluded" sensitivity experiment Stage 06+ için **planlanmıştır** (henüz
  çalıştırılmamıştır).
- **Required Domain Confirmation:** Weight'in sevkiyat planlaması anında mı yoksa paketleme/
  teslimat sonrasında mı ölçüldüğü.
- **Related Artifacts:** `aggregation_semantics_audit.csv`

### D-007 — Temporal Split Feasibility (DOWNGRADED)

- **Previous Status:** Accepted
- **New Status:** **Conditional** (düşürüldü)
- **New Evidence:** Stage 03.5 Section 08/11 — **10 shipment'ta** (7030'un) `Scheduled
  Delivery Date` kendi grubu içinde tutarsız (Stage 03'ün "0 inconsistency" ön-bulgusuyla
  **çelişen, daha ayrıntılı bir kontrol** — eski bulgu silinmedi, ama bu yeni kontrol daha
  kapsamlıydı); 2015 aylık satır sayıları Eylül'den sonra çöküyor (Ekim=1, Kasım=0, Aralık=2),
  2014'ün tam-yıl dağılımıyla tezat oluşturuyor.
- **Decision Rationale:** `Scheduled Delivery Date` teknik olarak hâlâ güvenilir (parse
  oranı %100, grup-içi tutarlılık %99.86) ama bu teknik geçerlilik, alanın **business-valid**
  (gerçek booking anında bilinen) olduğunu kanıtlamaz; 10 shipment'lık istisna ve doğrulanmış
  partial-year riski, koşulsuz `Accepted` durumunu haklı çıkarmıyor.
- **Related Artifacts:** `shipment_field_consistency.csv`

### D-009 — Reference Resolution Policy (NEW, Accepted)

- **Question:** Reference satırları (`"See ASN/DN-xxxx (ID#:yyyy)"`) nasıl güvenilir biçimde
  çözümlenir?
- **Hypothesis:** Metindeki `(ASN/DN, ID)` çifti, gerçek bir satıra ve doğru shipment'a karşılık
  gelmelidir.
- **Evidence:** Stage 03.5 Section 05 — 2445/2445 satır regex ile parse edildi (%100); hepsi
  `"Resolved - Same Shipment"` (0 Missing Anchor, 0 Cross-Shipment, 0 Ambiguous, 0 Invalid
  Format).
- **Decision:** Structural resolution (metin-ASN vs gerçek-anchor-ASN eşleşmesi) ile anchor
  content type (numeric mi değil mi) **ayrı sorular olarak ele alınmalıdır** — ilk analizde bu
  ikisinin birleştirilmesi, 105 geçerli referansı yanlışlıkla "mismatch" olarak işaretlemişti.
- **Status:** Accepted
- **Confidence:** High
- **Limitations:** Bu politika yalnızca bu dataset'in gözlenen referans formatı için
  doğrulanmıştır.
- **Related Artifacts:** `reference_resolution_summary.csv`
- **Next Action:** Yok — bu karar kapalıdır.

### D-010 — Aggregation Semantics (NEW, Pending/Conditional — mixed)

- **Question:** Line-item kayıtlarından shipment-level representation oluşturulurken hangi
  kolonlar nasıl aggregate edilmeli?
- **Hypothesis:** Her kolon için doğru aggregation, kolonun semantic level'ına (shipment vs
  line-item) bağlıdır.
- **Evidence:** Stage 03.5 Section 08 Aggregation Decision Matrix (gerçek veri üzerinde
  hesaplandı).
- **Decision:** Weight (Kilograms) → First Non-Null (Conditional, eligibility ayrı); Shipment
  Mode / Vendor INCO Term → First Non-Null (Accepted, %100 tek-değerli); Scheduled Delivery
  Date → Min (Conditional, 10 istisna); Line Item Quantity / Line Item Value → Sum adayı, ama
  **Pending** (ürün türleri arası toplamanın iş anlamı doğrulanmadı).
- **Status:** Mixed (bkz. yukarıdaki detay) — genel karar `Conditional`.
- **Confidence:** Medium
- **Related Artifacts:** `aggregation_semantics_audit.csv`
- **Next Action:** Line Item Quantity/Value için domain-expert görüşü Stage 04'te alınmalı.

### D-011 — Target Coverage Definition (NEW, Accepted)

- **Question:** "Target coverage" tek bir sayı mı, yoksa birden fazla tanım mı gerektiriyor?
- **Hypothesis:** Row-level ve shipment-level coverage farklı popülasyonları temsil eder ve
  birbirinin yerine kullanılamaz.
- **Evidence:** Stage 03.5 Section 06 — Row-level %60.03 vs Shipment-level %88.17 (28.14 puan
  fark); fark INCO Term bazında da gösterildi (Section 09, örn. DDP %21.0→%49.2).
- **Decision:** Dört ayrı coverage tanımı resmi olarak benimsenmiştir: Row-Level, Shipment-
  Level, Reference Resolution Rate, Deployment Population Coverage (bu dördüncüsü şu an
  tanımlanamıyor). Bu tanımlar birbirinin yerine **kullanılamaz.**
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `target_coverage_by_granularity.csv`
- **Next Action:** Stage 04+ raporlamada her zaman hangi coverage tanımının kullanıldığı
  açıkça belirtilmelidir.

### D-012 — Selection Bias Evaluation Policy (NEW, Accepted)

- **Question:** INCOTERM-temelli selection bias, doğru observation unit üzerinde yeniden
  değerlendirildiğinde hâlâ önemli mi?
- **Hypothesis:** Shipment-level'de yeniden hesaplandığında bias azalacak ama kaybolmayacak.
- **Evidence:** Stage 03.5 Section 09 — DDP shipment-level coverage %49.2 (EXW/FCA ~%93'ün
  belirgin altında); fark row-level'deki kadar (%21 vs %89) dramatik değil, ama gerçek.
- **Decision:** Selection bias riski hem row-level hem shipment-level'de **doğrulanmıştır** --
  bu, bir causal ilişki kanıtı değildir, ama gözlemlenen güçlü bir association'dır. Gelecekteki
  model evaluation tasarımı, INCOTERM bazlı segment-level performansı izlemelidir.
- **Status:** Accepted
- **Confidence:** Medium-High
- **Related Artifacts:** `incoterm_coverage_reconciliation.csv`
- **Next Action:** Stage 04+ evaluation protokolüne INCOTERM segment monitoring eklenmelidir.

---

## Stage 04 Update — D-013 … D-022

Aşağıdaki kararlar Stage 04 (Evidence-Based EDA & Statistical Analysis) kapsamında
eklenmiştir. Stage 01-03.5 kararları (yukarıda) **değiştirilmemiştir.**

### D-013 — EDA Isolation Protocol (Accepted)

- **Question:** Stage 05 split'i henüz yokken, target-dependent EDA selection bias riski
  taşımadan nasıl yapılabilir?
- **Hypothesis:** Target dağılımına bakılmadan, önceden sabitlenmiş bir cutoff tarihi ile
  historical/protected-future ayrımı yapmak bu riski kontrol eder.
- **Evidence:** Stage 04 Section 04 — cutoff=2013-12-31, Population A=7030/B=5551/C=4987/
  D=1479; D hiçbir target-dependent analizde kullanılmadı (explicit assert ile doğrulandı).
- **Alternatives:** EDA'yı hiç izole etmeden tüm veri üzerinde yapmak (reddedildi — selection
  bias riski).
- **Decision:** Fixed cutoff = 2013-12-31, `stage04_eda_protocol.json`'da belgelendi.
- **Status:** Accepted
- **Confidence:** High
- **Limitations:** `Scheduled Delivery Date`'in business-valid zamanlaması D-007 kapsamında
  hâlâ Conditional — bu izolasyon teknik bir proxy kullanıyor.
- **Related Artifacts:** `stage04_eda_protocol.json`, `stage04_population_profile.json`
- **Next Action:** Stage 05, bu izolasyonu zayıflatacak biçimde değiştirilmemelidir.

### D-014 — Target Distribution & Transformation Candidates (Pending Validation)

- **Question:** Freight Cost'un dağılımsal özellikleri hangi transformation hipotezlerini
  destekliyor?
- **Evidence:** Population C (n=4987): Skewness≈5.36, Excess Kurtosis≈53.9, Mean/Median
  oranı≈1.8, P99≈76398 USD.
- **Candidate Methods:** Original / Log-Transformed / Log1p-Transformed.
- **Decision:** Hiçbiri seçilmedi; Stage 06 EXP-01'de original-scale MAE/RMSE/high-cost
  segment error ile karşılaştırılacak.
- **Status:** Pending Validation
- **Confidence:** Medium
- **Related Artifacts:** `stage04_target_statistics.json`

### D-015 — Numerical Feature Diagnostics (Pending Validation)

- **Question:** Weight/Line Item Quantity/Line Item Value, Freight Cost ile ne tür bir
  ilişki taşıyor?
- **Evidence:** Weight_KG Pearson r≈0.14 / Spearman ρ≈0.73 (nonlinear); Line_Item_Qty_Sum
  Spearman ρ≈0.64; Line_Item_Value_Sum Spearman ρ≈0.70 (tümü Population C, n=4987).
- **Decision:** Hiçbir feature seçimi henüz yapılmadı; Weight DIAGNOSTIC ONLY olarak
  kalıyor (D-006 koşuluna bağlı).
- **Status:** Pending Validation
- **Confidence:** Medium
- **Related Artifacts:** `stage04_numeric_associations.csv`

### D-016 — Categorical Feature Diagnostics (Pending Validation)

- **Question:** Shipment Mode/INCO Term/Country/Product Group segmentleri arasında freight
  cost farklılıkları var mı?
- **Evidence:** Air vs Truck Mann-Whitney U p≈0.0002 (medyan farkı ≈1140 USD); INCO Term
  segmentleri arasında medyan farkları gözlemlendi (Section 07).
- **Decision:** Gözlemlenen farklar gerçek ama encoding kararı için **tek başına** yeterli
  değil -- Stage 06'da validation performansıyla birlikte değerlendirilecek.
- **Status:** Pending Validation
- **Confidence:** Medium
- **Related Artifacts:** `stage04_categorical_segments.csv`

### D-017 — Outlier Treatment Experiment Candidates (Pending Validation)

- **Question:** Freight Cost'taki uç değerler nasıl ele alınmalı?
- **Evidence:** IQR upper fence≈30696 USD, Population C'nin %5.8'i üzerinde; bu değerler
  tüm Shipment Mode'larda dağılmış (bir moda yoğunlaşmamış).
- **Decision:** Hiçbir satır silinmedi/capping uygulanmadı. Keep-All, IQR Flagging, Quantile
  Capping, Log Transformation adayları Stage 06 EXP-05'te test edilecek.
- **Status:** Pending Validation
- **Confidence:** Medium
- **Related Artifacts:** `stage04_outlier_diagnostics.csv`

### D-018 — Missing Value Strategy Candidates (Pending Validation)

- **Question:** Weight_KG'nin eksik değerleri (23/4987) nasıl ele alınmalı?
- **Evidence:** Eksiklik oranı düşük ama Weight'in genel availability'si zaten D-006
  kapsamında Unknown.
- **Decision:** No Imputation / Median Imputation / Missing Indicator / Exclusion adayları
  belgelendi; hiçbiri seçilmedi.
- **Status:** Pending Validation
- **Confidence:** Low-Medium
- **Related Artifacts:** `stage04_preprocessing_hypotheses.csv`

### D-019 — Scaling Strategy Candidates (Pending Validation)

- **Question:** Hangi scaling yöntemi Ridge gibi scale-sensitive modeller için uygun bir
  deney adayı?
- **Evidence:** Numeric feature diagnostics, StandardScaler ve RobustScaler yöntemlerinin
  Ridge üzerinde karşılaştırılmasını destekliyor; tree-based modellerde No Scaling kontrol
  adayı olarak korunacak.
- **Decision:** Hiçbir scaler seçilmedi.
- **Status:** Pending Validation
- **Confidence:** Medium
- **Related Artifacts:** `stage04_preprocessing_hypotheses.csv`

### D-020 — Encoding Strategy Candidates (Pending Validation)

- **Question:** Shipment Mode/INCO Term/Country/Product Group için hangi encoding yaklaşımı
  aday?
- **Evidence:** Cardinality analizi (Country=43 yüksek, Product Group=5 düşük); `LabelEncoder`
  nominal feature'lar için varsayılan olarak **önerilmiyor.**
- **Decision:** OneHotEncoder/Rare Category Grouping/Native Categorical Handling adayları
  belgelendi; hiçbiri seçilmedi.
- **Status:** Pending Validation
- **Confidence:** Medium
- **Related Artifacts:** `stage04_feature_eligibility.csv`, `stage04_preprocessing_hypotheses.csv`

### D-021 — Temporal Stability Risks (Conditional)

- **Question:** Freight cost ve target availability zaman içinde kararlı mı?
- **Evidence:** Median Freight Cost 2006→2013 arasında ~2830→~7568 USD'ye yükseldi (~2.7x);
  numeric-target coverage %82.7→%96.0'a yükseldi (Population B/C).
- **Decision:** Temporal distribution shift riski **doğrulanmıştır** (nedeni kanıtlanmamış
  olsa da). Stage 05 split tasarımı bunu göz önünde bulundurmalı.
- **Status:** Conditional
- **Confidence:** Medium
- **Related Artifacts:** `stage04_temporal_diagnostics.csv`

### D-022 — Stage 06 Experiment Plan (Proposed)

- **Question:** Stage 06'da hangi preprocessing deneyleri hangi sırayla ve hangi kriterlerle
  çalıştırılacak?
- **Evidence:** D-014 ... D-021'in tamamı.
- **Decision:** 5 deneylik bir Experiment Matrix (EXP-01...EXP-05) oluşturuldu, her biri en az
  1 linear + 1 tree-based model, aynı CV folds ve seed ile planlandı.
- **Status:** Proposed
- **Confidence:** Medium
- **Related Artifacts:** `stage04_statistical_evidence.csv`,
  `docs/stage06_preprocessing_experiment_plan.md`
- **Next Action:** Stage 06 implementasyonunda bu matris baz alınmalıdır.

---

## Stage 05 Update — D-023 … D-032

Stage 01-04 kararları (yukarıda) **değiştirilmemiştir.** Aşağıdakiler Stage 05 (Temporal &
Group-Aware Data Splitting) kapsamında eklenmiştir.

### D-023 — Temporal Split Protocol (Accepted)

- **Question:** Hangi chronological boundaries Train/Validation/Protected Test için kullanılmalı?
- **Evidence:** Target-free calendar coverage (2006-05-02→2015-12-31), yearly shipment counts,
  partial-2015 kanıtı (Section 07).
- **Decision:** Train < 2014-01-01 (5551 shipment) / Validation 2014 (910) / Protected Test
  ≥2015-01-01 (569, gerçek max 2015-12-31). Toplam=7030.
- **Status:** Accepted
- **Confidence:** High
- **Limitations:** Boundary seçimi target dağılımına bakılmadan yapıldı; bu, istatistiksel bir
  optimality garantisi değildir.
- **Related Artifacts:** `stage05_split_metadata.json`, `stage05_split_manifest.csv`

### D-024 — Shipment Group Isolation Policy (Accepted)

- **Question:** Split/CV boyunca group integrity nasıl korunur?
- **Evidence:** 0 ASN/DN overlap (Train/Val/Test), 0 CV fold group overlap, 0 cross-shipment
  cost-anchor dependency (Stage 03.5'ten yeniden doğrulandı).
- **Decision:** `ASN/DN #` tek ve yeterli grouping key'dir; connected-component grouping
  katmanı **gerekli değildir** (gereksiz karmaşıklık önlendi).
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage05_group_integrity_report.json`

### D-025 — External Validation Policy (Accepted)

- **Question:** 2014 Validation dönemi nasıl kullanılacak?
- **Decision:** Stage 11'de önceden belirlenmiş finalistlerin **sınırlı** değerlendirmesi
  için; Stage 06-10'da **kullanılmayacak** (Model Selection Budget, Section 15).
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage05_evaluation_contract.json`

### D-026 — Protected Test Policy (Accepted)

- **Question:** 2015 Protected Test dönemi nasıl korunacak?
- **Evidence:** Raw dataset fiziksel olarak erişilebilir (mutlak güvenlik sınırı yok) --
  bu nedenle access contract + programmatic assertions + artifact rules ile korunuyor.
- **Decision:** "Tamamen görülmemiş veri" değil, **"model development, preprocessing
  selection, hyperparameter optimization ve performans-temelli kararlardan korunmuş"**
  tanımı kullanıldı. Stage 14'e kadar hiçbir target değeri okunmadı (doğrulandı).
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage05_leakage_audit.json`

### D-027 — Expanding-Window CV Design (Accepted)

- **Question:** Training dönemi (2006-2013) içinde hangi CV stratejisi kullanılmalı?
- **Evidence:** 4 fold (val years 2010-2013) feasibility testi -- her fold'da yeterli
  train/validation observation (en küçük: Fold 1, train=2028/eligible=1735).
- **Decision:** Expanding Window (default), group-aware, calendar-aware custom fold generator
  (`create_expanding_cv_folds`) ile. Rolling window'un daha kötü olacağı varsayılmadı
  (Advanced Challenge 1'de karşılaştırıldı).
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage05_cv_fold_manifest.csv`, `stage05_cv_fold_summary.csv`

### D-028 — Temporal Gap & Label Availability (Conditional)

- **Question:** Training/CV-Validation arasında bir temporal gap gerekli mi?
- **Evidence:** Gerçek bir freight settlement/booking timestamp bu veri setinde **yok**
  (Section 11 mandatory audit).
- **Decision:** `gap_days=0` default; 30/60 günlük senaryolar yalnızca **protokol tasarımı
  sensitivity senaryoları** olarak belgelendi, doğrulanmış lag değerleri olarak **sunulmadı.**
- **Status:** Conditional
- **Confidence:** Low-Medium
- **Limitations:** D-007'nin Conditional statüsü gerekli domain kanıtı olmadan Accepted'a
  yükseltilmedi.
- **Related Artifacts:** `stage05_temporal_integrity_report.json`

### D-029 — Target Eligibility After Split (Accepted)

- **Question:** Split membership target eligibility'den önce mi sonra mı belirlenmeli?
- **Decision:** **Önce** complete shipment population üzerinde temporal split membership
  belirlendi; target eligibility filtreleri **yalnızca** training-only CV feasibility için
  (Section 09) uygulandı. Validation/Test membership target eligibility ile **değiştirilmedi.**
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage05_training_population_profile.json`

### D-030 — Model Selection Budget (Accepted)

- **Question:** Validation(2014) ve Test(2015) hangi stage'lerde kullanılacak?
- **Decision:** Stage 06-10: training-only CV. Stage 11: frozen 2014 evaluation. Stage 12:
  calibration (test tuning olmadan). Stage 13: persistence. Stage 14: one-time test
  evaluation.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage05_evaluation_contract.json`

### D-031 — Reproducibility & Protocol Fingerprint (Accepted)

- **Question:** Split/CV protokolü nasıl versioned ve reproducible hale getirilir?
- **Evidence:** Deterministic protocol fingerprint (dataset hash + boundaries + fold
  boundaries + grouping/gap policy, runtime timestamp hariç) rerun'da aynı hash'i üretti.
- **Decision:** `stage05_protocol_fingerprint.json` içinde saklandı.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage05_protocol_fingerprint.json`

### D-032 — Stage 06 Evaluation Contract (Accepted)

- **Question:** Stage 06 preprocessing deneyleri hangi kurallara uyacak?
- **Decision:** Her fold için preprocessing yalnızca fold training data'ya fit edilecek;
  fold validation'a sadece transform uygulanacak. Bu, Stage 05'te **henüz uygulanmadı** --
  yalnızca contract tanımlandı.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage05_evaluation_contract.json`,
  `docs/stage05_evaluation_contract.md`

### D-033 — Stage 05 Protocol Recovery & Fingerprint Verification (Accepted)

- **Question:** Stage 06, Stage 05'in dondurulmuş split/CV protokolünü değiştirmeden mi
  kullanıyor?
- **Evidence:** Dataset SHA-256 (`9cffdb4a...578a`) Stage 01-03→05→06 boyunca değişmeden
  doğrulandı; Stage 05 protokol fingerprint'i (`b87ca0fd...8935e`) notebook içinde yeniden
  hesaplanıp birebir eşleşti.
- **Decision:** Stage 06, Stage 05 split/CV manifest'lerini **salt-okunur** olarak kullanır;
  hiçbir boundary/fold değiştirilmedi.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage05_protocol_fingerprint.json`, `stage05_cv_fold_manifest.csv`

### D-034 — Stage 06 Feature Allowlist Freeze (Accepted)

- **Question:** Stage 06 deneyleri hangi feature setinde çalışacak?
- **Decision:** Numeric: `Line_Item_Qty_Sum`, `Line_Item_Value_Sum`. Categorical:
  `Shipment_Mode`, `INCO_Term`, `Country`, `Product_Group`. `Weight_KG` (D-006) ana setten
  dışlandı, sadece sensitivity analizinde kullanıldı.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage06_feature_schema.json`

### D-035 — EXP-01 Missing Value Handling (Inconclusive / Deferred)

- **Question:** Median imputation + Missing Indicator, sadece median imputation'a göre
  ölçülebilir bir fark yaratıyor mu?
- **Evidence:** Ridge pooled MAE farkı tam sıfır (8001.52 = 8001.52); Random Forest'ta
  fark -1.08 USD (pratik önemsiz). Ana feature set'te gerçek missing value yok (%0.0).
- **Decision:** Missing Indicator varsayılan pipeline'a **dahil edilmedi.**
- **Status:** Inconclusive / Deferred
- **Confidence:** High (ölçüm güvenilir, ancak ayırt edici sinyal yok)
- **Related Artifacts:** `stage06_missingness_diagnostics.csv`, `stage06_cv_results.csv`

### D-036 — EXP-02 Categorical Encoding (Accepted)

- **Question:** OneHot, Ordinal, Rare-Category-Grouped OneHot arasında hangisi tercih
  edilmeli?
- **Evidence:** Ordinal, Ridge pooled MAE'yi +257.76 USD kötüleştirdi (semantik + ölçülen
  kanıt). Rare-category grouping, boyutu 57→43'e indirdi ve her iki estimator'da en iyi/
  en yakın ikinci sonucu verdi.
- **Decision:** `OneHotEncoder` + rare-category grouping (`min_frequency=10`) **tercih
  edilen**; `OrdinalEncoder` **reddedildi.**
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage06_encoding_diagnostics.csv`,
  `stage06_encoding_output_dimensions.csv`

### D-037 — EXP-03 Feature Scaling (Model-Dependent)

- **Question:** Scaling, Ridge ve Random Forest üzerinde nasıl farklılaşıyor?
- **Evidence:** Random Forest'ta fark <0.4 USD (ölçek-bağımsız). Ridge'de MinMaxScaler en
  iyi sonucu verdi (-310.45 USD none'a göre) ancak tek bir uç değere (≈290k USD) duyarlılık
  riski taşıyor.
- **Decision:** Random Forest için scaling **gereksiz**; Ridge için MinMaxScaler
  **Acceptable** (Preferred değil) kategorisinde.
- **Status:** Model-Dependent Decision
- **Confidence:** Medium (tek uç değer riski nedeniyle)
- **Related Artifacts:** `stage06_scaling_diagnostics.csv`

### D-038 — EXP-04 Outlier Treatment (Mixed)

- **Question:** Quantile capping (P1/P99), raw feature'lara göre ölçülebilir bir fayda
  sağlıyor mu?
- **Evidence:** Ridge pooled MAE -245.87 USD iyileşti; Random Forest'ta fark <0.2 USD.
  Capped fraction ~%2.
- **Decision:** Ridge için **Acceptable**; Random Forest için **Inconclusive** (gerekirse
  atlanabilir). Target hiçbir zaman capping'e uğramaz.
- **Status:** Mixed (model-bağımlı)
- **Confidence:** High
- **Related Artifacts:** `stage06_outlier_diagnostics.csv`

### D-039 — EXP-05 Target Transformation (Model-Dependent, Kritik Bulgu — Stage 07'de
derinleştirildi)

- **Question:** Log/log1p target dönüşümü, orijinal skalaya göre tahmin performansını
  iyileştiriyor mu?
- **Evidence (orijinal):** Ridge pooled MAE, log transform ile 8001.52'den **59,303.40
  USD'ye** fırladı (~7.4x kötüleşme).
- **Evidence (Stage 07 OOF-level re-analiz ile düzeltildi):** Blowup, uniform bir
  "retransformation bias" değil. Ridge+log için **median abs error aslında daha iyi**
  (3489.0 vs original'ın 4963.5 USD). Blowup, 3252 tahminin sadece **7'sinin (%0.2)**
  >1M USD absürt tahmin üretmesinden kaynaklanıyor (top-5 error, toplam error'ın %80.1'i).
  Bu extreme tahminler neredeyse tamamen **Fold 2'de** yoğunlaşıyor (RMSE=5,004,844 vs
  diğer fold'larda 30,689-56,626 USD). Kök neden: exponential inverse-transform, Fold
  2'nin training verisindeki nadir bir feature kombinasyonu için oluşan orta büyüklükteki
  log-space hatasını katlanarak büyütüyor; ayrıca Ridge log-uzayda squared-error minimize
  ettiği için (yaklaşık medyan/relative hata) USD-space MAE (ortalama-hataya dayalı) ile
  hedef uyumsuzluğu var.
- **Decision:** Log/log1p, **Ridge için kesin olarak reddedildi** (hem orijinal hem
  düzeltilmiş kanıtla); Random Forest için **Acceptable** (Preferred ilan edilecek kadar
  büyük değil, extreme blowup gözlenmedi). Varsayılan: original scale.
- **Status:** Model-Dependent Decision (Rejected for Ridge, Acceptable for Random Forest)
- **Confidence:** High
- **Limitations:** Bu düzeltme, var olan OOF prediction artifact'inin (yeniden fit
  gerektirmeden) derinlemesine re-analizidir — yeni bir CV deneyi çalıştırılmadı.
- **Related Artifacts:** `stage06_target_transform_diagnostics.csv`,
  `stage06_paired_comparisons.csv`, `stage06_oof_predictions.csv`

### D-040 — Preprocessing Fit Boundary Enforcement (Accepted)

- **Question:** Tüm preprocessing parametreleri gerçekten yalnızca fold-training'den mi
  fit edildi?
- **Evidence:** Her fold için yeni pipeline instance'ı oluşturuldu; OOF prediction
  shipment key'lerinin Training split'ine ait olduğu programatik `issubset` kontrolüyle
  doğrulandı; 2014/2015 target değerlerine hiçbir hücrede erişilmedi.
- **Decision:** CV fitting boundary kuralı **ihlal edilmedi.**
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage06_oof_predictions.csv`

### D-041 — Reproducibility Verification (Accepted)

- **Question:** Stage 06 pipeline'ları deterministik mi?
- **Evidence:** Referans pipeline iki kez fit edildi; tahminler `np.allclose` ile
  eşleşti. Local (`uv run`) ve Docker (`ml-lab`) ortamlarında ayrı ayrı "temiz kernel"
  execution'ları 0 hata/0 uyarı ile tamamlandı; dataset hash her iki ortamda sabit kaldı.
- **Decision:** `random_seed=42`; multi-threaded Random Forest için bit-bazında birebir
  eşitlik garanti edilmez (kabul edilen sınırlama), `np.allclose` yeterli kabul edildi.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage06_reproducibility_report.json`

### D-042 — Stage 07 Readiness & Deferred Decisions (Accepted)

- **Question:** Stage 06 sonunda Stage 07'ye geçiş için ne hazır, ne hâlâ açık?
- **Decision:** Feature allowlist, missing-value/encoding/outlier politikaları dondurulmuş
  adaylar olarak hazır. Scaling ve target transformation politikaları **model seçimi
  sonrası yeniden teyit edilmelidir** (model-dependent). D-006 (Weight) ve D-010 (Qty/Value
  aggregation) hâlâ açık. Stage 07'ye geçilmemiştir.
- **Status:** Accepted (GO — conditional on Section 14 handoff checklist)
- **Confidence:** High
- **Related Artifacts:** `stage06_preprocessing_contract.json`,
  `docs/stage06_preprocessing_contract.md`

### D-043 — Stage 07 Feature Eligibility Contract (Accepted)

- **Question:** Hangi raw SCMS kolonlari Stage 07 feature engineering icin aday
  olusturur, hangileri mandatory exclusion'dir?
- **Evidence:** 14 feature katalogu (`stage07_feature_catalog.csv`) Prediction_Time_
  Availability, Leakage_Risk ve Decision_Status alanlariyla dondu.
- **Decision:** `Freight Cost (USD)`, raw ID'ler, post-shipment tarihler mandatory
  exclusion; digerleri Section 04-dekiler gibi kategorize edildi.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage07_feature_catalog.csv`, `stage07_feature_availability_audit.csv`

### D-044 — Shipment Composition Features (Accepted)

- **Question:** `Line_Item_Count`, `Distinct_Item_Description_Count`,
  `Distinct_Molecule_Count` olcumsel katki sagliyor mu?
- **Evidence:** Add-one-group ablation: F1 (Core+Composition) her iki estimator icin de
  F0'dan daha iyi (Ridge -58.17 USD, RF -13.78 USD pooled). Drop-one-group: cikarilmasi
  her iki estimator icin de kotulesme (Ridge +29.85, RF +16.57).
- **Decision:** Accepted -- "Adds Consistent Value".
- **Status:** Accepted
- **Confidence:** Medium-High (4 fold, kucuk ama tutarli etki)
- **Related Artifacts:** `stage07_ablation_results.csv`, `docs/stage07_ablation_study.md`

### D-045 — Shipment Value Features (Model-Dependent / Conditional)

- **Question:** `Line_Item_Value_Mean/Max`, `Value_Dispersion` -- katki mi redundancy mi?
- **Evidence:** Ridge icin hafif pozitif katki (-30.60 USD, F2 vs F0). Random Forest icin
  F4'ten cikarilmasi performansi IYILESTIRDI (-95.64 USD) -- Line_Item_Value_Sum (core) ile
  yuksek korelasyon (Section 09) nedeniyle redundant. Ayrica %13.97 "Freight Included in
  Commodity Cost" bundling riski (D-010 baglantili).
- **Decision:** Conditional -- Ridge icin Acceptable, Random Forest icin Potentially
  Redundant/Harmful. Production eligibility onayi YOK.
- **Status:** Conditional
- **Confidence:** Medium
- **Related Artifacts:** `stage07_ablation_results.csv`, `stage07_numeric_associations.csv`

### D-046 — Product Diversity Features (Rejected)

- **Question:** `Product_Group_Diversity` predictive bir feature olabilir mi?
- **Evidence:** 7030/7030 shipment tam olarak 1 Product Group iceriyor (sifir varyans,
  ampirik olarak dogrulandi). F3 vs F0 ablation sanity-check: Ridge farki TAM SIFIR,
  RF farki numeric noise (-0.57 USD).
- **Decision:** REJECTED -- zero-variance feature, modele dahil edilemez.
- **Status:** Rejected
- **Confidence:** High (dogrudan, kesin ampirik kanit)
- **Related Artifacts:** `stage07_feature_lineage.csv` (F-C1)

### D-047 — Calendar Feature Availability (Conditional, D-007 Korunuyor)

- **Question:** `Scheduled_Month`/`Scheduled_Quarter`/`Scheduled_Year` production
  feature seti icin uygun mu?
- **Evidence:** Calendar_Sensitivity konfigurasyonu, her iki estimator icin de hafif
  kotulesme gosterdi (RF +43.83, Ridge +38.78 USD vs F4). `Scheduled_Year`, split
  boundary ile dolayli iliskisi nedeniyle ayrica Excluded edildi.
- **Decision:** Month/Quarter Conditional/Sensitivity-Only (D-007 korunuyor); Year
  Excluded.
- **Status:** Conditional
- **Confidence:** Medium
- **Related Artifacts:** `stage07_ablation_results.csv` (Calendar_Sensitivity)

### D-048 — Weight Sensitivity Policy (D-006 Korunuyor)

- **Question:** Weight_KG'nin buyuk olcumsel faydasi, D-006 kararini degistirir mi?
- **Evidence:** Weight_Sensitivity konfigurasyonu Random Forest'i carpici sekilde
  iyilestirdi (-542.09 USD pooled MAE), Ridge'i ihmal edilebilir etkiledi (-0.41 USD).
- **Decision:** Performans etkisi ne olursa olsun, D-006 (prediction-time availability
  Unknown) **DEGISMEDI** -- Weight_KG Sensitivity-Only kalmaya devam ediyor.
- **Status:** Accepted (D-006 unchanged)
- **Confidence:** High
- **Related Artifacts:** `stage07_ablation_results.csv` (Weight_Sensitivity)

### D-049 — Filter Feature Selection (Acceptable Alternative)

- **Question:** `SelectKBest(mutual_info_regression)` No_Selection'a kiyasla nasil
  performans gosteriyor?
- **Evidence:** k=5/10/15 icin Ridge MAE 8155-8214 (No_Selection: 7921); RF MAE
  6421-6883 (No_Selection: 6239). Jaccard stability (k=10): 0.483.
- **Decision:** Acceptable Alternative -- No_Selection'dan biraz daha kotu ama daha az
  feature ile makul bir trade-off sunuyor.
- **Status:** Acceptable Alternative
- **Confidence:** Medium
- **Related Artifacts:** `stage07_feature_selection_results.csv`

### D-050 — Embedded Feature Selection (Acceptable Alternative)

- **Question:** `SelectFromModel(Lasso(alpha=50.0))` nasil performans gosteriyor?
- **Evidence:** Ridge MAE 8065.87, RF MAE 6332.24 (No_Selection'dan biraz daha kotu,
  ~22.75 encoded feature secerek).
- **Decision:** Acceptable Alternative.
- **Status:** Acceptable Alternative
- **Confidence:** Medium
- **Related Artifacts:** `stage07_feature_selection_results.csv`

### D-051 — Wrapper Feature Selection (Rejected, bu konfigurasyonla)

- **Question:** Limited `RFE(n_features_to_select=8)` nasil performans gosteriyor?
- **Evidence:** Ridge MAE 8645.20, RF MAE 7438.38 -- test edilen 3 yontem arasinda
  en kotu, No_Selection'dan acikca daha yuksek.
- **Decision:** Bu n=8/step=2 konfigurasyonuyla Rejected; daha genis n ile yeniden
  denenmesi gelecek bir arastirma konusu olabilir (Stage 07 kapsaminda degil).
- **Status:** Rejected (bu konfigurasyonla)
- **Confidence:** Medium
- **Related Artifacts:** `stage07_feature_selection_results.csv`

### D-052 — Feature Group Ablation (Accepted, bkz D-044/D-045/D-046/D-047)

- **Question:** Hangi feature group'lari F4'e dahil etmek/cikarmak degistiriyor?
- **Decision:** Composition "Adds Consistent Value"; Value "Model-Dependent" (RF icin
  redundant); Diversity "Rejected"; Transport Extensions "Inconclusive" (kucuk etki).
- **Status:** Accepted
- **Confidence:** Medium-High
- **Related Artifacts:** `stage07_ablation_results.csv`, `docs/stage07_ablation_study.md`

### D-053 — Feature Importance & Stability (Accepted)

- **Question:** Permutation importance ve ablation sonuclari birbiriyle tutarli mi?
- **Evidence:** Value grubu YUKSEK permutation importance gosterdi (RF: 1158.83, Ridge:
  1840.54) AMA ablation'da cikarilmasi RF'yi iyilestirdi -- correlated feature'larin
  (Line_Item_Value_Sum ile) importance'i "paylastigi" klasik senaryo (master prompt'un
  ongordugu).
- **Decision:** Permutation importance TEK BASINA feature'in production degerine karar
  vermek icin yeterli degildir -- ablation ile birlikte degerlendirilmelidir.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage07_permutation_importance.csv`

### D-054 — Performance-Complexity Trade-Off (Accepted)

- **Question:** Daha fazla feature, anlamli bir MAE iyilestirmesiyle sonuclaniyor mu?
- **Evidence:** F0 (6 feature) -> F1 (9 feature) iyi bir trade-off; F0 -> F4 (15 feature)
  Ridge'i iyilestirirken RF'yi kotulestiriyor -- 2.5x feature artisi net kazanc
  saglamiyor.
- **Decision:** Feature count artisi, otomatik olarak daha iyi secim degildir --
  model-ozgu degerlendirme gerektirir.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage07_performance_complexity.csv`

### D-055 — Stage 08-09 Feature Set Handoff (Accepted)

- **Question:** Stage 08-09'a hangi feature set adaylari tasinacak?
- **Decision:** Candidate A (Minimal Core) -- Recommended for Next Stage; Candidate B
  (Extended Eligible) -- Acceptable Alternative; Candidate C (Reduced, Filter k=10) --
  Conditional; Candidate D (Sensitivity-Only, Weight dahil) -- SADECE sensitivity analizi,
  production karsilastirmasina DAHIL EDILMEZ. **Final production feature set
  KESINLESMEMISTIR.**
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage07_recommended_feature_sets.json`,
  `stage07_feature_contract.json`, `docs/stage07_feature_contract.md`

### D-056 — Stage 08 Baseline Evaluation Contract (Accepted)

- **Question:** Stage 08 baseline degerlendirmesi Stage 05'in dondurulmus protokolunu
  degistirmeden mi kullaniyor?
- **Evidence:** Dataset SHA-256 ve Stage 05 protokol fingerprint'i notebook icinde
  yeniden hesaplanip birebir eslesti; development population (5551/4987) Stage 05
  raporuyla eslesti.
- **Decision:** Stage 08, Stage 05 split/CV manifest'lerini degistirmeden kullandi.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage08_fold_statistics.csv`

### D-057 — Global Median Baseline (B0) (Accepted)

- **Question:** B0'in gercek CV performansi nedir?
- **Evidence:** Pooled MAE=9226.37 USD, RMSE=17773.47, Bias=-7136.96 (net underprediction).
- **Decision:** Accepted as baseline, ancak Statistical Reference olarak secilmedi
  (B1 daha iyi performans gosterdi).
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage08_cv_results.csv`

### D-058 — Global Mean Baseline (B1) (Accepted — Statistical Reference)

- **Question:** B1, B0'a kiyasla nasil performans gosteriyor?
- **Evidence:** Pooled MAE=9106.34 USD -- B0'dan daha iyi. Training population uzerinde
  median teorik olarak MAE-optimal olsa da, bu CV'de (temporal shift nedeniyle) mean
  daha iyi sonuc verdi.
- **Decision:** B1, **Statistical Reference Baseline** olarak secildi. Bu bulgu
  **genel bir kural olarak sunulmamalidir** -- bu CV'ye ozgudur.
- **Status:** Accepted
- **Confidence:** Medium (temporal-shift-sensitive, genellenebilirligi sinirli)
- **Related Artifacts:** `stage08_cv_results.csv`, `stage08_baseline_acceptance.json`

### D-059 — Shipment Mode Median Baseline (B2) (Accepted)

- **Question:** Shipment Mode segmentasyonu olcumsel katki sagliyor mu?
- **Evidence:** Pooled MAE=8791.55 USD (B0'dan -434.82 USD daha iyi), fallback rate=0.000.
- **Decision:** Accepted -- tek-segment baseline'lar arasinda en guclusu.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage08_segment_support.csv`

### D-060 — INCOTERM Median Baseline (B3) (Conditional)

- **Question:** INCOTERM segmentasyonu olcumsel katki sagliyor mu?
- **Evidence:** Pooled MAE=9145.64 USD -- B0'dan sadece -80.73 USD daha iyi, marjinal.
  INCOTERM'in target availability ile olasi iliskisi (Stage 03.5/04) ayrica risk olarak
  not edildi.
- **Decision:** Conditional -- istatistiksel katki zayif, deployment semantics ayrica
  degerlendirilmeli.
- **Status:** Conditional
- **Confidence:** Medium
- **Related Artifacts:** `stage08_segment_support.csv`

### D-061 — Hierarchical Segment Baseline (B4) (Accepted — Business Reference)

- **Question:** Mode+INCOTERM birlikte kullanimi, tek-segment baseline'lardan daha iyi
  mi?
- **Evidence:** Pooled MAE=8694.56 USD -- butun baseline'lar arasinda en iyisi, B2'ye
  kiyasla -96.99 USD (kucuk ama 4 fold'un hepsinde tutarli) iyilesme. Fallback rate=0.041.
- **Decision:** B4, **Business Reference Baseline** ve **Robust Fallback Baseline**
  olarak secildi.
- **Status:** Accepted
- **Confidence:** Medium-High (kazanc kucuk, ama tutarli)
- **Related Artifacts:** `stage08_baseline_ranking.csv`, `stage08_fallback_diagnostics.csv`

### D-062 — Unseen Category & Fallback Policy (Accepted)

- **Question:** Unseen/missing category'ler ve low-support segment'ler nasil ele
  alinmali?
- **Evidence:** Sirali fallback (combined->mode->incoterm->global) 8 unit-level fixture
  testiyle (known/unknown/low-support/missing/single-observation) ve gercek fold
  diagnostikleriyle dogrulandi -- 0 NaN/infinite prediction, 0 crash.
- **Decision:** Accepted.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage08_fallback_diagnostics.csv`

### D-063 — Minimum Segment Support (Accepted, Non-Universal)

- **Question:** B4 icin min_support degeri nasil belirlenmeli?
- **Evidence:** `min_support=10`, gercek training verisinde 17 (Mode x INCOTERM)
  kombinasyonundan 8'inin (%47) 10'dan az gozlem icermesiyle gerekcelendirildi.
- **Decision:** `min_support=10` kabul edildi -- **evrensel bir istatistiksel kural
  olarak sunulmamaktadir**, sadece bu veri setine ozgu bir karar.
- **Status:** Accepted (non-universal)
- **Confidence:** Medium
- **Related Artifacts:** `stage08_segment_support.csv`

### D-064 — Baseline Error Metrics (Accepted)

- **Question:** Hangi metrikler tum baseline'lar icin tutarli hesaplandi?
- **Decision:** MAE, RMSE, Median AE, WAPE, Bias (pred-actual), High-Cost MAE (fold-
  training P90 threshold) -- 5 baseline'in hepsinde ayni tanimla hesaplandi.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage08_cv_results.csv`

### D-065 — Tail-Risk Evaluation (Accepted, Kritik Bulgu)

- **Question:** Baseline'lar high-cost shipment'larda sistematik olarak basarisiz mi?
- **Evidence:** **5 baseline'in HEPSINDE %100 underprediction rate** (fold-training
  P90+ segmentinde).
- **Decision:** Bu, basit constant/median-tabanli predictor'larin sag-kuyruklu
  dagilimda **yapisal bir ozelligidir**, duzeltilebilir bir hata degildir. Stage 09
  modelleri bu zayifligi olcumsel olarak raporlamalidir.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage08_tail_error_analysis.csv`

### D-066 — Baseline Comparative Ranking (Accepted)

- **Question:** B0-B4 arasindaki genel siralama nedir?
- **Evidence:** Pooled MAE siralamasi: B4 (8694.56) < B2 (8791.55) < B1 (9106.34) < B3
  (9145.64) < B0 (9226.37).
- **Decision:** Accepted -- ancak final karar sadece en dusuk MAE'ye gore verilmedi
  (complexity/fallback/robustness birlikte degerlendirildi).
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage08_baseline_ranking.csv`

### D-067 — Business Baseline Acceptance (Accepted, SLA Yok)

- **Question:** Stage 09 icin hangi baseline'lar referans olarak kabul edildi?
- **Decision:** Statistical Reference=B1, Business Reference=B4, Robust Fallback=B4.
  **%5 MAE improvement provisional bir engineering threshold'dur -- business-approved
  bir SLA degildir.**
- **Status:** Accepted (Provisional threshold, Pending Business Validation for SLA)
- **Confidence:** Medium (SLA onayi eksik)
- **Related Artifacts:** `stage08_baseline_acceptance.json`

### D-068 — Stage 09 Benchmark Contract (Accepted)

- **Question:** Stage 09'a hangi degerlendirme kurallari tasinacak?
- **Decision:** Dataset/protocol fingerprint, baseline registry, kabul edilen referans
  baseline'lar, metrik tanimlari, model comparison rules (Stage 06-07 probe sonuclari
  SADECE contextual referans) belgelendi.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage08_benchmark_contract.json`, `docs/stage09_benchmark_contract.md`

### D-069 — Stage 09 Benchmark Protocol (Accepted)

- **Question:** Stage 09 model training, Stage 05-08'in dondurulmus kararlarini
  degistirmeden mi yapiliyor?
- **Evidence:** 5 gate (A-E: Dataset, Evaluation, Feature Contract, Baseline Contract,
  Dependency Compatibility) programatik olarak dogrulandi ve PASSED.
- **Decision:** Accepted -- butun gate'ler gecti, training'e izin verildi.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage09_environment_compatibility.json`

### D-070 — Model Family Registry (Accepted)

- **Question:** Hangi 6 model, hangi ailelerle benchmark'a dahil edildi?
- **Decision:** M01 Ridge, M02 ElasticNet (Regularized Linear); M03 Random Forest, M04
  ExtraTrees (Bagging); M05 XGBoost, M06 LightGBM (Gradient Boosting).
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage09_model_registry.json`

### D-071 — Fixed Estimator Configurations (Accepted)

- **Question:** Model hyperparameters nasil belirlendi?
- **Decision:** Sabit, optimize edilmemis baslangic degerleri (Stage 06 probe
  parametreleri uyumlu oldugu yerde yeniden kullanildi, ancak modeller Stage 09'un
  kendi protokolune yeniden fit edildi -- eski probe sonuclari dogrudan kullanilmadi).
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `config/settings.yaml` (lab12.stage09.models)

### D-072 — Model-Specific Preprocessing (Accepted)

- **Question:** Scaling politikasi model ailesine gore nasil uygulanmali?
- **Evidence:** Stage 06 EXP-03: scaling Ridge icin faydali olabilir, RF icin
  onemsiz.
- **Decision:** Ridge/ElasticNet icin `StandardScaler`; RF/ExtraTrees/XGBoost/LightGBM
  icin scaling YOK.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage09_feature_preprocessing_registry.json`

### D-073 — Linear Model Comparison (Accepted)

- **Question:** Ridge vs ElasticNet, freight cost prediction'da nasil performans
  gosteriyor?
- **Evidence:** M01=8029.16 USD (96 negatif tahmin, %2.95), M02=7993.60 USD (0 negatif
  tahmin).
- **Decision:** ElasticNet hafifce daha iyi VE daha guvenli (negatif tahmin riski yok).
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage09_model_comparison.csv`

### D-074 — Bagging Model Comparison (Accepted)

- **Question:** Random Forest vs ExtraTrees, hangisi daha iyi?
- **Evidence:** M03=6151.90 USD, M04=5880.35 USD.
- **Decision:** ExtraTrees, Random Forest'tan daha iyi performans gosterdi.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage09_model_comparison.csv`

### D-075 — Boosting Model Comparison (Accepted)

- **Question:** XGBoost vs LightGBM, hangisi daha iyi?
- **Evidence:** M05=5808.51 USD, M06=6236.25 USD.
- **Decision:** XGBoost, LightGBM'den belirgin olarak daha iyi -- ve butun 6 modelin
  en iyisi.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage09_model_comparison.csv`

### D-076 — Primary Benchmark Feature Set (Accepted)

- **Question:** Primary benchmark hangi feature set'i kullanmali?
- **Decision:** Stage 07 Minimal Core (6 feature) -- tum 6 model bu ayni feature set
  uzerinden degerlendirildi (fair comparison).
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage09_cv_results.csv`

### D-077 — Secondary Feature Set Evaluation (Conditional/Exploratory)

- **Question:** Extended Eligible feature set, best-of-family modellerde ek fayda
  sagliyor mu?
- **Evidence:** M02 -46.47 USD (hafif iyilesme), M04 +44.14 USD (hafif kotulesme), M05
  +130.22 USD (kotulesme) -- tutarsiz, model-bagimli.
- **Decision:** Extended feature set, Stage 09'da **confirmatory kanit saglamadi** --
  Stage 10'un varsayilan feature setine yukseltilmedi.
- **Status:** Conditional (exploratory, adaptive-selection riski)
- **Confidence:** Medium
- **Related Artifacts:** `stage09_feature_set_sensitivity.csv`

### D-078 — Baseline Relative Improvement (Accepted)

- **Question:** Modeller B4/B1'e gore gercek iyilesme sagliyor mu?
- **Evidence:** Tum 6 model B4'u asti (%7.7-%33.2 araliginda); en iyi model M05
  (XGBoost), B4'e gore %33.2, B1'e gore %36.2 iyilesme gosterdi.
- **Decision:** Accepted -- iyilesme gercek ve 4 fold'un hepsinde tutarli.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage09_baseline_improvements.csv`

### D-079 — Generalization Gap Evaluation (Accepted)

- **Question:** Training-validation gap, overfitting kaniti olarak kullanilabilir mi?
- **Decision:** Gap hesaplandi (`stage09_generalization_gap.csv`) ama **tek basina
  overfitting kaniti olarak yorumlanmadi** -- temporal distribution shift confound'u
  acikca belirtildi.
- **Status:** Accepted (with explicit confound caveat)
- **Confidence:** Medium
- **Related Artifacts:** `stage09_generalization_gap.csv`

### D-080 — High-Cost Shipment Risk (Accepted, Kritik Bulgu)

- **Question:** Stage 09 modelleri, Stage 08 baseline'larinin %100 underprediction
  sorununu azaltiyor mu?
- **Evidence:** Tum 6 model underprediction rate'i %100'un altina dusurdu (araligi
  %83.1-%92.5) -- ama HICBIRI sorunu tamamen ortadan kaldirmadi.
- **Decision:** Gercek ama KISMI iyilesme olarak kabul edildi -- "cozuldu" olarak
  sunulmadi.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage09_tail_risk_analysis.csv`

### D-081 — Temporal Stability (Accepted)

- **Question:** Model performansi 4 fold arasinda tutarli mi?
- **Evidence:** M05 en stabil ust-performans model (fold-std=665.48); M02 en az
  stabil (fold-std=1634.11).
- **Decision:** Fold-level tutarlilik, Section 16 shortlisting kriterine dahil edildi.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage09_cv_results.csv`

### D-082 — Computational Complexity (Accepted)

- **Question:** Ek model complexity'si operasyonel olarak maliyetli mi?
- **Evidence:** Tum modellerin fit/predict suresi <1 saniye.
- **Decision:** Bu olcekte complexity farki operasyonel bir engel degil.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage09_runtime_benchmark.csv`

### D-083 — Model Shortlisting (Accepted)

- **Question:** Stage 10 icin hangi modeller secildi?
- **Evidence:** M05 (XGBoost, %33.2 iyilesme, fold-std=665) ve M04 (ExtraTrees, %32.4
  iyilesme, fold-std=935) -- her ikisi de kendi ailesinde en iyi, meaningful-improvement/
  stability/negligible-negative-rate kriterlerini karsiladi.
- **Decision:** Shortlisted: M05, M04 (2 farkli aile). M01 Inconclusive (negatif tahmin
  riski); M02/M03/M06 Conditional Candidate (zayif veya redundant).
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage09_model_shortlist.csv`, `stage09_model_shortlist.json`

### D-084 — Stage 10 Optimization Handoff (Accepted)

- **Question:** Stage 10'a hangi sozlesme tasinacak?
- **Decision:** Dataset/protokol fingerprint, shortlisted model'lar, sabit baslangic
  konfigurasyonlari, feature/preprocessing policy, metrik/tail-risk kisitlari,
  selection-bias kontrolleri belgelendi. **Optimization search Stage 09'da
  CALISTIRILMADI.**
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage09_stage10_handoff.json`, `docs/stage10_optimization_contract.md`
