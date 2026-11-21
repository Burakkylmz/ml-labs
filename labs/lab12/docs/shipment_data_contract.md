# LAB12 — Shipment Data Contract

Bu belge, Stage 03.5'te gerçek veri üzerinde doğrulanan bulgulara dayanarak, LAB12'nin
shipment-level dataset contract'ını tanımlar.

## 1. Business Entity

**Shipment** — fiziksel bir sevkiyat, `ASN/DN #` ile tanımlanır.

## 2. Primary Key

**`ASN/DN #`** — doğrulandı: 0 eksik değer, 7030 benzersiz değer, referans mekanizmasıyla
%100 tutarlı (bkz. Bölüm 8).

## 3. Observation Unit

**Bir shipment = bir model observation.** Bu karar D-005 kapsamında **Accepted** olarak
kesinleşmiştir (Stage 03.5 Section 07) — line-item-level modelleme, shipment-level target'ı
(D-002) yanlış temsil edeceği için reddedilmiştir.

## 4. Target Contract

- **Alan:** `Freight Cost (USD)`
- **Unit:** USD
- **Semantic level:** Shipment (hiçbir shipment'ta 1'den fazla numeric anchor yok — doğrulandı)
- **Target eligibility:** Numeric Positive, business meaning'i (gerçekleşmiş vs quoted) henüz
  tam doğrulanmamış bir koşula bağlı
- **Missing/non-numeric categories:** Ayrı izlenir — "Freight Included in Commodity Cost"
  (1442 satır), "Invoiced Separately" (239 satır), "Reference to Another Shipment" (2445 satır,
  %100 structural resolution ile çözüldü)
- **Zero/negative values:** 0 satırda bulundu (açıkça ölçüldü, varsayılmadı)

## 5. Prediction Time

**Pre-Shipment Cost Estimation** — ancak `Scheduled Delivery Date`'in business-valid (gerçek
booking anında bilinen) bir alan olduğu hâlâ **doğrulanamamıştır** (D-001, Conditional).

## 6. Feature Eligibility

| Feature | Category |
|---|---|
| Shipment Mode | Conditionally Available (360 shipment'ta eksik) |
| Vendor INCO Term | Available (shipment içinde %100 tek değerli) |
| Country, Product Group | Available |
| Line Item Quantity / Value | Available (line-item düzeyinde, aggregation Pending) |
| Weight (Kilograms) | **Unknown** (D-006, planlı mı ölçülmüş mü doğrulanamadı) |
| Scheduled Delivery Date | Conditionally Available (10 shipment'ta grup-içi tutarsız) |
| Delivered to Client Date / Delivery Recorded Date | Unavailable (post-shipment) |

## 7. Aggregation Contract

| Source Column | Semantic Level | Aggregation Candidate | Evidence | Double-Counting Risk | Decision |
|---|---|---|---|---|---|
| Weight (Kilograms) | Shipment-Level Numeric | First Non-Null (≡ Max/Sum) | 0 shipment'ta >1 numeric weight satırı | None | Conditional |
| Line Item Quantity | Line-Item Numeric | Sum (candidate) | Multi-item shipment'larda gerçekten farklı değerler | Low if summed once | Pending |
| Line Item Value | Line-Item Numeric | Sum (candidate) | Aynı şekilde | Low if summed once | Pending |
| Shipment Mode | Shipment-Level Categorical | First Non-Null | %100 shipment-içi tek değerli | None | Accepted |
| Vendor INCO Term | Shipment-Level Categorical | First Non-Null | %100 shipment-içi tek değerli | None | Accepted |
| Scheduled Delivery Date | Shipment-Level Date | Min (candidate) | %99.86 shipment-içi tutarlı (10/7030 istisna) | None | Conditional |

## 8. Reference Resolution Contract

- **Reference pattern:** `See <ASN/DN> (ID#:<row_id>)` — gerçek veride %100 bu formatta
  (regex ile doğrulandı, 0 parse hatası).
- **Anchor matching rule:** Metinde belirtilen `ID#`, gerçek bir satıra ve metinde belirtilen
  `ASN/DN`'ye karşılık gelmelidir.
- **Ambiguous reference policy:** Bu veri setinde gözlenmedi (0 vaka) — `ID` benzersiz olduğu
  için yapısal olarak ambiguous anchor oluşamaz.
- **Missing anchor policy:** Bu veri setinde gözlenmedi (0 vaka).
- **Cross-shipment reference policy:** Bu veri setinde gözlenmedi (0 vaka) — tüm referanslar
  kendi shipment'larına işaret ediyor.
- **Validation condition:** Bir referansın "çözülmüş" sayılması için, metindeki `ASN/DN` değeri
  gerçek anchor satırının `ASN/DN #` değeriyle eşleşmelidir — anchor'ın numeric olup olmaması
  **ayrı bir sorudur** (105 referans numeric olmayan ama geçerli bir "Invoiced Separately"
  anchor'a işaret eder).

## 9. Data Quality Invariants (Verified)

- Bir canonical observation için bir shipment key.
- Shipment başına en fazla bir eligible cost anchor (doğrulandı — istisna yok).
- Sessizce çözülmemiş referans yok (%100 resolution rate).
- Freight cost çift sayılmıyor (asla toplanmıyor).
- Uydurma target label yok.
- Desteklenmeyen aggregation uygulanmadı (Section 08 önizlemesi read-only/audit-only).
- Post-shipment feature leakage yok (Delivered/Recorded tarihleri Unavailable kalıyor).

## 10. Population Definition

| Population | Size |
|---|---|
| Entire Raw Dataset | 10324 rows |
| Unique Shipment Population | 7030 shipments |
| Numeric-Target Shipment Population | 6198 shipments (%88.17) |
| Potential Inference Population | Tanımlanamıyor — ex-ante bir business rule (örn. INCO Term tabanlı) henüz resmi olarak kabul edilmedi |

## 11. Known Limitations

- Gerçekleşmiş vs quoted maliyet ayrımı doğrulanamıyor.
- Weight zamanlaması (planlı/ölçülmüş) doğrulanamıyor.
- Selection bias (INCO Term ile) shipment-level'de de mevcut (azalmış ama kalıcı).
- 2015 kısmi yıl.
- Line Item Quantity/Value aggregation kuralı (farklı ürün türleri arasında toplamanın
  geçerliliği) henüz çözülmedi.

## 12. Acceptance Criteria

Bu shipment-level contract, aşağıdaki koşullar sağlandığında **kabul edilmiş** sayılır:

1. Observation unit = Shipment (✅ sağlandı, D-005 Accepted).
2. Primary key benzersizliği ve referans bütünlüğü doğrulandı (✅ sağlandı, %100 resolution).
3. Target eligibility popülasyonu açıkça tanımlı (✅ sağlandı — Numeric Positive, %88.17
   shipment coverage).
4. Her feature için availability sınıflandırması mevcut (✅ sağlandı, bazıları `Unknown`/
   `Conditionally Available` olarak açıkça işaretli).
5. Aggregation kuralları ya `Accepted` ya da açıkça `Pending`/`Conditional` olarak işaretli
   (✅ sağlandı — hiçbiri gizlenmiş/varsayılmış değil).

Bu kriterlerin tamamı karşılanmıştır — contract **auditable ve Stage 04'e aktarılabilir**
durumdadır, ancak 3 açık koşul (Weight, Quantity/Value aggregation, 2015 partial-year)
belgelendiği şekliyle devam etmektedir.
