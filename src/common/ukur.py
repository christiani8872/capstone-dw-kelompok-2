"""Utilitas pengukur waktu eksekusi dan penggunaan memori pandas (Kartu #4).

Contoh penggunaan di kode:
    from src.common.ukur import ukur_pandas, ukur_df_mb

    with ukur_pandas("ekstraksi") as catatan:
        df = pd.read_parquet("data/silver/raw_gabungan.parquet")
        catatan["df_mb"] = ukur_df_mb(df)

Jalankan uji mandiri:
    python -m src.common.ukur
"""
from contextlib import contextmanager
from functools import wraps
from pathlib import Path
import time
import tracemalloc

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]


def ukur_df_mb(obj):
    """Hitung total memori DataFrame (atau dict/list berisi DataFrame) dalam MB."""
    if isinstance(obj, pd.DataFrame):
        return round(obj.memory_usage(deep=True).sum() / (1024 * 1024), 4)
    if isinstance(obj, dict):
        return round(sum(ukur_df_mb(v) for v in obj.values()), 4)
    if isinstance(obj, (list, tuple)):
        return round(sum(ukur_df_mb(v) for v in obj), 4)
    return 0.0


@contextmanager
def ukur_pandas(nama="proses", cetak=True):
    """Context manager untuk mengukur durasi (detik), puncak RAM tracemalloc (MB), dan memori DataFrame."""
    catatan = {"nama": nama, "durasi_detik": 0.0, "puncak_ram_mb": 0.0, "df_mb": 0.0}
    was_tracing = tracemalloc.is_tracing()
    if not was_tracing:
        tracemalloc.start()
    else:
        tracemalloc.reset_peak()

    mulai = time.perf_counter()
    try:
        yield catatan
    finally:
        catatan["durasi_detik"] = round(time.perf_counter() - mulai, 4)
        _, puncak_byte = tracemalloc.get_traced_memory()
        catatan["puncak_ram_mb"] = round(puncak_byte / (1024 * 1024), 4)
        if not was_tracing:
            tracemalloc.stop()
        if cetak:
            print(
                f"[UKUR] {catatan['nama']:<28} | "
                f"waktu={catatan['durasi_detik']:.4f} s | "
                f"puncak_ram={catatan['puncak_ram_mb']:.4f} MB | "
                f"memori_df={catatan['df_mb']:.4f} MB"
            )


def pantau_pandas(nama=None, cetak=True):
    """Dekorator untuk mengukur fungsi yang mengembalikan DataFrame atau kumpulan DataFrame."""
    def dekorator(fn):
        label = nama or fn.__name__

        @wraps(fn)
        def pembungkus(*args, **kwargs):
            with ukur_pandas(label, cetak=cetak) as catatan:
                hasil = fn(*args, **kwargs)
                catatan["df_mb"] = ukur_df_mb(hasil)
            return hasil

        return pembungkus

    return dekorator


def main():
    ringkasan = []
    target_uji = [
        ("baca_raw_gabungan_parquet", ROOT / "data" / "silver" / "raw_gabungan.parquet", pd.read_parquet),
        ("baca_nasional_rekonsiliasi", ROOT / "data" / "gold" / "tabel_nasional_rekonsiliasi.csv", pd.read_csv),
    ]
    for label, jalur, pembaca in target_uji:
        if not jalur.exists():
            continue
        with ukur_pandas(label) as catatan:
            df = pembaca(jalur)
            catatan["baris"] = len(df)
            catatan["df_mb"] = ukur_df_mb(df)
        ringkasan.append(catatan)

    if ringkasan:
        print("\nRingkasan Pengukuran Pandas:")
        print(pd.DataFrame(ringkasan).to_string(index=False))


if __name__ == "__main__":
    main()
