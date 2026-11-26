
"""Pembentukan panel Gold provinsi untuk indikator BPS Case 02."""

from pathlib import Path

import pandas as pd


def jalankan(silver):
    """Membentuk panel 38 provinsi x periode x indikator."""

    root = Path(__file__).resolve().parents[2]

    # Membaca referensi kelengkapan 38 provinsi.
    referensi = pd.read_csv(
        root / "reports" / "kelengkapan-panel-38-provinsi.csv",
        dtype={"periode": str},
    )

    seri = ["var1373", "var1584", "var1541"]
    referensi = referensi[
        referensi["seri_kode"].isin(seri)
    ].copy()

    # Memilih data BPS dari JSON sebagai sumber kanonis.
    df = silver.copy()
    df = df[
        (df["sumber"] == "BPS")
        & (df["seri_kode"].isin(seri))
        & (df["wilayah_kode"] != 9999)
        & (df["_berkas_raw"].str.lower().str.endswith(".json"))
    ].copy()

    kunci = ["wilayah_kode", "periode", "seri_kode"]

    # Pastikan observasi JSON tidak memiliki kunci ganda.
    if df.duplicated(kunci).any():
        raise ValueError("Ditemukan kunci panel ganda pada data Silver JSON.")

    observasi = df[
        kunci
        + [
            "nilai",
            "satuan",
            "jenis_periode",
            "rincian",
            "_berkas_raw",
            "_sha256_raw",
        ]
    ]

    # Membentuk grid lengkap 38 provinsi untuk setiap indikator-periode.
    panel = referensi.merge(
        observasi,
        on=kunci,
        how="left",
        validate="one_to_one",
    )

    # Menetapkan satuan meskipun nilai belum tersedia.
    satuan_indikator = {
        "var1373": "per_1000_kelahiran_hidup",
        "var1584": "per_1000_kelahiran_hidup",
        "var1541": "persen",
    }

    panel["satuan"] = panel["satuan"].fillna(
        panel["seri_kode"].map(satuan_indikator)
    )

    panel["sumber"] = "BPS"
    panel["jenis_periode"] = panel["jenis_periode"].fillna("tahun")
    panel["rincian"] = panel["rincian"].fillna("total")

    # Status teramati harus memiliki nilai.
    tidak_ada_nilai = (
        (panel["status"] == "teramati")
        & panel["nilai"].isna()
    )

    if tidak_ada_nilai.any():
        raise ValueError(
            "Ada baris berstatus teramati tetapi nilai JSON tidak ditemukan."
        )

    # Memastikan ukuran panel 38 x 9 = 342 baris.
    if len(panel) != 342:
        raise ValueError(
            f"Panel seharusnya 342 baris, ditemukan {len(panel)}."
        )

    if panel.duplicated(kunci).any():
        raise ValueError("Kunci panel Gold tidak unik.")

    kolom = [
        "sumber",
        "seri_kode",
        "wilayah_kode",
        "nama_wilayah",
        "periode",
        "jenis_periode",
        "rincian",
        "nilai",
        "satuan",
        "status",
        "_berkas_raw",
        "_sha256_raw",
    ]

    panel = panel[kolom].sort_values(kunci).reset_index(drop=True)

    # Menyimpan panel provinsi ke Gold.
    folder_gold = root / "data" / "gold"
    folder_gold.mkdir(parents=True, exist_ok=True)

    panel.to_parquet(
        folder_gold / "panel_provinsi.parquet",
        index=False,
    )

    print(f"Panel provinsi Gold: {len(panel)} baris")
    print(f"Jumlah provinsi: {panel['wilayah_kode'].nunique()}")
    print(
        "Jumlah kombinasi indikator-periode: "
        f"{panel[['seri_kode', 'periode']].drop_duplicates().shape[0]}"
    )

    return {"panel_provinsi": panel}
