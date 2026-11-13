import pandas as pd
import hashlib
from pathlib import Path

def hitung_sha256(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def baca_who():
    folder_who = Path("data/raw/who_gho/2026-10-20/datadot")
    
    # File WHO yang akan dibaca
    daftar_file = [
        "2322814_MDG_0000000007.csv", # Kematian Balita
        "AC597B1_MDG_0000000026.csv", # Kematian Ibu
        "A4C49D3_WHOSIS_000003.csv"   # Kematian Neonatal
    ]
    
    semua_data = []

    for nama_file in daftar_file:
        file_path = folder_who / nama_file
        if not file_path.exists():
            print(f"Peringatan: File {nama_file} tidak ditemukan!")
            continue

        hash_file = hitung_sha256(file_path)
        print(f"Membaca {nama_file} | SHA256: {hash_file}")

        # Baca CSV
        df_raw = pd.read_csv(file_path)
        
        # Cari kolom nilai (N), batas bawah (NL), batas atas (NU)
        kolom_n = [c for c in df_raw.columns if c.endswith('_N')][0]
        kolom_nl = [c for c in df_raw.columns if c.endswith('_NL')][0]
        kolom_nu = [c for c in df_raw.columns if c.endswith('_NU')][0]
        
        # 1. Filter HANYA TOTAL (Jika ada kolom SEX atau WEALTH_QUINTILE)
        if 'DIM_SEX' in df_raw.columns:
            df_raw = df_raw[df_raw['DIM_SEX'] == 'TOTAL']
        if 'DIM_POP_WEALTH_QUINTILE' in df_raw.columns:
            df_raw = df_raw[df_raw['DIM_POP_WEALTH_QUINTILE'] == 'TOTAL']

        # 2. Ekstrak Data
        for _, baris in df_raw.iterrows():
            semua_data.append({
                "sumber": "WHO_GHO",
                "kode_indikator": baris["IND_CODE"],
                "nama_indikator": baris["IND_NAME"],
                "wilayah": baris["GEO_NAME_SHORT"],
                "tahun": int(baris["DIM_TIME"]),
                "nilai": float(baris[kolom_n]),
                "nilai_bawah": float(baris[kolom_nl]),
                "nilai_atas": float(baris[kolom_nu]),
                "berkas_raw": nama_file,
                "sha256_raw": hash_file
            })

    # 3. Simpan ke Parquet
    df = pd.DataFrame(semua_data)
    if not df.empty:
        df = df.sort_values(by=["kode_indikator", "tahun"]).reset_index(drop=True)
        print(f"\nBerhasil mengekstrak {len(df)} baris data WHO GHO.")
        
        output_path = Path("data/silver/who_ekstrak.parquet")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(output_path, index=False)
        print(f"Data disimpan ke {output_path}")
        
        print("\nPreview Data:")
        print(df.head())
    else:
        print("\nTidak ada data yang diekstrak.")

if __name__ == "__main__":
    baca_who()