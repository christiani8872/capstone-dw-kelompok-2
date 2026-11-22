# Tabel Nasional Seri Utama vs Pembanding & Daftar Pasangan Rekonsiliasi (Kartu #16)

## 1. Inventaris Seri Nasional (317 Observasi di data/gold/tabel_nasional_rekonsiliasi.csv)

| Kelompok | Peran Seri | Sumber | Kode Seri | Ukuran (Sesuai Metadata Sumber) | Satuan Baku | Cakupan Tahun | Baris | Rujukan Keputusan |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :--- |
| **K1: Kematian Balita** | Seri Utama | BPS | var1373 | Angka Kematian Balita (<5 thn) per 1.000 Kelahiran Hidup (SDKI) | per_1000_kh | 2012, 2017 | 2 | K-004 |
| **K1: Kematian Balita** | Pembanding Nasional | WDI | SH.DYN.MORT | Under-five mortality rate (per 1.000 live births, UN IGME) | per_1000_kh | 1960-2024 | 65 | K-010 |
| **K1: Kematian Balita** | Pembanding Nasional | WHO GHO | MDG_0000000007 | Under-five mortality rate (probability of dying by age 5 per 1.000 live births) | per_1000_kh | 1951-2023 | 73 | K-007 |
| **K1B: Sub-Komponen Umur** | Seri Utama (Bayi <1 thn) | BPS | var1584 | Angka Kematian Bayi (AKB) per 1.000 Kelahiran Hidup (SDKI) | per_1000_kh | 2012, 2017 | 2 | K-005 |
| **K1B: Sub-Komponen Umur** | Pembanding (Neonatal <28 hr) | WHO GHO | WHOSIS_000003 | Neonatal mortality rate (per 1.000 live births, DIM_AGE D_LE27) | per_1000_kh | 1953-2023 | 71 | K-009 |
| **K2: Rasio Kematian Ibu** | Pembanding Nasional | WDI | SH.STA.MMRT | Maternal mortality ratio (modeled estimate, per 100.000 live births) | per_100000_kh | 1985-2023 | 39 | K-011 |
| **K2: Rasio Kematian Ibu** | Pembanding Nasional | WHO GHO | MDG_0000000026 | Maternal mortality ratio (per 100.000 live births, MMEIG) | per_100000_kh | 1985-2023 | 39 | K-008 |
| **K3: Persalinan Faskes/Nakes** | Seri Utama (40% Bawah) | BPS | var1541 | Persalinan terakhir di fasilitas kesehatan (kelompok 40% terbawah) | persen | 2015-2019 | 5 | K-006 |
| **K3: Persalinan Faskes/Nakes** | Pembanding Nasional (Total) | WDI | SH.STA.BRTC.ZS | Births attended by skilled health staff (% of total) | persen | 1987-2019 | 21 | K-012 |

**Rujukan Berkas Metadata Sumber Asli:**
- **BPS:** data/raw/bps/2026-10-20/json/sdg3_3_2_1_v1373.json, sdg3_3_2_1_v1584.json, sdg3_3_1_2_v1541.json
- **WHO GHO:** data/raw/who_gho/2026-10-20/odata/Indicator.json
- **WDI:** data/raw/wdi/2026-10-20/metadata/sumber46_indikator.json

---

## 2. Daftar 5 Pasangan Rekonsiliasi & Aturan Komparasi

Total terdapat **5 pasangan rekonsiliasi** (terdiri dari 3 pasangan seri utama BPS vs pembanding dengan **6 periode beririsan**: 2012, 2017 untuk K1 dan 2016-2019 untuk K3; serta 2 pasangan lintas pembanding internasional) ditambah 1 aturan validasi hierarki umur:

1. **Pasangan 1 (K1 - SDG 3.2.1): BPS var1373 vs WDI SH.DYN.MORT**
   - **Kesesuaian Definisi:** Setara secara definisi (kematian anak <5 tahun) dan satuan (per_1000_kh).
   - **Periode Beririsan (2 tahun):** 2012 (BPS 40,0 vs WDI 29,9; selisih +10,1) dan 2017 (BPS 32,0 vs WDI 23,8; selisih +8,2).
   - **Alasan Selisih:** BPS menggunakan estimasi langsung survei SDKI (jendela 5 tahun sebelum survei), sedangkan WDI memakai estimasi kurva halus model UN IGME.

2. **Pasangan 2 (K1 - SDG 3.2.1): BPS var1373 vs WHO GHO MDG_0000000007**
   - **Kesesuaian Definisi:** Setara secara definisi dan satuan (per_1000_kh).
   - **Periode Beririsan (2 tahun):** 2012 (BPS 40,0 vs WHO 30,96; selisih +9,04) dan 2017 (BPS 32,0 vs WHO 25,38; selisih +6,62).
   - **Alasan Selisih:** Perbedaan metode estimasi langsung SDKI vs pemodelan UN IGME yang diadopsi WHO GHO.

3. **Pasangan 3 (K1 - Lintas Pembanding): WDI SH.DYN.MORT vs WHO GHO MDG_0000000007**
   - **Kesesuaian Definisi:** Setara penuh (per_1000_kh, 1960-2023). Selisih kecil (~1,0-1,6 poin) berasal dari perbedaan vintage pemodelan UN IGME.

4. **Pasangan 4 (K2 - SDG 3.1.1): WDI SH.STA.MMRT vs WHO GHO MDG_0000000026**
   - **Kesesuaian Definisi:** Setara penuh (per_100000_kh, 1985-2023), tanpa seri provinsi BPS pada paket Kasus 02.
   - **Hasil Perbandingan:** Keduanya bersumber dari model MMEIG; nilai WDI merupakan pembulatan bilangan bulat dari nilai WHO GHO (mis. 2021: 226,0 vs 226,46; 2023: 140,0 vs 140,50).

5. **Pasangan 5 (K3 - SDG 3.1.2): BPS var1541 vs WDI SH.STA.BRTC.ZS**
   - **Kesesuaian Definisi:** Komparabilitas parsial (sama-sama bersatuan persen, tetapi berbeda cakupan populasi dan lokasi). BPS var1541 khusus kelompok 40% terbawah di fasilitas kesehatan, sedangkan WDI mencakup seluruh populasi nasional yang ditolong tenaga kesehatan terlatih.
   - **Periode Beririsan (4 tahun):** 2016 (73,05% vs 92,6%), 2017 (74,89% vs 90,9%), 2018 (76,82% vs 93,6%), dan 2019 (81,02% vs 94,7%). Tren selisih menyempit dari -19,55 menjadi -13,68 poin persen.

**Catatan Hierarki Umur (K1B - Validasi Lintas Seri):**
- WHO GHO WHOSIS_000003 (Neonatal <28 hari) <= BPS var1584 (Bayi <1 tahun) <= BPS var1373 (Balita <5 tahun). Bukan pasangan identik, melainkan aturan validasi batas atas/bawah lintas umur.

---

## 3. Ringkasan Metrics Kontribusi (results/124450099/metrics.json)
- **NIM / Nama:** 124450099 / Muhammad Syafiqul Falakh
- **Berkas mentah terverifikasi:** 16
- **Total baris tabel nasional (long):** 317 baris (data/gold/tabel_nasional_rekonsiliasi.csv)
- **Total periode tabel lebar (wide):** 74 periode x 9 seri (data/gold/tabel_nasional_periode_x_seri.csv)
- **Pasangan rekonsiliasi:** 5 pasangan
- **Periode beririsan (BPS vs pembanding):** 6 periode (2012, 2017 untuk K1; 2016-2019 untuk K3)
- **data_hash:** f496e0a1ba4c0743ff4cb11f45b27d6cb50a064ebca7fefdf86bf32c28e8070d
