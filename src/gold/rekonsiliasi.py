"""Tahap 6 — Pembentuk tabel rekonsiliasi berpasangan dengan kategori selisih (Kartu #29).

Dapat dipanggil dari pipeline.py maupun mandiri:
    python -m src.gold.rekonsiliasi
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
NASIONAL_PARQUET = ROOT / "data" / "gold" / "tabel_nasional_rekonsiliasi.parquet"
OUT_REKONSILIASI_PARQUET = ROOT / "data" / "gold" / "rekonsiliasi.parquet"
OUT_REKONSILIASI_CSV = ROOT / "data" / "gold" / "rekonsiliasi.csv"

KATEGORI_RESMI = {
    "definisi berbeda",
    "metode berbeda",
    "vintage berbeda",
    "cakupan berbeda",
    "belum terjelaskan",
}

DAFTAR_PASANGAN = [
    {
        "kode_pasangan": "P1_BALITA_BPS_WHO",
        "seri_utama": "var1373",
        "sumber_utama": "BPS",
        "seri_pembanding": "MDG_0000000007",
        "sumber_pembanding": "WHO_GHO",
        "kategori": "metode berbeda",
        "catatan": (
            "BPS var1373 (Angka Kematian Balita) berasal dari survei retrospektif SDKI dengan jendela rujukan "
            "nasional 5 tahun, sedangkan WHO MDG_0000000007 menggunakan estimasi model statistik UN IGME."
        ),
    },
    {
        "kode_pasangan": "P2_BALITA_BPS_WDI",
        "seri_utama": "var1373",
        "sumber_utama": "BPS",
        "seri_pembanding": "SH.DYN.MORT",
        "sumber_pembanding": "WDI",
        "kategori": "metode berbeda",
        "catatan": (
            "BPS var1373 mengukur kematian balita berbasis survei SDKI (jendela rujukan 5 tahun), "
            "sedangkan WDI SH.DYN.MORT merupakan seri estimasi model tahunan UN IGME."
        ),
    },
    {
        "kode_pasangan": "P3_BAYI_NEONATAL_BPS_WHO",
        "seri_utama": "var1584",
        "sumber_utama": "BPS",
        "seri_pembanding": "WHOSIS_000003",
        "sumber_pembanding": "WHO_GHO",
        "kategori": "definisi berbeda",
        "catatan": (
            "BPS var1584 mengukur Angka Kematian Bayi (usia < 1 tahun / 0-11 bulan), "
            "sedangkan WHO WHOSIS_000003 hanya mengukur kematian neonatal (usia 0-27 hari, DIM_AGE=D_LE27)."
        ),
    },
    {
        "kode_pasangan": "P4_PERSALINAN_BPS_WDI",
        "seri_utama": "var1541",
        "sumber_utama": "BPS",
        "seri_pembanding": "SH.STA.BRTC.ZS",
        "sumber_pembanding": "WDI",
        "kategori": "definisi berbeda",
        "catatan": (
            "BPS var1541 mengukur persalinan di fasilitas kesehatan khusus kelompok 40% pengeluaran terbawah, "
            "sedangkan WDI SH.STA.BRTC.ZS mengukur persalinan ditolong tenaga kesehatan terlatih untuk seluruh populasi."
        ),
    },
    {
        "kode_pasangan": "P5_BALITA_WHO_WDI",
        "seri_utama": "MDG_0000000007",
        "sumber_utama": "WHO_GHO",
        "seri_pembanding": "SH.DYN.MORT",
        "sumber_pembanding": "WDI",
        "kategori": "vintage berbeda",
        "catatan": (
            "Keduanya merujuk pada estimasi kematian balita UN IGME per 1.000 kelahiran hidup; "
            "selisih kecil mencerminkan perbedaan vintage rilis dan pembulatan publikasi antarlembaga."
        ),
    },
]


def bangun_rekonsiliasi(nasional_long: pd.DataFrame) -> pd.DataFrame:
    """Pasangkan seri utama dengan pembanding dari tabel nasional Gold."""
    nas = nasional_long.copy()
    nas["periode"] = nas["periode"].astype(str)

    semua_pasangan = []
    for cfg in DAFTAR_PASANGAN:
        if cfg["kategori"] not in KATEGORI_RESMI:
            raise ValueError(f"Kategori tidak valid: {cfg['kategori']}")

        df_u = nas[
            (nas["seri_kode"] == cfg["seri_utama"])
            & (nas["sumber"] == cfg["sumber_utama"])
        ][["periode", "nilai", "satuan_baku"]].rename(
            columns={"nilai": "nilai_utama", "satuan_baku": "satuan_utama"}
        )

        df_p = nas[
            (nas["seri_kode"] == cfg["seri_pembanding"])
            & (nas["sumber"] == cfg["sumber_pembanding"])
        ][["periode", "nilai", "satuan_baku"]].rename(
            columns={"nilai": "nilai_pembanding", "satuan_baku": "satuan_pembanding"}
        )

        # Outer join agar periode tanpa pasangan tetap tampil
        m = (
            pd.merge(df_u, df_p, on="periode", how="outer")
            .sort_values("periode")
            .reset_index(drop=True)
        )

        satuan_u = df_u["satuan_utama"].iloc[0] if not df_u.empty else ""
        satuan_p = df_p["satuan_pembanding"].iloc[0] if not df_p.empty else ""
        m["satuan_utama"] = m["satuan_utama"].fillna(satuan_u)
        m["satuan_pembanding"] = m["satuan_pembanding"].fillna(satuan_p)

        m["kode_pasangan"] = cfg["kode_pasangan"]
        m["seri_utama"] = cfg["seri_utama"]
        m["sumber_utama"] = cfg["sumber_utama"]
        m["seri_pembanding"] = cfg["seri_pembanding"]
        m["sumber_pembanding"] = cfg["sumber_pembanding"]

        # Selisih dihitung apa adanya tanpa dihapus atau dipaksa sama
        m["selisih"] = m["nilai_utama"] - m["nilai_pembanding"]

        berpasangan = m["nilai_utama"].notna() & m["nilai_pembanding"].notna()
        m["status_pasangan"] = "berpasangan"
        m.loc[m["nilai_utama"].notna() & m["nilai_pembanding"].isna(), "status_pasangan"] = "hanya_utama"
        m.loc[m["nilai_utama"].isna() & m["nilai_pembanding"].notna(), "status_pasangan"] = "hanya_pembanding"

        m["kategori_penjelasan"] = None
        m.loc[berpasangan, "kategori_penjelasan"] = cfg["kategori"]

        m["catatan_penjelasan"] = cfg["catatan"]
        m.loc[~berpasangan, "catatan_penjelasan"] = (
            "Periode tidak beririsan antar kedua sumber; dipertahankan sesuai aturan kelengkapan tabel. "
            + cfg["catatan"]
        )

        semua_pasangan.append(m)

    kolom_urut = [
        "kode_pasangan",
        "periode",
        "seri_utama",
        "sumber_utama",
        "nilai_utama",
        "satuan_utama",
        "seri_pembanding",
        "sumber_pembanding",
        "nilai_pembanding",
        "satuan_pembanding",
        "selisih",
        "status_pasangan",
        "kategori_penjelasan",
        "catatan_penjelasan",
    ]
    hasil = (
        pd.concat(semua_pasangan, ignore_index=True)[kolom_urut]
        .sort_values(["kode_pasangan", "periode"])
        .reset_index(drop=True)
    )

    # Validasi internal: kunci unik & setiap baris berpasangan wajib berkategori
    if hasil.duplicated(["kode_pasangan", "periode"]).any():
        raise ValueError("Ditemukan duplikasi kunci (kode_pasangan, periode) pada tabel rekonsiliasi.")
    if hasil.loc[hasil["status_pasangan"] == "berpasangan", "kategori_penjelasan"].isna().any():
        raise ValueError("Ada baris rekonsiliasi berpasangan tanpa kategori_penjelasan.")

    OUT_REKONSILIASI_PARQUET.parent.mkdir(parents=True, exist_ok=True)
    hasil.to_parquet(OUT_REKONSILIASI_PARQUET, index=False)
    hasil.to_csv(OUT_REKONSILIASI_CSV, index=False, encoding="utf-8")
    return hasil


if __name__ == "__main__":
    nas_df = pd.read_parquet(NASIONAL_PARQUET)
    rek_df = bangun_rekonsiliasi(nas_df)
    berpasangan_df = rek_df[rek_df["status_pasangan"] == "berpasangan"]
    print(f"Tabel rekonsiliasi : {OUT_REKONSILIASI_PARQUET} ({len(rek_df)} total baris, {len(berpasangan_df)} berpasangan)")
    print(f"Selisih median     : {berpasangan_df['selisih'].median():.4f}")