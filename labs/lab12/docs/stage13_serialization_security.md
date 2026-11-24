# LAB12 — Stage 13 Serialization Security

## 1. Serialization Fundamentals

Serialization = Python object graph'ini (fitted Pipeline) byte stream'e
donusturme. Deserialization = ters islem. Her ikisi de `joblib` ile
yapilir -- bu, scikit-learn/numpy objeleri icin verimli calisan, projenin
zaten var olan bir bagimliligidir.

## 2. Joblib vs Pickle vs skops

| Format | Secim Nedeni |
|---|---|
| Pickle | Dusunuldu ama joblib zaten numpy-array-agir sklearn objeleri icin daha verimli |
| **joblib (secilen)** | Native sklearn/numpy destegi, mevcut bagimlilik, trusted-artifact policy ile guvenli hale getirildi |
| skops.io | Degerlendirildi (Advanced Challenge 4) ama ek bagimlilik gerekcesi bu prototype icin yeterli bulunmadi |
| ONNX | Degerlendirildi ama `ColumnTransformer`+`ExtraTrees` icin conversion fidelity riski nedeniyle ERTELENDI |

## 3. Trusted Artifacts

`joblib.load()` **asla** dogrudan cagrilmaz. `TrustedBundleLoader.load()`,
6 kontrolden (path/manifest/identity/SHA-256/dependency) SONRA deserialize
eder.

## 4. Code Execution Risk

Pickle/joblib deserialization, keyfi Python kod calistirabilir. Bu nedenle
**guvenilmeyen** bir kaynaktan artifact yuklenmesi asla desteklenmez.

## 5. Integrity vs Authenticity

**Integrity:** Dosya beklenen bytes ile eslesiyor (SHA-256 testi ile
dogrulandi). **Authenticity:** Artifact'in gercekten guvenilen bir
build surecinden geldigi. **Eger manifest VE model dosyasi ayni saldirgan
tarafindan birlikte degistirilmisse, checksum eslesmesi authenticity
KANITLAMAZ.** Bu prototype'ta signed release/trusted distribution
mekanizmasi YOKTUR -- bu acikca bir sinirlama olarak belgelenmistir.

## 6. Secure Loading

Sira: (1) path `allowed_root` icinde mi, (2) manifest var mi, (3)
model_id/trial_id manifest'te beklenenle eslesiyor mu, (4) SHA-256
eslesiyor mu, (5) python/sklearn version uyumlu mu, (6) **ancak o zaman**
`joblib.load()`.

## 7. Safe Artifact Paths

`TrustedBundleLoader(allowed_root=...)`, path'i `allowed_root.resolve()`
disina cikan HERHANGI bir bundle'i reddeder (path traversal/arbitrary path
koruması, test edildi: `untrusted_path_outside_allowed_root_rejected`).

## 8. Version Compatibility

**Gercek, bu notebook'ta bulunan bir finding:** Local (Python 3.11.15) ve
bu projenin Docker image'i (Python 3.11.18) arasinda bir PATCH version
farki var. Orijinal strict-exact-match politika bunu dogru bicimde
REJECT etti (fail-closed calisti). Bu, bilincli bir policy duzeltmesine
yol acti: `python_version` artik SADECE major.minor karsilastirilir (patch
sürümleri joblib/pickle uyumlulugunu etkilemez); `sklearn_version` ise HALA
exact-match gerektirir (estimator internals/pickle format sklearn minor
surumleri arasinda degisebilir).

## 9. Corrupted Artifact Handling

`model.joblib` dosyasi 3 farkli corruption senaryosunda (truncate last
byte, flip first byte, truncate half) test edildi -- **3/3 dogru tespit
edildi** (Advanced Challenge 1, izole test copy uzerinde, orijinal
artifact BOZULMADI).

## 10. Security Test Results

6/6 security failure-mode test PASSED (`stage13_artifact_security_tests.csv`):
corrupted checksum, wrong model_id, wrong trial_id, untrusted path, missing
manifest, dependency version mismatch -- hepsi dogru sekilde REJECTED.

## 11. Residual Risks

(1) Integrity != authenticity -- signed release YOK. (2) Trusted
distribution mekanizmasi (orn. internal package registry) bu prototype
kapsaminda implement edilmedi. (3) `allowed_root` restriction, loader
instance'inin dogru configure edilmis olmasina baglidir -- Stage 14, bu
degeri sabit/hardcoded tutmalidir, kullanicidan path ALMAMALIDIR.
