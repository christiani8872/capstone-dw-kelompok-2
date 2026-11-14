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

def baca_wdi():
    # Path disesuaikan dengan hasil pencarian terminalmu
    file_data = Path("data/raw/wdi/2026-10-20/data/kelompok-05-hal-01.json")
    file_meta = Path("data/raw/wdi/2026-10-20/metadata/sumber2_indikator.json")
    
    if not file_data.exists():
        print(f"Error: File tidak ditemukan di {file_data}")
        return

    # 1. Hitung SHA256 (Syarat Lineage)
    hash_file = hitung_sha256(file_data)
    print(f"Membaca {file_data.name} | SHA256: {hash_file}")

    # 2. Baca Metadata untuk terjemahan nama indikator
    with open(file_meta, "r", encoding="utf-8") as f:
        meta_json = json.load(f)
    peta_indikator = {item["id"]: item["name"] for item in meta_json[1] if "id" in item}

    # 3. Baca Data Aktual
    with open(file_data, "r", encoding="utf-8") as f:
        data_json = json.load(f)

    # 4. Filter HANYA indikator yang kita butuhkan (Kematian Anak & Ibu)
    # Sesuai PDF: SH.DYN.MORT, SH.STA.MMRT, SH.STA.BRTC.ZS
    kode_target = ["SH.DYN.MORT", "SH.STA.MMRT", "SH.STA.BRTC.ZS"]
    
    hasil = []
    for baris in data_json[1]:
        kode = baris["indicator"]["id"]
        
        if kode in kode_target and baris["value"] is not None:
            hasil.append({
                "sumber": "WDI",
                "kode_indikator": kode,
                "nama_indikator": peta_indikator.get(kode, "Unknown"),
                "wilayah": baris["country"]["value"],
                "tahun": int(baris["date"]),
                "nilai": float(baris["value"]),
                "berkas_raw": file_data.name, # Syarat Lineage
                "sha256_raw": hash_file       # Syarat Lineage
            })

    # 5. Simpan ke Parquet
    df = pd.DataFrame(hasil)
    print(f"Berhasil mengekstrak {len(df)} baris data WDI.")
    
    output_path = Path("data/silver/wdi_ekstrak.parquet")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)
    print(f"Data disimpan ke {output_path}")

if __name__ == "__main__":
    baca_wdi()