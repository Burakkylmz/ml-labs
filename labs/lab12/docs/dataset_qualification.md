# LAB12 — Dataset Qualification Decision

## Dataset Qualification: CONDITIONAL GO

## Qualification Dimensions

| Dimension | Assessment | Evidence |
|---|---|---|
| **Q1 — Target Semantic Validity** | Partially confirmed | Freight Cost (USD) shipment-level toplam (D-002); gerçekleşmiş/quoted ayrımı doğrulanamadı. |
| **Q2 — Target Coverage** | Orta, dengesiz | 6198/10324 (%60.03) numeric; segmentler arasında %20.6-%79.4. |
| **Q3 — Target Representation** | Endişe verici | Numeric-target alt kümesi tüm popülasyonu temsil etmiyor — Vendor INCO Term ile güçlü ilişkili (Stage 3.4). |
| **Q4 — Observation Granularity** | İyi anlaşıldı | Freight Cost her ASN/DN grubunda en fazla bir kez kaydediliyor (D-004). |
| **Q5 — Feature Availability** | Yeterli, bir açık soru hariç | Shipment Mode/Country/INCO Term/Product Group mevcut; Weight'in zamanlaması doğrulanamadı (D-006). |
| **Q6 — Temporal Evaluation Feasibility** | Mümkün, bir uyarıyla | `Scheduled Delivery Date`: %100 parse, 2006-2015 kapsama, 2015 muhtemelen kısmi (D-007). |
| **Q7 — Sample Size & Segment Coverage** | Büyük segmentler için yeterli | Air (n=6113), Truck (n=2830); bazı küçük segmentler var (örn. DAP n=9). |
| **Q8 — Leakage Risk** | Yönetilebilir | `Freight Cost / Weight` gibi türetilmiş oranlar feature olarak **oluşturulmadı**. |

## Five Key Supporting Findings

1. Target coverage gerçek ve önemli (6198 Numeric Positive satır, ~%60.03) — bir NO-GO
   seviyesinde veri boşluğu değil.
2. Observation granularity artık tam olarak anlaşıldı: Freight Cost, shipment (ASN/DN) başına
   bir kez kaydedilen bir toplam; sibling line item'lar buna açıkça referans veriyor — büyük bir
   bilinmeyen ortadan kalktı.
3. Numeric-target bulunma oranı **rastgele değil** — Vendor INCO Term ile güçlü biçimde
   açıklanabiliyor (%21 DDP'ye karşı %89 FCA), bilinen, sevkiyat-öncesi erişilebilir bir alan.
   Bu, belirsiz bir kaygı değil, gerçek ve mekanik bir selection-bias riskidir.
4. Güvenilir bir prediction-time tarih alanı (`Scheduled Delivery Date`) mevcut — %100 parse
   oranı ve shipment-grubu içi tam tutarlılıkla — bu, group-aware bir chronological split'i
   mümkün kılıyor.
5. Weight (Kilograms), Freight Cost ile gerçek bir ilişki taşıyor (log-log korelasyon ~0.73),
   ama prediction-time availability'si (planlanmış mı, ölçülmüş mü) bu veri setinden
   doğrulanamıyor.

## Conditions for Proceeding to Stage 04

1. PoC'un target popülasyonunu, navlunun sözleşmesel olarak ayrı faturalandırıldığı sevkiyatlarla
   **açıkça sınırlandır** (Commodity-Included/Invoiced-Separately/Reference satırlarını
   regression target popülasyonundan çıkar ve bunu bilinen bir deployment-coverage sınırlaması
   olarak belgeleyin — sessizce atmadan).
2. Herhangi bir feature engineering başlamadan önce **D-005'i çöz** (line-item vs shipment-level
   modelleme birimi).
3. Weight (Kilograms) prediction-time availability (D-006) için **açık bir yanıt elde edin
   veya belgeleyin** — çözülemezse, Weight garanti bir production girdisi değil, bir sensitivity
   -analysis feature'ı olarak ele alınmalı.
4. Herhangi bir chronological split tasarımında **2015'i kısmi yıl olarak ele alın** (D-007).
5. **Selection-bias riskini (Q3)** model evaluation tasarımına açıkça taşıyın — özellikle INCO
   Term bazında segment-level performans, sadece genel metrikler değil, izlenmelidir.

## Why Not GO

Target representation (Q3) riski ve Weight'in prediction-time availability'sindeki (Q6/D-006)
açık soru, kayıtsız şartsız bir GO kararını haklı çıkarmayacak kadar önemlidir — ancak bu
riskler **yönetilemez** değildir (Observation Granularity gibi en büyük bilinmeyen zaten
çözüldü).

## Why Not NO-GO

Target semantiği büyük ölçüde anlaşılabilir durumda (D-002), coverage gerçek ve kullanılabilir
(~%60), observation granularity tam olarak çözüldü, ve en az bir güvenilir prediction-time
tarih alanı mevcut. Bu, "dataset kullanılamaz" seviyesinde bir engel değildir.

## Final Note

NO-GO kararı başarısız bir LAB anlamına gelmez; bu dataset için NO-GO kararı verilmedi, ancak
bu ilke CONDITIONAL GO için de geçerlidir: "sorunsuz" anlamına gelmez. Yukarıdaki 5 koşul,
Stage 04 başlamadan önce belgelenmeli ve takip edilmelidir.
