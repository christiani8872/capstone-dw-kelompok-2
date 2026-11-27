import pandas as pd
from pathlib import Path
from .bps import baca_bps
from .wdi import baca_wdi
from .who import baca_who

def jalankan():
    print("=== MEMULAI TAHAP EKSTRAKSI (Dipanggil oleh pipeline.py) ===")

    # 1. Jalankan semua pembaca
    baca_bps()
    baca_wdi()
    baca_who()

        # 2. Gabungkan semua hasil (Tugas #9)
    print("\nMenggabungkan semua data ekstraksi...")
    folder_silver = Path("data/silver")

    df_bps = pd.read_parquet(folder_silver / "bps_ekstrak.parquet")
    df_wdi = pd.read_parquet(folder_silver / "wdi_ekstrak.parquet")
    df_who = pd.read_parquet(folder_silver / "who_ekstrak.parquet")

    df_gabungan = pd.concat([df_bps, df_wdi, df_who], ignore_index=True)

    # --- PERBAIKAN: Paksa semua kolom kunci menjadi string agar PyArrow tidak error ---
    kolom_rawan = ["tahun", "kode_tahun", "kode_wilayah", "kode_turvar", "kode_indikator", "nilai"]
    for kol in kolom_rawan:
        if kol in df_gabungan.columns:
            # Ubah ke string murni, biarkan NaN/None tetap kosong
            df_gabungan[kol] = df_gabungan[kol].apply(lambda x: str(x) if pd.notna(x) else None)
    # ---------------------------------------------------------------------------------

    output_path = folder_silver / "raw_gabungan.parquet"
    df_gabungan.to_parquet(output_path, index=False)

    # 3. Pemeriksaan Cakupan (Cek MANIFEST.csv)
    print("\n=== PEMERIKSAAN CAKUPAN EKSTRAKSI ===")
    manifest_path = Path("data/raw/MANIFEST.csv")
    if manifest_path.exists():
        df_manifest = pd.read_csv(manifest_path)
        total_file_manifest = len(df_manifest)
        file_terbaca = df_gabungan["_berkas_raw"].nunique()

        print(f"Total file terdaftar di MANIFEST.csv: {total_file_manifest}")
        print(f"File yang berhasil diekstrak: {file_terbaca}")

        if file_terbaca >= total_file_manifest:
            print(" Cakupan 100%: Semua file berhasil diekstrak.")
        else:
            print(" Ada file yang belum diekstrak. Cek kembali data/raw/.")
    else:
        print(" File MANIFEST.csv tidak ditemukan.")

    print(f"\n Selesai. Total baris gabungan: {len(df_gabungan)}")
    print(f"Data disimpan ke: {output_path}")

    return str(output_path)
