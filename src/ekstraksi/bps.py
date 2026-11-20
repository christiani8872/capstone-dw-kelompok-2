import json
import pandas as pd
from pathlib import Path
from src.common.manifest import sha256_raw

def baca_bps():
    # Kedua folder ada di dalam 2026-10-20
    folder_json = Path("data/raw/bps/2026-10-20/json")
    folder_csv = Path("data/raw/bps/2026-10-20")
    
    daftar_json = [
        "sdg3_3_2_1_v1373.json",
        "sdg3_3_2_1_v1584.json",
        "sdg3_3_1_2_v1541.json"
    ]
    
    daftar_csv = [
        "sdg3_3_2_1_v1373.csv",
        "sdg3_3_2_1_v1584.csv",
        "sdg3_3_1_2_v1541.csv"
    ]
    
    semua_data = []

    # --- 1. PROSES JSON ---
    print("=== Memproses File JSON ===")
    for nama_file in daftar_json:
        file_path = folder_json / nama_file
        if not file_path.exists():
            print(f"Peringatan: File JSON {nama_file} tidak ditemukan!")
            continue

        path_relatif = f"bps/2026-10-20/json/{nama_file}"
        hash_file = sha256_raw(path_relatif)
        print(f"Membaca {nama_file} | SHA256: {hash_file}")

        with open(file_path, "r", encoding="utf-8") as f:
            data_json = json.load(f)

        for block in data_json:
            var_info = block["var"][0]
            kode_var = str(var_info["val"])
            nama_var = var_info["label"]
            
            for kunci, nilai in block.get("datacontent", {}).items():
                inti_kunci = kunci[:-1] 
                kode_prov = inti_kunci[:4]
                kode_tahun = inti_kunci[-3:]
                
                prov_label = "UNKNOWN"
                for p in block.get("vervar", []):
                    if str(p["val"]) == kode_prov:
                        prov_label = p["label"]
                        break
                        
                tahun_label = "UNKNOWN"
                for t in block.get("tahun", []):
                    if str(t["val"]) == kode_tahun:
                        tahun_label = t["label"]
                        break
                
                if tahun_label != "UNKNOWN" and prov_label != "UNKNOWN":
                    semua_data.append({
                        "sumber": "BPS",
                        "kode_indikator": kode_var,
                        "nama_indikator": nama_var,
                        "wilayah": prov_label,
                        "tahun": int(tahun_label),
                        "nilai": float(nilai),
                        "_berkas_raw": nama_file,
                        "_sha256_raw": hash_file
                    })

    # --- 2. PROSES CSV ---
    print("\n=== Memproses File CSV ===")
    for nama_file in daftar_csv:
        file_path = folder_csv / nama_file
        if not file_path.exists():
            print(f"Peringatan: File CSV {nama_file} tidak ditemukan!")
            continue
            
        path_relatif = f"bps/2026-10-20/{nama_file}"
        hash_file = sha256_raw(path_relatif)
        print(f"Membaca {nama_file} | SHA256: {hash_file}")

        df_csv = pd.read_csv(file_path)
        
        for _, baris in df_csv.iterrows():
            semua_data.append({
                "sumber": "BPS",
                "kode_indikator": str(baris["var_id"]),
                "nama_indikator": f"Var {baris['var_id']}",
                "wilayah": baris["wilayah"],
                "tahun": int(baris["tahun"]),
                "nilai": float(baris["nilai"]),
                "_berkas_raw": nama_file,
                "_sha256_raw": hash_file
            })

    # --- 3. SIMPAN ---
    df = pd.DataFrame(semua_data)
    if not df.empty:
        df = df.sort_values(by=["kode_indikator", "wilayah", "tahun"]).reset_index(drop=True)
        print(f"\nBerhasil mengekstrak TOTAL {len(df)} baris data BPS.")
        
        output_path = Path("data/silver/bps_ekstrak.parquet")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(output_path, index=False)
        print(f"Data disimpan ke {output_path}")
        
        print("\nJumlah baris per file:")
        print(df.groupby("_berkas_raw").size())
    else:
        print("\nTidak ada data yang diekstrak.")

if __name__ == "__main__":
    baca_bps()