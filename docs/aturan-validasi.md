# Aturan Validasi Data Silver — Case 02

## 1. Tujuan

Validasi dilakukan untuk memastikan data Silver memiliki nilai yang masuk akal,
kunci data yang unik, konsistensi satuan, serta tidak mengandung hasil interpolasi
yang tidak diberi penanda.

## 2. Aturan validasi

### V01 — Rentang nilai berdasarkan satuan

Nilai setiap indikator harus berada pada rentang yang sesuai dengan definisi
dan satuannya.

| Indikator | Sumber | Satuan | Rentang validasi |
|---|---|---|---|
| Angka Kematian Balita (1373) | BPS | Per 1.000 kelahiran hidup | 0–1.000 |
| Angka Kematian Bayi (1584) | BPS | Per 1.000 kelahiran hidup | 0–1.000 |
| Kematian maternal (SH.STA.MMRT) | WDI | Per 100.000 kelahiran hidup | 0–100.000 |
| Kelahiran ditolong tenaga kesehatan (SH.STA.BRTC.ZS) | WDI | Persen | 0–100 |
| Kematian balita (MDG_0000000007) | WHO GHO | Per 1.000 kelahiran hidup | 0–1.000 |

Rentang di atas merupakan pemeriksaan batas logis berdasarkan satuan, bukan
pernyataan bahwa seluruh nilai dalam rentang tersebut pasti benar.

### V02 — Konsistensi batas bawah dan batas atas WHO

Untuk baris WHO yang memiliki interval estimasi:
- Nilai batas bawah tidak boleh lebih besar daripada nilai batas atas.
- Nilai utama harus berada di antara batas bawah dan batas atas.
- Baris tanpa interval estimasi tidak dipaksakan memiliki nilai batas.

### V03 — Hubungan angka kematian balita dan bayi

Pada data BPS, indikator 1373 adalah angka kematian balita dan indikator 1584
adalah angka kematian bayi.

Untuk wilayah dan periode yang sama:

Angka Kematian Balita >= Angka Kematian Bayi.

Perbandingan hanya dilakukan pada pasangan wilayah-periode yang tersedia
untuk kedua indikator. Data nasional dan provinsi dibedakan.

### V04 — Keunikan kunci data

Tidak boleh ada duplikasi berdasarkan kombinasi kunci:

- sumber
- seri_kode
- wilayah_kode
- periode
- rincian
- _berkas_raw

Aturan ini mengikuti pemeriksaan kunci pada skema minimal proyek.

### V05 — Konsistensi satuan

Satuan setiap baris harus sesuai dengan definisi indikator dan sumbernya.
Indikator dengan satuan persen tidak boleh tercampur dengan indikator
berbasis jumlah kematian per kelahiran hidup.

Metadata BPS untuk indikator 1373 dan 1584 memiliki kolom unit kosong,
tetapi label indikator secara eksplisit menyatakan per 1.000 kelahiran hidup.
Informasi definisi tersebut harus dipertahankan dalam dokumentasi.

### V06 — Larangan interpolasi tanpa penanda

Tahun yang tidak tersedia pada sumber tidak boleh diisi menggunakan interpolasi
tanpa penanda dan dokumentasi keputusan.

Ketiadaan data tidak boleh otomatis dianggap sebagai nilai nol.

## 3. Catatan ketersediaan data BPS

Berdasarkan metadata BPS SDKI:
- Angka nasional tahun 2012 dan 2017 menggunakan rujukan lima tahun sebelum survei.
- Angka provinsi menggunakan rujukan sepuluh tahun sebelum survei.
- Angka provinsi tahun 2017 tidak tersedia untuk indikator 1373 dan 1584.

Karena itu, ketiadaan angka provinsi tahun 2017 bukan otomatis merupakan
kesalahan data atau kegagalan ekstraksi.

## 4. Status pengujian awal

Pengujian awal dilakukan pada hasil ekstraksi, bukan Silver final.

| Pemeriksaan | Hasil awal |
|---|---|
| Hubungan kematian balita dan bayi | 33 pasangan provinsi memenuhi aturan |
| Batas bawah dan atas WHO | 0 pelanggaran |
| Keunikan kunci Silver | Menunggu Silver final |
| Konsistensi satuan Silver | Menunggu Silver final |
| Penanda interpolasi | Menunggu Silver final |

Hasil pengujian awal tidak menggantikan validasi pada Silver final.

## 5. Pelaksanaan

Seluruh aturan harus dijalankan melalui tahap validasi pada pipeline utama:

`python pipeline.py`

Hasil validasi dan jumlah aturan yang lolos harus dilaporkan setelah
Silver final tersedia.
