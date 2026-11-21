import json
import pandas as pd
from pathlib import Path
from src.common.manifest import sha256_raw

def _parse_kunci_bps(kunci, vervar, turvar, tahun_list):
    kode_vervar, kode_turvar, kode_tahun = None, None, None
    label_vervar, label_turvar, label_tahun = None, None, None

    # 1. Cari Wilayah (Vervar)
    for v in vervar:
        val_str = str(v["val"])
        if kunci.startswith(val_str):
            kode_vervar = val_str
            label_vervar = v["label"]
            break
    if not kode_vervar:
        kode_vervar = kunci[:2]
        label_vervar = next((v["label"] for v in vervar if str(v["val"]) == kode_vervar), kode_vervar)

    sisa_kunci = kunci[len(kode_vervar):]

    # 2. Cari Turvar
    kode_turvar = sisa_kunci[0]
    label_turvar = next((t["label"] for t in turvar if str(t["val"]) == kode_turvar), kode_turvar)
    sisa_kunci = sisa_kunci[1:]

    # 3. Cari Tahun (Cocokkan LANGSUNG dengan yang ada di tahun_list BPS)
    found_tahun = False
    for t in tahun_list:
        val_tahun = str(t["val"])
        if val_tahun in sisa_kunci:
            kode_tahun = val_tahun
            label_tahun = t["label"]
            found_tahun = True
            break
            
    if not found_tahun:
        kode_tahun = sisa_kunci[-4:] if len(sisa_kunci) >= 4 else sisa_kunci
        label_tahun = next((t["label"] for t in tahun_list if str(t["val"]) == kode_tahun), kode_tahun)

    # NORMALISASI: Karena kode tahun BPS aneh (112, dll), kita samakan kode_tahun dengan tahun (label)
    # Agar konsisten dengan CSV
    kode_tahun = label_tahun if label_tahun else kode_tahun

    return kode_vervar, label_vervar, kode_turvar, label_turvar, kode_tahun, label_tahun


def baca_bps():
    folder_json = Path("data/raw/bps/2026-10-20/json")
    folder_csv = Path("data/raw/bps/2026-10-20")

    daftar_json = ["sdg3_3_2_1_v1373.json", "sdg3_3_2_1_v1584.json", "sdg3_3_1_2_v1541.json"]
    daftar_csv = ["sdg3_3_2_1_v1373.csv", "sdg3_3_2_1_v1584.csv", "sdg3_3_1_2_v1541.csv"]

    semua_data = []
    laporan_file = {} 

    # --- PROSES JSON ---
    for nama_file in daftar_json:
        file_path = folder_json / nama_file
        if not file_path.exists():
            print(f"Peringatan: {nama_file} tidak ditemukan!")
            continue

        hash_file = sha256_raw(f"bps/2026-10-20/json/{nama_file}")
        with open(file_path, "r", encoding="utf-8") as f:
            data_json = json.load(f)

        baris_awal = len(semua_data)
        for block in data_json:
            vervar = block.get("vervar", [])
            turvar = block.get("turvar", [])
            tahun_list = block.get("tahun", [])
            
            for var_info in block.get("var", []):
                for kunci, nilai in block.get("datacontent", {}).items():
                    kode_vervar, label_vervar, kode_turvar, label_turvar, kode_tahun, label_tahun = _parse_kunci_bps(
                        kunci, vervar, turvar, tahun_list
                    )
                    semua_data.append({
                        "sumber": "BPS",
                        "kode_indikator": str(var_info["val"]),
                        "nama_indikator": var_info["label"],
                        "kode_wilayah": kode_vervar,
                        "wilayah": label_vervar,
                        "kode_turvar": kode_turvar,
                        "turvar": label_turvar,
                        "kode_tahun": kode_tahun,
                        "tahun": label_tahun,
                        "nilai": str(nilai) if nilai is not None else None,
                        "_berkas_raw": nama_file,
                        "_sha256_raw": hash_file,
                    })
        laporan_file[nama_file] = len(semua_data) - baris_awal

    # --- PROSES CSV ---
    for nama_file in daftar_csv:
        file_path = folder_csv / nama_file
        if not file_path.exists():
            print(f"Peringatan: {nama_file} tidak ditemukan!")
            continue

        hash_file = sha256_raw(f"bps/2026-10-20/{nama_file}")
        df_csv = pd.read_csv(file_path, dtype=str)
        
        baris_awal = len(semua_data)
        for _, baris in df_csv.iterrows():
            semua_data.append({
                "sumber": "BPS",
                "kode_indikator": baris.get("var_id"),
                "nama_indikator": f"Var {baris.get('var_id')}",
                "kode_wilayah": baris.get("kode_wilayah"),
                "wilayah": baris.get("wilayah"),
                "kode_turvar": None,
                "turvar": None,
                "kode_tahun": baris.get("tahun"),
                "tahun": baris.get("tahun"),
                "nilai": baris.get("nilai"),
                "_berkas_raw": nama_file,
                "_sha256_raw": hash_file,
            })
        laporan_file[nama_file] = len(semua_data) - baris_awal

    # --- SIMPAN & VALIDASI ---
    df = pd.DataFrame(semua_data)
    if df.empty:
        print("Tidak ada data yang diekstrak.")
        return

    df = df.sort_values(by=["kode_indikator", "kode_wilayah", "tahun"], na_position="last").reset_index(drop=True)
    
    # Paksa tipe string agar parquet aman
    kolom_string = ["kode_indikator", "kode_wilayah", "kode_turvar", "kode_tahun", "nilai"]
    for kol in kolom_string:
        df[kol] = df[kol].apply(lambda x: str(x) if pd.notna(x) else None)

    # Validasi Lineage
    assert df["_berkas_raw"].notna().all(), "GAGAL: _berkas_raw ada yang kosong!"
    assert df["_sha256_raw"].notna().all(), "GAGAL: _sha256_raw ada yang kosong!"

    output_path = Path("data/silver/bps_ekstrak.parquet")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)

    # --- CETAK BUKTI ---
    print(f"\n Berhasil mengekstrak TOTAL {len(df)} baris data BPS.")
    print(" Validasi Lineage: Semua baris memiliki _berkas_raw dan _sha256_raw.")
    print("\n BUKTI JUMLAH BARIS PER BERKAS:")
    for fname, n in laporan_file.items():
        print(f"  - {fname}: {n} baris")
    
    print("\n SAMPEL PEMETAAN DIMENSI (5 Baris Pertama):")
    print(df[["kode_indikator", "kode_wilayah", "wilayah", "kode_turvar", "turvar", "kode_tahun", "tahun", "_berkas_raw"]].head(5).to_string())


if __name__ == "__main__":
    baca_bps()