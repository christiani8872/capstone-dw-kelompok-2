"""Pembentuk tabel nasional (long & wide periode x seri) dan daftar pasangan rekonsiliasi (Kartu #16).

Jalankan:
    python -m src.gold.rekonsiliasi_nasional
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW_GABUNGAN = ROOT / "data" / "silver" / "raw_gabungan.parquet"
KAMUS_SATUAN = ROOT / "docs" / "kamus-satuan.csv"
OUT_LONG_CSV = ROOT / "data" / "gold" / "tabel_nasional_rekonsiliasi.csv"
OUT_WIDE_CSV = ROOT / "data" / "gold" / "tabel_nasional_periode_x_seri.csv"

KELOMPOK_REKONSILIASI = {
    "1373": ("K1_Kematian_Balita", "Seri Utama (BPS)"),
    "SH.DYN.MORT": ("K1_Kematian_Balita", "Pembanding Nasional (WDI)"),
    "MDG_0000000007": ("K1_Kematian_Balita", "Pembanding Nasional (WHO GHO)"),
    "1584": ("K1B_Komponen_Bayi_Neonatal", "Seri Utama (BPS - Bayi <1 thn)"),
    "WHOSIS_000003": ("K1B_Komponen_Bayi_Neonatal", "Pembanding Nasional (WHO GHO - Neonatal <28 hr)"),
    "SH.STA.MMRT": ("K2_Rasio_Kematian_Ibu", "Pembanding Nasional (WDI - Konteks Nasional)"),
    "MDG_0000000026": ("K2_Rasio_Kematian_Ibu", "Pembanding Nasional (WHO GHO - Konteks Nasional)"),
    "1541": ("K3_Persalinan_Faskes_Nakes", "Seri Utama (BPS - Faskes 40% Bawah)"),
    "SH.STA.BRTC.ZS": ("K3_Persalinan_Faskes_Nakes", "Pembanding Nasional (WDI - Nakes Total)"),
}


def norm_kode(kode):
    k = str(kode).strip()
    return f"var{k}" if k.isdigit() else k


def bangun_tabel_nasional(
    raw_path=RAW_GABUNGAN,
    kamus_path=KAMUS_SATUAN,
    out_long=OUT_LONG_CSV,
    out_wide=OUT_WIDE_CSV,
):
    df = pd.read_parquet(raw_path)
    kamus = pd.read_csv(kamus_path)

    nas = df[df["wilayah"].astype(str).str.strip().str.upper() == "INDONESIA"].copy()
    nas["kode_asli"] = nas["kode_indikator"].astype(str).str.strip()
    nas["seri_kode"] = nas["kode_asli"].map(norm_kode)
    nas["tahun"] = nas["tahun"].astype(int)
    nas = nas.merge(kamus[["seri_kode", "ukuran", "satuan_baku"]], on="seri_kode", how="left")

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

    # Tabel wide periode x seri
    nas["kolom_seri"] = nas["sumber"] + "__" + nas["seri_kode"]
    wide = (
        nas.pivot_table(index="tahun", columns="kolom_seri", values="nilai", aggfunc="first")
        .sort_index()
        .reset_index()
        .rename(columns={"tahun": "periode"})
    )
    wide.columns.name = None

    Path(out_long).parent.mkdir(parents=True, exist_ok=True)
    nas.drop(columns=["kolom_seri"]).to_csv(out_long, index=False, encoding="utf-8")
    wide.to_csv(out_wide, index=False, encoding="utf-8")
    return nas, wide


def main():
    nas, wide = bangun_tabel_nasional()

    # Hitung tahun beririsan antara seri utama (BPS) dan seri pembanding (WDI/WHO_GHO)
    tahun_bps = set(nas[nas["sumber"] == "BPS"]["tahun"].unique())
    tahun_pembanding = set(nas[nas["sumber"] != "BPS"]["tahun"].unique())
    periode_beririsan = sorted(tahun_bps & tahun_pembanding)

    # 3 pasangan lintas BPS vs pembanding + 2 pasangan lintas pembanding (WDI vs WHO_GHO) = 5 pasangan
    print(f"Tabel long  : {OUT_LONG_CSV} ({len(nas)} baris)")
    print(f"Tabel wide  : {OUT_WIDE_CSV} ({wide.shape[0]} periode x {wide.shape[1]-1} seri)")
    print(f"Periode beririsan BPS vs Pembanding ({len(periode_beririsan)} tahun): {periode_beririsan}")


if __name__ == "__main__":
    main()
