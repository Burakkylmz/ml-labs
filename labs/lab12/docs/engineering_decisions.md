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
