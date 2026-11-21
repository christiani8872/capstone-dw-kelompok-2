# Sprint Goal, Log Sprint Anggota & Demo Sprint 1 — Kelompok 2 (Kasus 02)

## 1. Sprint Goal Sprint 1
> "Menuntaskan fondasi pipeline lapisan Bronze ke Silver untuk Kasus 02 (Kematian Anak dan Ibu — SDG 3): memverifikasi integritas 16 berkas mentah (MANIFEST.csv), mengekstraksi dan menggabungkan 553 observasi lintas sumber (BPS, WDI, WHO GHO), menetapkan kamus data, aturan validasi, dan skema SQL DuckDB lapisan Silver, serta menyiapkan tabel rekonsiliasi nasional periode x seri dan utilitas pengukur performa pandas."

---

## 2. Log Sprint 1 Semua Anggota Kelompok 2

| NIM | Nama / Akun GitHub | Peran & Kartu Utama | Capaian & Bukti Artefak di Repo | Kendala & Tindak Lanjut Sprint 2 |
| :--- | :--- | :--- | :--- | :--- |
| **124450099** | Muhammad Syafiqul Falakh (syafiq-sss) | Koordinator Sprint 1, Skema SQL Silver, Rekonsiliasi Nasional & Pengukur Pandas (Kartu #17, #16, #4, #20) | - PR #13: Skema DDL DuckDB (sql/silver.sql), skrip pemuat (src/silver/muat_duckdb.py), dan perbandingan basis data vs JSON (docs/rancangan-skema-silver.md).<br>- PR #14 & #17: Tabel nasional periode x seri (data/gold/tabel_nasional_periode_x_seri.csv, 74 periode x 9 seri), tabel panjang (317 baris), laporan pasangan rekonsiliasi (reports/pasangan-rekonsiliasi.md), dan results/124450099/metrics.json.<br>- PR #16: Utilitas pengukur waktu & memori pandas (src/common/ukur.py). | Tidak ada hambatan teknis; lanjut mengintegrasikan pengukur performa ke pipeline penuh dan penyusunan panel Gold 38 provinsi di Sprint 2. |
| **124450064** | Hafidz Wahdiansyah | Ekstraksi Multi-Sumber & Lineage SHA-256 (Kartu #9 & modul src/ekstraksi/) | - PR #7, #8, #15: Pembaca BPS (src/ekstraksi/bps.py, 245 baris), WDI (src/ekstraksi/wdi.py, 125 baris), WHO GHO (src/ekstraksi/who.py, 183 baris), dan penggabung (src/ekstraksi/gabung_ekstrak.py -> data/silver/raw_gabungan.parquet, 553 baris), serta pembaruan log-keputusan.csv & results/124450064/metrics.json. | Nama kolom hasil ekstraksi masih menggunakan format mentah (kode_indikator, wilayah, tahun); pada Sprint 2 akan dipetakan ke 11 kolom baku Silver (skema.py) untuk dimuat penuh ke DuckDB. |
| **121450030** | Pramudya (121450030/kerja) | Kamus Data & Aturan Validasi Silver | - PR #11: Menyusun kamus data lengkap 11 kolom Silver (docs/data-dictionary.md) dan aturan validasi skema, rentang nilai, serta hierarki indikator (docs/aturan-validasi.md). | Aturan validasi sudah terdokumentasi; pada Sprint 2 akan diimplementasikan ke dalam skrip otomatis src/validasi/. |
| **124450046** & **124450038** | Anggota Kelompok 2 (christiani8872 / tim) | Verifikasi Manifest, Audit Satuan & Log Keputusan | - PR #9 & commit awal: Verifikasi 16 berkas mentah (data_hash: f496e0a1ba4c0743ff4cb11f45b27d6cb50a064ebca7fefdf86bf32c28e8070d), pembakuan satuan (docs/kamus-satuan.csv), pencatatan keputusan metadata (log-keputusan.csv), serta results/124450046/metrics.json dan results/124450038/metrics.json. | Seluruh anggota telah menyelaraskan data_hash yang identik; siap melanjutkan pemetaan 38 provinsi dan panel Gold di Sprint 2. |

---

## 3. Langkah Reproduksi Demo Sprint 1

1. Verifikasi integritas 16 berkas mentah terhadap MANIFEST.csv:
   python -m src.common.manifest
2. Jalankan ekstraksi dan penggabungan data mentah BPS, WDI, dan WHO GHO (553 baris):
   python -m src.ekstraksi.gabung_ekstrak
3. Uji skema DDL SQL Silver dan pemuatan ke basis data DuckDB:
   python -m src.silver.muat_duckdb
4. Bangun tabel nasional (long & wide periode x seri) untuk persiapan rekonsiliasi Gold:
   python -m src.gold.rekonsiliasi_nasional
5. Jalankan pengukur waktu eksekusi dan penggunaan memori pandas:
   python -m src.common.ukur
