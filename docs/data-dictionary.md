# Data Dictionary — Case 02: Kematian Anak dan Ibu

## 1. Tujuan

Dokumen ini menjelaskan struktur, tipe data, satuan atau format,
arti, dan asal setiap kolom pada tabel Silver.

Dokumentasi mengacu pada skema minimal yang ditetapkan dalam
`src/common/skema.py`.

Tipe data pada tabel berikut merupakan tipe yang diharapkan berdasarkan
fungsi kolom dan ketentuan skema. Tipe aktual akan dikonfirmasi kembali
setelah `data/silver/silver.parquet` tersedia.

## 2. Data Dictionary Silver

Lokasi keluaran: `data/silver/silver.parquet`

| Kolom | Tipe data yang diharapkan | Satuan/format | Boleh kosong | Arti | Asal |
|---|---|---|---|---|---|
| `sumber` | string | Nama sumber data | Tidak | Identitas penyedia data | Nama sumber pada berkas mentah |
| `seri_kode` | string | Kode indikator | Tidak | Kode unik seri atau indikator dari sumber | Metadata indikator atau API sumber |
| `wilayah_kode` | integer | Kode wilayah BPS x 100; 9999 untuk Indonesia | Tidak | Kode numerik wilayah pengamatan | Metadata wilayah sumber dan aturan pemetaan wilayah |
| `nama_wilayah` | string | Nama wilayah | Tidak | Nama wilayah yang terkait dengan observasi | Metadata wilayah sumber |
| `periode` | string | YYYY, YYYY-S1/S2, YYYY-Q1/Q2/Q3/Q4, atau YYYY-MM | Tidak | Waktu pengamatan suatu nilai | Dimensi waktu pada berkas mentah dan aturan standardisasi periode |
| `jenis_periode` | string | tahun, semester, triwulan, atau bulan | Tidak | Jenis periode pengamatan | Dimensi waktu sumber dan aturan transformasi |
| `rincian` | string | Label disagregasi atau rincian | Tidak | Kategori tambahan yang membedakan observasi dalam satu indikator, wilayah, dan periode | Dimensi rincian pada berkas mentah atau aturan standardisasi |
| `nilai` | numerik | Mengikuti satuan indikator | Tidak | Nilai hasil pengamatan indikator | Nilai observasi pada berkas mentah |
| `satuan` | string | Misalnya persen atau per 1.000 kelahiran hidup | Tidak | Satuan pengukuran nilai indikator | Metadata indikator atau keputusan standardisasi yang terdokumentasi |
| `_berkas_raw` | string | Path relatif terhadap `data/raw/` | Tidak | Lokasi berkas mentah asal observasi | `MANIFEST.csv` dan proses ekstraksi |
| `_sha256_raw` | string | SHA-256 heksadesimal | Tidak | Sidik digital berkas mentah untuk pemeriksaan integritas dan penelusuran asal data | `MANIFEST.csv` |

## 3. Ketentuan kunci dan kualitas data

### 3.1 Kunci unik

Kombinasi kolom berikut digunakan sebagai kunci pemeriksaan duplikasi:

- `sumber`
- `seri_kode`
- `wilayah_kode`
- `periode`
- `rincian`
- `_berkas_raw`

Satu kombinasi kunci tersebut tidak boleh muncul lebih dari satu kali.

### 3.2 Ketentuan nilai dan periode

- `nilai` harus bertipe numerik dan tidak boleh kosong.
- `wilayah_kode` harus berupa bilangan bulat.
- Kolom selain `nilai` tidak boleh kosong.
- `jenis_periode` hanya menerima tahun, semester, triwulan, atau bulan.
- Format `periode` harus sesuai dengan `jenis_periode`.

Ketentuan teknis tersebut mengikuti pemeriksaan pada `src/common/skema.py`.

## 4. Contoh penelusuran data mentah

Setiap baris Silver harus memiliki informasi asal berupa `_berkas_raw`
dan `_sha256_raw`.

Contoh referensi berkas BPS untuk indikator 1373:

| Atribut | Nilai |
|---|---|
| Sumber | BPS |
| Kode indikator | 1373 |
| `_berkas_raw` | `bps/2026-10-20/json/sdg3_3_2_1_v1373.json` |
| Ukuran berkas | 4.038 byte |
| `_sha256_raw` | `7512780e34bc137cce49db6bdd213765ad52cb2bce3a56dbd0778bf57ffcd9bb` |

Nilai path dan hash tersebut diambil dari `data/raw/MANIFEST.csv`.

Alur penelusuran:

1. Ambil nilai `_berkas_raw` dari baris Silver.
2. Cari path yang sama pada kolom `berkas` di `data/raw/MANIFEST.csv`.
3. Bandingkan `_sha256_raw` dengan nilai `sha256` pada manifest.
4. Jika keduanya cocok, berkas mentah yang menjadi asal observasi sesuai dengan catatan integritas pada manifest.

Contoh ini merupakan referensi berkas pada manifest. Kesesuaian pasangan
path dan hash pada baris Silver aktual akan diperiksa setelah
`silver.parquet` tersedia.

## 5. Sumber dan keputusan transformasi

Asal kolom dapat berasal dari:

- Berkas mentah pada `data/raw/`.
- Metadata indikator dan wilayah dari sumber data.
- Aturan standardisasi periode, wilayah, rincian, dan satuan.
- Keputusan pembersihan atau transformasi yang dicatat dalam `log-keputusan.csv`.

Setiap perubahan yang tidak langsung berasal dari sumber mentah harus
memiliki dokumentasi keputusan agar proses transformasi dapat ditelusuri.

## 6. Data Gold

Kolom Gold belum didokumentasikan pada Sprint 1 karena struktur tabel
Gold akan ditetapkan pada Sprint 2–3.

Data dictionary Gold akan ditambahkan setelah struktur dan keluaran
tabel Gold tersedia.
