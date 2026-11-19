# PROMPT UNTUK AI AGEN PENGGANTI — LANJUTKAN REMEDIASI AGENT 3

Anda menggantikan Agent 3 pada Jakarta Heat Inequality Mapper. **Lanjutkan pekerjaan yang sudah ada; jangan mulai audit umum atau riset baru dari nol.** User menghentikan agen sebelumnya karena limit dan meminta pekerjaan tersisa dialihkan kepada Anda. Tujuannya menuntaskan implementasi, pengujian, dokumentasi dan bukti penerimaan isu Agent 3 sejauh input nyata mendukung, lalu menyerahkan hasil untuk integrasi/re-audit. Jawaban akhir wajib Bahasa Indonesia.

## Batas kerja dan sumber wajib

- Satu-satunya worktree tulis: `D:\jakarta-heat-agent3` (PowerShell, Python `.venv/Scripts/python.exe`). Jangan mengubah worktree Agent1/2 atau original.
- Auditor read-only di `D:\jakarta-heat\audit`. Baca tujuh sumber wajib: `ISSUE_REGISTER.csv`, `INDEPENDENT_AUDIT_REPORT.md`, `OWNER_TASKS.md`, `REMEDIATION_ROADMAP.md`, `NOVELTY_REVIEW.md`, `ACCEPTANCE_MATRIX.md`, `RELEASE_GATE.md`.
- Baca dahulu `handoff/REMEDIATION_AGENT3.md` (ledger interim rinci per isu), `docs/AGENT3_REMEDIATION_REPRODUCE.md`, `docs/research_decisions.md`, `docs/demographic_model_interface.md`, `docs/spatial_inference_spec.md`, dan `handoff/AGENT3_HANDOFF.md` (sejarah lama, status terbaru mengesampingkan klaim historis).
- Isu milik Anda seluruhnya P1: **DM-02, MD-02, MD-03, EL-01, RS-02, ST-01, NV-02, IN-03, UI-01**. Baca dependency AC-01/02, DM-01, TM-01/02, MD-01, BG-01, RS-01, NV-01, IN-01/02, QA-01. Tidak ada P0 terbukti yang ditugaskan ke Agent3.
- Jangan reset/clean/force-push; jangan commit/push/merge/publish tanpa instruksi. Banyak perubahan belum di-commit sudah ada sebelum sprint; jangan hapus atau menimpa pekerjaan lama. Jangan spawn subagent kecuali user/AGENTS/skill secara eksplisit mengizinkan.

## Kondisi yang sudah dikerjakan — jangan diulang tanpa sebab

Kode support ingestion/null/eligibility, per-grid contribution, ablation, Shapley ranking, selection bias/bounds, thermal QA sensitivity, spatial tails/BH/BY, scenario registry/joint factorial, provenance freshness, dan perbaikan dashboard **sudah diimplementasikan**. Script utama:

- `scripts/run_agent3_remediation.py` → menjalankan kandidat terpisah.
- `scripts/verify_agent3_remediation.py` → verifikasi persamaan/ID/GIS/BH/BY/Moran secara independen.
- `scripts/check_agent3_replay.py` → capture dan compare dua run, **belum dieksekusi**.
- `scripts/check_agent3_dashboard.py` → browser corrected-data8 halaman, screenshot desktop/narrow.
- Kode utama baru: `jhim/remediation.py`, `jhim/provenance.py`; modifikasi `jhim/data.py`, `spatial.py`, `pipeline.py`, `config.py`, `sensitivity.py` serta dashboard/tests.

**Baseline resmi dipertahankan** di `data/processed/modeling`, `outputs/tables`, `outputs/figures`, `outputs/gis`. Jangan menjalankan pipeline standar ke folder tersebut untuk mengganti hasil resmi diam-diam.

**Kandidat**: `data/processed/modeling_remediation` dan `outputs/remediation/{tables,figures,gis,paper,qa}`. **Input beku**: `data/processed/remediation_inputs` dengan `input_lineage.json`. RS kandidat diturunkan dari tabel merged baseline lokal karena file ekspor Agent1 kanonis belum ada di worktree ini. Auditor menyediakan bukti masker/support dan network yang disalin read-only; support berstatus `audit-2026-11-20-fractional-mask-v1-PROVISIONAL`, bukan pemulihan raster DM-01. Jangan mengklaim raw-to-result atau provenance RS lengkap.

Hasil aktual yang sudah ada:

- 2765 master ID; pembanding lama2538 → kandidat2526; top10 lama254 →253.19 age-no-support dan6 total-no-support menjadi null analitis; raw dipertahankan. M3/M4 top10 retain252/Jaccard.988235; fixed retained-ID J=1.
- n2526 top253: total-count swap retain250/J=.9765625; age-share retain131/J=.3493333; child-share J=.4582133; elderly-share J=.3939394; no-park J=.4253521; no-demography J=.6535948; proportionalM3+park J=.9166667; heat-only J=.3863014; equal-weight J=.8671587. Ini sensitivity/objective comparisons, bukan causal/health/policy superiority.
- 226 walking-route-missing dan1 thermal-QA berbeda. Full-thermal top277 kehilangan18 ke common comparison. Unknown walks tidak diisi sebagai pengamatan; bounds deficit[0,1] diekspor.
- JKT_R037_C062 **punya data LST/NDVI**, bukan gagal delivery. Support≈27.7592%; threshold.25 memasukkan target n2527 tanpa perubahan top5/10/20; strict.50+QA memberi2515/Jtop10≈.996047. Angka flags baru harus diambil dari output, jangan paksa benchmark lama.
- M4 local: directed999/BH718; two-sided999/BH560; directed9999/BH703; two-sided9999/BH527. Queen correctedn2526,no islands,18336 directed edges. Signifikansi bukan validasi indeks.
- 16 joint scenarios executed; akses destination/entry/barrier dan alternatif seasonal belum ada per-grid, tercatat BLOCKED. Jangan membuat per-grid skenario dari agregat audit atau mengklaim semua keluarga robust.

Bukti sudah selesai:

- `outputs/remediation/qa/pytest_all.log` dan `.xml`: **111passed,1skipped,1warning**. Skip karena RS kanonis lokal belum ada; warning intentional missing CRS. Setelah run ini terdapat **tambahan kecil tes/asser­si runtime/top-budget** sehingga jumlah/hasil final wajib dites lagi.
- `outputs/remediation/qa/independent_verification.json`: PASS local; error dekomposisi2.498e-16, Shapley2.274e-13; manual MoranM4=.59214069539; baseline byte hashes tetap.
- `outputs/remediation/qa/final_run1.log`: complete candidate run. Manifest schema2 terakhir dicek `is_current=True`, actualR999/high9999/seed42, stale empty.
- `outputs/remediation/qa/dashboard/browser_check.json`:8 pages,no exceptions/pageerror,2024/2026+n2526 visible. Screenshot halaman0/1/3/5/7 desktop/narrow ada. Agen sebelumnya baru melihat satu annotated research map; screenshot lain belum diperiksa visual.
- `pip_check.log`: no broken requirements. `requirements-agent3.lock` hanya snapshot environment lokal, bukan fresh consolidated lock.

## Pekerjaan tersisa — kerjakan sampai konkret

1. **Periksa keadaan sekarang** (`git status`, log, manifest) dan proses yang mungkin masih berjalan akibat interrupt. Jangan mengganggu proses worktree lain. Pastikan angka/bukti di atas cocok dengan berkas aktual. Baca source/tes tepat sebelum menyunting; lanjutkan, jangan rewrite semua.

2. **Jalankan suite final sesudah perubahan terakhir**:

```powershell
.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider tests/agent3 --junitxml=outputs/remediation/qa/pytest_final.xml *> outputs/remediation/qa/pytest_final.log
.venv/Scripts/python.exe -m pip check
```

Perbaiki kegagalan nyata, jangan melemahkan tes. Perubahan tes zero-denominator terdahulu disengaja: composition zero-population wajib NaN. Tambahan meaningful regressions ada di `test_remediation.py`. Pastikan assertion CLI actualperms/top-frac, safe config/code/support/output mutations berjalan. Uji spatial correction/tail interaction jika belum tercakup; jangan anggap screenshot statis membuktikan semua interaksi.

3. **Sertifikasi replay dua run dengan source/config/inputs yang sama.** Helper belum dipakai; cek logic-nya sebelum mengandalkan. Bila kandidat saat ini masih fresh dan source tidak berubah, boleh capture run final yang sudah lengkap; bila source/config berubah, bangun ulang dahulu. Urutan:

```powershell
.venv/Scripts/python.exe scripts/check_agent3_replay.py --capture
.venv/Scripts/python.exe scripts/run_agent3_remediation.py --audit D:\jakarta-heat\audit *> outputs/remediation/qa/final_run2.log
.venv/Scripts/python.exe scripts/check_agent3_replay.py
.venv/Scripts/python.exe scripts/verify_agent3_remediation.py
```

Capture menyimpan CSV model/table dan GPKG di QA; compare mewajibkan identity code/config/inputs/runtime sama, numeric1e-12 dan geometriWKB sama. GPKG/SVG timestamps/byte variability bukan scientific difference, tetapi output hash freshness tetap konservatif. Hasil yang dicari `replay_verification.json`. Bila helper menemukan masalah, betulkan secara bertanggung jawab dan ulang hanya tahap yang terdampak. Jangan menyatakan dua-run PASS sebelum report nyata ada.

4. **Periksa output/gambar dan tampilan final lokal.** Buka PNG hasil riset dan screenshot desktop/narrow yang sudah ada; cek legend excluded/unknown, caption periode, clipping/annotations, kecocokan grid/city/top membership. Periksa figure-manifest source paths dan hashes; beberapa output nama sumber kolektif perlu dibuat menjadi daftar file nyata bila belum inspectable. Jika memperbaiki kode gambar/dashboard, lakukan rerun yang relevan dan refresh manifest/replay source identity sesudah kode final. Lengkapi `outputs/qa/dashboard_scientific_scope_check.md` (atau canonical documented equivalent) dengan scope nyata:8 routes actual/noRS/demo, filtermissing, customweights, tail/correction controls; screenshot ini **workstream lokal, bukan kandidat terintegrasi**.

5. **Tuntaskan bukti masing-masing acceptance.** Gunakan ledger interim; verifikasi kontribusi sum<1e-10, fixed/common versus changing-universe denominator, count/share/age-specific, exacttop5/10/20, allIDeligibility, sourceunknown, geographic cases dan internal benchmarks. Jangan menyebut heat-only/equalweight atau satelit sama sebagai independent outcomevalidation. All-grid M1–M3 versus common map sudah dibuat; cek file aktual. Tambahkan ringkasan ilmiah hasil baru, contoh grid/city yang benar, dan batasan yang mengubah klaim. Tidak perlu riset literatur baru luas; NV-01 adalah keputusanlintastim.

6. **Dependency di luar Agent3 harus tetap eksplisit.** DM-01: canonical corrected values/support/version dari Agent2; AC-01/02: dated park/entrance evidence+per-grid revised routes; BG-01: canonical aggregation; RS-01: canonical export/provenance/temporal support Agent1; IN-01/02: clean consolidated candidate+freshenvironment. Jangan menulis worktree mereka atau membuat data pengganti. Jika artefak kanonis nyata disediakan di worktree Anda, gunakan interface nullable/hash, simpan versi audited-derived, rerun semua efek relevan. Jika belum ada, tandai PARTIAL/BLOCKED dengan path/file yang belum ada, bukan klaim closing. Per-grid GIS scenario tidak boleh direkayasa dari aggregateJaccard auditor.

7. **Keputusan manusia belum disahkan**: mixed-reference-period vs historical(TM-01), count/composition dan bobot/normalisasi/cap/missingness(MD-01), primarythermalQA(RS-02), scenarioenvelope(MD-03), spatialtail/testingfamily(ST-01), novelty/claimscope(NV-01/QA-01). Rekomendasi/alternatif sudah ada di `docs/research_decisions.md` dan `model_specification.json`; jangan silently promote ke official. Jangan berhenti unrelatedwork hanya karena sign-offbelumada.

8. **Finalisasi dokumentasi wajib**: ubah `handoff/REMEDIATION_AGENT3.md` dari interim menjadi ledger final jujur per9isu: severity, originalfinding, rootcause, files, correction, exacttestcommands/results, before/aftereffect, acceptance, PASS/PARTIAL/BLOCKED, dependencies dan human decisions. Status implementer PASS bukan penutupan independen auditor. Update handofflama agar klaim historis tidak menyesatkan; inventaris source vs generated/inputhash, integrationinterfaces, environment dan commands. Jangan edit register auditor.

9. **Serahkan dalam Bahasa Indonesia** dengan9unsur permintaan asli: isu assigned, closedwithevidence, openwhy, filesmodified, testsactual, scientificfindings, downstreamintegration, humandecisions, readiness. Katakan siap untuk integrasi **sebatas workstream terverifikasi**, atau apa blocker tersisa; finalintegratedtests dan independentre-audit belum dapat diklaim. Jangan sebut seluruh proyek paperready.

User meminta eksekusi berkelanjutan, bukan berhenti di rencana. Namun instruksi terbaru adalah transfer kepada Anda: lanjutkan dari keadaan ini, pertahankan baseline, selesaikan semua langkah feasible, dan laporkan keterbatasan yang benar.
