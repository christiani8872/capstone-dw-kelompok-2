import json
import pandas as pd
from pathlib import Path
from src.common.manifest import sha256_raw

def baca_wdi():
    # Path disesuaikan dengan hasil pencarian terminalmu
    file_data = Path("data/raw/wdi/2026-10-20/data/kelompok-05-hal-01.json")
    file_meta = Path("data/raw/wdi/2026-10-20/metadata/sumber2_indikator.json")
    
    if not file_data.exists():
        print(f"Error: File tidak ditemukan di {file_data}")
        return

    # 1. Gunakan Manifest untuk Lineage
    hash_file = sha256_raw("wdi/2026-10-20/data/kelompok-05-hal-01.json")
    print(f"Membaca {file_data.name}")

    # 2. Baca Metadata untuk terjemahan nama indikator
    with open(file_meta, "r", encoding="utf-8") as f:
        meta_json = json.load(f)
    peta_indikator = {item["id"]: item["name"] for item in meta_json[1] if "id" in item}

    # 3. Baca Data Aktual
    with open(file_data, "r", encoding="utf-8") as f:
        data_json = json.load(f)

    # 4. Filter HANYA indikator yang kita butuhkan (Kematian Anak & Ibu)
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
                "_berkas_raw": file_data.name, # Standarisasi kolom lineage
                "_sha256_raw": hash_file       # Standarisasi kolom lineage
            })

    # 5. Simpan ke Parquet & Cetak Bukti
    df = pd.DataFrame(hasil)
    
    if not df.empty:
        # Paksa tipe string pada kolom kode indikator agar aman saat disimpan Parquet
        df["kode_indikator"] = df["kode_indikator"].astype(str)
        
        output_path = Path("data/silver/wdi_ekstrak.parquet")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(output_path, index=False)
        
        print(f"\n Berhasil mengekstrak TOTAL {len(df)} baris data WDI.")
        
        # --- CETAK BUKTI UNTUK KOMENTAR ARDIKA ---
        print("\n BUKTI JUMLAH BARIS PER BERKAS:")
        print(f"  - {file_data.name}: {len(df)} baris")
        
        print("\n SAMPEL PEMETAAN DATA (5 Baris Pertama):")
        # Tampilkan kolom penting saja agar muat di layar
        kolom_tampil = ["kode_indikator", "nama_indikator", "wilayah", "tahun", "nilai", "_berkas_raw", "_sha256_raw"]
        print(df[kolom_tampil].head(5).to_string())
    else:
        print("\nTidak ada data yang diekstrak.")

if __name__ == "__main__":
    baca_wdi()