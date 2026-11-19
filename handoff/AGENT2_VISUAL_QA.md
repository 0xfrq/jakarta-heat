# Catatan inspeksi visual GIS

Tanggal sesi: 20 November 2026, Asia/Jakarta. Pemeriksa: Agent 2 melalui image viewer pada PNG yang benar-benar dirender. Ini bukan inspeksi lapangan atau sesi GUI QGIS interaktif. Proyek QGIS dibuat dan diverifikasi melalui standalone PyQGIS; 21 layer valid.

| Bukti | Yang diperiksa | Temuan dan batas interpretasi |
| --- | --- | --- |
| `outputs/qa/agent2/gis_review_atlas.png` | LST, NDVI, populasi, jumlah usia rentan, jarak, missingness, M1–M4, perubahan peringkat, skenario jaringan penuh | Tidak terlihat pergeseran geografis besar; jumlah usia rentan mengikuti pola populasi. Lubang model mengikuti eksklusi input. Pemeriksaan numerik terpisah mengonfirmasi geometri dan nilai. |
| `outputs/qa/agent2/network_edge_qa_map.png` | Sebaran 226 rute kosong, 66 far-snap, taman kandidat dan sel kecil | Missingness tampak berkelompok, terutama pada kantong utara/pantai dan timur/selatan. Titik pada panel sel kecil menandai lokasi sel, bukan memperbesar luas analisisnya. |
| `outputs/qa/agent2/far_snap_sample_details.png` | `JKT_R056_C000`, `JKT_R024_C047`, `JKT_R023_C045`, `JKT_R004_C037` | R056_C000 adalah sel sempit terpotong. R024_C047 memperlihatkan ruas dekat bagian dalam sel meskipun node snap jauh. Sampel lain memperlihatkan ruas yang jarang di sekitar titik. Tidak ada klasifikasi air, industri, kepemilikan atau penghalang fisik yang dipastikan dari peta ini. |
| `outputs/qa/agent2/eastern_raster_coverage_detail.png` | `JKT_R037_C061`, `JKT_R037_C062`, `JKT_R038_C061`, `JKT_R038_C062`; piksel LST dan band validitas raster asli | Kekosongan piksel LST berada di sisi timur, selaras dengan valid fraction rendah. R037_C062 memiliki bagian valid sekitar 0,278; nilai grid tetap telah dikirim. Batas aset GEE remote tidak diperiksa langsung. |
| `outputs/qa/agent2/lisa_m4_qa.png` | Label `klaster_fdr` keluaran snapshot Agent 3 | Klaster menggunakan geometri grid yang sama. Area putih adalah grid tanpa hasil, bukan kelas tidak signifikan. Tidak dilakukan ulang permutasi statistik atau validasi ilmiah klaster melalui gambar. |
| `outputs/qa/agent2/park_samples_qa.png` | Enam poligon, titik representatif dan ruas di sekitarnya | Titik adalah representative point, bukan entrance. Jalan yang tampak dekat tidak membuktikan akses legal atau pintu masuk terbuka. |

Sampel taman yang benar-benar ditampilkan:

| OSM park ID | Nama lokal | Tag akses | Bukti yang tersedia | Status akses nyata |
| --- | --- | --- | --- | --- |
| `way_33194134` | Unnamed Park | unknown | Poligon, representative point, ruas sekitar; 44 tujuan grid dalam skenario jaringan penuh | Belum diverifikasi |
| `way_153936931` | Unnamed Park | unknown | Poligon dan ruas sekitar; 38 tujuan grid | Belum diverifikasi |
| `way_1378191866` | RPTRA Rorotan | unknown | Poligon dengan ruas internal yang dipetakan; 36 tujuan grid | Belum diverifikasi |
| `way_668817880` | Taman Sungai Kendal | unknown | Poligon dan ruas internal; 32 tujuan grid | Belum diverifikasi |
| `way_1497568802` | Lapangan Tenis | yes | Tag positif dan poligon kecil; 20 tujuan grid | Tag bukan verifikasi publik; nama juga perlu ditinjau untuk definisi taman |
| `way_1530586555` | Blok C | unknown | Sampel dekat batas administratif, poligon dan ruas sekitar | Belum diverifikasi |

Tidak ada eksklusi baru yang diklaim terkonfirmasi melalui visual ini. Dua eksklusi historis berdasarkan tag `private` dan `permit` tersedia di `parks_excluded_original_tags.csv`. Tidak ada jam buka atau status gate yang diperkirakan.

Auditor manusia disarankan membuka proyek QGIS dan menambahkan bukti pemerintah/kunjungan lapangan, khususnya untuk poligon tanpa nama, objek dengan nama lapangan olahraga, tujuan yang melayani banyak grid, node terbatas, serta konektor yang mungkin melintasi penghalang.
