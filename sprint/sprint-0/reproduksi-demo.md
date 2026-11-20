# Dokumentasi Reproduksi dan Demo - Sprint 0

## 1. Persiapan Lingkungan

Lingkungan pengembangan telah dipersiapkan menggunakan Python Virtual Environment (`.venv`). Seluruh dependensi proyek berhasil dipasang berdasarkan `requirements.txt`.

## 2. Pengunduhan Data

Pengunduhan data Kasus 02 - Kematian Anak dan Ibu berhasil dilakukan menggunakan perintah:

```powershell
python unduh_data.py --kasus 2
```

Hasil pemeriksaan menunjukkan sebanyak 16 berkas berhasil dicocokkan dengan `MANIFEST.csv`.

## 3. Pengujian Pipeline

Pengujian dilakukan menggunakan perintah:

```powershell
python pipeline.py
```

Hasil pemeriksaan integritas data menunjukkan:

```text
data/raw: 16 berkas cocok dengan MANIFEST.csv
```

Pipeline kemudian berhenti pada tahap ekstraksi dengan pesan `NotImplementedError` karena implementasi pembaca data belum tersedia pada repository starter.

Kondisi tersebut sesuai dengan tahapan persiapan Sprint 0.

## 4. Kesimpulan

Persiapan lingkungan lokal, instalasi dependensi, pengunduhan data, dan pemeriksaan integritas data berhasil dilakukan. Pengujian awal pipeline juga telah dilaksanakan sebagai persiapan reproduksi proyek pada sprint berikutnya.