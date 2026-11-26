
"""Tahap 2–4 — Profil, pembersihan, dan penyeragaman ke Silver."""

from pathlib import Path

import pandas as pd
from src.common.manifest import baca


SATUAN = {
    "1373": "per_1000_kelahiran_hidup",
    "1584": "per_1000_kelahiran_hidup",
    "1541": "persen",
    "SH.DYN.MORT": "per_1000_kelahiran_hidup",
    "SH.STA.MMRT": "per_100000_kelahiran_hidup",
    "SH.STA.BRTC.ZS": "persen",
    "MDG_0000000007": "per_1000_kelahiran_hidup",
    "MDG_0000000026": "per_100000_kelahiran_hidup",
    "WHOSIS_000003": "per_1000_kelahiran_hidup",
}


def rincian_baris(row):
    """Standarkan rincian agar sesuai dengan aturan pemilihan Gold."""
    if row["sumber"] != "WHO_GHO":
        return "Tidak ada"

    bagian = []

    if pd.notna(row["DIM_AGE"]):
        bagian.append(f"AGE={row['DIM_AGE']}")

    if pd.notna(row["DIM_SEX"]):
        bagian.append(f"SEX={row['DIM_SEX']}")

    if pd.notna(row["DIM_POP_WEALTH_QUINTILE"]):
        bagian.append(
            f"WEALTH_QUINTILE={row['DIM_POP_WEALTH_QUINTILE']}"
        )

    return "; ".join(bagian) if bagian else "Tidak ada"


def jalankan(mentah):
    """Terima keluaran ekstraksi, tulis dan kembalikan DataFrame Silver."""

    df = pd.read_parquet(mentah).copy()

    # Cocokkan nama berkas dan hash dengan jalur lengkap MANIFEST.
    manifest = baca()
    peta_berkas = {}

    for path, hash_file in manifest.items():
        kunci = (Path(path).name, hash_file)
        peta_berkas.setdefault(kunci, []).append(path)

    def cari_path(row):
        kunci = (Path(row["_berkas_raw"]).name, row["_sha256_raw"])
        kandidat = peta_berkas.get(kunci, [])

        if len(kandidat) != 1:
            raise ValueError(
                f"Jalur MANIFEST tidak unik atau tidak ditemukan: {kunci}"
            )

        return kandidat[0]

    df["_berkas_raw"] = df.apply(cari_path, axis=1)

    # Samakan format kode indikator dan tahun.
    df["kode_indikator"] = (
        df["kode_indikator"].astype(str).str.strip()
    )
    df["tahun"] = df["tahun"].astype(str).str.strip()

    # Lengkapi kode wilayah CSV BPS menggunakan pasangan JSON.
    bps = df[df["sumber"] == "BPS"]
    json_bps = bps[bps["_berkas_raw"].str.endswith(".json")]

    kunci_wilayah = ["kode_indikator", "wilayah", "tahun"]

    peta_wilayah = (
        json_bps[kunci_wilayah + ["kode_wilayah"]]
        .drop_duplicates()
    )

    if peta_wilayah.duplicated(kunci_wilayah).any():
        raise ValueError("Pemetaan kode wilayah BPS tidak unik.")

    peta = {
        tuple(row[k] for k in kunci_wilayah): row["kode_wilayah"]
        for _, row in peta_wilayah.iterrows()
    }

    mask_csv = (
        (df["sumber"] == "BPS")
        & df["_berkas_raw"].str.endswith(".csv")
    )

    df.loc[mask_csv, "kode_wilayah"] = [
        peta.get(tuple(row[k] for k in kunci_wilayah))
        for _, row in df.loc[mask_csv].iterrows()
    ]

    # Wilayah nasional untuk WDI dan WHO.
    mask_nasional = df["sumber"].isin(["WDI", "WHO_GHO"])
    df.loc[mask_nasional, "kode_wilayah"] = "9999"

    # Bentuk kode seri yang konsisten.
    df["seri_kode"] = df["kode_indikator"].map(
        lambda x: f"var{x}" if x in {"1373", "1584", "1541"} else x
    )

    # Standarkan periode dan nilai.
    df["periode"] = df["tahun"]
    df["jenis_periode"] = "tahun"
    df["nilai"] = pd.to_numeric(df["nilai"], errors="coerce")

    # Bentuk rincian dan satuan.
    df["rincian"] = df.apply(rincian_baris, axis=1)
    df["satuan"] = df["kode_indikator"].map(SATUAN)

    # Bentuk nama wilayah.
    df["nama_wilayah"] = df["wilayah"]
    df.loc[mask_nasional, "nama_wilayah"] = "Indonesia"

    # Susun kolom sesuai skema Silver.
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
        "_berkas_raw",
        "_sha256_raw",
    ]

    df["wilayah_kode"] = pd.to_numeric(
        df["kode_wilayah"], errors="coerce"
    )

    silver = df[kolom].copy()

    # Jangan membuang data yang gagal dipetakan secara diam-diam.
    if silver.isna().any().any():
        raise ValueError(
            "Ada nilai kosong di Silver:\n"
            + silver.isna().sum().to_string()
        )

    silver["wilayah_kode"] = silver["wilayah_kode"].astype("int64")

    # Periksa duplikasi berdasarkan kunci skema.
    kunci = [
        "sumber",
        "seri_kode",
        "wilayah_kode",
        "periode",
        "rincian",
        "_berkas_raw",
    ]

    if silver.duplicated(kunci).any():
        raise ValueError("Ditemukan duplikasi kunci pada Silver.")

    # Simpan hasil.
    keluaran = Path("data/silver/silver.parquet")
    keluaran.parent.mkdir(parents=True, exist_ok=True)
    silver.to_parquet(keluaran, index=False)

    print(f"Silver berhasil dibuat: {len(silver)} baris")

    return silver
