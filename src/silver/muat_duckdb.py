"""Skrip pemuat lapisan Silver ke basis data DuckDB (Kartu #17).

Jalankan:
    python -m src.silver.muat_duckdb
"""
import sys
from pathlib import Path

import duckdb
import pandas as pd

from src.common.manifest import baca, sha256_raw
from src.common.skema import KOLOM, periksa_silver

ROOT = Path(__file__).resolve().parents[2]
DDL_PATH = ROOT / "sql" / "silver.sql"
SILVER_PARQUET = ROOT / "data" / "silver" / "silver.parquet"
SILVER_DB = ROOT / "data" / "silver" / "silver.duckdb"


def buat_sampel_silver():
    """Buat contoh 11 kolom valid dari MANIFEST.csv untuk uji muat sebelum Silver tim siap."""
    manifest = baca()
    berkas_bps = sorted([b for b in manifest if b.startswith("bps/") and b.endswith(".csv")])[0]
    berkas_wdi = sorted([b for b in manifest if b.startswith("wdi/") and b.endswith(".json")])[0]
    return pd.DataFrame([
        {
            "sumber": "BPS",
            "seri_kode": "var1373",
            "wilayah_kode": 9999,
            "nama_wilayah": "INDONESIA",
            "periode": "2020",
            "jenis_periode": "tahun",
            "rincian": "total",
            "nilai": 189.0,
            "satuan": "per 100.000 kelahiran hidup",
            "_berkas_raw": berkas_bps,
            "_sha256_raw": sha256_raw(berkas_bps),
        },
        {
            "sumber": "WDI",
            "seri_kode": "SH.DYN.MORT",
            "wilayah_kode": 9999,
            "nama_wilayah": "Indonesia",
            "periode": "2020",
            "jenis_periode": "tahun",
            "rincian": "total",
            "nilai": 23.0,
            "satuan": "per 1.000 kelahiran hidup",
            "_berkas_raw": berkas_wdi,
            "_sha256_raw": sha256_raw(berkas_wdi),
        },
    ])[KOLOM]


def muat_ke_duckdb(parquet_path=SILVER_PARQUET, db_path=SILVER_DB, ddl_path=DDL_PATH):
    """Validasi skema minimal lalu muat Silver ke tabel SQL DuckDB."""
    if Path(parquet_path).exists():
        df = pd.read_parquet(parquet_path)
        sumber_data = f"berkas asli ({parquet_path})"
    else:
        df = buat_sampel_silver()
        sumber_data = "sampel uji 11 kolom (silver.parquet tim belum tersedia)"

    pelanggaran = periksa_silver(df, baca())
    if pelanggaran:
        sys.exit(f"Gagal validasi skema sebelum muat DuckDB: {pelanggaran}")

    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    ddl_sql = Path(ddl_path).read_text(encoding="utf-8")
    with duckdb.connect(str(db_path)) as con:
        con.execute(ddl_sql)
        con.register("df_silver", df[KOLOM])
        con.execute("INSERT INTO silver SELECT * FROM df_silver")
        total = con.execute("SELECT COUNT(*) FROM silver").fetchone()[0]
        ringkasan = con.execute(
            "SELECT sumber, seri_kode, COUNT(*) AS baris FROM silver GROUP BY sumber, seri_kode ORDER BY sumber, seri_kode"
        ).fetchdf()

    print(f"Sumber data : {sumber_data}")
    print(f"Basis data  : {db_path}")
    print(f"Total baris dimuat ke tabel SQL 'silver': {total:,}\n")
    print(ringkasan.to_string(index=False))


if __name__ == "__main__":
    muat_ke_duckdb()
