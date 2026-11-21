# Ketersediaan Seri Pembanding

## Tujuan

Profil ini merangkum ketersediaan enam seri pembanding nasional, periode, wilayah, nilai, dan irisan tahun dengan seri utama BPS.

## Ringkasan enam seri pembanding

| Sumber | Kode | Indikator | Baris | Nilai tersedia | Wilayah | Tahun awal | Tahun akhir |
|---|---|---|---:|---:|---|---:|---:|
| WDI | SH.DYN.MORT | Mortality rate, under-5 (per 1,000 live births) | 65 | 65 | Indonesia | 1960 | 2024 |
| WDI | SH.STA.BRTC.ZS | Births attended by skilled health staff (% of total) | 21 | 21 | Indonesia | 1987 | 2019 |
| WDI | SH.STA.MMRT | Maternal mortality ratio (modeled estimate, per 100,000 live births) | 39 | 39 | Indonesia | 1985 | 2023 |
| WHO_GHO | MDG_0000000007 | Mortality rate (under 5) | 73 | 73 | Indonesia | 1951 | 2023 |
| WHO_GHO | MDG_0000000026 | Maternal mortality ratio | 39 | 39 | Indonesia | 1985 | 2023 |
| WHO_GHO | WHOSIS_000003 | Mortality rate (neonetal) | 71 | 71 | Indonesia | 1953 | 2023 |

## Irisan periode dengan seri utama BPS

Irisan tahun menunjukkan tahun yang tersedia pada kedua seri. Irisan periode saja tidak membuktikan bahwa definisi atau metode pengukuran kedua indikator sama.

| Seri pembanding | Seri utama | Tahun yang sama | Jumlah tahun |
|---|---|---|---:|
| SH.DYN.MORT | BPS var1373 (kematian balita) | 2012, 2017 | 2 |
| SH.DYN.MORT | BPS var1584 (kematian bayi) | 2012, 2017 | 2 |
| SH.DYN.MORT | BPS var1541 (persalinan di fasilitas kesehatan, kelompok 40% pengeluaran terbawah) | 2015, 2016, 2017, 2018, 2019 | 5 |
| SH.STA.BRTC.ZS | BPS var1373 (kematian balita) | 2012, 2017 | 2 |
| SH.STA.BRTC.ZS | BPS var1584 (kematian bayi) | 2012, 2017 | 2 |
| SH.STA.BRTC.ZS | BPS var1541 (persalinan di fasilitas kesehatan, kelompok 40% pengeluaran terbawah) | 2016, 2017, 2018, 2019 | 4 |
| SH.STA.MMRT | BPS var1373 (kematian balita) | 2012, 2017 | 2 |
| SH.STA.MMRT | BPS var1584 (kematian bayi) | 2012, 2017 | 2 |
| SH.STA.MMRT | BPS var1541 (persalinan di fasilitas kesehatan, kelompok 40% pengeluaran terbawah) | 2015, 2016, 2017, 2018, 2019 | 5 |
| MDG_0000000007 | BPS var1373 (kematian balita) | 2012, 2017 | 2 |
| MDG_0000000007 | BPS var1584 (kematian bayi) | 2012, 2017 | 2 |
| MDG_0000000007 | BPS var1541 (persalinan di fasilitas kesehatan, kelompok 40% pengeluaran terbawah) | 2015, 2016, 2017, 2018, 2019 | 5 |
| MDG_0000000026 | BPS var1373 (kematian balita) | 2012, 2017 | 2 |
| MDG_0000000026 | BPS var1584 (kematian bayi) | 2012, 2017 | 2 |
| MDG_0000000026 | BPS var1541 (persalinan di fasilitas kesehatan, kelompok 40% pengeluaran terbawah) | 2015, 2016, 2017, 2018, 2019 | 5 |
| WHOSIS_000003 | BPS var1373 (kematian balita) | 2012, 2017 | 2 |
| WHOSIS_000003 | BPS var1584 (kematian bayi) | 2012, 2017 | 2 |
| WHOSIS_000003 | BPS var1541 (persalinan di fasilitas kesehatan, kelompok 40% pengeluaran terbawah) | 2015, 2016, 2017, 2018, 2019 | 5 |

## Ketersediaan nilai dan dimensi data

| Kode | Baris | Nilai tersedia | Nilai kosong | Batas bawah tersedia | Batas atas tersedia |
|---|---:|---:|---:|---:|---:|
| SH.DYN.MORT | 65 | 65 | 0 | 0 | 0 |
| SH.STA.BRTC.ZS | 21 | 21 | 0 | 0 | 0 |
| SH.STA.MMRT | 39 | 39 | 0 | 0 | 0 |
| MDG_0000000007 | 73 | 73 | 0 | 73 | 73 |
| MDG_0000000026 | 39 | 39 | 0 | 39 | 39 |
| WHOSIS_000003 | 71 | 71 | 0 | 71 | 71 |

Dimensi yang tersedia pada berkas gabungan ini adalah sumber, kode dan nama indikator, wilayah, tahun, nilai, berkas sumber, hash sumber, serta batas bawah dan batas atas jika tersedia. Kolom rincian tidak tersedia pada skema ekstraksi ini, sehingga tidak boleh disimpulkan bahwa seluruh dimensi rincian sumber asli sudah diperiksa.

## Catatan interpretasi

- WDI dan WHO merupakan pembanding nasional untuk konteks dan rekonsiliasi, bukan pengganti otomatis data BPS.
- WDI SH.DYN.MORT dan WHO MDG_0000000007 sama-sama mengukur kematian balita, tetapi sumber dan metodologinya dapat berbeda.
- WHO WHOSIS_000003 mengukur kematian neonatal, bukan kematian bayi atau balita secara keseluruhan.
- WDI SH.STA.BRTC.ZS mengukur persalinan dengan tenaga kesehatan terampil. Ini tidak identik dengan BPS var1541 yang mengukur persalinan di fasilitas kesehatan pada kelompok pengeluaran 40 persen terbawah.
- WDI SH.STA.MMRT dan WHO MDG_0000000026 mengukur rasio kematian ibu. Keduanya menjadi konteks kesehatan ibu, bukan ukuran yang sama dengan var1541.
- Perbedaan nilai antar-sumber tidak otomatis merupakan kesalahan. Periksa definisi, satuan, periode, dan metode pengumpulan sebelum menarik kesimpulan.

## Kesimpulan

Profil menemukan 6 dari 6 seri pembanding yang diharapkan. Rincian periode dan irisan tahun ditampilkan di atas. Perbandingan substantif perlu mempertimbangkan kesesuaian definisi dan metode masing-masing indikator.
