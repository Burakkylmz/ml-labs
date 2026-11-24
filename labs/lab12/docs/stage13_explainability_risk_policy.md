# LAB12 — Stage 13 Explainability & Risk Policy

## 1. Stage 12 Evidence

Stage 12'nin kabul ettigi default: `shap.TreeExplainer` + `tree_path_dependent`
background policy (acik background dataset gerektirmez), `model_output="raw"`.
Stage 12, bu policy ile `interventional`'in MATERYAL olarak farkli sonuclar
urettigini (en buyuk fark `Line_Item_Qty_Sum` icin ~1231 USD) belgeledi --
Stage 13 bu secimi **yeniden optimize ETMEMISTIR**, Stage 12'nin karari
reuse edilmistir.

## 2. SHAP Integration

`ShapExplainer` sinifi, `fitted_estimator`'i (ExtraTrees, pipeline icinden
cikarilmis) alir ve her `predict_one(explain=True)` cagrisinda LAZY olarak
insa edilir (ilk explain cagrisina kadar olusturulmaz).

## 3. Feature Attribution Schema

Encoded SHAP degerleri, row-bazinda SIGNED toplam ile raw source feature'a
gruplanir (Stage 12'nin metodolojisiyle AYNI). Cikti:
`{feature, signed_contribution_usd, absolute_contribution_usd}`.

## 4. Explanation Metadata

Her explanation: `method="tree_shap"`, `model_output="raw"`,
`background_policy="tree_path_dependent"`, `shap_library_version`,
`base_value_usd`, `additivity_valid`, `additivity_diff_usd`.

## 5. Additivity

$\hat y \approx E[f(X)] + \sum_j \phi_j$ her local explanation icin
kontrol edilir. 10/10 test shipment'ta additivity PASSED (max diff=0.000000
USD, `stage13_shap_additivity_audit.json`).

## 6. Explainability Failure Modes

SHAP computation basarisiz olursa: point prediction HALA gecerlidir,
`explanation_status="failed"` olarak isaretlenir, hata nedeni
(`exc` mesaji) kaydedilir, `EXPLANATION_UNAVAILABLE` risk flag'i eklenir --
**fabricated explanation URETILMEZ**.

## 7. Risk Flag Definitions

| Flag | Trigger | Deterministic Kaynak |
|---|---|---|
| `UNKNOWN_CATEGORY` | Categorical deger fitted encoder'da yok | Schema validation |
| `UNVERIFIED_FEATURE_AVAILABILITY` | HER prediction'da (yapisal) | D-006/D-007 acik kararlar |
| `PREDICTION_OUTSIDE_REFERENCE_RANGE` | Prediction, training y_dev [min,max] disinda | Training-only istatistik |
| `INTERVAL_NOT_APPROVED` | `request_interval=True` | Stage 12 karari |
| `EXPLANATION_UNAVAILABLE` | SHAP hesaplama hatasi | Runtime exception |
| `MISSING_OPTIONAL_FEATURE` | (Bu schema'da tum alanlar required -- şu an tetiklenmez) | Infrastructure-ready, unused |
| `INVALID_PREDICTION_DOMAIN` | Non-finite prediction | Output validation |

## 8. High-Cost Risk Limitations

Stage 11'in %89.9 high-cost underprediction bulgusu **DOGRUDAN bir
inference-time flag'e CEVRILEMEZ** -- cunku inference sirasinda gercek
target bilinmez. Bunun yerine `PREDICTION_OUTSIDE_REFERENCE_RANGE` gibi
GOZLEMLENEBILIR gostergeler kullanilir. **Gercek, bu notebook'ta bulunan
bulgu:** ExtraTrees (herhangi bir tree ensemble gibi) training leaf
degerlerinin disina extrapolate EDEMEZ -- bu nedenle bu flag, girdi ne
kadar ekstrem olursa olsun, pratikte NEREDEYSE HIC tetiklenmez (test
edildi: qty=1,000,000 / value=50,000,000 girdisi bile training range
icinde bir tahmin uretti).

## 9. Uncertainty Disabled Policy

`uncertainty_status` HER ZAMAN `"disabled"`dir. `request_interval=True`
SADECE `INTERVAL_NOT_APPROVED` flag'ini ekler -- hicbir lower/upper bound
veya fake confidence score **URETILMEZ**.

## 10. Business SLA Limitations

Bu notebook/policy, business-approved bir SLA veya asymmetric loss
function VARSAYMAZ. Risk flag'leri, bir fiyatlandirma/onay karari
mekanizmasi DEGILDIR -- sadece gozlemlenebilir, denetlenebilir sinyallerdir.
