import pandas as pd
from pathlib import Path
from src.common.manifest import sha256_raw

def baca_who():
    folder_who = Path("data/raw/who_gho/2026-10-20/datadot")
    
    # File WHO yang akan dibaca
    daftar_file = [
        "2322814_MDG_0000000007.csv", # Kematian Balita
        "AC597B1_MDG_0000000026.csv", # Kematian Ibu
        "A4C49D3_WHOSIS_000003.csv"   # Kematian Neonatal
    ]
    
    semua_data = []
    laporan_file = {}

    for nama_file in daftar_file:
        file_path = folder_who / nama_file
        if not file_path.exists():
            print(f"Peringatan: File {nama_file} tidak ditemukan!")
            continue

        # 1. AMBIL HASH DARI MANIFEST
        hash_file = sha256_raw(f"who_gho/2026-10-20/datadot/{nama_file}")

        # Baca CSV (dtype=str agar tidak ada konversi otomatis yang merusak)
        df_raw = pd.read_csv(file_path, dtype=str)
        
        # Cari kolom nilai (N), batas bawah (NL), batas atas (NU)
        kolom_n = [c for c in df_raw.columns if c.endswith('_N')][0]
        kolom_nl = [c for c in df_raw.columns if c.endswith('_NL')][0]
        kolom_nu = [c for c in df_raw.columns if c.endswith('_NU')][0]
        
        # 2. FILTER HANYA TOTAL UNTUK SETIAP DIMENSI
        # Kita cek semua kolom yang berawalan 'DIM_', lalu ambil yang 'TOTAL'
        for col in df_raw.columns:
            if col.startswith('DIM_') and col != 'DIM_TIME': # TIME jangan difilter
                if 'TOTAL' in df_raw[col].values:
                    df_raw = df_raw[df_raw[col] == 'TOTAL']

        baris_awal = len(semua_data)
        
        # 3. Ekstrak Data (Pertahankan semua dimensi sumber)
        for _, baris in df_raw.iterrows():
            # Mengumpulkan semua kolom DIM_ untuk dipertahankan
            dimensi_data = {col: baris[col] for col in df_raw.columns if col.startswith('DIM_')}
            
            row_data = {
                "sumber": "WHO_GHO",
                "kode_indikator": baris["IND_CODE"],
                "nama_indikator": baris["IND_NAME"],
                "wilayah": baris["GEO_NAME_SHORT"],
                "tahun": int(baris["DIM_TIME"]),
                "nilai": float(baris[kolom_n]) if pd.notna(baris[kolom_n]) else None,
                "nilai_bawah": float(baris[kolom_nl]) if pd.notna(baris[kolom_nl]) else None,
                "nilai_atas": float(baris[kolom_nu]) if pd.notna(baris[kolom_nu]) else None,
                "_berkas_raw": nama_file,    # Standarisasi kolom
                "_sha256_raw": hash_file     # Standarisasi kolom
            }
            
            # Gabungkan data dimensi dengan row_data
            row_data.update(dimensi_data)
            semua_data.append(row_data)
            
        laporan_file[nama_file] = len(semua_data) - baris_awal

    # 4. Simpan ke Parquet
    df = pd.DataFrame(semua_data)
    if not df.empty:
        df = df.sort_values(by=["kode_indikator", "tahun"]).reset_index(drop=True)
        
        output_path = Path("data/silver/who_ekstrak.parquet")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(output_path, index=False)
        
        print(f"\n Berhasil mengekstrak TOTAL {len(df)} baris data WHO GHO.")
        
        # --- CETAK BUKTI UNTUK KOMENTAR ARDIKA ---
        print("\n BUKTI JUMLAH BARIS PER BERKAS:")
        for fname, n in laporan_file.items():
            print(f"  - {fname}: {n} baris")
        
        print("\n SAMPEL PEMETAAN DATA (3 Baris Pertama):")
        # Tampilkan beberapa kolom penting (termasuk dimensi)
        kolom_tampil = ["kode_indikator", "wilayah", "tahun", "nilai", "nilai_bawah", "nilai_atas", "_berkas_raw", "_sha256_raw"]
        # Tampilkan jika kolom dimensi ada
        if 'DIM_SEX' in df.columns: kolom_tampil.insert(3, 'DIM_SEX')
        
        print(df[kolom_tampil].head(3).to_string())
    else:
        print("\nTidak ada data yang diekstrak.")

if __name__ == "__main__":
    baca_who()