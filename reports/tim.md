# Laporan Tim — Kelompok 2 · Data Saviors, Kasus 02 Kematian Anak dan Ibu

## Ringkasan

Kelompok 2 mengerjakan Kasus 02, yaitu indikator kematian anak dan ibu dalam SDG 3. Data yang dianalisis berasal dari Badan Pusat Statistik (BPS), World Development Indicators (WDI), dan WHO Global Health Observatory (WHO GHO).

Seri utama BPS yang dianalisis adalah `var1373` (angka kematian balita), `var1584` (angka kematian bayi), dan `var1541` (persalinan di fasilitas kesehatan pada kelompok 40 persen pengeluaran terbawah). Enam seri nasional WDI dan WHO digunakan sebagai pembanding.

Hasil profiling mencakup 245 observasi seri utama BPS dan 308 observasi enam seri pembanding. Transformasi menghasilkan Data Silver sebanyak **798 baris, 9 seri indikator, 35 wilayah, dan 10 berkas sumber**. Tabel rekonsiliasi Gold memuat 317 observasi dari sembilan seri berdasarkan hasil yang tercatat pada artefak Gold.

Temuan utama kualitas data meliputi wilayah dan periode yang belum memiliki observasi, kandidat outlier yang tetap valid setelah pemeriksaan terhadap data mentah, serta perbedaan definisi dan metode antarsumber yang membatasi perbandingan langsung.

## Data dan lineage

Data mentah berasal dari tiga sumber:

| Sumber                | Format data  | Berkas data |
|:----------------------|:-------------|------------:|
| BPS                   | CSV dan JSON |           6 |
| WDI                   | JSON         |           1 |
| WHO GHO               | CSV          |           3 |
| **Total berkas data** |              |      **10** |

MANIFEST mencatat 16 berkas, terdiri atas 10 berkas data dan 6 berkas pendukung berupa metadata atau manifest. Pemeriksaan MANIFEST menunjukkan seluruh 16 berkas sesuai dengan snapshot yang tersedia.

Ekstraksi menghasilkan 490 baris BPS, 125 baris WDI, dan 183 baris WHO GHO, sehingga totalnya 798 baris. Setiap baris hasil ekstraksi membawa informasi lineage berupa _berkas_raw dan _sha256_raw untuk menjaga keterlacakan serta integritas data.

Snapshot data yang digunakan berasal dari periode 17–20 Oktober 2026. Penarikan ulang API dan perbandingan menyeluruh terhadap snapshot baru belum dapat dibuktikan dari artefak yang tersedia.

### Pembentukan Data Silver

Data Silver dibentuk melalui proses transformasi pada src/silver/__init__.py, yang meliputi:
1. Penyeragaman kode indikator, periode, nilai, dan satuan.
2. Pelengkapan kode wilayah pada data CSV BPS menggunakan pasangan data JSON.
3. Penetapan kode wilayah 9999 untuk data nasional WDI dan WHO.
4. Pemertahanan dimensi WHO (jenis kelamin, kelompok umur, dan kelompok kesejahteraan) pada kolom rincian.
5. Pencocokan nama berkas dan SHA-256 dengan jalur relatif lengkap pada MANIFEST.csv.

Hasil transformasi disimpan dalam data/silver/silver.parquet dengan total 798 baris, 9 seri indikator, 35 wilayah (34 provinsi dan 1 wilayah nasional), serta 10 berkas sumber. Dengan demikian, data yang tersedia belum mencakup seluruh 38 provinsi.

## Masalah data dan penanganannya

| Masalah                                | Temuan dan jumlah terdampak                                                                                                              | Keputusan                                                                                                                                 | Referensi    |
|:---------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------|:-------------|
| Standar wilayah                        | Data perlu diselaraskan dengan standar 38 provinsi, termasuk daerah otonomi baru Papua                                                   | Menggunakan kode wilayah BPS 2025; tidak menggunakan nama bebas atau standar 34 provinsi                                                  | K-001, K-002 |
| Kunci panel                            | Penggabungan berdasarkan nama wilayah atau tahun saja berisiko menghasilkan pasangan yang keliru                                         | Menggunakan kunci kode wilayah dan tahun                                                                                                  | K-003        |
| Metadata satuan                        | Metadata satuan beberapa berkas CSV/JSON tidak selalu terisi                                                                             | Menetapkan satuan berdasarkan judul dan definisi indikator; tidak mengubah jumlah baris                                                   | K-004–K-012  |
| Missing var1373 dan var1584 tahun 2012 | Masing-masing 5 provinsi tidak memiliki observasi: Kalimantan Utara, Papua Barat Daya, Papua Selatan, Papua Tengah, dan Papua Pegunungan | Dipertahankan sebagai missing; tidak diimputasi                                                                                           | K-013, K-014 |
| Missing var1541 tahun 2015–2019        | Empat provinsi baru di wilayah Papua tidak memiliki observasi pada setiap tahun                                                          | Tidak mengisi nilai kosong dengan nol atau interpolasi                                                                                    | K-015        |
| Data provinsi tahun 2017               | Nilai provinsi var1373 dan var1584 tidak dipublikasikan; yang tersedia hanya nilai nasional                                              | Tidak dianggap sebagai kegagalan ekstraksi atau nilai nol                                                                                 | K-016        |
| Kandidat outlier var1373               | Papua 2012 = 115 dan Papua Barat 2012 = 109; keduanya melewati batas atas IQR 92                                                         | Dipertahankan karena sesuai dengan JSON mentah                                                                                            | K-017, K-018 |
| Kandidat outlier var1584               | Papua Barat 2012 = 74; melewati batas atas IQR 71,5                                                                                      | Dipertahankan karena sesuai dengan JSON mentah                                                                                            | K-019        |
| Perubahan tahunan var1541              | Diperiksa lima perubahan tahunan terbesar; belum ditemukan bukti meyakinkan adanya patahan struktural                                    | Tidak melakukan koreksi nilai                                                                                                             | K-020        |
| Duplikasi dan revisi                   | Satu snapshot tersedia untuk setiap sumber; belum cukup bukti untuk mengidentifikasi revisi antar-snapshot                               | Tidak menghapus baris hanya karena nilai sama; perbedaan antar-snapshot perlu diperiksa sebagai kemungkinan revisi apabila arsip tersedia | K-021        |

Pada profil seri utama terdapat 35 observasi var1373, 35 observasi
var1584, dan 175 observasi var1541, sehingga totalnya 245 observasi.
Pemeriksaan hierarki var1373 ≥ var1584 pada 35 pasangan menghasilkan 0
pelanggaran.

Kandidat outlier diperiksa kembali terhadap JSON mentah dan nilainya
sesuai. Seluruh keputusan K-013 sampai K-021 tidak menghapus atau
mengubah baris data (`dampak_baris = 0`). Missing pada panel merupakan
keterbatasan cakupan data, bukan alasan untuk mengarang nilai.


## Integrasi dan rekonsiliasi

Tabel `data/gold/tabel_nasional_rekonsiliasi.csv` memuat 317 observasi dari sembilan seri indikator. Jumlah tersebut terdiri atas 308 observasi dari enam seri pembanding WDI dan WHO serta 9 observasi dari tiga seri utama BPS.

### Perbandingan cakupan Silver dan Gold

Data Silver terbaru memiliki 798 baris, termasuk 326 baris dengan kode wilayah nasional (`9999`). Dari 326 baris tersebut, terdapat 308 observasi seri pembanding WDI dan WHO serta 18 baris seri BPS.

Perbedaan jumlah baris nasional BPS pada Silver dan Gold terjadi karena setiap nilai nasional BPS tersimpan dalam dua berkas sumber, yaitu CSV dan JSON. Nilai dan periodenya sama pada kedua berkas tersebut. Dalam tabel Gold, setiap observasi BPS diwakili oleh satu catatan yang menggunakan sumber JSON.

| Seri BPS | Baris Silver | Baris Gold | Keterangan |
|:--|--:|--:|:--|
| `var1373` | 4 | 2 | 2 tahun, masing-masing dari CSV dan JSON |
| `var1584` | 4 | 2 | 2 tahun, masing-masing dari CSV dan JSON |
| `var1541` | 10 | 5 | 5 tahun, masing-masing dari CSV dan JSON |
| **Total** | **18** | **9** | **9 observasi unik** |

Dengan demikian, selisih 9 baris antara data nasional Silver dan Gold bukan menunjukkan kehilangan observasi, melainkan pemilihan satu representasi sumber untuk setiap observasi BPS dalam tabel rekonsiliasi.

### Kematian balita

BPS `var1373`, WDI `SH.DYN.MORT`, dan WHO `MDG_0000000007` sama-sama
berkaitan dengan kematian balita dan menggunakan satuan per 1.000
kelahiran hidup.

| Tahun | BPS var1373 | WDI SH.DYN.MORT | WHO MDG_0000000007 |
|:------|------------:|----------------:|-------------------:|
| 2012  |        40,0 |            29,9 |              30,96 |
| 2017  |        32,0 |            23,8 |              25,38 |

Selisih BPS terhadap WDI adalah 10,1 per 1.000 pada 2012 dan 8,2 per
1.000 pada 2017. Perbedaan tidak otomatis menunjukkan kesalahan.
Estimasi BPS berasal dari survei dengan periode rujukan tertentu,
sedangkan WDI dan WHO menggunakan estimasi model. Perbedaan metode dan
vintage estimasi perlu dipertimbangkan.

### Kematian neonatal dan bayi

WHO `WHOSIS_000003` mengukur kematian neonatal, sedangkan BPS `var1584`
mengukur kematian bayi. Kematian neonatal merupakan bagian dari kematian
bayi sehingga kedua indikator tidak identik. Pemeriksaan hierarki
dilakukan pada 35 pasangan data var1373 dan var1584 dan tidak menemukan
pelanggaran.

### Kematian ibu

WDI `SH.STA.MMRT` dan WHO `MDG_0000000026` sama-sama mengukur rasio
kematian ibu per 100.000 kelahiran hidup.

| Tahun | WDI SH.STA.MMRT | WHO MDG_0000000026 |
|:------|----------------:|-------------------:|
| 2021  |           226,0 |             226,46 |
| 2023  |           140,0 |             140,50 |

Perbedaan angka relatif kecil pada contoh tersebut. WDI menampilkan
angka bulat, sedangkan WHO menampilkan angka desimal. Keduanya merupakan
estimasi nasional dan bukan data provinsi BPS.

### Persalinan

BPS `var1541` mengukur persalinan di fasilitas kesehatan pada kelompok
40 persen pengeluaran terbawah, sedangkan WDI `SH.STA.BRTC.ZS` mengukur
persalinan dengan tenaga kesehatan terampil.

| Tahun | BPS var1541 (%) | WDI SH.STA.BRTC.ZS (%) | Selisih (poin persentase) |
|:------|----------------:|------------------------|--------------------------:|
| 2016  |           73,05 | 92,6                   |                    -19,55 |
| 2017  |           74,89 | 90,9                   |                    -16,01 |
| 2018  |           76,82 | 93,6                   |                    -16,78 |
| 2019  |           81,02 | 94,7                   |                    -13,68 |

Kedua indikator memiliki satuan persentase, tetapi definisi, cakupan
populasi, dan konsep pengukurannya berbeda. Karena itu, selisih tidak
dapat ditafsirkan sebagai kesalahan data.

### Pemeriksaan revisi WDI

Pemeriksaan revisi antar-snapshot belum dapat dilakukan karena bukti
yang tersedia hanya menunjukkan satu snapshot per sumber. Sesuai K-021,
kesamaan nilai tidak otomatis dianggap duplikasi dan perbedaan nilai
antar-snapshot harus diperiksa sebagai kemungkinan revisi apabila arsip
tambahan tersedia.


## Validasi dan reproduksibilitas

### Pemeriksaan yang telah dilakukan

Transformasi Data Silver dilakukan melalui modul `src/silver/__init__.py` dan menghasilkan berkas `data/silver/silver.parquet`.

Pemeriksaan skema dilakukan menggunakan perintah:

```powershell
python -m src.common.skema data/silver/silver.parquet
```

Hasil pemeriksaan menunjukkan status **LOLOS**, dengan rincian:

| Pemeriksaan | Hasil |
|:--|--:|
| Status pemeriksaan skema | LOLOS |
| Jumlah baris Silver | 798 |
| Jumlah seri indikator | 9 |
| Jumlah wilayah | 35 |
| Jumlah berkas sumber | 10 |

Pemeriksaan transformasi juga mencakup kelengkapan kolom sesuai skema, tipe data, keunikan kunci, serta pencocokan informasi lineage dengan MANIFEST.

Pemeriksaan hierarki indikator kematian balita dan bayi pada 35 pasangan data seri utama BPS menghasilkan 0 pelanggaran.

### Aturan validasi

Aturan validasi yang digunakan dan direncanakan mencakup:

1. Rentang nilai logis sesuai satuan indikator.
2. Batas bawah tidak melebihi batas atas untuk data WHO yang memiliki interval.
3. Nilai kematian balita tidak lebih kecil daripada nilai kematian bayi pada wilayah dan periode yang sama.
4. Keunikan kunci Silver.
5. Konsistensi satuan.
6. Missing tidak boleh diubah menjadi nol atau diisi melalui interpolasi tanpa penanda.

### Keterbatasan validasi dan reproduksibilitas

Pemeriksaan skema standar Silver telah berhasil dilakukan. Namun, validasi lanjutan Silver dan Gold menggunakan Pandera atau Great Expectations belum dapat dinyatakan selesai sebelum implementasinya tersedia dan hasil pengujiannya diperoleh.

Reproduksibilitas pipeline secara keseluruhan dari kondisi awal atau clean clone juga masih perlu dibuktikan. Pengujian transformasi Silver dan pemeriksaan skema sudah berhasil dilakukan, tetapi hal tersebut belum otomatis membuktikan seluruh pipeline dapat dijalankan dari awal hingga akhir.

Perbandingan kinerja pandas dengan DuckDB atau Dask belum dilakukan sehingga belum ada hasil benchmark yang dapat dilaporkan.

Keterbatasan lainnya meliputi belum tersedianya pemeriksaan revisi antar-snapshot dan keterbatasan data provinsi pada beberapa periode.


## Pembagian kerja

| Anggota                   | NIM       | Komponen                                                                                                | Tugas sampingan                                 | Bagian laporan yang ditulis              |
|:--------------------------|:----------|:--------------------------------------------------------------------------------------------------------|:------------------------------------------------|:-----------------------------------------|
| Pramudya Wibowo           | 121450030 | Validasi Silver dan Gold, dokumentasi data dictionary                                                   | Reproduksi & Demo | Validasi dan reproduksibilitas           |
| Audina Fitria             | 124450038 | Metadata satuan, periode, SDG; pemeriksaan Silver; profil masalah data                                  | Analis Utama dan transformasi        | Data dan lineage; masalah data           |
| Teresa Christiani Purba   | 124450046 | Profil seri BPS dan pembanding nasional, kelengkapan panel 38 provinsi, pemeriksaan outlier dan patahan | Penjaga Data & Evaluasi                            | Masalah data; integrasi dan rekonsiliasi |
| Hafidz Wahdiansyah        | 124450064 | Ekstraksi BPS, WDI, dan WHO GHO beserta lineage                                                         | Integrator                    | Data dan lineage                         |
| Muhammad Syafiqful Falakh | 124450099 | Sprint Goal dan Log Sprint; kamus satuan BPS; tabel seri nasional utama dan pembanding serta pasangan rekonsiliasi; rancangan skema SQL Silver; benchmark waktu dan memori pandas                          | Koordinator        |  Integrasi dan rekonsiliasi; rancangan skema dan benchmark                         |

