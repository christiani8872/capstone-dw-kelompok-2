"""Tahap 5 — Pemuat lapisan Silver dan Gold ke basis data DuckDB (Kartu #28).

Dapat dipanggil dari pipeline.py maupun mandiri:
    python -m src.gold.muat_duckdb
"""
from pathlib import Path
import duckdb
import pandas as pd

from src.common.skema import KOLOM as KOLOM_SILVER

ROOT = Path(__file__).resolve().parents[2]
DDL_SILVER = ROOT / "sql" / "silver.sql"
DDL_GOLD = ROOT / "sql" / "gold.sql"

SILVER_PARQUET = ROOT / "data" / "silver" / "silver.parquet"
PANEL_PARQUET = ROOT / "data" / "gold" / "panel_provinsi.parquet"
NASIONAL_PARQUET = ROOT / "data" / "gold" / "tabel_nasional_rekonsiliasi.parquet"
REKONSILIASI_PARQUET = ROOT / "data" / "gold" / "rekonsiliasi.parquet"

CAPSTONE_DB = ROOT / "data" / "gold" / "capstone.duckdb"


def _eksekusi_ddl(con: duckdb.DuckDBPyConnection, sql_text: str) -> None:
    """Jalankan tiap pernyataan DDL secara terpisah dan tutup kursor hasilnya."""
    for stmt in sql_text.split(";"):
        bersih = "\n".join(
            baris for baris in stmt.splitlines()
            if not baris.strip().startswith("--")
        ).strip()
        if bersih:
            con.execute(bersih).fetchall()


def muat_semua_ke_duckdb(
    silver_df: pd.DataFrame | None = None,
    panel_df: pd.DataFrame | None = None,
    nasional_df: pd.DataFrame | None = None,
    rekonsiliasi_df: pd.DataFrame | None = None,
    db_path: Path = CAPSTONE_DB,
) -> dict[str, int]:
    """Muat Silver dan seluruh tabel Gold ke DuckDB lalu verifikasi jumlah baris."""
    silver_df = silver_df if silver_df is not None else pd.read_parquet(SILVER_PARQUET)
    panel_df = panel_df if panel_df is not None else pd.read_parquet(PANEL_PARQUET)
    nasional_df = (
        nasional_df.drop(columns=["kolom_seri"], errors="ignore")
        if nasional_df is not None
        else pd.read_parquet(NASIONAL_PARQUET)
    )
    rekonsiliasi_df = rekonsiliasi_df if rekonsiliasi_df is not None else pd.read_parquet(REKONSILIASI_PARQUET)

    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    ddl_silver_sql = DDL_SILVER.read_text(encoding="utf-8")
    ddl_gold_sql = DDL_GOLD.read_text(encoding="utf-8")

    tabel_dan_df = [
        ("silver", silver_df[KOLOM_SILVER]),
        ("panel_provinsi", panel_df),
        ("tabel_nasional", nasional_df),
        ("rekonsiliasi", rekonsiliasi_df),
    ]

    ringkasan_baris = {}
    with duckdb.connect(str(db_path)) as con:
        _eksekusi_ddl(con, ddl_silver_sql)
        _eksekusi_ddl(con, ddl_gold_sql)

        for nama_tabel, df in tabel_dan_df:
            con.register("df_sementara", df)
            con.execute(f"INSERT INTO {nama_tabel} SELECT * FROM df_sementara").fetchall()
            con.unregister("df_sementara")

            jumlah_sql = con.execute(f"SELECT COUNT(*) FROM {nama_tabel}").fetchall()[0][0]
            if jumlah_sql != len(df):
                raise AssertionError(
                    f"Jumlah baris SQL '{nama_tabel}' ({jumlah_sql}) != Parquet ({len(df)})"
                )
            ringkasan_baris[nama_tabel] = jumlah_sql

    print(f"Basis data DuckDB terbentuk: {db_path}")
    for nama_tabel, jumlah in ringkasan_baris.items():
        print(f"  - Tabel '{nama_tabel:<15}': {jumlah:,} baris (cocok dengan Parquet)")

    return ringkasan_baris


if __name__ == "__main__":
    muat_semua_ke_duckdb()