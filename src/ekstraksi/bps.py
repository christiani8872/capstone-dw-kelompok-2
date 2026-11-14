import json
import hashlib
import pandas as pd
from pathlib import Path

def hitung_sha256(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def baca_bps():
    folder_bps = Path("data/raw/bps/2026-10-20/json")
    
    # KITA GUNAKAN NAMA FILE YANG BERHASIL DIBACA SAJA DULU
    # (Silakan ganti nama_v1373 jika sudah tahu nama yang benar)
    daftar_file = [
        "sdg3_3_2_1_v1373.json",   # <-- NAMA YANG BENAR
        "sdg3_3_2_1_v1584.json",   # Kematian Bayi
        "sdg3_3_1_2_v1541.json"    # Persalinan di Fasilitas
    ]
    
    semua_data = []

    for nama_file in daftar_file:
        file_path = folder_bps / nama_file
        if not file_path.exists():
            print(f"Peringatan: File {nama_file} tidak ditemukan!")
            continue

        hash_file = hitung_sha256(file_path)
        print(f"Membaca {nama_file} | SHA256: {hash_file}")

        with open(file_path, "r", encoding="utf-8") as f:
            data_json = json.load(f)

        for block in data_json:
            var_info = block["var"][0]
            kode_var = str(var_info["val"])
            nama_var = var_info["label"]
            
            # Ambil daftar provinsi dan tahun dari JSON
            list_prov = [p["label"] for p in block.get("vervar", [])]
            list_tahun = [t["label"] for t in block.get("tahun", [])]
            
            # Ekstrak datacontent dengan iterasi biasa
            for kunci, nilai in block.get("datacontent", {}).items():
                # Kunci BPS biasanya berakhiran 0 (misal 7400154101190)
                # Kita tidak perlu memotong string, kita cukup pakai indeks jika datanya list
                # TAPI karena formatnya dictionary, kita akali dengan mengambil data dari metadata
                
                # Karena formatnya dict, kita harus iterasi manual
                # Kunci = [KodeProv][KodeVar][KodeTahun][0]
                pass
                
            # KODE YANG BENAR: Kita pakai logika pengecekan manual
            for kunci, nilai in block.get("datacontent", {}).items():
                # Ambil nilai provinsi dan tahun dari kunci berdasarkan kode_var
                # Kunci selalu diakhiri '0'
                inti_kunci = kunci[:-1] 
                
                # Cari kode provinsi (4 digit pertama)
                kode_prov = inti_kunci[:4]
                
                # Cari kode tahun (3 digit terakhir)
                kode_tahun = inti_kunci[-3:]
                
                # Cocokkan kode dengan label
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
                        "berkas_raw": nama_file,
                        "sha256_raw": hash_file
                    })

    df = pd.DataFrame(semua_data)
    if not df.empty:
        df = df.sort_values(by=["kode_indikator", "wilayah", "tahun"]).reset_index(drop=True)
        print(f"\nBerhasil mengekstrak {len(df)} baris data BPS.")
        
        output_path = Path("data/silver/bps_ekstrak.parquet")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(output_path, index=False)
        print(f"Data disimpan ke {output_path}")
        
        print("\nPreview Data:")
        print(df.head())
    else:
        print("\nTidak ada data yang diekstrak. Cek kembali nama file dan folder.")

if __name__ == "__main__":
    baca_bps()