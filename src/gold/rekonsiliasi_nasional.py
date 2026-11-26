
"""Membangun tabel rekonsiliasi nasional dari data Silver."""

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
KAMUS_SATUAN = ROOT / "docs" / "kamus-satuan.csv"

OUT_LONG_CSV = ROOT / "data" / "gold" / "tabel_nasional_rekonsiliasi.csv"
OUT_LONG_PARQUET = ROOT / "data" / "gold" / "tabel_nasional_rekonsiliasi.parquet"
OUT_WIDE_CSV = ROOT / "data" / "gold" / "tabel_nasional_periode_x_seri.csv"
OUT_WIDE_PARQUET = ROOT / "data" / "gold" / "tabel_nasional_periode_x_seri.parquet"


KELOMPOK_REKONSILIASI = {
    "var1373": (
        "K1_Kematian_Balita",
        "Seri Utama (BPS)",
    ),
    "SH.DYN.MORT": (
        "K1_Kematian_Balita",
        "Pembanding Nasional (WDI)",
    ),
    "MDG_0000000007": (
        "K1_Kematian_Balita",
        "Pembanding Nasional (WHO GHO)",
    ),
    "var1584": (
        "K1B_Komponen_Bayi_Neonatal",
        "Seri Utama (BPS - Bayi <1 tahun)",
    ),
    "WHOSIS_000003": (
        "K1B_Komponen_Bayi_Neonatal",
        "Pembanding Nasional (WHO GHO - Neonatal <28 hari)",
    ),
    "SH.STA.MMRT": (
        "K2_Rasio_Kematian_Ibu",
        "Pembanding Nasional (WDI)",
    ),
    "MDG_0000000026": (
        "K2_Rasio_Kematian_Ibu",
        "Pembanding Nasional (WHO GHO)",
    ),
    "var1541": (
        "K3_Persalinan_Faskes_Nakes",
        "Seri Utama (BPS - Faskes 40% Bawah)",
    ),
    "SH.STA.BRTC.ZS": (
        "K3_Persalinan_Faskes_Nakes",
        "Pembanding Nasional (WDI - Nakes Total)",
    ),
}


def bangun_tabel_nasional(
    silver: pd.DataFrame,
    kamus_path=KAMUS_SATUAN,
    out_long=OUT_LONG_CSV,
    out_wide=OUT_WIDE_CSV,
):
    """Membentuk tabel rekonsiliasi nasional long dan wide dari Silver."""

    kamus = pd.read_csv(kamus_path, dtype={"seri_kode": str})

    # Pilih hanya baris nasional dari Silver.
    nas = silver[
        silver["wilayah_kode"].astype(str).eq("9999")
        & silver["seri_kode"].isin(KELOMPOK_REKONSILIASI)
    ].copy()

    nas["seri_kode"] = nas["seri_kode"].astype(str)
    nas["periode"] = nas["periode"].astype(str)

    # Tambahkan metadata ukuran dan satuan baku.
    nas = nas.merge(
        kamus[["seri_kode", "ukuran", "satuan_baku"]],
        on="seri_kode",
        how="left",
        validate="many_to_one",
    )

    nas["kelompok_rekonsiliasi"] = nas["seri_kode"].map(
        lambda kode: KELOMPOK_REKONSILIASI[kode][0]
    )
    nas["peran_seri"] = nas["seri_kode"].map(
        lambda kode: KELOMPOK_REKONSILIASI[kode][1]
    )

    kolom = [
        "kelompok_rekonsiliasi",
        "peran_seri",
        "sumber",
        "seri_kode",
        "ukuran",
        "wilayah_kode",
        "nama_wilayah",
        "periode",
        "nilai",
        "satuan",
        "satuan_baku",
        "rincian",
        "_berkas_raw",
        "_sha256_raw",
    ]

    nas = nas[kolom].sort_values(
        ["kelompok_rekonsiliasi", "periode", "sumber", "seri_kode"]
    ).reset_index(drop=True)

    # Pastikan tidak ada lebih dari satu nilai untuk kunci seri-periode-sumber.
    kunci = ["sumber", "seri_kode", "periode"]
    if nas.duplicated(kunci).any():
        duplikat = nas.loc[nas.duplicated(kunci, keep=False), kunci]
        raise ValueError(
            "Ditemukan duplikat pada tabel nasional:\n"
            + duplikat.to_string(index=False)
        )

    # Tabel wide: satu baris per periode, satu kolom per seri sumber.
    nas["kolom_seri"] = nas["sumber"] + "__" + nas["seri_kode"]

    wide = (
        nas.pivot(
            index="periode",
            columns="kolom_seri",
            values="nilai",
        )
        .sort_index()
        .reset_index()
    )
    wide.columns.name = None

    # Simpan tabel long dan wide dalam CSV serta Parquet.
    Path(out_long).parent.mkdir(parents=True, exist_ok=True)

    nas.drop(columns=["kolom_seri"]).to_csv(
        out_long,
        index=False,
        encoding="utf-8",
    )
    nas.drop(columns=["kolom_seri"]).to_parquet(
        OUT_LONG_PARQUET,
        index=False,
    )

    wide.to_csv(out_wide, index=False, encoding="utf-8")
    wide.to_parquet(OUT_WIDE_PARQUET, index=False)

    return nas, wide


def main():
    silver_path = ROOT / "data" / "silver" / "silver.parquet"
    silver = pd.read_parquet(silver_path)

    nas, wide = bangun_tabel_nasional(silver)

    print(f"Tabel long : {OUT_LONG_CSV} ({len(nas)} baris)")
    print(
        f"Tabel wide : {OUT_WIDE_CSV} "
        f"({wide.shape[0]} periode x {wide.shape[1] - 1} seri)"
    )
    print("Jumlah seri:", nas["seri_kode"].nunique())


if __name__ == "__main__":
    main()
