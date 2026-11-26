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
    
    # 3. Pemeriksaan Cakupan Ekstraksi
    print("\n=== PEMERIKSAAN CAKUPAN EKSTRAKSI ===")

    manifest_path = Path("data/raw/MANIFEST.csv")

    if manifest_path.exists():
        df_manifest = pd.read_csv(manifest_path)

        # Normalisasi path agar konsisten di Windows dan Linux
        path_manifest = (
            df_manifest["berkas"]
            .astype(str)
            .str.replace("\\", "/", regex=False)
            .str.lower()
        )

        # Pilih hanya berkas data utama yang dibaca ekstraktor
        mask_bps = (
            path_manifest.str.contains("bps/", regex=False)
            & path_manifest.str.contains("sdg", regex=False)
            & (
                path_manifest.str.endswith(".csv")
                | path_manifest.str.contains("/json/", regex=False)
            )
        )

        mask_wdi = (
            path_manifest.str.contains("wdi/", regex=False)
            & path_manifest.str.contains("/data/", regex=False)
            & path_manifest.str.endswith(".json")
        )

        mask_who = (
            path_manifest.str.contains("who_gho/", regex=False)
            & path_manifest.str.contains("/datadot/", regex=False)
            & path_manifest.str.endswith(".csv")
        )

        df_data_utama = df_manifest[mask_bps | mask_wdi | mask_who]

        nama_data_diharapkan = set(
            df_data_utama["berkas"]
            .astype(str)
            .str.replace("\\", "/", regex=False)
            .str.split("/")
            .str[-1]
        )

        nama_data_terbaca = set(
            df_gabungan["_berkas_raw"]
            .dropna()
            .astype(str)
        )

        belum_terbaca = nama_data_diharapkan - nama_data_terbaca

        print(f"Total file di MANIFEST.csv: {len(df_manifest)}")
        print(f"File data utama yang diharapkan: {len(nama_data_diharapkan)}")
        print(f"File data utama berhasil diekstrak: {len(nama_data_terbaca)}")
        print(f"File metadata/pendukung tidak diekstrak: {len(df_manifest) - len(df_data_utama)}")

        if not belum_terbaca:
            print("Cakupan data utama 100%: semua berkas data utama berhasil diekstrak.")
        else:
            print("Ada berkas data utama yang belum diekstrak:")
            for nama in sorted(belum_terbaca):
                print(f" - {nama}")

    else:
        print("File MANIFEST.csv tidak ditemukan.")
    print(f"Data disimpan ke: {output_path}")
    
    return str(output_path)
