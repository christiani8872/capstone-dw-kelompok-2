    from src.ekstraksi.bps import baca_bps
    from src.ekstraksi.wdi import baca_wdi
    from src.ekstraksi.who import baca_who
    import pandas as pd
    from pathlib import Path

    def main():
        print("=== MEMULAI PIPELINE EKSTRAKSI ===")
        
        # 1. Jalankan semua pembaca
        print("\n[1/4] Menjalankan Ekstraksi BPS...")
        baca_bps()
        
        print("\n[2/4] Menjalankan Ekstraksi WDI...")
        baca_wdi()
        
        print("\n[3/4] Menjalankan Ekstraksi WHO...")
        baca_who()

        # 2. Gabungkan semua hasil
        print("\n[4/4] Menggabungkan Semua Data...")
        folder_silver = Path("data/silver")
        
        df_bps = pd.read_parquet(folder_silver / "bps_ekstrak.parquet")
        df_wdi = pd.read_parquet(folder_silver / "wdi_ekstrak.parquet")
        df_who = pd.read_parquet(folder_silver / "who_ekstrak.parquet")
        
        # Gabungkan
        df_gabungan = pd.concat([df_bps, df_wdi, df_who], ignore_index=True)
        
        # Simpan
        output_path = folder_silver / "raw_gabungan.parquet"
        df_gabungan.to_parquet(output_path, index=False)
        print(f"✅ Berhasil menggabungkan data. Total baris: {len(df_gabungan)}")
        
        # 3. Pemeriksaan Cakupan (Cek MANIFEST.csv vs jumlah file)
        print("\n=== PEMERIKSAAN CAKUPAN ===")
        manifest_path = Path("data/raw/MANIFEST.csv")
        if manifest_path.exists():
            df_manifest = pd.read_csv(manifest_path)
            # Menghitung jumlah file unik di manifest
            total_file_manifest = df_manifest['path'].nunique() if 'path' in df_manifest.columns else len(df_manifest)
            print(f"Total file terdaftar di MANIFEST.csv: {total_file_manifest}")
            
            # Cek file yang terbaca di raw_gabungan
            file_terbaca = df_gabungan["_berkas_raw"].unique()
            print(f"File yang berhasil diekstrak & digabung: {len(file_terbaca)}")
            
            # Validasi silang
            if len(file_terbaca) >= total_file_manifest:
                print(" Semua file di MANIFEST.csv berhasil diekstrak (Cakupan 100%).")
            else:
                print(f" Ada file yang belum diekstrak. Cek kembali folder data/raw/.")
        else:
            print(" File MANIFEST.csv tidak ditemukan di data/raw/.")

    if __name__ == "__main__":
        main()