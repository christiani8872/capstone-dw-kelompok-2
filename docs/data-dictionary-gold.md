

\# Data Dictionary Gold



\## 1. Tujuan



Gold merupakan tahap penyajian data yang dibentuk dari Silver untuk mendukung analisis indikator kesehatan Indonesia.



Gold menghasilkan:

\- Panel indikator BPS tingkat provinsi.

\- Tabel rekonsiliasi indikator nasional dalam format long.

\- Tabel rekonsiliasi indikator nasional dalam format wide.

\- Basis data SQLite yang memuat ketiga tabel tersebut.



\## 2. Panel Provinsi



File: `data/gold/panel\_provinsi.parquet`



Tabel SQLite: `panel\_provinsi`



Panel dibentuk dari grid kelengkapan 38 provinsi dan nilai aktual dari Silver.



| Kolom | Keterangan |

|---|---|

| `seri\_kode` | Kode indikator BPS |

| `periode` | Tahun pengamatan |

| `wilayah\_kode` | Kode wilayah provinsi |

| `nama\_wilayah` | Nama wilayah |

| `nilai` | Nilai indikator dari Silver; kosong jika tidak tersedia |

| `satuan` | Satuan asli indikator |

| `\_berkas\_raw` | Nama berkas sumber raw |

| `\_sha256\_raw` | Hash SHA-256 berkas raw |

| `status\_ketersediaan` | Status observasi berdasarkan grid kelengkapan |



Panel mencakup indikator `var1373`, `var1584`, dan `var1541`.



Status ketersediaan:

\- `teramati`: nilai tersedia di Silver.

\- `tidak\_diterbitkan`: indikator tidak diterbitkan pada tingkat wilayah-periode tersebut.

\- `tidak\_tersedia\_dalam\_periode\_terbit`: periode diterbitkan, tetapi observasi wilayah tidak tersedia.



Nilai kosong tidak diubah menjadi nol dan tidak diimputasi.



\## 3. Rekonsiliasi Nasional Long



File:

\- `data/gold/tabel\_nasional\_rekonsiliasi.csv`

\- `data/gold/tabel\_nasional\_rekonsiliasi.parquet`



Tabel SQLite: `rekonsiliasi\_nasional`



Setiap baris mewakili satu observasi nasional dari satu seri dan satu periode.



Kolom utama:

\- `kelompok\_rekonsiliasi`: kelompok indikator yang dibandingkan.

\- `peran\_seri`: peran seri dalam kelompok.

\- `sumber`: BPS, WDI, atau WHO GHO.

\- `seri\_kode`: kode indikator.

\- `ukuran`: deskripsi ukuran indikator.

\- `wilayah\_kode`: kode wilayah nasional, yaitu 9999.

\- `nama\_wilayah`: nama wilayah nasional.

\- `periode`: tahun pengamatan.

\- `nilai`: nilai indikator dari Silver.

\- `satuan`: satuan pada Silver.

\- `satuan\_baku`: satuan standar dari kamus satuan.

\- `rincian`: dimensi atau rincian indikator.

\- `\_berkas\_raw`: nama berkas sumber raw.

\- `\_sha256\_raw`: hash SHA-256 berkas raw.



\## 4. Rekonsiliasi Nasional Wide



File:

\- `data/gold/tabel\_nasional\_periode\_x\_seri.csv`

\- `data/gold/tabel\_nasional\_periode\_x\_seri.parquet`



Tabel SQLite: `nasional\_periode\_x\_seri`



Setiap baris mewakili satu periode. Setiap kolom indikator berisi nilai dari kombinasi sumber dan kode seri, misalnya `BPS\_\_var1373` atau `WDI\_\_SH.DYN.MORT`.



Periode yang tidak tersedia pada suatu seri akan tetap kosong.



\## 5. Kelompok Rekonsiliasi



| Kelompok | Seri |

|---|---|

| K1 Kematian Balita | BPS `var1373`, WDI `SH.DYN.MORT`, WHO `MDG\_0000000007` |

| K1B Bayi dan Neonatal | BPS `var1584`, WHO `WHOSIS\_000003` |

| K2 Rasio Kematian Ibu | WDI `SH.STA.MMRT`, WHO `MDG\_0000000026` |

| K3 Persalinan Faskes/Nakes | BPS `var1541`, WDI `SH.STA.BRTC.ZS` |



Seri dalam kelompok yang sama tidak selalu identik definisinya. Perbandingan harus memperhatikan populasi, metode, satuan, dan periode pengamatan.



\## 6. Aturan Pengolahan



1\. Nilai Gold berasal dari Silver, bukan angka yang diketik manual.

2\. Tidak dilakukan imputasi atau interpolasi untuk nilai yang tidak tersedia.

3\. Data nasional dipilih menggunakan `wilayah\_kode = 9999`.

4\. Panel provinsi menggunakan grid kelengkapan 38 provinsi.

5\. Empat provinsi baru di Papua tidak diberi nilai hasil pemecahan dari provinsi induk.

6\. Data historis mengikuti batas wilayah dan definisi sumber pada periode masing-masing.

7\. Hash sumber dipertahankan sebagai informasi lineage.

8\. Gold tidak mengubah data raw maupun Silver.



