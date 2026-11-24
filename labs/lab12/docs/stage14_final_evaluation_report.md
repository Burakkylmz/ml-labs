# LAB12 — Final Evaluation Report (2015 Protected Test)

**Bu rapor, 2015 Protected Test'in TEK SEFERLIK, kullanicinin acik
yazili onayi ile gerceklesen degerlendirmesinin sonucunu belgeler.
Degerlendirme `evaluation.cli unlock` ile BIR KEZ calistirildi; rapor
`artifacts/stage14_final_evaluation_report.json`'dan alinmistir. Bu
degerlendirme TEKRAR CALISTIRILMAYACAKTIR (`AlreadyEvaluatedError`
guard'i artik aktif).**

## 1. Model & Dataset Integrity

| Kontrol | Sonuc |
|---|---|
| Model bundle SHA-256 (calistirma oncesi) | `71a451344f8b88a8d440d90325b88668cd3a8c16379425f5a4e95061bed77782` |
| Model bundle SHA-256 (calistirma sonrasi) | `71a451344f8b88a8d440d90325b88668cd3a8c16379425f5a4e95061bed77782` -- **AYNI** |
| Dataset SHA-256 | `9cffdb4ab8c6135b0f999c91b3a5c6e88a3c3dfc28c7c85feb9e97f986e3578a` -- dogrulandi |
| Stage 05 protocol fingerprint | `b87ca0fde5fd9ddef45f191a0bb1c3e4e2a014b9c9641be5e8d20bb2458935e7` -- dogrulandi |
| Feature contract | `stage07-v1-minimal-core` -- degismedi |
| Preprocessing contract | `stage06-v1-tree-model-no-scaling` -- degismedi |
| Canonical runtime | Python 3.11.15 (major.minor), sklearn 1.9.1 (exact) -- dogrulandi |

## 2. Pre-Access Baseline Verification (Section 2 Gate)

`PreUnlockGate.run_checks()`, 2015'e erisimden ONCE 9 kontrolun
TUMUNDEN gecti: `explicit_authorization`, `no_silent_rerun`,
`frozen_model_identity`, `live_model_bundle_unchanged`,
`dataset_fingerprint`, `stage05_protocol_fingerprint`,
`frozen_evaluation_code_and_protocol`, `canonical_runtime`,
`audit_log_writable`.

Ayrica, `FinalEvaluationRunner.run()` icinde, development population
(2006-2013, Train split) yuklenip B1 fit edildikten SONRA ama Protected
Test okunmadan ONCE, **B1'in full-development mean'i frozen referansla
(`10456.218411870865` USD) karsilastirildi -- ESLESTI (fark < 1e-6 USD),
`DevelopmentPopulationIntegrityError` RAISE EDILMEDI.** Bu, development
population'in GERCEKTEN dogru (Stage 05/11 ile ayni) yuklendigini
bagimsiz olarak kanitlayan TEK somut kontroldu (D-174) -- ve basariyla
GECTI.

B4, development population uzerinde `min_support=10`, fallback zinciri
(Combined -> Mode -> INCOTERM -> Global) ile fit edildi -- Stage 08'den
degistirilmedi.

**2015 etiketleri, hicbir baseline fitting isleminde KULLANILMADI** --
`load_development_population` yapisal olarak sadece `Split=="Train"`
okur, Protected Test'ten bagimsizdir.

## 3. Protected-Test Execution Audit

```
pre_unlock_checks_passed -> unlock_token_issued -> (2015 okundu, TEK KEZ) -> token.consume() -> rapor yazildi
```

Audit log (`artifacts/stage14_evaluation_audit_log.json`): 2 kayit
(`pre_unlock_checks_passed`, `unlock_token_issued`). Token tek kullanimlik
tuketildi. Calistirma komutu:
`python -m evaluation.cli unlock --confirm-phrase "I AUTHORIZE 2015 PROTECTED TEST EVALUATION"`
-- **TEK KEZ calistirildi, tekrar CALISTIRILMADI.**

## 4. 2015 Population & Label Coverage

`stage05_split_manifest.csv`'nin `Protected_Test` split'i: **569**
shipment. Target eligibility filtresinden (tek numeric anchor) sonra:
**n_protected_eligible = 392** (569'un %68.9'u -- 2014'teki 910->819
(%90.0) oranindan DUSUK; bu fark, 2015 verisinin eligibility
karakteristiginde gercek bir fark olabilir, ayrica incelenmedi --
mevcut rapor semasinda eligibility-kaybi breakdown'i YOK, bu bir
sinirlama olarak Section 12'de not edildi).

## 5. Final ExtraTrees (M04-T003) Sonuclari

| Metrik | 2015 Protected Test (n=392) |
|---|---|
| **MAE** | **8540.83 USD** |
| RMSE | 16822.81 USD |
| Median AE | 3883.81 USD |
| WAPE | 55.59% |
| **Bias** | **-2616.18 USD** (sistematik underprediction) |
| P90 AE | 21835.96 USD |
| P95 AE | 34705.31 USD |
| Prediction Validity Rate | 100.00% |
| Negative Prediction Count | 0 |
| High-Cost MAE | 24649.00 USD |
| High-Cost Underprediction Rate | 80.49% |

## 6. B1/B4 Final Karsilastirmasi (2015, Ayni 392 Shipment)

| Model | MAE | RMSE | Bias | High-Cost Underprediction |
|---|---|---|---|---|
| **M04-T003** | **8540.83** | **16822.81** | -2616.18 | **80.49%** |
| B4 (Hierarchical Median) | 12233.66 | 22092.01 | -8392.29 | 100.00% |
| B1 (Global Mean) | 12795.47 | 21805.62 | -4907.98 | 100.00% |

B4'un fallback dagitimi: **392/392 shipment COMBINED_SEGMENT** (hicbir
parent/global fallback gerekmedi -- 2015'teki Mode x INCOTERM
kombinasyonlarinin hepsi development population'da >=10 destege
sahipti).

## 7. B4'e Gore Iyilesme

**(12233.66 - 8540.83) / 12233.66 = %30.2 MAE iyilesmesi** -- kabul
esigi (>= %10) rahatlikla gecildi.

## 8. Development CV vs 2014 vs 2015 (Generalization Gap)

| Donem | M04-T003 MAE | B4 MAE | M04 vs B4 Iyilesme |
|---|---|---|---|
| Dev-CV (Stage 10, pooled) | 5686.34 | 8694.56 | %34.6 |
| 2014 External (Stage 11) | 6485.63 | 9770.79 | %33.6 |
| **2015 Protected (bu rapor)** | **8540.83** | **12233.66** | **%30.2** |

**Gercek, elverissiz bulgu:** MAE boşlugu (gap), Dev-CV->2014'te +%14.1,
2014->2015'te +%31.7 -- **belirgin bir HIZLANMA** gosteriyor (Dev-CV'den
2015'e toplam gap: +%50.2). RMSE de benzer sekilde buyudu (11654->16823,
+%44.3). **Ancak bu durum SADECE M04-T003'e ozgu degil** -- B1 (+%15.1)
ve B4 (+%25.2) de 2014->2015 arasinda benzer orantida kotulesti. Bu,
muhtemelen 2015'in genel maliyet dagiliminda (muhtemelen enflasyon/hacim
degisikligi) bir KAYMA oldugunu, modelin KENDI kalitesinin COKMEDIGINI
gosteriyor -- ama bu hipotez bu raporun kapsaminda BAGIMSIZ olarak
DOGRULANMADI (feature'larda yillik agregalar/zaman trendi analizi
yapilmadi).

## 9. High-Cost Underprediction & Tail Risk

M04-T003'un high-cost underprediction rate'i **80.49%** -- 2014'teki
(%89.93) ve her iki baseline'in 2015'teki (%100) sonucundan **DAHA IYI**.
Bu, D-173'un yeni relative-to-B4 kriterinin (ACCEPTED icin gerekli)
basariyla gecildigi somut kanittir. **Sinirlama:** 2015'teki high-cost
segment'in tam shipment SAYISI bu rapor semasinda KAYITLI DEGIL (sadece
MAE/rate) -- Protected Test tekrar erisilemeyecegi icin bu sayi geriye
donuk olarak HESAPLANAMAZ; bu, gelecekteki benzer degerlendirmeler icin
rapor semasina eklenmesi gereken bir eksiklik olarak kayit altina
alinmistir (bkz Section 12).

## 10. Prediction Validity

**392/392 (%100.00) valid.** 0 negatif/non-finite tahmin. D-149'un
"negatif tahminler clip edilmez, invalid olarak raporlanir" politikasi
test edildi ama bu calistirmada HICBIR invalid prediction olusmadi.

## 11. Frozen Acceptance Criteria Sonuclari

| Kriter | Esik | Gercek | Sonuc |
|---|---|---|---|
| MAE iyilesmesi vs B4 | >= %10 | %30.2 | **GECTI** |
| Prediction Validity Rate | >= %99 | %100.00 | **GECTI** |
| High-Cost Underprediction vs B4 (ayni donem) | model < B4 | %80.49 < %100.00 | **GECTI** |

**Siniflandirma: ACCEPTED.** (Bundle integrity de dogrulandi --
kosulsuz FAILED tetiklenmedi.)

**High-cost risk monitor (bilgi amacli, gating DEGIL):** 2014 referansi
(%89.93) + 10pp = %99.93 esigi karsisinda `flagged_vs_2014_reference =
false` (model %80.49, esigin cok altinda) -- eski kuralin kendisi de
(gating olmasaydi) GECERDI, ama bu bir tesadüf degil: eski kural zaten
D-173'te "neredeyse her zaman geçer" olarak teshis edilmisti.

## 12. Kalan Metodolojik ve Operasyonel Sinirlamalar

- **Business-approved SLA hala YOK** -- ACCEPTED, bir production-deployment
  onayi DEGILDIR.
- **D-006 (Weight), D-007 (label timestamp), D-010 (Qty/Value
  aggregation)** hala ACIK -- prediction-time feature availability hic
  bagimsiz dogrulanmadi.
- **Generalization gap hizlaniyor** (Section 8) -- nedeni (distribution
  shift vs model degradation) bu raporda AYRISTIRILMADI.
- **High-cost segment shipment sayisi** 2015 icin KAYITLI DEGIL (rapor
  semasi eksikligi, Section 9).
- **Relative high-cost kriteri (D-173)** sadece BU TEK calistirmada
  test edildi -- istatistiksel genellemesi (baska bir donemde de
  anlamli olur mu) DOGRULANMADI.
- **Authentication/rate-limiting** Stage 14 API'sinde hala YOK.
- **Tek bir Protected Test calistirmasi** -- istatistiksel guven araligi
  (confidence interval) bu MAE/RMSE degerleri icin HESAPLANMADI; n=392
  ornekleme gurultusu, nokta tahminlerin KESIN dogrulugu anlamina GELMEZ.

## 13. Final Technical PoC Acceptance

**Teknik PoC olarak ACCEPTED.** M04-T003, B4'u (business baseline)
2015 Protected Test'te **%30.2** MAE iyilesmesiyle gecti, bu Stage
08-11 boyunca gozlenen patern ile TUTARLIDIR (dev-CV: %34.6, 2014:
%33.6, 2015: %30.2 -- yavas ama izlenebilir bir erosion, ESIGIN (>=%10)
UZERINDE kaldi).

## 14. Production-Readiness Restrictions

Bu ACCEPTED sonucu **PRODUCTION DEPLOYMENT ONAYI DEGILDIR**:
- Business-approved SLA/asymmetric loss function YOK.
- High-cost shipment'larda (>=23897.32 USD) MAE hala ~24649 USD --
  mutlak buyuklukte YUKSEK risk.
- Authentication/rate-limiting YOK.
- Tek bir yillik degerlendirme (2015) -- sürdürülebilir performans
  garantisi SAGLAMAZ.
- Uncertainty/interval cikisi hala Research Only/Disabled by Default.

## 15. Model Card

| Alan | Deger |
|---|---|
| Model | ExtraTreesRegressor, M04-T003, artifact v1 |
| Egitim verisi | SCMS Delivery History 2006-2013, n=4987 eligible shipment |
| Feature'lar | Line_Item_Qty_Sum, Line_Item_Value_Sum (numeric); Shipment_Mode, INCO_Term, Country, Product_Group (categorical) |
| Hedef | Freight Cost (USD), orijinal olcek |
| Degerlendirme | Dev-CV (MAE 5686) -> 2014 External (MAE 6486) -> **2015 Protected (MAE 8541)** |
| Kabul durumu | **ACCEPTED** (teknik, business-SLA DEGIL) |
| Bilinen riskler | High-cost underprediction (%80.5, 2015), genelleme gap'i buyuyor, D-006/D-007 acik |
| Kullanim amaci | Pre-shipment cost estimation PROTOTYPE -- production SLA'si YOK |
| Kullanilmamasi gereken baglam | Business-critical finansal karar, SLA-bagli sozlesme, otomatik fiyatlandirma |

## 16. No-Retuning & Scope-Integrity Verification

- Model bundle **hic retrain/tune EDILMEDI** -- SHA-256 calistirma
  oncesi ve sonrasi AYNI.
- Feature engineering/preprocessing **DEGISTIRILMEDI**.
- Acceptance esikleri, sonuclar GORULDUKTEN SONRA **DEGISTIRILMEDI**
  (D-173 revizyonu, 2015 erisiminden ONCE, sadece 2014/Stage08 kanitiyla
  yapildi -- bu rapor BUNU dogrular, cunku revizyon audit log'un
  `pre_unlock_checks_passed` kaydindan ONCE commit edildi).
- Baseline'lar **2015 etiketleriyle optimize EDILMEDI**.
- Conformal calibration **YAPILMADI**.
- "En iyi performans gosteren ortam" **SECILMEDI** -- degerlendirme
  local ortamda, tek kez calistirildi.
- **Production onayi ICAT EDILMEDI.**
- Onceki asama artifact'leri (Stage 05-13) **DEGISTIRILMEDI**.
- Git commit/push **YAPILMADI**.
- Degerlendirme **TEKRAR CALISTIRILMADI** (`AlreadyEvaluatedError` guard'i
  artik aktif -- bir sonraki `unlock` cagrisi, acik bir `allow_rerun` +
  ayri onay OLMADAN REDDEDILECEKTIR).
