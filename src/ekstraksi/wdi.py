import json
import pandas as pd
from pathlib import Path
from src.common.manifest import sha256_raw

def baca_wdi():
    folder_data = Path("data/raw/wdi/2026-10-20/data")
    file_meta = Path("data/raw/wdi/2026-10-20/metadata/sumber2_indikator.json")

    if not folder_data.exists():
        print(f"Error: Folder data tidak ditemukan di {folder_data}")
        return

    # 1. Baca Metadata untuk terjemahan nama indikator
    with open(file_meta, "r", encoding="utf-8") as f:
        meta_json = json.load(f)
    peta_indikator = {item["id"]: item["name"] for item in meta_json[1] if "id" in item}

    # 2. Cari SEMUA file JSON di dalam folder data
    daftar_file = list(folder_data.glob("*.json"))
    if not daftar_file:
        print("Tidak ada file JSON di folder tersebut.")
        return

    kode_target = ["SH.DYN.MORT", "SH.STA.MMRT", "SH.STA.BRTC.ZS"]

    semua_data = []
    laporan_file = {}

    # 3. Looping setiap file WDI
    for file_path in daftar_file:
        nama_file = file_path.name

        # Ambil hash via manifest
        hash_file = sha256_raw(f"wdi/2026-10-20/data/{nama_file}")
        print(f"Membaca {nama_file} | SHA256: {hash_file[:10]}...")

        with open(file_path, "r", encoding="utf-8") as f:
            data_json = json.load(f)

        baris_awal = len(semua_data)

        # Looping data di dalam file
        for baris in data_json[1]:
            kode = baris.get("indicator", {}).get("id")

            if kode in kode_target and baris.get("value") is not None:
                semua_data.append({
                    "sumber": "WDI",
                    "kode_indikator": kode,
                    "nama_indikator": peta_indikator.get(kode, "Unknown"),
                    "wilayah": baris["country"]["value"],
                    "tahun": int(baris["date"]),
                    "nilai": float(baris["value"]),
                    "_berkas_raw": nama_file,
                    "_sha256_raw": hash_file
                })

        # Catat jumlah baris per file
        laporan_file[nama_file] = len(semua_data) - baris_awal

    # 4. Simpan ke Parquet & Cetak Bukti
    df = pd.DataFrame(semua_data)

    if not df.empty:
        df["kode_indikator"] = df["kode_indikator"].astype(str)

        output_path = Path("data/silver/wdi_ekstrak.parquet")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(output_path, index=False)

        print(f"\n Berhasil mengekstrak TOTAL {len(df)} baris data WDI.")

        print("\n BUKTI JUMLAH BARIS PER BERKAS:")
        for fname, n in laporan_file.items():
            print(f"  - {fname}: {n} baris")

        print("\n SAMPEL PEMETAAN DATA (5 Baris Pertama):")
        kolom_tampil = ["kode_indikator", "nama_indikator", "wilayah", "tahun", "nilai", "_berkas_raw", "_sha256_raw"]
        print(df[kolom_tampil].head(5).to_string())
    else:
        print("\nTidak ada data yang diekstrak.")

if __name__ == "__main__":
    baca_wdi()
