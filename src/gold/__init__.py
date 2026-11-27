"""Tahap Gold: panel provinsi dan rekonsiliasi nasional."""

from pathlib import Path
import sqlite3

import pandas as pd

from src.gold.panel_provinsi import bangun_panel
from src.gold.pemilihan_nilai import (
    pilih_periode_gold,
    pilih_rincian_gold,
    pilih_snapshot_terbaru,
)
from src.gold.rekonsiliasi import bangun_rekonsiliasi
from src.gold.rekonsiliasi_nasional import bangun_tabel_nasional


ROOT = Path(__file__).resolve().parents[2]
GOLD_DIR = ROOT / "data" / "gold"
SQLITE_PATH = GOLD_DIR / "gold.sqlite"


def jalankan(silver: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Terima Silver, bangun tabel Gold, simpan Parquet dan SQLite."""

    GOLD_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Terapkan aturan pemilihan Gold.
    snapshot, audit_snapshot = pilih_snapshot_terbaru(silver)

    panel_rincian, audit_panel_rincian = pilih_rincian_gold(
        snapshot, "panel"
    )
    panel_siap, audit_panel_periode = pilih_periode_gold(
        panel_rincian, "panel"
    )

    nasional_rincian, audit_nasional_rincian = pilih_rincian_gold(
        snapshot, "nasional"
    )
    nasional_siap, audit_nasional_periode = pilih_periode_gold(
        nasional_rincian, "nasional"
    )

    # 2. Panel indikator BPS tingkat provinsi.
    panel = bangun_panel(panel_siap)
    panel.to_parquet(
        GOLD_DIR / "panel_provinsi.parquet",
        index=False,
    )

    # 3. Tabel rekonsiliasi nasional long dan wide.
    nasional_long, nasional_wide = bangun_tabel_nasional(
        nasional_siap
    )

    # 4. Tabel rekonsiliasi berpasangan dengan kategori selisih (Kartu #29).
    rekonsiliasi = bangun_rekonsiliasi(nasional_long)

    # 5. Simpan seluruh tabel ke SQLite.
    with sqlite3.connect(SQLITE_PATH) as conn:
        panel.to_sql(
            "panel_provinsi",
            conn,
            if_exists="replace",
            index=False,
        )
        nasional_long.drop(
            columns=["kolom_seri"],
            errors="ignore",
        ).to_sql(
            "rekonsiliasi_nasional",
            conn,
            if_exists="replace",
            index=False,
        )
        nasional_wide.to_sql(
            "nasional_periode_x_seri",
            conn,
            if_exists="replace",
            index=False,
        )
        rekonsiliasi.to_sql(
            "rekonsiliasi",
            conn,
            if_exists="replace",
            index=False,
        )

    return {
        "panel_provinsi": panel,
        "rekonsiliasi_nasional": nasional_long,
        "nasional_periode_x_seri": nasional_wide,
        "rekonsiliasi": rekonsiliasi,
    }