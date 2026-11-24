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
  (Line_Item_Value_Sum ile) importance'i "paylastigi" klasik senaryo.
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

### D-085 — Stage 10 Optimization Protocol (Accepted)

- **Question:** Stage 10 optimization, Stage 05-09'un dondurulmus kararlarini
  degistirmeden mi yapiliyor?
- **Evidence:** 5 gate (A-E) + Gate F (dependency compatibility) programatik olarak
  dogrulandi ve PASSED.
- **Decision:** Accepted -- butun gate'ler gecti, optimization'a izin verildi.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage10_environment_report.json`, `stage10_protocol_integrity.json`

### D-086 — Pooled OOF MAE Search Objective (Accepted)

- **Question:** Search objective'i, Stage 08-09'un pooled MAE tanimiyla nasil tutarli
  tutulur?
- **Decision:** `RandomizedSearchCV`'nin varsayilan fold-score-averaging mekanizmasi
  **kullanilmadi** -- `ParameterSampler` + mevcut frozen CV runner (bounded manual
  search) kullanildi, pooled-metric tanimi korundu.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage10_optimization_registry.json`

### D-087 — Search Budget (Accepted)

- **Question:** Search budget ne zaman ve nasil dondu?
- **Decision:** 16 trial/model (T000 referans dahil) x 4 fold = 128 fit, hicbir trial
  sonucu gorulmeden sabitlendi.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage10_search_budget.json`, `stage10_trial_manifest.csv`

### D-088 — ExtraTrees Search Space (Accepted)

- **Question:** ExtraTrees icin hangi search space tanimlandi ve sonuc ne oldu?
- **Evidence:** 5-boyutlu bounded space; en iyi trial M04-T003 (n_estimators=200,
  min_samples_split=10, min_samples_leaf=2, max_features=0.8, max_depth=12) =
  5686.34 USD, 4/4 fold'da tutarli +3.30% iyilesme.
- **Decision:** Accepted -- M04-T003, Preferred Tuned Candidate.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage10_search_spaces.json`, `stage10_trial_results.csv`

### D-089 — XGBoost Search Space (Inconclusive)

- **Question:** XGBoost icin hangi search space tanimlandi ve sonuc ne oldu?
- **Evidence:** 9-boyutlu bounded space; **hicbir sampled trial (15 aday) referansi
  (T000) gecemedi** -- +0.00% iyilesme.
- **Decision:** Tuning Benefit Inconclusive -- Stage 09 referansi korunuyor.
- **Status:** Inconclusive
- **Confidence:** High (negatif sonuc, ama saglam kanitla)
- **Related Artifacts:** `stage10_search_spaces.json`, `stage10_trial_results.csv`

### D-090 — Reference Configuration Policy (Accepted, Kritik Bulgu)

- **Question:** Stage 09'un raporlanan referans skorlari bu oturumda yeniden
  uretilebiliyor mu?
- **Evidence:** M04 (ExtraTrees) **%0.000 fark** ile birebir reprodukte edildi. M05
  (XGBoost) **%0.17 fark** gosterdi (bu oturum: 5818.29, Stage 09'un orijinal raporu:
  5808.51). Kontrollu bir `n_jobs=1/2/4` deneyi, XGBoost'un `hist` tree_method'unun
  thread-sayisina bagli floating-point non-determinism gosterdigini **kanitladi**.
  Ayrica Docker'da calistirildiginda, M05'in "en iyi trial"i bile degisti (M05-T010
  Docker'da, M05-T000 local'de, ~%0.10 fark).
- **Decision:** Bu bir konfigurasyon/leakage hatasi DEGILDIR -- dokumante edilmis bir
  XGBoost sinirlamasidir. Local sonuclar bu notebook'un canonical artifact'lari olarak
  kabul edildi; Docker sonucu confirmatory bir diagnostic olarak kayit altina alindi.
- **Status:** Accepted (documented limitation, not a bug)
- **Confidence:** High (kontrollu deneyle dogrulandi)
- **Related Artifacts:** `stage10_reproducibility_report.json`

### D-091 — Trial Execution & Reproducibility (Accepted)

- **Question:** Secilen trial'lar tekrar calistirildiginda ayni sonucu veriyor mu?
- **Evidence:** M04'un en iyi trial'i (M04-T003) iki kez fit edildi, tahminler
  `np.allclose` ile birebir eslesti.
- **Decision:** Accepted.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage10_reproducibility_report.json`

### D-092 — Hyperparameter Sensitivity (Accepted, Descriptive)

- **Question:** Hangi parametreler Pooled MAE ile en yuksek korelasyonu gosteriyor?
- **Evidence:** M04: `max_depth` (corr=-0.84), `min_samples_leaf` (corr=+0.45). M05:
  `min_child_weight` (corr=+0.70), `max_depth` (corr=-0.54).
- **Decision:** Bu korelasyonlar **descriptive**'dir -- 16 trial'lik kucuk bir
  orneklemden geldigi icin causal bir hyperparameter importance iddiasi olarak
  sunulmamaktadir.
- **Status:** Accepted (descriptive only)
- **Confidence:** Medium
- **Related Artifacts:** `stage10_parameter_sensitivity.csv`

### D-093 — Hyperparameter Interactions (Inconclusive)

- **Question:** `learning_rate x n_estimators`, `max_depth x min_child_weight` gibi
  interaction'lar gozlemlenebiliyor mu?
- **Evidence:** Korelasyonlar hesaplandi (`stage10_parameter_interactions.csv`) ama
  ornek buyuklugu (16 trial) kesin bir interaction kaniti icin yetersiz.
- **Decision:** Inconclusive -- descriptive olarak raporlandi, kesin sonuc cikarilmadi.
- **Status:** Inconclusive
- **Confidence:** Low (kucuk ornek)
- **Related Artifacts:** `stage10_parameter_interactions.csv`

### D-094 — Optimization Improvement Assessment (Accepted)

- **Question:** Hangi model tuning'den gercek fayda gordu?
- **Decision:** M04: +3.30% (Preferred Tuned Candidate). M05: +0.00% (Retain
  Reference, Inconclusive).
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage10_baseline_comparison.csv`

### D-095 — Generalization Gap & Temporal Stability (Accepted)

- **Question:** M04'un tuned configuration'i overfitting riski tasiyor mu?
- **Evidence:** M04 tuned Gen_Gap=2512.67 (referans 2179.13'ten biraz yuksek) ama 4/4
  fold'da validation MAE'si hala daha iyi.
- **Decision:** Gap artisi tek basina overfitting kaniti olarak yorumlanmadi --
  temporal distribution shift confound'u acikca belirtildi.
- **Status:** Accepted (with explicit confound caveat)
- **Confidence:** Medium
- **Related Artifacts:** `stage10_generalization_diagnostics.csv`, `stage10_temporal_stability.csv`

### D-096 — High-Cost Shipment Risk (Accepted)

- **Question:** Tuning, high-cost shipment performansini kotulestirdi mi?
- **Evidence:** M04 tuned High-Cost MAE=17626.69 (referans 18353.31'den **daha iyi**).
  M05 degismedi (17119.78).
- **Decision:** Tuning, high-cost riskini kotulestirmedi -- her iki model icin de
  kabul edilebilir.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage10_tail_risk_analysis.csv`

### D-097 — Negative Prediction Policy (Accepted)

- **Question:** Negatif tahminler otomatik veto sebebi mi?
- **Evidence:** M04: 0 negatif tahmin (referans ve tuned). M05: 3 negatif tahmin
  (degismedi).
- **Decision:** Negatif tahminler sayildi ve raporlandi, otomatik veto edilmedi --
  raw (unclipped) scoring politikasi korundu.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage10_negative_prediction_audit.csv`

### D-098 — Search Selection Optimism (Accepted, Acikca Belgelendi)

- **Question:** Stage 10'un en iyi trial secimi bagimsiz bir dogrulama midir?
- **Decision:** **HAYIR.** 16 configuration'in en iyisinin secilmesi development-CV'ye
  adaptiftir -- Stage 11 (2014) ve Stage 14 (2015) bu nedenle korunmaktadir.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `docs/stage11_external_validation_contract.md`

### D-099 — Provisional Model Selection (Accepted)

- **Question:** Stage 11'e hangi configuration'lar gonderiliyor?
- **Decision:** Primary: M04 (ExtraTrees, M04-T003, 5686.34 USD). Alternative: M05
  (XGBoost, M05-T000, 5818.29 USD). **Final model secimi burada YAPILMAMAKTADIR.**
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage10_model_selection.json`, `stage10_selected_configurations.json`

### D-100 — Stage 11 External Validation Handoff (Accepted)

- **Question:** Stage 11'e hangi sozlesme tasinacak?
- **Decision:** Dataset/protokol fingerprint, dondurulmus feature set/preprocessing,
  iki candidate configuration, metrik tanimlari, tie-breaking kurali belgelendi.
  2014 bu notebookta hicbir sekilde kullanilmadi.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage10_stage11_handoff.json`, `docs/stage11_external_validation_contract.md`

### D-101 — Full Development Refit Policy (Accepted)

- **Question:** Stage 11, Stage 10'un fold-bazli fit edilmis modellerini 2014
  inference icin yeniden kullanabilir mi?
- **Decision:** **HAYIR.** M04-T003 ve M05-T000 (ve B1/B4), butun eligible
  development population (N=4987, 2006-2013) uzerinde sifirdan yeniden egitildi.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage11_development_refit_report.json`

### D-102 — Evaluation Population Audit (Accepted)

- **Question:** 2014'teki 910 shipment'in tamami otomatik olarak scorable midir?
- **Evidence:** 910 toplam shipment, ancak sadece 819'u (`Has_Numeric_Target`)
  numeric target'a sahip (%90.0 label coverage).
- **Decision:** Eligibility, 910'u VARSAYMADAN bagimsiz olarak olculdu. Scoring
  sadece 819 eligible shipment uzerinde yapildi.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage11_validation_population_audit.json`

### D-103 — High-Cost Threshold Freezing Order (Accepted)

- **Question:** High-cost threshold, 2014 target degerleri okunmadan once mi
  dondu?
- **Decision:** EVET. `HIGH_COST_THRESHOLD` (23,897.32 USD), full eligible
  development targetlarinin P90'i olarak, 2014 degerleri okunmadan once hesaplandi.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** notebook Section 05

### D-104 — External Model Ranking Result (Accepted, Acikca Belgelendi)

- **Question:** Development-CV ranking (M04 < M05) 2014'te korunuyor mu?
- **Evidence:** M04-T003=6485.63 USD, M05-T000=6591.33 USD.
- **Decision:** **EVET**, ranking korundu -- M04-T003 2014'te de en iyi model.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage11_external_metrics.csv`

### D-105 — Paired Error / Win-Rate Nuance (Accepted, Acikca Belgelendi)

- **Question:** MAE ranking tek basina yeterli bir karsilastirma midir?
- **Evidence:** M05-T000 shipment-level win-rate=%51.3 (M04-T003'ten yuksek), ancak
  MAE'de M04-T003 daha iyi -- bir dizi buyuk disagreement (en fazla ~21,490 USD)
  M05-T000'in aggregate MAE'sini agirlikli olarak yukari cekiyor.
- **Decision:** Win-rate ve MAE birlikte raporlandi; hicbiri tek basina nihai karar
  olarak kullanilmadi.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage11_paired_error_analysis.csv`

### D-106 — Negative Prediction Re-Audit on 2014 (Accepted)

- **Question:** M05'in bilinen negatif tahmin riski 2014'te gozlemleniyor mu?
- **Evidence:** 0/819 negatif tahmin, her iki model icin de (0.0%).
- **Decision:** Bu sample-ozel bir gozlemdir -- riskin ortadan kalktigi iddia
  edilmemektedir; raw unclipped scoring korunmustur.
- **Status:** Accepted
- **Confidence:** Medium (tek sample'a dayanir)
- **Related Artifacts:** `stage11_negative_prediction_audit.csv`

### D-107 — High-Cost Underprediction Independent Replication (Accepted, Kritik Bulgu)

- **Question:** Stage 08-10'un baseline %100 high-cost underprediction bulgusu
  2014'te tekrarlaniyor mu?
- **Evidence:** B1=%100.0, B4=%100.0 (2014); M04-T003=%89.9, M05-T000=%89.9.
- **Decision:** Bulgu **bagimsiz olarak dogrulandi** -- ML modelleri riski azaltiyor
  ama ortadan kaldirmiyor.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage11_tail_risk_analysis.csv`

### D-108 — Generalization Gap Reporting (Accepted)

- **Question:** Dev-CV -> External MAE farki nasil raporlanmali?
- **Evidence:** M04-T003: +799.29 USD (+14.1%). M05-T000: +773.04 USD (+13.3%).
- **Decision:** Gap raporlandi, ancak overfitting'e tek basina atfedilmedi --
  farkli yil, farkli training size, selection exposure, temporal shift confound'lari
  acikca belirtildi.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage11_generalization_gap.csv`

### D-109 — Covariate Shift Finding (Accepted, Acikca Belgelendi)

- **Question:** 2014'teki feature dagilimlari development'tan farkli mi?
- **Evidence:** Line_Item_Qty_Sum median +75% (5478->9575), Line_Item_Value_Sum
  median +17% (74200->86482); kategorik feature'larda 0 yeni kategori, ancak daha
  dar cardinality (ornegin Country: 37->22).
- **Decision:** Gercek bir covariate shift gozlemlendi ve risk dokumantasyonu olarak
  raporlandi -- model/feature degisikligi icin KULLANILMADI.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage11_covariate_shift.csv`, `stage11_category_drift.csv`

### D-110 — Label Coverage Stability (Accepted)

- **Question:** Label coverage orani zamanla degisiyor mu?
- **Evidence:** Development=%89.8, 2014=%90.0.
- **Decision:** Coverage oran istikrarli -- missing-not-at-random mekanizmasinin
  zamanla degistigine dair kanit yok (ancak mekanizmanin kendisi hala bilinmiyor).
- **Status:** Accepted
- **Confidence:** Medium
- **Related Artifacts:** notebook Section 08

### D-111 — Cross-Environment Reproducibility Audit (Accepted, Kritik Bulgu)

- **Question:** Stage 10'un XGBoost thread-dependent non-determinism bulgusu,
  Stage 11'in gercek local/Docker calistirmasinda da gozlemleniyor mu?
- **Evidence:** M04-T003 max abs prediction diff=2.91e-11 USD (etkin olarak ozdes).
  M05-T000 max abs prediction diff=**9338.69 USD**, median=308.28 USD -- aggregate
  MAE farki yalnizca ~%0.10 (6591.33 vs 6598.21) iken, tekil shipment tahminleri
  cok daha fazla degisebiliyor.
- **Decision:** Bulgu dogrulandi ve nicellendirildi; ranking (M04<M05) iki ortamda
  da ayni kaldi -- "Inconclusive" degil, ama M05'in tekil-tahmin seviyesinde
  reproducibility riski acikca belgelendi. Hicbir ortam cherry-pick edilmedi; local
  canonical olarak korundu.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage11_reproducibility_report.json`

### D-112 — Fair Comparison Gate Enforcement (Accepted)

- **Question:** 4 predictor (M04-T003, M05-T000, B1, B4) ayni shipment set'i
  uzerinde mi karsilastirildi?
- **Decision:** EVET, programatik `assert` ile dogrulandi -- 819 eligible shipment,
  hepsi icin ozdes.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** notebook Section 06

### D-113 — Bootstrap Uncertainty Scope Limitation (Accepted)

- **Question:** External MAE farki icin bir uncertainty tahmini sunulmali mi?
- **Evidence:** M04-T003 bootstrap (n=500) mean=6472.71, [P2.5,P97.5]=[5843.21,
  7175.73]; M05-T000'in nokta MAE'si (6591.33) bu aralik icinde.
- **Decision:** Bootstrap sunuldu ama **resmi bir confidence interval olarak
  degil** (i.i.d. varsayimi zayif) -- acceptance karari bununla degistirilmedi.
- **Status:** Accepted
- **Confidence:** Medium
- **Related Artifacts:** notebook Advanced Challenge 4

### D-114 — Model Acceptance Decision (Accepted)

- **Question:** Hangi candidate Stage 12'ye kabul ediliyor?
- **Decision:** **Accepted for Stage 12 (Primary: M04-T003).** M05-T000 ikincil
  karsilastirma olarak korunuyor, atilmiyor.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage11_model_acceptance.json`

### D-115 — No Business SLA Claim (Accepted, Kritik Kisitlama)

- **Question:** Bu stage "production-ready" veya "SLA satisfied" sonucu uretebilir
  mi?
- **Decision:** **HAYIR.** Business-approved monetary tolerance yok. Stage 08'in
  %5 kriteri sadece provisional engineering target'tir.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage11_model_acceptance.md`

### D-116 — 2015 Protected Test Isolation Confirmed (Accepted)

- **Question:** 2015 verisi bu notebookta herhangi bir sekilde okundu/analiz
  edildi mi?
- **Decision:** **HAYIR.** `shipment_view` 2015 kayitlarini yapisal olarak
  icerebilir, ancak hicbir hucre 2015 `Freight_Cost_USD` degerini okumadi,
  aggregate etmedi veya kullanmadi.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** notebook Section 03

### D-117 — Stage 12 Explainability/Uncertainty Candidate Priority (Accepted)

- **Question:** Stage 12, hangi candidate'a oncelik vermeli?
- **Decision:** M04-T003 (ExtraTrees) birincil explainability hedefi; M05-T000
  (XGBoost) ikincil karsilastirma -- ikisi arasindaki yakinlik (bootstrap
  overlap) nedeniyle M05 atilmadi.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage12_explainability_uncertainty_contract.md`

### D-118 — Stage 12 Calibration Data Policy (Accepted)

- **Question:** Stage 12, 2014 external validation label'larini calibration
  fitting icin kullanabilir mi?
- **Decision:** **HAYIR.** 2014 label'lari sadece diagnostic/evaluation amacli
  kullanilabilir -- calibration fitting icin training-period OOF residuals veya
  zaman-izole bir development subset kullanilmali.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage12_explainability_uncertainty_contract.md`

### D-119 — Stage 12 Explainability Contract (Accepted)

- **Question:** Stage 12'de hangi model aciklanacak ve hangi kisitlamalar
  gecerli olacak?
- **Decision:** M04-T003 (ExtraTrees) birincil aciklama hedefi, M05-T000
  (XGBoost) ikincil karsilastirma. Model degistirilmedi, yeniden tune edilmedi.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage12_integrity_report.json`

### D-120 — Frozen Model Attribution (Accepted)

- **Question:** Stage 11'in fitted estimator'i persist edilmedigi icin
  explainability amacli yeniden fit, Object A ile ayni mi?
- **Evidence:** Refit model, Stage 11'in 2014 external predictions'i ile
  **0.000000 USD** farkla eslesti (n=819).
- **Decision:** Refit, numerical identity check ile dogrulanmis bicimde
  Object A'nin gecerli bir temsilidir.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** notebook Section 04

### D-121 — Global Importance Methodology (Accepted)

- **Question:** Hangi global importance yontemleri kullanilacak?
- **Decision:** Impurity-based Tree Importance + Permutation Importance
  (development population, MAE scoring) + Mean Absolute SHAP (TreeExplainer).
  Uc yontem birbirini tamamlar, tek basina hicbiri yeterli kabul edilmedi.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage12_tree_importance.csv`, `stage12_permutation_importance.csv`, `stage12_global_shap_importance.csv`

### D-122 — SHAP Attribution Semantics (Accepted)

- **Question:** SHAP additivity dogrulandi mi ve output scale dogru mu?
- **Evidence:** Max additivity diff=1.89e-10 USD (n=200), tum SHAP degerleri
  finite, output scale=raw USD.
- **Decision:** SHAP additivity PASSED -- model attribution olarak
  guvenilir, ama **nedensel kanit olarak kullanilmadi**.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage12_shap_additivity_audit.json`

### D-123 — Encoded Feature Grouping (Accepted)

- **Question:** One-hot dummy columns'un SHAP degerleri raw feature
  seviyesine nasil toplanacak?
- **Decision:** Row-bazinda SIGNED toplam (her dummy'nin mean absolute
  SHAP'ini toplamaktan FARKLI) -- bu metodoloji acikca dokumante edildi.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage12_grouped_shap_importance.csv`

### D-124 — SHAP Additivity Audit (Accepted)

- **Question:** SHAP degerleri, baseline + sum(phi) = prediction ozelligini
  karsiliyor mu?
- **Evidence:** Primary max diff=1.89e-10 USD, Secondary (XGBoost) max
  diff=0.070312 USD -- ikisi de tolerance (<1.0 USD) icinde.
- **Decision:** Additivity PASSED, her iki model icin.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage12_shap_additivity_audit.json`

### D-125 — Local Explanation Policy (Accepted)

- **Question:** Hangi shipment'lar local explanation icin secilecek?
- **Decision:** 5 deterministic case (Typical, High-Predicted,
  Low-Predicted, High-Error-2014, Model-Disagreement-2014) -- 2014'ten
  secilen vakalar SADECE aciklama/risk amaclidir, yeni tuning icin
  kullanilmamistir.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage12_local_explanations.csv`

### D-126 — Correlated Feature Reliability (Accepted)

- **Question:** Stage 07'nin correlated-feature bulgusu SHAP/Permutation
  merceginden nasil gorunuyor?
- **Evidence:** Qty ve Value feature'lari her iki yontemde de en yuksek iki
  importance -- Stage 07'nin redundancy bulgusuyla tutarli.
- **Decision:** Bulgu dogrulandi ama CAUSAL bir cikarim olarak sunulmadi.
- **Status:** Accepted
- **Confidence:** Medium
- **Related Artifacts:** notebook Advanced Challenge 2

### D-127 — Explanation Stability (Accepted)

- **Question:** SHAP attribution'lari farkli background sample ve
  perturbation assumption altinda stabil mi?
- **Evidence:** 3 background seed arasinda rank range=0 (PERFECT stabilite);
  tree_path_dependent vs interventional, Line_Item_Qty_Sum icin ~1231 USD
  materyal fark gosterdi.
- **Decision:** Background-sample stabilitesi yuksek; perturbation-assumption
  sensitivity gercek ve dokumante edilmis bir sinirlamadir.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage12_explanation_stability.csv`

### D-128 — Uncertainty Quantification Scope (Accepted)

- **Question:** Stage 12'nin uncertainty calismasi hangi nesneye uygulanir?
- **Decision:** Object B (development-only research replicas) -- Object A
  (frozen full-development point predictor) DEGISTIRILMEDI veya
  recalibrate edilmedi.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** notebook Section 17

### D-129 — Time-Aware Calibration Protocol (Accepted)

- **Question:** Calibration/inner-training/evaluation donemleri nasil
  ayrilacak?
- **Decision:** Stage 05'in 4 frozen outer fold'u icinde, training
  history'nin son calendar year'i calibration, kalani inner training --
  tum invariant'lar (no overlap, no inversion) programatik dogrulandi.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage12_temporal_calibration_manifest.csv`

### D-130 — Calibration Data Separation (Accepted, Demonstrasyonla Dogrulandi)

- **Question:** Calibration leakage'in gercek etkisi nedir?
- **Evidence:** Leaky (in-sample) P90=7,900.34 USD vs honest (held-out)
  P90=9,511.30 USD -- leaky versiyon **%16.9 daha dar**.
- **Decision:** Notebook'un gercek calibration'inda SADECE honest
  (held-out) residuals kullanildi; leaky yaklasim demonstrasyon amacli
  izole edildi.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** notebook Section 15

### D-131 — Conformal Quantile Policy (Accepted)

- **Question:** Quantile index nasil hesaplanacak ve sample size yetersizse
  ne olacak?
- **Decision:** $k=\lceil (n_{cal}+1)(1-\alpha)\rceil$, capped at $n_{cal}$;
  `minimum_calibration_samples` esigi altinda `ValueError` firlatilir
  (sessiz fallback yok). 10 unit test ile dogrulandi.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** notebook Section 16 (unit tests)

### D-132 — Empirical Coverage Evaluation (Accepted, Kritik Bulgu)

- **Question:** Prediction interval'lar nominal coverage seviyesine ulasiyor
  mu?
- **Evidence:** 80% nominal -> %73.0 empirical (gap -7.0%); 90% nominal ->
  %83.1 empirical (gap -6.9%).
- **Decision:** Sistematik undercoverage gozlemlendi ve acikca raporlandi
  -- coverage guarantee iddia EDILMEDI.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage12_interval_metrics.csv`

### D-133 — Conditional Coverage Risk (Accepted)

- **Question:** Segment-seviyesinde coverage, overall'dan farkli mi?
- **Evidence:** 92 segment-satirindan 30'u minimum support (n<20) esigini
  gecemedi.
- **Decision:** Yetersiz-support segmentler acikca flaglendi; marginal
  conformal guarantee'nin segment-seviyesinde gecerli olmadigi acikca
  belirtildi.
- **Status:** Accepted
- **Confidence:** Medium
- **Related Artifacts:** `stage12_conditional_coverage.csv`

### D-134 — High-Cost Interval Reliability (Accepted, En Kritik Bulgu)

- **Question:** High-cost shipment'lar icin interval coverage guvenilir mi?
- **Evidence:** High-cost (90% nominal) coverage ortalamasi=**%43.6** (vs
  overall %83.1) -- Stage 11'in %89.9 point-level underprediction bulgusuyla
  dogrudan tutarli.
- **Decision:** High-cost segment icin interval'lar GUVENILMEZ olarak
  isaretlendi -- bu bulgu Model Risk R2'ye dogrudan kanit saglar.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage12_tail_coverage_analysis.csv`

### D-135 — Production Interval Approval Status (Accepted)

- **Question:** Object B'nin interval'lari production kullanimi icin
  onaylanabilir mi?
- **Decision:** **"Production Interval Not Approved."** Overall ve
  high-cost undercoverage, bu statuyu gerektirecek kadar buyuk. Bu karar
  SADECE Object B icindir, Object A'nin (Stage 11) kabul durumunu
  degistirmez.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage12_output_classification.csv`, `stage12_model_risk_summary.json`

### D-136 — Stage 13 Model Inference Handoff (Accepted)

- **Question:** Stage 13'e hangi sozlesme tasinacak?
- **Decision:** Point predictor + explainability "Approved for Stage 13
  Prototype"; uncertainty/interval "Research Only / Disabled by Default."
  Stage 13 readiness: **CONDITIONAL GO.**
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage12_stage13_handoff.json`, `stage13_model_inference_contract.md`

### D-137 — Stage 13 Artifact Packaging Contract (Accepted)

- **Question:** Stage 13 hangi scope'ta artifact uretecek?
- **Decision:** Tek bir versioned bundle (`stage13_model_bundle/v1/`) --
  model + preprocessing + manifest + schema + environment metadata
  BIRLIKTE. Yeni model training/tuning YAPILMADI.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage13_artifact_design.md`

### D-138 — Frozen Model Serialization (Accepted)

- **Question:** Hangi serialization format kullanilacak?
- **Decision:** `joblib` -- mevcut proje bagimliligi, sklearn/numpy icin
  verimli. skops.io/ONNX teorik olarak degerlendirildi (Advanced Challenge 4)
  ama mevcut format DEGISTIRILMEDI.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage13_serialization_security.md`

### D-139 — Full Pipeline Persistence (Accepted)

- **Question:** Model ve preprocessing ayri mi persist edilecek?
- **Decision:** **HAYIR.** Tek bir fitted `Pipeline` (preprocessing +
  ExtraTrees) persist edildi -- training-inference skew riski bu sekilde
  elimine edildi.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage13_model_bundle/v1/model.joblib`

### D-140 — Model Bundle Versioning (Accepted)

- **Question:** Bundle versioning policy nedir?
- **Evidence:** `write_bundle()`, mevcut non-empty version directory
  uzerine overwrite'i REFUSE eder (test edildi).
- **Decision:** Artifact version immutable; degisiklik gerekiyorsa yeni
  version directory ACILIR.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage13_artifact_integrity` test suite

### D-141 — Artifact Manifest (Accepted)

- **Question:** Manifest hangi bilgileri tasimali?
- **Decision:** Model identity, data/feature/preprocessing lineage,
  runtime versions, risk governance -- hepsi gercek artifact'lardan
  dolduruldu, placeholder YOK.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage13_model_bundle/v1/manifest.json`

### D-142 — SHA-256 Integrity Policy (Accepted)

- **Question:** Artifact integrity nasil dogrulanacak?
- **Decision:** `model.joblib`'in SHA-256'si manifest'te saklanir,
  yukleme ONCESI yeniden hesaplanip karsilastirilir. Circular dependency
  yok (manifest kendi hash'ini icermez).
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage13_artifact_security_tests.csv`

### D-143 — Trusted Artifact Loading (Accepted)

- **Question:** `joblib.load()` dogrudan cagrilabilir mi?
- **Decision:** **HAYIR.** `TrustedBundleLoader`, path/manifest/identity/
  SHA-256/dependency kontrollerini `joblib.load()`'dan ONCE yapar. 6/6
  security failure-mode test PASSED.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage13_serialization_security.md`

### D-144 — Dependency Compatibility Policy (Accepted, Gercek Bulguyla Duzeltildi)

- **Question:** Runtime dependency version uyumsuzlugu nasil ele alinmali?
- **Evidence:** Local (Python 3.11.15) ile Docker image (Python 3.11.18)
  arasinda gercek bir patch-version farki bulundu -- ilk strict exact-match
  politika bunu dogru REJECT etti.
- **Decision:** `python_version` artik SADECE major.minor karsilastirilir
  (patch surumleri pickle uyumlulugunu etkilemez); `sklearn_version` HALA
  exact-match gerektirir.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage13_dependency_compatibility.json`, `inference/model_loader.py`

### D-145 — Feature Schema Validation (Accepted)

- **Question:** Field presence ve value missingness ayri mi
  kontrol edilmeli?
- **Decision:** **EVET.** Tum Minimal Core feature'lari required (field
  presence), ama deger NaN/None olabilir (missingness, imputation'a
  birakilir).
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `inference/schemas.py`, `stage13_schema_validation_results.csv`

### D-146 — Feature Engineering Parity (Accepted)

- **Question:** Raw-line-item-to-shipment ETL Stage 13'te yeniden mi
  implement edilecek?
- **Decision:** **HAYIR.** Canonical input zaten shipment-seviyesinde --
  ayri bir `feature_adapter.py` gereksiz bulundu, scope acikca sinirlandi.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage13_feature_inference_contract.md` Section 7

### D-147 — Single Prediction Contract (Accepted)

- **Question:** `predict_one()` interface'i nasil tanimlanmali?
- **Decision:** `predict_one(shipment, explain=False, request_interval=False)
  -> PredictionResult`, internally `predict_batch([shipment])[0]` cagirir
  (duplikasyon yok).
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `inference/predictor.py`

### D-148 — Batch Prediction Contract (Accepted)

- **Question:** Batch validation policy nedir?
- **Decision:** Atomic batch validation -- tek bir satirin schema hatasi
  TUM batch'i reddeder. Max batch size=100 (config'den).
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage13_batch_parity.csv`

### D-149 — Prediction Validity Policy (Accepted)

- **Question:** Negatif/non-finite prediction nasil ele alinmali?
- **Decision:** Non-finite -> `PredictionValidationError`. Negatif ->
  `prediction_validity="invalid"`, **clip EDILMEZ**, acik `invalid_reason`
  ile raporlanir.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `inference/predictor.py`

### D-150 — Optional Explainability Integration (Accepted)

- **Question:** Explainability default olarak acik mi olmali?
- **Decision:** **HAYIR**, `explain=False` default. Bounded
  (`max_batch_explanations=10`), versioned, auditable.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage13_explainability_results.csv`

### D-151 — SHAP Additivity & Metadata (Accepted)

- **Question:** Her local explanation additivity kontrolu iceriyor mu?
- **Evidence:** 10/10 test shipment'ta additivity PASSED (max diff=5.09e-11 USD).
- **Decision:** EVET, her explanation additivity_valid/additivity_diff_usd
  tasir.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage13_shap_additivity_audit.json`

### D-152 — Deterministic Risk Flags (Accepted, Gercek Bulguyla Genisletildi)

- **Question:** Risk flag'leri label-based threshold'lara mi dayaniyor?
- **Evidence:** `PREDICTION_OUTSIDE_REFERENCE_RANGE`, extreme input'ta
  bile TETIKLENMEDI -- tree ensemble extrapolation yapamadigi icin.
- **Decision:** Flag'ler SADECE training-only istatistik/girdi yapisina
  dayanir; bu sinirlama acikca belgelendi, GIZLENMEDI.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage13_risk_flag_tests.csv`

### D-153 — Uncertainty Disabled Policy (Accepted)

- **Question:** `request_interval=True` interval dondurur mu?
- **Decision:** **HAYIR.** Sadece `INTERVAL_NOT_APPROVED` flag eklenir --
  Stage 12'nin "Production Interval Not Approved" karari aynen korunur.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage13_stage14_handoff.json`

### D-154 — Serialization Parity Tolerance Policy (Accepted, Hata Duzeltmesiyle)

- **Question:** Parity kontrolleri exact `==` mi, tolerance-based mi
  olmali?
- **Evidence:** Docker'da calistirilirken, iki strict `==` assertion
  (reordered-keys, post-security-test sanity check) basarisiz oldu --
  ExtraTrees `n_jobs=2` ile predict() sirasinda thread-order'a bagli
  ~1e-11 USD floating-point gurultusu gozlemlendi.
- **Decision:** Her iki assertion, projenin diger tum parity
  kontrolleriyle TUTARLI bicimde 1e-6 USD tolerance'a DUZELTILDI.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage13_validation_results.md` Section 13

### D-155 — Cross-Environment Reproducibility (Accepted)

- **Question:** Local'de uretilen bundle Docker'da (refit edilmeden)
  dogru yukleniyor mu?
- **Evidence:** Ayni SHA-256 (refit YOK), 25 shipment uzerinde max
  diff=7.28e-12 USD.
- **Decision:** EVET, cross-environment parity dogrulandi (D-144'teki
  policy duzeltmesi sonrasinda).
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage13_local_docker_parity.csv`, `stage13_reproducibility_report.json`

### D-156 — Stage 14 API Handoff (Accepted)

- **Question:** Stage 14'e hangi sozlesme tasinacak?
- **Decision:** `FreightCostPredictor` tek public interface; artifact
  loading/explainability/risk-flag/interval policy'leri Stage 14'e
  DEGISTIRILMEDEN tasinir. Stage 14 readiness: **CONDITIONAL GO.**
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage13_stage14_handoff.json`, `stage14_api_deployment_contract.md`

## Stage 14 (Phase A) — REST API, Docker Reuse, Automated Testing

### D-157 — Dedicated API Docker Service Degerlendirmesi (Accepted)

- **Question:** Stage 14 icin ayri bir Docker servisi mi olusturulmali?
- **Evidence:** `compose.yaml`/`Dockerfile` incelendi -- tek bir `ml-lab`
  servisi var, tum repo bind-mount, `jupyter lab` CMD. Contract Section
  14 mevcut servisin reuse edilmesini acikca istiyor.
- **Decision:** **HAYIR**, ayri servis olusturulmadi. `compose.yaml`'a
  `127.0.0.1:8000:8000` port mapping'i ve `Dockerfile`'a `EXPOSE 8000`
  eklendi (additive); CMD degismedi, mevcut jupyter workflow korundu.
  API, manuel `uv run uvicorn ...` veya testin kendi subprocess fixture'i
  ile baslatiliyor.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `compose.yaml`, `Dockerfile`, `stage14_api_implementation.md` §7

### D-158 — Request Body Validasyonu Duplike Edilmedi (Accepted)

- **Question:** API katmani kendi (Pydantic, sabit alanli) request
  schema'sini mi tanimlamali, yoksa `FeatureSchemaValidator`'a mi
  devretmeli?
- **Decision:** **Devretmeli.** Request body `await request.json()` ile
  ham okunur, `predictor.predict_one/predict_batch`'e DOGRUDAN verilir.
  Iki paralel validasyon kaynagi (D-146'nin ayni mantigi) contract
  drift riski tasir.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `api/app.py`, `api/schemas.py`

### D-159 — Error Code Extraction & HTTP Status Mapping (Accepted)

- **Question:** `inference` paketinin `"CODE: detail"` formatli exception
  mesajlari HTTP response'a nasil tasinmali?
- **Decision:** `error_code` alani mesajin ilk `":"`'den once gelen
  token'dan cikarilir (bilinen kod listesine karsi dogrulanir, bilinmeyen
  durumda `VALIDATION_ERROR`'a duser); tum error response'lar tek bir
  `{error_code, detail}` sekli kullanir (Section 10/11).
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `api/errors.py`, `test_error_contract.py`

### D-160 — Startup-Time Single Load, Fail-Closed Readiness (Accepted)

- **Question:** Predictor her request'te mi, yoksa bir kez mi
  yuklenmeli; yukleme basarisiz olursa servis ne yapmali?
- **Decision:** `lifespan` ile **tam olarak bir kez** yuklenir + sabit
  canary shipment ile dogrulanir. Basarisizlikta process CRASH ETMEZ,
  `app.state.ready=False` kalir, `/predict*` 503 doner, `/health` hala
  200 doner (process-alive != ready ayrimi).
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `api/app.py: lifespan`, `test_health_readiness.py`

### D-161 — Live-Server Integration Test Katmani (Accepted)

- **Question:** "Docker service integration test" (contract Section 16),
  in-process `TestClient`'tan nasil AYRISTIRILIR?
- **Decision:** Ayri bir katman: session-scoped `live_server` fixture,
  gercek bir `uvicorn` subprocess'ini gercek bir TCP port'a bind eder,
  testler `httpx` ile GERCEK HTTP uzerinden cagirir. Local'de ve Docker
  container'i icinde AYNI suite calistirilir -- fark sadece calistirma
  ortami, test kodu degismez.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `tests/stage14/conftest.py: live_server`, `test_docker_live_server.py`

### D-162 — Floating-Point Tolerance Policy API Katmanina Genisletildi (Accepted, Gercek Bulguyla)

- **Question:** API katmaninda batch-of-N vs N x batch-of-1, veya iki
  ayri yuklenen predictor instance'i arasinda prediction karsilastirmasi
  exact `==` mi olmali?
- **Evidence:** Local'de 1, Docker'da 2 test, `prediction_usd` alaninda
  ~1e-13 - ~3e-13 USD farkla basarisiz oldu -- Stage 13'un D-154'uyle
  AYNI kok neden (ExtraTrees `n_jobs=2` thread-order-dependent summation),
  bu kez API katmaninda tekrar gozlemlendi.
- **Decision:** `test_predict_batch.py` ve `test_model_parity.py`'deki
  ilgili assertion'lar, projenin geri kalaniyla TUTARLI olacak sekilde
  1e-6 USD tolerance'a cevrildi; diger tum alanlar (model_id, risk_flags,
  prediction_validity) hala TAM esitlikle kontrol edilir.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `test_predict_batch.py`, `test_model_parity.py`, `stage14_test_results.md` §3

### D-163 — API Latency Batch-Size'tan Bagimsiz (Accepted, Gercek Bulgu)

- **Question:** Batch prediction, latency acisindan tekil cagrilara
  kiyasla olceklenir mi?
- **Evidence:** `batch=1` ile `batch=100` arasinda p50 latency
  istatistiksel olarak ayirt edilemez (~30-40ms local, ~60-65ms Docker)
  -- `ExtraTreesRegressor.predict()`'in `n_jobs=2` thread-pool dispatch
  maliyeti bu aralikta DOMINANT. `explain=true` satir basina ~10ms
  ekliyor, bu da `max_batch_explanations=10` siniri icin ek bir sayisal
  gerekce saglar.
- **Decision:** Bulgu belgelendi (gizlenmedi); Phase A herhangi bir
  "production throughput SLA'si" iddia ETMEZ -- sadece gozlem.
- **Status:** Accepted
- **Confidence:** Medium (tek host, tek calistirma ortami; sustained-load
  testi yapilmadi)
- **Related Artifacts:** `artifacts/stage14_performance_benchmark.json`, `stage14_performance_benchmark.md`

### D-164 — Pre-Test Freeze Manifest & Phase B Gating (Accepted)

- **Question:** Phase B (2015 Protected Test) baslamadan once hangi
  durum "dondurulmus" olarak kayit altina alinmali?
- **Decision:** `stage14_pretest_freeze_manifest.json`: model bundle
  SHA-256 (Phase A basi/sonu ayni), test sonuclari (90/90, local+Docker),
  cross-environment parity, ve `protected_test_policy.accessed_in_phase_a:
  false`. Bu manifest Phase B'yi TETIKLEMEZ -- sadece referans
  noktasidir. Phase B'nin fiilen baslamasi kullanicinin ayri, acik
  onayini gerektirir.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage14_pretest_freeze_manifest.json`, `stage14_phase_a_final_report.md`

## Stage 14 (Phase B Preparation) — Final Evaluation Infrastructure, Gating & Freeze

### D-165 — Evaluation Package Architecture (Accepted)

- **Question:** Phase B mantigi tek bir buyuk modul mu, yoksa kucuk,
  tek-sorumluluklu modulller halinde mi organize edilmeli?
- **Decision:** `labs/lab12/evaluation/` -- 10 kucuk modul
  (`contracts`, `population`, `baselines`, `metrics`, `acceptance`,
  `freeze`, `gate`, `runner`, `cli`, `__init__`), her biri tek bir
  sorumluluk tasir. Gereksiz framework/base-class katmani eklenmedi.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `labs/lab12/evaluation/`

### D-166 — Token-Gated Protected Population Access (Accepted)

- **Question:** "pytest/notebook normal calismasi Protected Test'e
  erisemez" gereksinimi NASIL garanti edilmeli -- convention ile mi,
  yapisal olarak mi?
- **Decision:** **Yapisal olarak.** `population.load_protected_population()`,
  `gate.PreUnlockGate.unlock()`'un urettigi bir `UnlockToken` olmadan
  CALISMAZ (tip kontrolu + `is_valid()`). Token tek kullanimliktir
  (`consume()`). Bu, bir sozlesme degil, bir runtime garantisidir --
  `test_structural_safety.py` ile programatik olarak dogrulandi.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `evaluation/population.py`, `evaluation/gate.py`, `tests/stage14_evaluation/test_structural_safety.py`

### D-167 — Feature Aggregation Adapter Gerekli (Stage 13'un D-146'sindan Farkli Kapsam)

- **Question:** Stage 13 (D-146), "feature_adapter.py gereksiz" kararini
  vermisti -- bu, Phase B icin de gecerli mi?
- **Evidence:** D-146'nin gerekcesi "canonical input zaten shipment-seviyesinde"
  idi -- bu, API katmani icin DOGRU (zaten aggregate edilmis JSON alir).
  Phase B ise HAM, row-level (line-item) veriden baslar.
- **Decision:** **HAYIR, D-146 burada GECERLI DEGIL.** Evaluation'a ozgu
  `population.py:resolve_shipment_features`, Stage 07'nin aggregation
  semantics'ini (numeric->sum, categorical->first) uygular -- bu,
  Stage 13'un inference contract'ini DEGISTIRMEZ, sadece ondan BIR ADIM
  ONCESINI (raw->shipment-level) karsilar.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `evaluation/population.py`

### D-168 — High-Cost Threshold: Frozen Constant, Yeniden Hesaplanmadi (Accepted)

- **Question:** 2015 icin high-cost threshold'u, Protected Test'in kendi
  P90'indan mi hesaplanmali, yoksa Stage 11'in dondurdugu deger mi
  reuse edilmeli?
- **Decision:** **Reuse edilmeli.** `HIGH_COST_THRESHOLD_USD = 23897.32`,
  Stage 11'in 2006-2013 development population'indan (2014 OKUNMADAN
  ONCE) turettigi, zaten yayinlanmis deger -- "frozen-before-the-period-is-read"
  politikasi 2015 icin de aynen uygulanir. Test-setinin kendi dagiliminda
  bir threshold hesaplamak, segment tanimina dolayli bir leakage sokardi.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `evaluation/contracts.py`, `stage11_external_validation_results.md` Section 5

### D-169 — Hazirlik Asamasinda Gercek Veriyle Baseline Fitting Yapilmadi (Accepted)

- **Question:** B1/B4 baseline'lari, bu hazirlik asamasinda gercek
  2006-2013 development population'inda fit edilip sayisal olarak
  dogrulanmali mi?
- **Evidence:** Hazirlik asamasinda ham CSV erisimi engellendigi icin
  gercek development population uzerinde baseline fitting dogrulanamadi.
- **Decision:** Baseline fitting mantigi (`baselines.py`) KOD OLARAK
  yazildi ve SADECE sentetik fixture'larla test edildi
  (`tests/stage14_evaluation/test_baselines.py`, `test_runner.py`).
  Gercek development population'da fit, Phase B'nin unlock-sonrasi
  calismasina birakildi.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `evaluation/baselines.py`, `stage14_evaluation_validation_results.md` Section 5

### D-170 — Teknik Kabul Esikleri: Provisional, Business-SLA DEGIL (Accepted)

- **Question:** Model, Protected Test'te B4'u gectiginde "kabul edildi"
  diyebilmek icin hangi esik kullanilmali?
- **Decision:** Uc provisional, muhendislik-seviyesi esik (>=%10 MAE
  iyilesmesi vs B4, >=%99 validity rate, 2014 referansina +10pp
  high-cost tolerans) -- ACIKCA "business-approved SLA DEGIL" olarak
  etiketlendi (`classify_acceptance()` sonucu hicbir zaman `business_approved`/`sla`
  alani ICERMEZ, test ile dogrulandi).
- **Status:** Accepted
- **Confidence:** Medium (esikler, gercek 2015 sonucuyla hicbir zaman
  kalibre edilmedi -- provisional kalmaya devam ediyor)
- **Related Artifacts:** `evaluation/acceptance.py`, `stage14_metric_baseline_contract.md` Section 5

### D-171 — Freeze Manifest v2: Supersede Eder, Uzerine Yazmaz (Accepted)

- **Question:** Phase A'nin `stage14_pretest_freeze_manifest.json`'i
  (v1), Phase B icin yeterli mi?
- **Evidence:** v1, evaluation code/protocol/baseline/metric/acceptance
  fingerprint'lerini ICERMIYOR (o an bu kod yoktu).
- **Decision:** Yeni bir dosya, `stage14_evaluation_freeze_manifest_v2.json`,
  bu fingerprint'leri ekler ve `supersedes` alaniyla v1'e referans verir.
  **v1 dosyasi SILINMEDI, UZERINE YAZILMADI** -- audit trail icin
  korundu.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `evaluation/freeze.py`, `stage14_final_pretest_freeze.md`

### D-172 — Explicit CLI, Bu Asamada Cagrilmadi (Accepted)

- **Question:** "Separate explicit command" gereksinimi nasil implement
  edilmeli, ve bu asamada test edilmeli mi?
- **Decision:** `evaluation/cli.py`, `python -m evaluation.cli unlock
  --confirm-phrase ...` olarak implement edildi. **Bu komut, bu asamada
  HICBIR SEKILDE calistirilmadi** -- `PreUnlockGate.unlock()`/`run_checks()`
  bile gercek (`cli.py`'nin) yapilandirmasiyla CAGRILMADI; sadece
  tamamen sentetik, `tmp_path`-scoped fixture'larla test edildi
  (`tests/stage14_evaluation/test_gate.py`).
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `evaluation/cli.py`, `tests/stage14_evaluation/test_gate.py`

## Stage 14 — Pre-Unlock Audit

### D-175 — Real Development-Only Artifact Parity Verification (Accepted, Gercek Bulgu)

- **Question:** D-169 (Phase B hazirliginda), B1/B4 gercek development
  verisiyle hic dogrulanamamisti. Bu, HALA cozulemez bir eksiklik mi?
- **Evidence:** `stage08_fold_statistics.csv`/`stage08_oof_predictions.csv`/`stage08_segment_support.csv`
  (training-only CV, ham veri DEGIL) ile: B0/B1 formulleri 4/4 fold'da
  TAM parity (Train_Median/Train_Mean ile exact match); B4'un
  PARENT_FALLBACK/GLOBAL_FALLBACK degerleri segment_support tablosundaki
  >=10-support medianlarla TAM eslesti (4/4 fold). Daha da onemlisi:
  `stage11_baseline_predictions.csv` (gercek 2014, development population'da
  TEK SEFERLIK fit edilmis B1/B4) + `stage11_external_metrics.csv` ile,
  `evaluation/metrics.py`'nin TUM 10 metrigi (MAE/RMSE/WAPE/Bias/Median/P90/P95/High-Cost/vb.)
  **0.000000 fark ile TAM OLARAK** published referans degerleriyle eslesti.
- **Decision:** Metrics modulu icin gercek-veri parity **TAM OLARAK
  DOGRULANDI** (ham CSV'ye hic dokunulmadan). Baseline FITTING
  mantigi icin ise development population'in TEK, full-population
  fit'i (n=4987) hala bagimsiz olarak yeniden-uretilemedi (ham veri
  erisimi kisitlamasi devam ediyor) -- ama Stage 11'in zaten yayinladigi
  `b1.value_usd = 10456.218411870865` frozen referans degeri EXPECTED_B1_DEVELOPMENT_MEAN_USD
  olarak kaydedildi ve D-174'teki fail-closed kontrol icin kullanildi.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `stage14_pre_unlock_audit_report.md`, `stage08_fold_statistics.csv`, `stage11_baseline_predictions.csv`, `stage11_external_metrics.csv`

### D-174 — Development Population Integrity Check (Accepted)

- **Question:** D-175'te bulunan frozen B1 referans degeri (`10456.218411870865`),
  Phase B kodunda nasil kullanilmali?
- **Decision:** `FinalEvaluationRunner`, development population'i yukleyip
  B1'i fit ettikten SONRA ama Protected Test'i okumadan ONCE, freshly-fit
  B1 mean'inin bu frozen degerle (1e-6 USD tolerans ile) eslesmesini
  dogrular. Eslesmezse `DevelopmentPopulationIntegrityError` raise edilir
  -- **2015 hic okunmaz**. Parametre varsayilani `None`'dir (sentetik
  testler bu kontrolu atlar); `cli.py` gercek calismada her zaman
  gercek sabiti gecirir.
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `evaluation/runner.py`, `evaluation/contracts.py`, `tests/stage14_evaluation/test_runner.py`

### D-173 — High-Cost Acceptance Kriteri Revize Edildi (Accepted, Gercek Bulgu)

- **Question:** "2015 high-cost underprediction rate'i, 2014 referansini
  (%89.93) 10pp'den fazla asamaz" kurali, anlamli bir gate mi?
- **Evidence:** Metrik %100'de ustten sinirli; 2014 referansi zaten bu
  tavana yakin; **her iki mevcut baseline (B1, B4) 2014'te ZATEN TAM
  OLARAK %100 skorluyor**. +10pp tolerans -> %99.93 tavan -- bunu
  GECMEK icin bir modelin pratik olarak HER high-cost shipment'i
  underpredict etmesi gerekir (baseline'larin zaten yaptigi sey). Kural
  neredeyse HER ZAMAN gecer, sifir ayirt edicilik saglar.
- **Decision:** Kural bir GATING kriteri olmaktan **CIKARILDI**, bir
  **monitored risk indicator**'a donusturuldu (`high_cost_risk_monitor`,
  her zaman raporlanir, siniflandirmayi hicbir zaman etkilemez). Yerine,
  keyfi bir sabit GEREKTIRMEYEN, ayni donem icinde B4'e gore RELATIF bir
  kriter eklendi: `model_rate < B4_rate` (ayni Protected Test donemi).
- **Status:** Accepted
- **Confidence:** Medium (yeni kriter gercek 2015 verisiyle hic
  calistirilmadi; relative karsilastirma mantiksal olarak daha saglam
  ama empirik olarak dogrulanmadi)
- **Related Artifacts:** `evaluation/acceptance.py`, `evaluation/contracts.py`, `stage14_metric_baseline_contract.md` Section 5, `tests/stage14_evaluation/test_acceptance.py`

## Stage 14 — Final Evaluation (2015 Protected Test, One-Time)

### D-176 — Protected Test Executed, ACCEPTED (Accepted, Gercek Sonuc)

- **Question:** M04-T003, kullanicinin acik yetkilendirmesiyle
  calistirilan TEK SEFERLIK 2015 Protected Test degerlendirmesinde ne
  sonuc verdi?
- **Evidence:** `python -m evaluation.cli unlock` ile calistirildi
  (n_protected_eligible=392). Tum 9 pre-unlock kontrolu + D-174'un B1
  development-mean integrity check'i (frozen `10456.218411870865` USD
  ile TAM eslesme) 2015 okunmadan ONCE PASSED. M04-T003 MAE=8540.83 USD,
  B4'u %30.2 geçti (esik: >=%10), validity %100, high-cost
  underprediction %80.49 (B4'un ayni donemdeki %100'unden DUSUK) ->
  **ACCEPTED**.
- **Decision:** Sonuc, exactly-as-observed raporlandi
  (`stage14_final_evaluation_report.md`) -- elverissiz bulgu da dahil:
  Dev-CV->2014 gap (+%14.1) ile 2014->2015 gap (+%31.7) arasinda gercek
  bir HIZLANMA var (muhtemelen B1/B4'u de ayni oranda etkileyen bir
  distribution shift, bagimsiz dogrulanmadi). Model bundle SHA-256
  calistirma oncesi/sonrasi AYNI -- retrain/tune YAPILMADI. Degerlendirme
  **TEKRAR CALISTIRILMAYACAK** (`AlreadyEvaluatedError` guard'i aktif).
- **Status:** Accepted
- **Confidence:** High
- **Related Artifacts:** `artifacts/stage14_final_evaluation_report.json`, `artifacts/stage14_evaluation_audit_log.json`, `stage14_final_evaluation_report.md`
