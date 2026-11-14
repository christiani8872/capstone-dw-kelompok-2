# Rancangan Skema SQL Silver & Pemilihan Basis Data (Kartu #17)

## 1. Pilihan Basis Data: DuckDB
Sistem penyimpanan lapisan Silver menggunakan **DuckDB** dengan pertimbangan teknis berikut:
- **Arsitektur Embedded (Tanpa Server):** Berjalan langsung di dalam proses Python tanpa memerlukan instalasi atau konfigurasi daemon basis data terpisah di laptop tiap anggota tim.
- **Integrasi Langsung dengan Apache Parquet:** DuckDB dapat membaca dan menulis berkas `data/silver/silver.parquet` secara native (`read_parquet` / `COPY ... TO 'silver.parquet'`) dengan performa tinggi.
- **Kepatuhan Skema & Integritas Data:** Mendukung penuh kendala `PRIMARY KEY`, `NOT NULL`, dan `CHECK` pada SQL standar untuk mencegah duplikasi baris dan anomali tipe data saat proses pemuatan dari `pandas.DataFrame`.

## 2. Spesifikasi Tipe Kolom & Kunci Primer
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
