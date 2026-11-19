# Paket serah terima Agent 2

> **Koreksi 20 November 2026:** status di bawah mendahului audit independen. Status
> remediasi terkini (tujuh isu P1, PARTIAL/BLOCKED, belum ada penutupan independen)
> ada di [REMEDIATION_AGENT2.md](REMEDIATION_AGENT2.md); reproduksi offline di
> [`docs/REPRODUCE.md`](../docs/REPRODUCE.md). Angka 2.357 grid di bawah memakai
> demografi lama; dengan demografi terkoreksi skenario konservatif menjadi 2.355.

**Status (pra-audit): DONE WITH DOCUMENTED LIMITATIONS untuk paket implementasi dan QA.** Hasil ilmiah serta naskah belum dinyatakan final. Tidak ada commit, merge, atau perubahan di workspace Agent 1/3.

- [Handoff lengkap](AGENT2_HANDOFF.md): metode, bukti, reproduksi, dan instruksi auditor.
- [Daftar isu](AGENT2_ISSUES.md): perbaikan implementasi serta keterbatasan sumber/metode.
- [Kamus data](AGENT2_DATA_DICTIONARY.md): seluruh kolom, unit, missingness, dan kompatibilitas.
- [Register keputusan](AGENT2_DECISION_REGISTER.md): sepuluh keputusan ilmiah yang memerlukan kesepakatan tim.
- Tabel sumber terintegrasi: `data/processed/final_model_features.csv`, seluruh 2.765 ID.
- Bukti QA: `outputs/qa/agent2/`, termasuk CSV, GeoPackage, peta, hasil tes, dan manifest hash.
- Proyek QGIS: `qgis/agent2_gis_qa.qgz`.

Seluruh 226 jarak kosong berasal dari komponen jaringan tanpa node tujuan taman kandidat; jaringan penuh tidak memulihkannya. Ini bukan bukti bahwa akses pejalan kaki nyata tidak tersedia. Seluruh 66 far-snap telah diberi diagnosis; 17 juga tanpa rute, dan 19 memiliki ruas jalan lebih dekat daripada node yang dipilih.

Keselarasan Agent 1 diverifikasi menggunakan raster asli pada semua grid. Satu grid `JKT_R037_C062` memiliki nilai LST/NDVI yang telah dikirim, tetapi dikeluarkan oleh ambang kualitas provisional 50%. Eksklusi tersebut terpisah dari 226 rute kosong, sehingga baseline Agent 3 berisi 2.538 grid. Skor dan peringkat baseline berhasil direproduksi.

Temuan yang harus dibaca sebelum menerima rekomendasi: OSM taman/jaringan berasal dari 2026, sedangkan suhu dan demografi 2024; status akses 1.005 dari 1.015 taman tidak diketahui; pintu masuk belum diverifikasi; pembatasan node/gate diabaikan baseline. Skenario pembatasan konservatif dengan snap tetap menghasilkan 407 rute kosong dan 2.357 grid layak. Skenario ini terpisah dan tidak menggantikan hasil resmi secara diam-diam.

Korelasi jumlah penduduk dan jumlah usia rentan sangat tinggi (Spearman 0,99955). Alternatif porsi rentan telah tersedia. Ada 19 grid tanpa dukungan piksel umur valid, termasuk 13 grid berpenduduk; nilai lama dipertahankan dengan flag kualitas. Kebijakan sumber, akses, kerentanan, dan tahun OSM perlu diputuskan sebelum kesimpulan ilmiah final.

Mulai audit dari `outputs/qa/agent2/validation_summary.json` dan `artifact_manifest.json`, lalu jalankan perintah dalam handoff. Kode Agent 3 yang diuji adalah snapshot provisional yang hash-nya dibekukan, bukan rilis yang diasumsikan sudah di-commit.
