
"""Membangun panel indikator BPS tingkat provinsi untuk Gold."""

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
GRID_PATH = ROOT / "reports" / "kelengkapan-panel-38-provinsi.csv"


def bangun_panel(silver: pd.DataFrame) -> pd.DataFrame:
    """Gabungkan grid kelengkapan 38 provinsi dengan nilai Silver."""

    grid = pd.read_csv(
        GRID_PATH,
        dtype={
            "seri_kode": str,
            "wilayah_kode": str,
            "periode": str,
        },
    )

    seri_panel = ["var1373", "var1584", "var1541"]
    grid = grid[grid["seri_kode"].isin(seri_panel)].copy()

    data = silver.copy()
    data["seri_kode"] = data["seri_kode"].astype(str)
    data["wilayah_kode"] = data["wilayah_kode"].astype(str)
    data["periode"] = data["periode"].astype(str)

    # Gunakan data BPS JSON sebagai sumber observasi kanonis.
    observasi = data[
        data["sumber"].eq("BPS")
        & data["seri_kode"].isin(seri_panel)
        & data["wilayah_kode"].ne("9999")
        & data["_berkas_raw"].str.lower().str.endswith(".json")
    ].copy()

    kunci = ["wilayah_kode", "periode", "seri_kode"]

    if observasi.duplicated(kunci).any():
        raise ValueError("Ditemukan kunci panel ganda pada Silver.")

    kolom_observasi = kunci + [
        "nilai",
        "satuan",
        "jenis_periode",
        "rincian",
        "_berkas_raw",
        "_sha256_raw",
    ]

    panel = grid.merge(
        observasi[kolom_observasi],
        on=kunci,
        how="left",
        validate="one_to_one",
    )

    # Satuan tetap tersedia meskipun nilai belum diterbitkan.
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

    # Bawa penanda outlier Sprint 1 ke Gold tanpa mengubah nilai.
    panel["flag_outlier"] = (
        (
            panel["seri_kode"].eq("var1373")
            & panel["wilayah_kode"].eq("9400")
            & panel["periode"].eq("2012")
            & panel["nilai"].eq(115.0)
        )
        | (
            panel["seri_kode"].eq("var1373")
            & panel["wilayah_kode"].eq("9100")
            & panel["periode"].eq("2012")
            & panel["nilai"].eq(109.0)
        )
        | (
            panel["seri_kode"].eq("var1584")
            & panel["wilayah_kode"].eq("9100")
            & panel["periode"].eq("2012")
            & panel["nilai"].eq(74.0)
        )
    )

    # K-020: belum ada bukti kuat patahan pada seri var1541.
    panel["flag_patahan"] = False
    panel["catatan_patahan"] = ""
    panel.loc[
        panel["seri_kode"].eq("var1541"),
        "catatan_patahan",
    ] = "Belum ada bukti kuat patahan; nilai dipertahankan."

    panel["status_ketersediaan"] = panel["status"]
    panel = panel.drop(columns=["status"])

    tidak_ada_nilai = (
        panel["status_ketersediaan"].eq("teramati")
        & panel["nilai"].isna()
    )

    if tidak_ada_nilai.any():
        raise ValueError(
            "Ada baris berstatus teramati tetapi nilai Silver tidak ditemukan."
        )

    if len(panel) != 342:
        raise ValueError(
            f"Panel seharusnya 342 baris, ditemukan {len(panel)}."
        )

    if panel["wilayah_kode"].nunique() != 38:
        raise ValueError("Panel harus mencakup tepat 38 provinsi.")

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
        "status_ketersediaan",
        "flag_outlier",
        "flag_patahan",
        "catatan_patahan",
        "_berkas_raw",
        "_sha256_raw",
    ]

    return (
        panel[kolom]
        .sort_values(kunci)
        .reset_index(drop=True)
    )
