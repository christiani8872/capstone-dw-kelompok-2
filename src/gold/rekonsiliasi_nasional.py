"""Pembentuk tabel nasional seri utama vs pembanding dan rekonsiliasi lintas sumber (Kartu #16).

Jalankan:
    python -m src.gold.rekonsiliasi_nasional
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW_GABUNGAN = ROOT / "data" / "silver" / "raw_gabungan.parquet"
KAMUS_SATUAN = ROOT / "docs" / "kamus-satuan.csv"
OUT_CSV = ROOT / "data" / "gold" / "tabel_nasional_rekonsiliasi.csv"

KELOMPOK_REKONSILIASI = {
    "1373": ("K1_Kematian_Balita", "Seri Utama (BPS)"),
    "SH.DYN.MORT": ("K1_Kematian_Balita", "Pembanding Nasional (WDI)"),
    "MDG_0000000007": ("K1_Kematian_Balita", "Pembanding Nasional (WHO GHO)"),
    "1584": ("K1B_Komponen_Bayi_Neonatal", "Seri Utama (BPS - Bayi <1 thn)"),
    "WHOSIS_000003": ("K1B_Komponen_Bayi_Neonatal", "Pembanding Nasional (WHO GHO - Neonatal <28 hr)"),
    "SH.STA.MMRT": ("K2_Rasio_Kematian_Ibu", "Pembanding Nasional (WDI)"),
    "MDG_0000000026": ("K2_Rasio_Kematian_Ibu", "Pembanding Nasional (WHO GHO)"),
    "1541": ("K3_Persalinan_Faskes_Nakes", "Seri Utama (BPS - Faskes 40% Bawah)"),
    "SH.STA.BRTC.ZS": ("K3_Persalinan_Faskes_Nakes", "Pembanding Nasional (WDI - Nakes Total)"),
}


def norm_kode(kode):
    k = str(kode).strip()
    return f"var{k}" if k.isdigit() else k


def bangun_tabel_nasional(raw_path=RAW_GABUNGAN, kamus_path=KAMUS_SATUAN, out_csv=OUT_CSV):
    df = pd.read_parquet(raw_path)
    kamus = pd.read_csv(kamus_path)

    # Saring hanya baris tingkat nasional (INDONESIA / Indonesia)
    nas = df[df["wilayah"].astype(str).str.strip().str.upper() == "INDONESIA"].copy()
    nas["kode_asli"] = nas["kode_indikator"].astype(str).str.strip()
    nas["seri_kode"] = nas["kode_asli"].map(norm_kode)
    nas["tahun"] = nas["tahun"].astype(int)

    # Gabungkan satuan baku dari docs/kamus-satuan.csv
    nas = nas.merge(kamus[["seri_kode", "ukuran", "satuan_baku"]], on="seri_kode", how="left")

    # Petakan kelompok pasangan rekonsiliasi & peran seri
    nas["kelompok_rekonsiliasi"] = nas["kode_asli"].map(lambda k: KELOMPOK_REKONSILIASI.get(k, ("Lainnya", "Lainnya"))[0])
    nas["peran_seri"] = nas["kode_asli"].map(lambda k: KELOMPOK_REKONSILIASI.get(k, ("Lainnya", "Lainnya"))[1])

    kolom_urut = [
        "kelompok_rekonsiliasi",
        "peran_seri",
        "sumber",
        "seri_kode",
        "ukuran",
        "tahun",
        "nilai",
        "nilai_bawah",
        "nilai_atas",
        "satuan_baku",
        "berkas_raw",
    ]
    nas = nas[kolom_urut].sort_values(["kelompok_rekonsiliasi", "tahun", "sumber", "seri_kode"]).reset_index(drop=True)

    out_csv = Path(out_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    nas.to_csv(out_csv, index=False, encoding="utf-8")
    return nas


def main():
    nas = bangun_tabel_nasional()
    print(f"Total observasi nasional tersimpan di {OUT_CSV}: {len(nas):,} baris\n")

    print("=== Ringkasan Cakupan Nasional per Seri ===")
    ringkas = (
        nas.groupby(["kelompok_rekonsiliasi", "peran_seri", "sumber", "seri_kode", "satuan_baku"], dropna=False)
        .agg(baris=("nilai", "count"), tahun_min=("tahun", "min"), tahun_max=("tahun", "max"))
        .reset_index()
    )
    print(ringkas.to_string(index=False))

    print("\n=== Perbandingan Langsung Tahun Beririsan: Kematian Balita (per 1.000 KH) ===")
    k1 = nas[nas["kelompok_rekonsiliasi"] == "K1_Kematian_Balita"]
    tahun_bps = sorted(k1[k1["sumber"] == "BPS"]["tahun"].unique())
    piv_k1 = k1[k1["tahun"].isin(tahun_bps)].pivot_table(index="tahun", columns="seri_kode", values="nilai")
    print(piv_k1.to_string())

    print("\n=== Perbandingan Langsung Tahun Beririsan: Rasio Kematian Ibu (2015-2023, per 100.000 KH) ===")
    k2 = nas[(nas["kelompok_rekonsiliasi"] == "K2_Rasio_Kematian_Ibu") & (nas["tahun"] >= 2015)]
    piv_k2 = k2.pivot_table(index="tahun", columns="seri_kode", values="nilai")
    print(piv_k2.to_string())

    print("\n=== Perbandingan Langsung Tahun Beririsan: Persalinan Faskes vs Nakes (%) ===")
    k3 = nas[nas["kelompok_rekonsiliasi"] == "K3_Persalinan_Faskes_Nakes"]
    tahun_k3 = sorted(k3[k3["sumber"] == "BPS"]["tahun"].unique())
    piv_k3 = k3[k3["tahun"].isin(tahun_k3)].pivot_table(index="tahun", columns="seri_kode", values="nilai")
    print(piv_k3.to_string())


if __name__ == "__main__":
    main()
