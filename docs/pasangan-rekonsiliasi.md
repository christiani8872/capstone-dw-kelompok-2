# Tabel Nasional Seri Utama vs Pembanding & Daftar Pasangan Rekonsiliasi (Kartu #16)

## 1. Inventaris Seri Nasional (317 Observasi di `data/gold/tabel_nasional_rekonsiliasi.csv`)

| Kelompok Rekonsiliasi | Peran Seri | Sumber | Kode Seri | Ukuran | Satuan Baku | Cakupan Tahun | Jumlah Baris |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **K1: Kematian Balita** | Seri Utama | BPS | `var1373` | Kematian balita (<5 thn) | `per_1000_kh` | 2012, 2017 | 2 |
| **K1: Kematian Balita** | Pembanding Nasional | WDI | `SH.DYN.MORT` | Kematian balita (<5 thn) | `per_1000_kh` | 1960–2024 | 65 |
| **K1: Kematian Balita** | Pembanding Nasional | WHO GHO | `MDG_0000000007` | Kematian balita (<5 thn) | `per_1000_kh` | 1951–2023 | 73 |
| **K1B: Sub-Komponen Umur** | Seri Utama (Bayi <1 thn) | BPS | `var1584` | Angka Kematian Bayi (AKB) | `per_1000_kh` | 2012, 2017 | 2 |
| **K1B: Sub-Komponen Umur** | Pembanding (Neonatal <28 hr) | WHO GHO | `WHOSIS_000003` | Kematian neonatal | `per_1000_kh` | 1953–2023 | 71 |
| **K2: Rasio Kematian Ibu** | Pembanding Nasional | WDI | `SH.STA.MMRT` | Rasio kematian ibu (MMR) | `per_100000_kh` | 1985–2023 | 39 |
| **K2: Rasio Kematian Ibu** | Pembanding Nasional | WHO GHO | `MDG_0000000026` | Rasio kematian ibu (MMR) | `per_100000_kh` | 1985–2023 | 39 |
| **K3: Persalinan Faskes/Nakes** | Seri Utama (40% Bawah) | BPS | `var1541` | Persalinan di faskes (40% terbawah) | `persen` | 2015–2019 | 5 |
| **K3: Persalinan Faskes/Nakes** | Pembanding Nasional (Total) | WDI | `SH.STA.BRTC.ZS` | Persalinan ditolong nakes terlatih | `persen` | 1987–2019 | 21 |

---

## 2. Daftar Pasangan Rekonsiliasi & Aturan Komparasi

1. **Pasangan Rekonsiliasi Langsung 1 (`K1` — Kematian Balita / SDG 3.2.1):**
   - **Anggota:** `BPS:var1373` $\leftrightarrow$ `WDI:SH.DYN.MORT` $\leftrightarrow$ `WHO_GHO:MDG_0000000007`
   - **Status Komparabilitas:** **Setara secara definisi dan satuan (`per_1000_kh`)**, direkonsiliasi langsung pada tahun survei SDKI (2012 dan 2017).
   - **Hasil Perbandingan:**
     - **2012:** BPS `40,0` vs WHO GHO `30,96` vs WDI `29,9` (selisih BPS terhadap WDI sebesar `+10,1` per 1.000 KH).
     - **2017:** BPS `32,0` vs WHO GHO `25,38` vs WDI `23,8` (selisih BPS terhadap WDI sebesar `+8,2` per 1.000 KH).
   - **Penjelasan Selisih:** BPS menerbitkan estimasi langsung survei rumah tangga (SDKI) yang merepresentasikan jendela 5 tahun sebelum tahun survei, sedangkan WDI dan WHO GHO menyajikan kurva estimasi berbasis model UN IGME yang menghaluskan tren antartahun serta memiliki perbedaan kecil (~1,0–1,6 poin) akibat perbedaan *vintage* pemodelan UN IGME.

2. **Pasangan Hierarki Umur (`K1B` — Komponen Kematian Anak <5 Tahun):**
   - **Anggota:** `WHO_GHO:WHOSIS_000003` (Neonatal <28 hari) $\subset$ `BPS:var1584` (Bayi <1 tahun) $\subset$ `BPS:var1373` (Balita <5 tahun)
   - **Status Komparabilitas:** **Bukan pasangan identik (beda rentang usia)**; tidak diselisihkan sebagai satu indikator tunggal, melainkan digunakan sebagai aturan validasi hierarkis lintas seri: $\text{Neonatal} \le \text{AKB} \le \text{AKBa}$.

3. **Pasangan Rekonsiliasi Lintas Pembanding (`K2` — Rasio Kematian Ibu / SDG 3.1.1):**
   - **Anggota:** `WDI:SH.STA.MMRT` $\leftrightarrow$ `WHO_GHO:MDG_0000000026` *(tanpa seri provinsi BPS pada paket Kasus 02)*
   - **Status Komparabilitas:** **Setara penuh (`per_100000_kh`, 1985–2023)**.
   - **Hasil Perbandingan & Penjelasan:** Keduanya berasal dari estimasi model MMEIG (WHO/UNICEF/UNFPA/World Bank). Nilai WDI merupakan pembulatan bilangan bulat dari nilai WHO GHO (mis. tahun 2021: WDI `226,0` vs WHO GHO `226,46`; tahun 2023: WDI `140,0` vs WHO GHO `140,50`).

4. **Pasangan Rekonsiliasi Parsial (`K3` — Cakupan Persalinan Aman / SDG 3.1.2):**
   - **Anggota:** `BPS:var1541` $\leftrightarrow$ `WDI:SH.STA.BRTC.ZS`
   - **Status Komparabilitas:** **Parsial (perlu penyesuaian interpretasi karena beda cakupan populasi & lokasi)**, sama-sama bersatuan `persen`.
   - **Hasil Perbandingan (2016–2019):**
     - **2016:** BPS `73,05%` vs WDI `92,6%` (selisih `-19,55` poin persen)
     - **2017:** BPS `74,89%` vs WDI `90,9%` (selisih `-16,01` poin persen)
     - **2018:** BPS `76,82%` vs WDI `93,6%` (selisih `-16,78` poin persen)
     - **2019:** BPS `81,02%` vs WDI `94,7%` (selisih `-13,68` poin persen)
   - **Penjelasan Selisih:** BPS `var1541` membatasi populasi pada **40% rumah tangga berpendapatan terbawah** dan mensyaratkan lokasi **di fasilitas kesehatan**, sedangkan WDI `SH.STA.BRTC.ZS` mencakup **seluruh populasi nasional** dan menghitung semua persalinan yang ditolong **tenaga kesehatan terlatih** (termasuk persalinan di rumah dengan bidan). Tren konvergensi (selisih menyempit dari 19,55 menjadi 13,68 poin) mencerminkan peningkatan akses fasilitas kesehatan pada kelompok 40% terbawah.
