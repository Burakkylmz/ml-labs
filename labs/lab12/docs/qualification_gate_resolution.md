# LAB12 — Qualification Gate Resolution (Stage 03.5)

Bu belge, Stage 01-03 sonunda verilen **CONDITIONAL GO** kararının, Stage 03.5'teki yeni
kanıtlar ışığında ne duruma geldiğini açıklar.

## Five Conditions — Status

| Condition_ID | Condition | Evidence | Status | Blocking | Remaining Risk |
|---|---|---|---|---|---|
| C-1 | Target population explicitly scoped | Shipment-level numeric target popülasyonu kesin tanımlı: 6198/7030 (%88.17) | **Resolved** | No | Gerçekleşmiş vs quoted maliyet semantiği hâlâ doğrulanamıyor |
| C-2 | D-005 resolved | Section 07 — Shipment-Level Modeling, somut kanıtla (0 multi-anchor grup, %100 tek-değerli INCO Term/Mode) kabul edildi | **Resolved** | No | Quantity/Value aggregation kuralı hâlâ Pending |
| C-3 | D-006 Weight policy documented | Section 10 — korelasyon yeniden doğrulandı (0.23 linear / 0.73 log-log); availability hâlâ Unknown | **Partially Resolved** | No | Domain-expert teyidi alınmadı |
| C-4 | D-007 partial-year risk documented | Section 11 — 2015 aylık sayılar Eylül sonrası çöküyor; 10 shipment'ta grup-içi tarih tutarsızlığı | **Resolved (statü düşürüldü)** | No | Business-valid zamanlama hâlâ doğrulanamıyor |
| C-5 | Selection bias re-evaluated on correct observation unit | Section 09 — INCOTERM coverage shipment-level'de yeniden hesaplandı; fark küçülüyor (DDP %21→%49.2) ama kalıcı | **Resolved** | No | Segment-level model evaluation gerekli (modelleme başladığında) |

## Why No Condition Is Blocking

Hiçbir koşul `Blocking` olarak işaretlenmedi, çünkü:
- Reference integrity **%100** (en kritik bilinmezlik tamamen çözüldü).
- Shipment-level target mapping **net ve auditable** (Shipment Data Contract, Bölüm 9'daki
  invariant'lar).
- Kalan açık sorular (Weight, Quantity/Value aggregation, 2015) **production feature olarak
  onaylanmış gibi sunulmadan**, açıkça `Unknown`/`Pending`/`Conditional` olarak işaretli.

## Final Gate Decision

### Dataset Qualification: **CONDITIONAL GO** (devam ediyor)

**GO'ya yükseltilmedi çünkü:**
- D-006 (Weight) hâlâ `Under Investigation` / `Partially Resolved`.
- Line Item Quantity/Value aggregation hâlâ `Pending`.
- Gerçekleşmiş vs quoted maliyet semantiği hâlâ doğrulanamıyor.

**NO-GO'ya düşürülmedi çünkü:**
- Reference resolution %100 (kritik bir engel yok).
- Shipment-level coverage (%88.17) güçlü ve gerçek.
- D-005 artık `Accepted` — büyük bir mimari karar netleşti.
- Selection bias yönetilebilir (izlenmesi gereken, ama modellemeyi engellemeyen bir risk).

### Stage 04 Readiness: **CONDITIONAL GO**

Stage 01-03'teki CONDITIONAL GO'dan farkı: koşullar artık **soyut değil, somut ve
auditable** — her biri gerçek bir sayıya, gerçek bir kanıta bağlı.

## Updated D-005 / D-006 / D-007 Status

| Decision | Before Stage 03.5 | After Stage 03.5 |
|---|---|---|
| D-005 | Pending | **Accepted — Shipment-Level Modeling** |
| D-006 | Under Investigation | **Partially Resolved** (policy documented, availability still Unknown) |
| D-007 | Accepted | **Conditional** (downgraded — partial-year + 10-shipment inconsistency found) |

## Remaining Critical Risks (into Stage 04)

1. Gerçekleşmiş vs quoted navlun maliyeti semantiği doğrulanamadı.
2. Weight (Kilograms) prediction-time availability doğrulanamadı.
3. Line Item Quantity/Value için ürün türleri arası toplama kuralı hâlâ Pending.
4. 2015 kısmi yıl — Stage 05 split tasarımında dışlanmalı/caveat'lanmalı.
5. INCOTERM-temelli selection bias shipment-level'de de kalıcı — model evaluation'a taşınmalı.

## Critical Rule Compliance

Unresolved critical reference integrity veya shipment-level target mapping problemi
**bulunmadığından**, koşulsuz bir `GO` verilmemiştir ama `NO-GO` da gerekmemiştir. Weight
availability belirsizliği sürdüğü için Weight ana feature set'inden **çıkarılarak** kontrollü
ilerleme öneriliyor — bu, Weight'in production feature olarak onaylandığı anlamına **gelmez.**
