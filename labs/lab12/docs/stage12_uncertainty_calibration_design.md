# LAB12 — Stage 12 Uncertainty Calibration Design

## 1. Uncertainty Fundamentals

**Aleatoric:** Verinin dogal variability/noise -- daha fazla veri ile
AZALMAZ. **Epistemic:** Model bilgisi/veri eksikligi kaynakli -- daha
fazla/iyi veri ile AZALABILIR.

## 2. Prediction vs Confidence Intervals

Prediction Interval: YENI bir observation'in gercek degerini kapsamasi
amaclanan aralik. Confidence Interval: bir population parametresi hakkindaki
belirsizlik. **Bu notebook Prediction Interval ile ilgilenir.**

## 3. Conformal Prediction

6 adim: fit model -> independent calibration predictions -> conformity
scores ($r_i=|y_i-\hat y_i|$) -> calibration quantile -> interval ($L=\hat
y - q_\alpha$, $U=\hat y + q_\alpha$) -> future coverage degerlendirme.

## 4. Exchangeability

Standard split conformal finite-sample marginal coverage guarantee,
calibration/test observations arasinda exchangeability varsayimina dayanir.

## 5. Temporal Dependence

Freight shipments kronolojik yapidadir -- distribution shift, nonstationarity,
selection bias, degisen segment composition exchangeability'yi ihlal
edebilir. **Nominal %90 interval otomatik %90 coverage garantisi anlamina
GELMEZ.**

## 6. Calibration Leakage

Demonstrasyon (notebook Section 15): ayni modelin OWN training residuals'i
calibration icin kullanildiginda, P90 **%16.9 daha dar** cikti (7,900.34 USD
leaky vs 9,511.30 USD honest) -- yapay olarak dar/overconfident interval'lar
uretir. Bu yaklasim notebook'un gercek calibration'inda KULLANILMAMISTIR.

## 7. Stage 05 Compatibility

Stage 05'in 4 frozen outer fold'u (evaluation years 2010-2013) degistirilmeden
reuse edildi.

## 8. Inner Train/Calibration Policy

Her outer fold'un training history'sinin SON calendar year'i calibration,
kalani inner training:

| Outer Eval Year | Inner Train | Calibration | Inner Train N | Calibration N | Eval N |
|---|---|---|---:|---:|---:|
| 2010 | 2006-2008 | 2009 | 1071 | 664 | 780 |
| 2011 | 2006-2009 | 2010 | 1735 | 780 | 776 |
| 2012 | 2006-2010 | 2011 | 2515 | 776 | 861 |
| 2013 | 2006-2011 | 2012 | 3291 | 861 | 835 |

Tum invariant'lar (no overlap, no temporal inversion) programatik olarak
dogrulandi.

## 9. Frozen Estimator Configuration

M04-T003 parametreleri (ExtraTrees) degismeden reuse edildi -- her fold icin
**diagnostic-only research replica** fit edildi (Object A'nin full-development
modeli DEGIL).

## 10. Conformity Scores

$r_i = |y_i - \hat y_i|$ -- her fold'un kendi calibration donemi uzerinde
hesaplandi, `stage12_calibration_residuals.csv`.

## 11. Quantile Calculation

$k=\lceil (n_{cal}+1)(1-\alpha)\rceil$, capped at $n_{cal}$. `SplitConformalCalibrator`
sinifi 10 unit test ile dogrulandi (residual hesaplama, quantile index,
interval construction, invalid alpha, empty/insufficient sample, NaN/Inf,
ordering, determinism, leakage-by-construction).

## 12. Coverage Levels

%80 ve %90 nominal, deney oncesi dondu (`stage12_calibration_protocol.json`).

## 13. Nonnegative Interval Policy

RAW (unclipped) lower/upper bound tum coverage/width metriklerinde
kullanildi. **3,778/6,504 (%58.1) satirda raw lower bound negatif** --
Freight Cost negatif olamayacagi icin bu, interval'larin pratik kullanilabilirligi
acisindan onemli bir sinirlamadir. Bir nonnegative-domain presentation
varyanti (`Lower_Clipped`) ayrica hesaplandi ve display-only olarak
etiketlendi -- primary point prediction'a gizli clipping UYGULANMADI.

## 14. Known Limitations

(1) Development-only, sadece 4 outer fold -- coverage tahmininin kendisinde
orneklem belirsizligi var. (2) Research replicas, Object A'nin (full-dev)
BIREBIR AYNISI degil. (3) Stage 10 hyperparameter secimi development-CV'den
geldigi icin bu calibration evaluation'i da model-secim gecmisinden tam
bagimsiz degil. (4) 2014/2015 hicbir asamada kullanilmadi.
