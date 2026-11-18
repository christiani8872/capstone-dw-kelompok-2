# Rancangan Skema SQL Silver & Pemilihan Basis Data (Kartu #17)

## 1. Pilihan Basis Data: DuckDB
Sistem penyimpanan lapisan Silver menggunakan **DuckDB** dengan pertimbangan teknis berikut:
- **Arsitektur Embedded (Tanpa Server):** Berjalan langsung di dalam proses Python tanpa memerlukan instalasi atau konfigurasi daemon basis data terpisah di laptop tiap anggota tim.
- **Integrasi Langsung dengan Apache Parquet:** DuckDB dapat membaca dan menulis berkas `data/silver/silver.parquet` secara native (`read_parquet` / `COPY ... TO 'silver.parquet'`) dengan performa pemindaian kolumnar yang tinggi.
- **Penegakan Skema & Integritas Data:** Mendukung penuh kendala `PRIMARY KEY`, `NOT NULL`, dan `CHECK` pada SQL standar untuk mencegah duplikasi baris dan anomali tipe data saat proses pemuatan dari `pandas.DataFrame`.

## 2. Perbandingan Singkat: Tabel SQL Relasional vs Penyimpanan Dokumen JSON Mentah

| Aspek | Tabel SQL Silver (DuckDB) | Dokumen JSON Mentah (NoSQL / Berkas JSON) |
| :--- | :--- | :--- |
| **Struktur & Validasi Skema** | *Schema-on-write* ketat (11 kolom baku, tipe `DOUBLE`/`INTEGER`, `NOT NULL`, `CHECK`, dan `PRIMARY KEY`). Kesalahan tipe atau duplikat langsung tertolak saat pemuatan. | *Schema-less* (*schema-on-read*). Struktur bersarang (*nested*) berbeda-beda antar sumber (BPS vs WDI vs WHO GHO) sehingga rawan inkonsistensi tipe dan duplikasi diam-diam. |
| **Efisiensi Kueri & Agregasi** | Penyimpanan kolumnar terkompresi memungkinkan filter wilayah (`wilayah_kode`), pengelompokan periode, dan *join* lintas seri dieksekusi jauh lebih cepat dengan konsumsi memori rendah. | Harus mengurai (*parse*) seluruh pohon teks JSON dan melakukan *flattening* ulang setiap kali ingin menghitung agregasi atau membandingkan indikator lintas tahun. |
| **Kemudahan Rekonsiliasi & Panel** | Siap langsung di-reshape ke tabel panel Gold (provinsi × periode × indikator) menggunakan kueri SQL standar tanpa kode parser tambahan. | Memerlukan logika ekstraksi khusus per sumber di setiap tahap analisis hilir. |
| **Peran dalam Pipeline** | **Lapisan Silver (Terstandar):** Menyimpan observasi bersih yang siap dianalisis dan divalidasi. | **Lapisan Bronze (`data/raw/`):** Tetap dipertahankan apa adanya sebagai arsip bukti mentah (*lineage* SHA-256), bukan untuk kueri analitik langsung. |

## 3. Spesifikasi Tipe Kolom & Kunci Primer
Skema tabel `silver` terdiri atas 11 kolom baku yang diselaraskan dengan `src/common/skema.py`:

| Kolom | Tipe SQL | Kendala | Keterangan |
| :--- | :--- | :--- | :--- |
| `sumber` | `VARCHAR` | `NOT NULL`, `PK` | Asal penyedia data (`BPS`, `WDI`, `WHO_GHO`) |
| `seri_kode` | `VARCHAR` | `NOT NULL`, `PK` | Kode indikator sumber (mis. `var1373`, `SH.DYN.MORT`) |
| `wilayah_kode` | `INTEGER` | `NOT NULL`, `PK` | Kode wilayah numerik (`9999` = Indonesia; provinsi = kode BPS × 100) |
| `nama_wilayah` | `VARCHAR` | `NOT NULL` | Nama wilayah administratif atau negara |
| `periode` | `VARCHAR` | `NOT NULL`, `PK` | Label waktu observasi (mis. `2020`, `2020-S1`, `2020-Q1`, `2020-01`) |
| `jenis_periode` | `VARCHAR` | `NOT NULL`, `CHECK` | Granularitas waktu (`tahun`, `semester`, `triwulan`, `bulan`) |
| `rincian` | `VARCHAR` | `NOT NULL`, `PK` | Dimensi disagregasi (jenis kelamin, kelompok umur, atau `total`) |
| `nilai` | `DOUBLE` | `NOT NULL` | Nilai observasi numerik (tidak boleh `NULL`) |
| `satuan` | `VARCHAR` | `NOT NULL` | Satuan pengukuran baku indikator |
| `_berkas_raw` | `VARCHAR` | `NOT NULL`, `PK` | Jalur relatif berkas mentah asal di `data/raw/` |
| `_sha256_raw` | `VARCHAR` | `NOT NULL` | Sidik SHA-256 berkas mentah sesuai `MANIFEST.csv` |

### Kunci Primer (`PRIMARY KEY`)
Kunci primer ditetapkan pada kombinasi 6 kolom:
`(sumber, seri_kode, wilayah_kode, periode, rincian, _berkas_raw)`

Kombinasi ini menjamin setiap titik observasi unik berdasarkan sumber, indikator, wilayah, waktu, dimensi disagregasi, dan berkas rilis mentahnya, sekaligus tetap mengizinkan perbandingan nilai apabila indikator yang sama muncul dari dua berkas snapshot yang berbeda.
