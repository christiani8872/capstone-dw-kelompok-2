"""Membangun panel indikator BPS tingkat provinsi untuk Gold."""

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
GRID_PATH = ROOT / "reports" / "kelengkapan-panel-38-provinsi.csv"


def bangun_panel(silver: pd.DataFrame) -> pd.DataFrame:
    """Gabungkan grid kelengkapan 38 provinsi dengan nilai dari Silver."""

    grid = pd.read_csv(
        GRID_PATH,
        dtype={
            "seri_kode": str,
            "wilayah_kode": str,
            "periode": str,
        },
    )

    # Ambil hanya indikator BPS yang masuk panel provinsi.
    seri_panel = ["var1373", "var1584", "var1541"]
    grid = grid[grid["seri_kode"].isin(seri_panel)].copy()

    # Samakan format kunci agar dapat digabungkan dengan Silver.
    data = silver.copy()
    data["seri_kode"] = data["seri_kode"].astype(str)
    data["wilayah_kode"] = data["wilayah_kode"].astype(str)
    data["periode"] = data["periode"].astype(str)

    # Nilai aktual diambil dari Silver, bukan dari laporan kelengkapan.
    nilai_silver = data[
        data["sumber"].eq("BPS")
        & data["seri_kode"].isin(seri_panel)
        & data["wilayah_kode"].ne("9999")
    ][
        [
            "seri_kode",
            "periode",
            "wilayah_kode",
            "nilai",
            "satuan",
            "_berkas_raw",
            "_sha256_raw",
        ]
    ]

    panel = grid.merge(
        nilai_silver,
        on=["seri_kode", "periode", "wilayah_kode"],
        how="left",
        validate="one_to_one",
    )

    # Status mengikuti grid kelengkapan; nilai kosong tidak dianggap nol.
    panel["status_ketersediaan"] = panel["status"]
    panel = panel.drop(columns=["status"])

    # Urutkan agar hasil konsisten setiap kali dijalankan.
    panel = panel.sort_values(
        ["seri_kode", "periode", "wilayah_kode"]
    ).reset_index(drop=True)

    return panel