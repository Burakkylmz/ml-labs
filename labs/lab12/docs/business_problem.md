# LAB12 — Freight Cost Prediction: Business Problem

## Business Objective

Sevkiyat öncesinde erişilebilir operasyonel bilgilerden yararlanarak, gelecekteki bir
sevkiyatın navlun maliyetini (Freight Cost, USD) tahmin etmek.

**Out of Scope:** Freight Quote Optimization, Dynamic Pricing, Win Probability, Carrier Tender
Optimization, Route Optimization, Delivery Delay Prediction.

## Prediction Target

`Freight Cost (USD)`. Gerçek veri analizi (Stage 02-03), bu alanın **shipment-level** (ASN/DN
grubu başına en fazla bir numeric satır) bir toplam olduğunu göstermiştir — line-item'lar
arasında paylaştırılmış/tekrarlanmış değildir. Hedefin "gerçekleşmiş" mi yoksa "quoted" maliyet
mi olduğu bu veri setinden **doğrulanamamıştır** (açık soru).

## Prediction Time

**Pre-Shipment Cost Estimation** — sevkiyat planlamasına ilişkin temel bilgiler (Shipment Mode,
Vendor INCO Term, Country, Product Group, Line Item Quantity/Value) biliniyor, gerçek taşıma
maliyeti henüz kesinleşmemiş. `Scheduled Delivery Date`'in tam olarak freight booking'den önce
mi belirlendiği doğrulanamamıştır (açık soru, D-001).

## Observation Unit

Satır düzeyinde **line-item**; `ASN/DN #` gerçek fiziksel shipment'ı tanımlayan grup anahtarıdır
(10324 satır / 7030 benzersiz ASN/DN). Freight Cost, line-item değil, **shipment** düzeyinde bir
niceliktir (D-002, D-004).

## Required Inputs (Prediction-Time Feature Availability)

| Feature | Category |
|---|---|
| Destination Country | Available |
| Shipment Mode | Conditionally Available (360 satırda eksik) |
| Vendor INCO Term | Available |
| Product Group | Available |
| Line Item Quantity / Value | Available |
| Weight (Kilograms) | **Unknown** — planned mı yoksa measured mı olduğu doğrulanamıyor |
| Vendor | Available |
| Manufacturing Site | Conditionally Available |
| Scheduled Delivery Date | Conditionally Available |
| Delivered to Client Date / Delivery Recorded Date | **Unavailable** (post-shipment outcome) |

## Output Definition

Tek bir sayısal tahmin: tahmini navlun maliyeti (USD), shipment (ASN/DN) düzeyinde.

## Business Value

Fleet Capacity Planning, Resource Allocation, Maintenance Planning, Staffing Decisions, Service
Capacity Planning kararlarını besleyebilir.

## Evaluation Metrics

MAE (USD), RMSE (USD), WAPE (geçerli olduğunda), R² (destekleyici), Median Absolute Error,
High-Cost Segment MAE. Model başarısı yalnızca R² ile tanımlanmayacaktır.

## Assumptions

- `Freight Cost (USD)` değeri numeric olduğunda, o shipment'ın gerçek toplam navlun maliyetini
  temsil eder (doğrulanmış yapı, D-002).
- Pre-Shipment Cost Estimation geçerli bir çerçevedir (kısmen doğrulanmış, D-001).

## Known Limitations

- Numeric target coverage ~%60, segmentler arasında büyük farklılık gösteriyor (%21 DDP vs
  %89 FCA) — bu rastgele değil, Vendor INCO Term ile açıklanabilir.
- Weight (Kilograms) prediction-time availability doğrulanamamıştır.
- 2015 yılı muhtemelen kısmi (dataset `..._20150929` tarihli).

## Open Questions

1. Freight Cost gerçekleşmiş mi yoksa quoted maliyet mi?
2. Freight cost ile freight selling price ayrılabiliyor mu? (Bu dataset'te ayrı bir alan yok.)
3. Weight (Kilograms) planlanmış mı, ölçülmüş mü?
4. Scheduled Delivery Date, freight booking'den önce mi belirleniyor?
5. Line-item mi, shipment-level mi modelleme birimi olmalı? (D-005, henüz karara bağlanmadı.)

## Out-of-Scope Items

Freight Quote Optimization, Dynamic Pricing, Win Probability, Carrier Tender Optimization,
Route Optimization, Delivery Delay Prediction, model eğitimi, preprocessing, feature
engineering, train/test split (bunların tamamı Stage 04 ve sonrasının konusudur).

## Success Criteria (Pending Business Validation)

İş biriminden onaylanmış parasal tolerans değerleri bulunmadığından, kesin bir MAE acceptance
threshold **belirlenmemiştir** — bu değerler `Pending Business Validation` olarak
işaretlenmiştir. Başarı; baseline improvement, average absolute dollar error, high-cost
shipment performance, segment stability, reproducibility ve prediction-time validity unsurlarını
kapsamalıdır.
