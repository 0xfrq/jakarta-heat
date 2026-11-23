# Jakarta Heat

> **Status rilis:** paper final v1 dan seluruh output riset sudah dikonsolidasikan
> di branch `main`. Lihat [`FINAL_RELEASE.md`](FINAL_RELEASE.md) untuk peta
> deliverables, checksum paper, status verifikasi, dan batasan ilmiah.

RC1 integration: see [consolidated reproduction](docs/RC1_REPRODUCE.md),
[handoff](handoff/RC1_HANDOFF.md), and [verification](handoff/RC1_VERIFICATION.md).
These describe the consolidated candidate; workstream handoffs below retain
their historical scope. Scientific policy remains provisional pending re-audit.

Analisis spasial penduduk rentan dan akses berjalan kaki ke taman di lima kota Jakarta.
Unit analisisnya grid 500 meter. Script aksesibilitas menghasilkan jarak model ke taman
terdekat, termasuk jarak penghubung titik grid/taman ke jaringan jalan.

## Menjalankan jaringan offline

Aktifkan environment Python yang berisi GeoPandas, OSMnx, NetworkX, pandas,
requests, dan dependensinya. Jalankan perintah berikut dari folder proyek.

Jika proses versi lama masih berjalan, hentikan dengan **Ctrl+C** di terminalnya
sebelum menjalankan versi baru. Jangan jalankan dua builder ke file output yang sama.

Sediakan `data/raw/osm/jakarta_all.osm`, lalu:

```powershell
python scripts/05a_build_offline_network.py
python scripts/05_walking_accessibility.py --city "Jakarta Barat" --network-source offline
```

Builder memindai XML dua kali secara streaming: pertama menyimpan hanya way jalan
yang boleh dilalui pejalan kaki, lalu mengambil node yang dirujuk jalan tersebut.
Bangunan, relasi, dan node yang tidak diperlukan tidak dimuat ke graph.
File kecil `jakarta_all_walk.osm` dipakai untuk pembentukan dan penyederhanaan graph.
Pemindaian menampilkan persentase dan ETA **untuk pemindaian yang sedang berjalan**;
tahap graph menampilkan pesan aktivitas setiap 15 detik.

Hasilnya `data/processed/walk_jakarta_all.graphml`. File sementara baru diganti
menjadi hasil akhir setelah penyimpanan berhasil. Cache XML dapat dipakai lagi
jika pembentukan graph terputus. Graph tetap memerlukan RAM sesuai jumlah jalan;
streaming tidak membuat penggunaan memori keseluruhan menjadi konstan.

Cache menyimpan versi filter, ukuran, dan waktu perubahan sumber. Gunakan
`python scripts/05a_build_offline_network.py --force` untuk membangun ulang semuanya.

## Aksesibilitas dan fallback online

```powershell
python scripts/05_walking_accessibility.py --city "Jakarta Barat"
```

Mode `auto` mencari cache kota yang sesuai, lalu jaringan offline seluruh Jakarta,
lalu mengunduh online jika keduanya tidak tersedia. `--network-source offline`
menjamin tidak ada permintaan jaringan. Cache kota dari versi lama masih diterima
jika graph seluruh Jakarta belum tersedia, dengan pesan bahwa filternya masih lama.
Gunakan `--refresh-network` untuk melewati cache kota dan memakai sumber yang dipilih.

Untuk memilih online secara eksplisit:

```powershell
python scripts/05_walking_accessibility.py --city "Jakarta Barat" --network-source online --refresh-network
```

Unduhan online dibagi menjadi kotak 4 km, dengan timeout baca 90 detik dan dua
percobaan per endpoint per kotak. Server utama dan cadangan dicoba bergantian.
Bagian yang selesai disimpan di `cache/walking_network/`, sehingga rerun dapat
melanjutkan tanpa mengulang bagian yang berhasil. HTTP error, JSON rusak, respons
dengan pesan `remark`, dan referensi node yang tidak lengkap tidak dianggap sukses.
Ketersediaan server publik tetap di luar kendali script.

Opsi tambahan: `--tile-size-m 2000`, `--timeout 120`, `--attempts 2`,
`--buffer-m 1500`, dan `--overpass-url https://overpass-api.de/api` (boleh diulang
untuk server cadangan). Mengubah ukuran kotak/timeout dapat mengubah kunci cache.

Output per kota: `accessibility_<kota>.csv`, `accessibility_<kota>.gpkg`,
dan `roads_walk_<kota>.gpkg` di `data/processed/`. Titik taman masih memakai
titik representatif poligon, bukan pintu masuk yang diverifikasi.
Jaringan hasil generate dan cache tidak dimasukkan ke Git karena bisa besar.

## Verifikasi

```powershell
python -m unittest discover -s tests -v
```

Pengujian menggunakan data sintetis dan respons jaringan tiruan; tidak mengunduh
OSM atau menimpa hasil analisis proyek. Referensi API:
[dokumentasi OSMnx](https://osmnx.readthedocs.io/en/latest/user-reference.html).

## Handover Agent 2 dan QA integrasi

Mulai dari [ringkasan Indonesia](handoff/AGENT2_README_ID.md),
[handoff lengkap](handoff/AGENT2_HANDOFF.md), dan
[register keputusan ilmiah](handoff/AGENT2_DECISION_REGISTER.md).
Tabel `data/processed/final_model_features.csv` mempertahankan seluruh 2.765 grid;
kelayakan baseline Agent 3 dicatat terpisah (2.538 grid).

Status remediasi Agent 2 (audit independen 20 November 2026) ada di
[ledger remediasi](handoff/REMEDIATION_AGENT2.md); status lama "DONE WITH
DOCUMENTED LIMITATIONS" hanya berlaku untuk handover engineering sebelum audit.
Jalur reproduksi offline Agent 2 dari input beku terdokumentasi di
[docs/REPRODUCE.md](docs/REPRODUCE.md) (`scripts/run_reproduction.ps1 -Scope Agent2`).
Ini bukan reproduksi gabungan A1/A2/A3: verifikasi integrasi konsolidasi
**belum diuji** (IN-01). Output terkoreksi ditulis sebagai file `*_corrected*`
terpisah; file lama tetap dipertahankan.

OSM yang tersedia bertanggal 2026, sedangkan suhu dan demografi merujuk 2024
(proksi periode campuran). Akses publik/pintu masuk taman belum diverifikasi;
pembatasan node/konektor diuji sebagai skenario konservatif terpisah. Rute
kosong tetap tidak diketahui, bukan jarak nol. Grid tanpa dukungan piksel sumber
bernilai null, bukan nol. Hasil ilmiah dan bobot model tetap provisional.
## Modeling, statistik spasial, dan dashboard (Person 3 / Agent 3)

Lihat [`dashboard/README.md`](dashboard/README.md), metode di [`docs/agent3_methods.md`](docs/agent3_methods.md),
dan serah terima di [`handoff/AGENT3_HANDOFF.md`](handoff/AGENT3_HANDOFF.md).

```powershell
python -m pip install -r dashboard\requirements.txt
python -m pytest tests\agent3 -q
python scripts\run_agent3_pipeline.py --status
python -m streamlit run dashboard\app.py
```
