# LAB12 — Stage 14 Phase B: Metric & Baseline Contract

**Bu belge de, `stage14_final_evaluation_protocol.md` gibi, 2015 erisiminden
ONCE dondurulmustur** ve ayni fingerprint-ve-dogrulama mekanizmasina
tabidir (`acceptance_criteria_fingerprint`, `evaluation/gate.py`).

## 1. Baseline B1 — Global Mean

`evaluation/baselines.py:GlobalMeanBaseline`. Stage 08'den DEGISTIRILMEDEN
recovered: feature yok, `y_hat = mean(Target)`, development population
(2006-2013, n=4987) uzerinde fit edilir -- 2014/2015 target'lari HICBIR
sekilde fitting'e girmez (Stage 08 Section 14 leakage-prevention
invariant'i).

## 2. Baseline B4 — Hierarchical Segment Median

`evaluation/baselines.py:HierarchicalMedianBaseline`. Stage 08 Section
10-12'den recovered fallback zinciri:

1. **Combined** (`Shipment_Mode` + `INCO_Term`) segment median, eger
   `support >= min_support` (=10) ise -> reason `COMBINED_SEGMENT`.
2. Yoksa **Shipment_Mode** median, `support >= 10` ise -> reason
   `MODE_MEDIAN`.
3. Yoksa **INCO_Term** median, `support >= 10` ise -> reason
   `INCOTERM_MEDIAN`.
4. Yoksa **global** median -> reason `GLOBAL_MEDIAN`.

`min_support=10` degeri Stage 08'den DEGISTIRILMEDEN alinmistir (orada
"evrensel bir istatistiksel kural degildir, gercek development verisinde
17 kombinasyondan 8'i 10'dan az gozlem icerir" olarak belgelenmistir --
bu bulgu bu belgede tekrarlanmaz, sadece referans alinir).

**Leakage prevention:** `HierarchicalMedianBaseline.predict()` imzasi
`y`/`target` parametresi ICERMEZ (`test_hierarchical_median_predict_signature_never_accepts_target`
ile programatik olarak dogrulandi) -- Stage 08'in ayni invariant'i.

## 3. Development Population (Her Iki Baseline Icin)

`evaluation/population.py:load_development_population` -- `stage05_split_manifest.csv`'nin
`Split == "Train"` satirlarindan, Stage 03.5 target resolution policy'si
ile. **2014 (Validation) veya 2015 (Protected_Test) split'leri hicbir
baseline fit isleminde KULLANILMAZ** -- programatik olarak dogrulandi
(`test_load_development_population_filters_to_train_split_only`).

## 4. Model vs Baseline Karsilastirmasi

Tum modeller (M04-T003, B1, B4) **ayni eligible Protected Test shipment
kumesi** uzerinde skorlanir (Stage 11 Section 7'nin "Fair Comparison"
ilkesinin Phase B'deki karsiligi).

## 5. Teknik Kabul Kurallari (ENGINEERING, Business-SLA DEGIL)

**Bu kurallar bir is onayi veya production SLA'si DEGILDIR** -- sadece,
test erisiminden ONCE dondurulmus, acikca "provisional engineering
threshold" olarak etiketlenmis teknik esikerdir
(`evaluation/contracts.py`, `evaluation/acceptance.py`).

**REVIZE EDILDI (Stage 14 Pre-Unlock Audit, D-173) -- v3 freeze
manifest'te.** Orijinal high-cost kurali ("2015 orani <= 2014 referansi
(%89.93) + 10pp = %99.93") incelendiginde, ANLAMSIZ bir esige yakin
oldugu goruldu: bu metrik %100'de ustten sinirlanmistir, 2014 referansi
zaten bu tavana YAKINDIR, ve HER IKI mevcut baseline (B1, B4) 2014'te
ZATEN TAM OLARAK %100 skorlamaktadir. Bu durumda, +10pp'lik sabit bir
tolerans tavani %99.93'e tasir -- bu esigi GECMEK icin bir modelin
pratik olarak HER TEK high-cost shipment'i underpredict etmesi
gerekir, ki bu da zaten her iki baseline'in yaptigi seydir. Sonuc:
kural, hemen hemen HER ZAMAN gecer, hicbir gercek ayirt edicilik
saglamaz.

**Karar:** Bu kural bir GATING kriteri olmaktan cikarilip bir
**monitored risk indicator**'a (`high_cost_risk_monitor`, her zaman
raporlanir, siniflandirmayi ASLA etkilemez) donusturuldu. Onun yerine,
ayni donem icinde B4'e gore RELATIF bir kriter eklendi -- hicbir
keyfi tolerans sabiti gerektirmez:

| Esik | Deger | Kaynak |
|---|---|---|
| B4'e gore minimum MAE iyilesmesi | >= %10 | Provisional, mühendislik karari |
| Minimum Prediction Validity Rate | >= %99 | Provisional, mühendislik karari |
| **High-Cost Underprediction Rate (GATING, v3)** | **model_rate < B4_rate (ayni donem)** | Pre-Unlock Audit'te revize edildi (D-173) -- keyfi sabit YOK |
| High-Cost Underprediction Rate (MONITOR, bilgi amacli) | 2014 referansi (%89.93) + 10pp | Artik SADECE raporlama, gating DEGIL |

**Siniflandirma mantigi** (`classify_acceptance`):

- Bundle integrity dogrulanamadiysa -> **FAILED** (kosulsuz).
- Model, B4'u MAE'de GECMIYORSA (iyilesme <= %0) -> **FAILED**.
- Model B4'u geciyor ama (iyilesme < %10) VEYA (validity < %99) VEYA
  (high-cost underprediction rate >= B4'un AYNI donemdeki orani) ->
  **CONDITIONAL**.
- Model B4'u >= %10 geciyor VE validity >= %99 VE high-cost
  underprediction rate B4'unkinden KESINLIKLE DUSUKSE (veya high-cost
  segment bos ise) -> **ACCEPTED** (yine de business-approved SLA
  DEGIL).

## 6. Acikca Reddedilen Alternatifler

- Business-approved bir SLA ICAT EDILMEDI -- boyle bir onay bu projede
  hicbir asamada (Stage 08-13 dahil) verilmemistir, bu durum acik kalmaya
  devam etmektedir.
- High-cost threshold, Protected Test'in KENDI dagiliminda yeniden
  hesaplanmadi (bu, test setinin kendisinden bir "self-referential"
  esik yaratirdi -- Section 4, `stage14_final_evaluation_protocol.md`).
