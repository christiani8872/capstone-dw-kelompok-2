# Profil Seri Utama

## 1. Tujuan
Analisis dilakukan terhadap var1373, var1584, dan var1541 untuk melihat profil statistik, distribusi, perkembangan waktu, dan kandidat anomali.

## 2. Ringkasan statistik per seri
```text
kode_indikator  jumlah_data  jumlah_wilayah  tahun_awal  tahun_akhir  minimum  maksimum  rata_rata  standar_deviasi
          1373           35              34        2012         2017    28.00    115.00      49.91            22.46
          1584           35              34        2012         2017    21.00     74.00      38.26            14.05
          1541          175              35        2015         2019    13.06     99.98      66.97            21.73
```

Tabel lengkap: `profil-per-seri.csv`.

## 3. Statistik per provinsi
Statistik dihitung untuk setiap kombinasi seri dan wilayah.
Kolom meliputi jumlah data, periode, minimum, maksimum, rata-rata, dan standar deviasi.

Tabel lengkap: `profil-per-provinsi.csv`.

## 4. Metode deteksi kandidat anomali
Deteksi menggunakan metode Interquartile Range (IQR).

- IQR = Q3 - Q1
- Batas bawah = Q1 - 1.5 x IQR
- Batas atas = Q3 + 1.5 x IQR

Perhitungan dilakukan secara terpisah untuk setiap seri dengan menggunakan seluruh observasi pada seri tersebut.
Nilai di bawah batas bawah atau di atas batas atas ditandai sebagai kandidat anomali.

Kandidat bukan bukti kesalahan data. Pemeriksaan lanjutan terhadap wilayah, periode, metadata, dan sumber data tetap diperlukan.

## 5. Batas IQR setiap seri
```text
1373: Q1=34.50, Q3=57.50, IQR=23.00, batas bawah=0.00, batas atas=92.00
1584: Q1=29.00, Q3=46.00, IQR=17.00, batas bawah=3.50, batas atas=71.50
1541: Q1=51.87, Q3=84.73, IQR=32.87, batas bawah=2.57, batas atas=134.03
```

## 6. Daftar kandidat anomali
Jumlah kandidat anomali: 3.

```text
kode_indikator     wilayah  tahun  nilai                                      alasan
          1373       PAPUA   2012  115.0 Nilai 115.00 di atas batas atas IQR (92.00)
          1373 PAPUA BARAT   2012  109.0 Nilai 109.00 di atas batas atas IQR (92.00)
          1584 PAPUA BARAT   2012   74.0  Nilai 74.00 di atas batas atas IQR (71.50)
```

Tabel lengkap: `kandidat-anomali-iqr.csv`.

## 7. Lima perubahan tahunan terbesar var1541
```text
        wilayah  tahun  nilai  perubahan  perubahan_absolut
SULAWESI TENGAH   2017  61.34      16.93              16.93
   MALUKU UTARA   2019  41.32      15.55              15.55
    PAPUA BARAT   2019  54.51      14.69              14.69
           ACEH   2016  76.39      14.56              14.56
      GORONTALO   2017  87.78      12.95              12.95
```

Daftar ini merupakan pemeriksaan perubahan tahunan, bukan hasil deteksi anomali IQR.

## 8. Pemeriksaan hubungan kematian balita dan bayi
Jumlah pasangan wilayah-tahun yang dapat dibandingkan: 35.
Jumlah pelanggaran var1373 < var1584: 0.

```text
Tidak ditemukan pelanggaran.
```

## 9. Visualisasi
- `gambar/distribusi-seri-utama.png`
- `gambar/perubahan-kandidat-var1541.png`
- `gambar/deret-waktu-var1373.png`
- `gambar/deret-waktu-var1584.png`
- `gambar/deret-waktu-var1541.png`

## 10. Catatan dan keterbatasan
IQR pada analisis ini membandingkan distribusi seluruh observasi dalam masing-masing seri. Karena data mencakup beberapa wilayah dan tahun, nilai ekstrem perlu diperiksa lebih lanjut dalam konteks wilayah dan periode.

Tidak ada nilai yang dihapus atau diperbaiki dalam proses deteksi. Data Silver dan data raw tidak diubah oleh analisis ini.