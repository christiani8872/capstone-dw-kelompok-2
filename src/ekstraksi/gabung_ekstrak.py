import pandas as pd
from pathlib import Path

def gabung_semua():
    folder_silver = Path("data/silver")
    
    # Daftar file yang mau digabung
    file_wdi = folder_silver / "wdi_ekstrak.parquet"
    file_bps = folder_silver / "bps_ekstrak.parquet"
    file_who = folder_silver / "who_ekstrak.parquet"
    
    # Baca semua file
    df_wdi = pd.read_parquet(file_wdi)
    df_bps = pd.read_parquet(file_bps)
    df_who = pd.read_parquet(file_who)
    
    # Tugas #9: Gabungkan semuanya
    df_gabungan = pd.concat([df_wdi, df_bps, df_who], ignore_index=True)
    
    # Simpan sebagai tabel mentah gabungan (sebelum masuk Silver final)
    output_path = folder_silver / "raw_gabungan.parquet"
    df_gabungan.to_parquet(output_path, index=False)
    
    print(f"Berhasil menggabungkan data. Total baris: {len(df_gabungan)}")
    print(f"Data disimpan ke {output_path}")

if __name__ == "__main__":
    gabung_semua()