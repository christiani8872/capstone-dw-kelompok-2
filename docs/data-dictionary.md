# Data Dictionary — Case 02: Kematian Anak dan Ibu

## 1. Tujuan

Dokumen ini menjelaskan struktur, tipe data (diharapkan dan aktual), satuan atau format,
arti, dan asal setiap kolom pada tabel Silver.

Dokumentasi mengacu pada skema minimal yang ditetapkan dalam `src/common/skema.py`
dan telah dikonfirmasi langsung terhadap berkas aktual `data/silver/silver.parquet`
(798 baris, 11 kolom).

## 2. Data Dictionary Silver

Lokasi keluaran: `data/silver/silver.parquet` (798 baris)

| Kolom | Tipe Diharapkan | Tipe Aktual (`silver.parquet`) | Satuan/Format | Boleh Kosong | Arti | Asal |
|---|---|---|---|---|---|---|
| `sumber` | string | `str` | Nama sumber data (`BPS`, `WDI`, `WHO_GHO`) | Tidak | Identitas penyedia data | Nama sumber pada berkas mentah |
| `seri_kode` | string | `str` | Kode indikator (mis. `var1373`, `SH.DYN.MORT`) | Tidak | Kode unik seri atau indikator dari sumber | Metadata indikator atau API sumber (`K-004` s.d. `K-012`) |
| `wilayah_kode` | integer | `int64` | Kode wilayah BPS x 100 (mis. `1100`); `9999` untuk Indonesia | Tidak | Kode numerik wilayah pengamatan | Metadata wilayah sumber dan aturan pemetaan wilayah (`K-001`, `K-002`) |
| `nama_wilayah` | string | `str` | Nama wilayah (mis. `ACEH`, `INDONESIA`) | Tidak | Nama wilayah yang terkait dengan observasi | Metadata wilayah sumber |
| `periode` | string | `str` | `YYYY`, `YYYY-S1/S2`, `YYYY-Q1/Q2/Q3/Q4`, atau `YYYY-MM` | Tidak | Waktu pengamatan suatu nilai | Dimensi waktu pada berkas mentah dan aturan standardisasi periode |
| `jenis_periode` | string | `str` | `tahun`, `semester`, `triwulan`, atau `bulan` | Tidak | Jenis periode pengamatan | Dimensi waktu sumber dan aturan transformasi |
| `rincian` | string | `str` | Label disagregasi atau rincian (mis. `total`) | Tidak | Kategori tambahan yang membedakan observasi dalam satu indikator, wilayah, dan periode | Dimensi rincian pada berkas mentah atau aturan standardisasi |
| `nilai` | numerik | `float64` | Mengikuti satuan indikator | Tidak | Nilai hasil pengamatan indikator | Nilai observasi pada berkas mentah |
| `satuan` | string | `str` | `per_1000_kelahiran_hidup`, `per_100000_kelahiran_hidup`, atau `persen` | Tidak | Satuan pengukuran nilai indikator | Metadata indikator dan `docs/kamus-satuan.csv` (`K-004` s.d. `K-012`) |
| `_berkas_raw` | string | `str` | Path relatif terhadap `data/raw/` | Tidak | Lokasi berkas mentah asal observasi | `data/raw/MANIFEST.csv` dan proses ekstraksi |
| `_sha256_raw` | string | `str` | SHA-256 heksadesimal (64 karakter) | Tidak | Sidik digital berkas mentah untuk pemeriksaan integritas dan penelusuran asal data | `data/raw/MANIFEST.csv` |

## 3. Ketentuan Kunci dan Kualitas Data

### 3.1 Kunci Unik

Kombinasi kolom berikut digunakan sebagai kunci pemeriksaan duplikasi:

- `sumber`
- `seri_kode`
- `wilayah_kode`
- `periode`
- `rincian`
- `_berkas_raw`

Satu kombinasi kunci tersebut tidak boleh muncul lebih dari satu kali.

### 3.2 Ketentuan Nilai dan Periode

- `nilai` harus bertipe numerik (`float64`) dan tidak boleh kosong.
- `wilayah_kode` harus berupa bilangan bulat (`int64`).
- Kolom selain `nilai` tidak boleh kosong.
- `jenis_periode` hanya menerima `tahun`, `semester`, `triwulan`, atau `bulan`.
- Format `periode` harus sesuai dengan `jenis_periode`.

Ketentuan teknis tersebut mengikuti pemeriksaan pada `src/common/skema.py`.

## 4. Contoh Satu Baris Aktual & Penelusuran ke Berkas Mentah

Berikut adalah **contoh satu baris aktual (indeks 0)** yang diambil langsung dari `data/silver/silver.parquet`:

| Kolom | Nilai Aktual (`silver.parquet` indeks 0) | Tipe Aktual |
|---|---|---|
| `sumber` | `BPS` | `str` |
| `seri_kode` | `var1373` | `str` |
| `wilayah_kode` | `1100` | `int64` |
| `nama_wilayah` | `ACEH` | `str` |
| `periode` | `2012` | `str` |
| `jenis_periode` | `tahun` | `str` |
| `rincian` | `total` | `str` |
| `nilai` | `52.0` | `float64` |
| `satuan` | `per_1000_kelahiran_hidup` | `str` |
| `_berkas_raw` | `bps/2026-10-20/json/sdg3_3_2_1_v1373.json` | `str` |
| `_sha256_raw` | `7512780e34bc137cce49db6bdd213765ad52cb3bce3a56dbd0778bf57ffcd9bb` | `str` |

**Alur penelusuran ke berkas mentah (terverifikasi):**

1. Ambil nilai `_berkas_raw` dari baris Silver: `bps/2026-10-20/json/sdg3_3_2_1_v1373.json`.
2. Cocokkan path tersebut pada kolom `berkas` di `data/raw/MANIFEST.csv`.
3. Bandingkan `_sha256_raw` baris Silver (`7512780e34bc137cce49db6bdd213765ad52cb3bce3a56dbd0778bf57ffcd9bb`) dengan nilai `sha256` pada `MANIFEST.csv`.
4. Kedua nilai cocok 100%, sehingga observasi `ACEH` tahun `2012` bernilai `52.0` dapat ditelusuri langsung ke berkas mentah aslinya.

## 5. Sumber dan Keputusan Transformasi

Asal kolom dapat berasal dari:

- Berkas mentah pada `data/raw/`.
- Metadata indikator dan wilayah dari sumber data.
- Aturan standardisasi periode, wilayah, rincian, dan satuan.
- Keputusan pembersihan atau transformasi yang dicatat dalam `log-keputusan.csv` (`K-001` s.d. `K-021`).

Setiap perubahan yang tidak langsung berasal dari sumber mentah memiliki dokumentasi keputusan agar proses transformasi dapat ditelusuri.

## 6. Data Gold

Kolom Gold belum didokumentasikan pada Sprint 1 karena struktur tabel Gold akan ditetapkan pada Sprint 2–3. Data dictionary Gold akan ditambahkan setelah struktur dan keluaran tabel Gold tersedia.
