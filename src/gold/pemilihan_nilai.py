"""Aturan pemilihan snapshot untuk tahap Gold."""

import pandas as pd


KUNCI_SNAPSHOT = [
    "sumber",
    "seri_kode",
    "wilayah_kode",
    "periode",
    "jenis_periode",
    "rincian",
]


def pilih_snapshot_terbaru(silver: pd.DataFrame):
    """Pilih snapshot terbaru untuk setiap kunci indikator.

    Mengembalikan:
      - DataFrame baris terpilih
      - dictionary audit jumlah baris
    """
    data = silver.copy()

    tanggal = data["_berkas_raw"].astype(str).str.extract(
        r"(\d{4}-\d{2}-\d{2})",
        expand=False,
    )

    if tanggal.isna().any():
        contoh = data.loc[tanggal.isna(), "_berkas_raw"].head(5).tolist()
        raise ValueError(
            "Tanggal snapshot tidak ditemukan pada _berkas_raw. "
            f"Contoh jalur: {contoh}"
        )

    data["_tanggal_snapshot"] = pd.to_datetime(
        tanggal,
        format="%Y-%m-%d",
        errors="raise",
    )

    terpilih = []

    for _, grup in data.groupby(KUNCI_SNAPSHOT, dropna=False, sort=True):
        tanggal_terbaru = grup["_tanggal_snapshot"].max()
        kandidat = grup[grup["_tanggal_snapshot"].eq(tanggal_terbaru)].copy()

        if kandidat["nilai"].nunique(dropna=False) > 1:
            kunci = kandidat[KUNCI_SNAPSHOT].iloc[0].to_dict()
            raise ValueError(
                "Ada nilai berbeda pada snapshot terbaru untuk kunci "
                f"{kunci}, tanggal {tanggal_terbaru.date()}. "
                "Perlu pemeriksaan manual sebelum Gold dibangun."
            )

        kandidat = kandidat.sort_values(
            ["_berkas_raw", "_sha256_raw"],
            na_position="last",
        )

        terpilih.append(kandidat.iloc[[0]])

    hasil = pd.concat(terpilih, ignore_index=True)
    hasil = hasil.drop(columns=["_tanggal_snapshot"])

    audit = {
        "baris_silver": int(len(silver)),
        "baris_terpilih": int(len(hasil)),
        "baris_tidak_terpilih": int(len(silver) - len(hasil)),
    }

    return hasil, audit

# Rincian yang diperbolehkan untuk setiap seri pada keluaran Gold.
RINCIAN_PANEL = {
    ("BPS", "var1373"): "Tidak ada",
    ("BPS", "var1584"): "Tidak ada",
    ("BPS", "var1541"): "Tidak ada",
}

RINCIAN_NASIONAL = {
    ("BPS", "var1373"): "Tidak ada",
    ("WDI", "SH.DYN.MORT"): "Tidak ada",
    ("WHO_GHO", "MDG_0000000007"):
        "AGE=Y_LT5; SEX=TOTAL; WEALTH_QUINTILE=TOTAL",
    ("BPS", "var1584"): "Tidak ada",
    ("WHO_GHO", "WHOSIS_000003"): "AGE=D_LE27; SEX=TOTAL",
    ("WDI", "SH.STA.MMRT"): "Tidak ada",
    ("WHO_GHO", "MDG_0000000026"): "Tidak ada",
    ("BPS", "var1541"): "Tidak ada",
    ("WDI", "SH.STA.BRTC.ZS"): "Tidak ada",
}


def pilih_rincian_gold(data: pd.DataFrame, konteks: str):
    """Pilih rincian yang sah untuk panel atau rekonsiliasi nasional.

    Baris rincian lain tetap berada di Silver, tetapi tidak masuk
    keluaran Gold yang sedang dibangun.
    """
    if konteks == "panel":
        aturan = RINCIAN_PANEL
    elif konteks == "nasional":
        aturan = RINCIAN_NASIONAL
    else:
        raise ValueError(
            "konteks harus 'panel' atau 'nasional'"
        )

    kandidat_mask = pd.Series(False, index=data.index)

    for sumber, seri in aturan:
        kandidat_mask |= (
            data["sumber"].astype(str).eq(sumber)
            & data["seri_kode"].astype(str).eq(seri)
        )

    kandidat = data.loc[kandidat_mask].copy()
    terpilih_mask = pd.Series(False, index=kandidat.index)

    for (sumber, seri), rincian_diizinkan in aturan.items():
        terpilih_mask |= (
            kandidat["sumber"].astype(str).eq(sumber)
            & kandidat["seri_kode"].astype(str).eq(seri)
            & kandidat["rincian"].astype(str).eq(rincian_diizinkan)
        )

    hasil = kandidat.loc[terpilih_mask].copy()

    audit = {
        "konteks": konteks,
        "baris_kandidat": int(len(kandidat)),
        "baris_terpilih": int(len(hasil)),
        "baris_tidak_terpilih": int(len(kandidat) - len(hasil)),
    }

    return hasil, audit

def pilih_periode_gold(data: pd.DataFrame, konteks: str):
    """Pilih periode tahunan untuk keluaran Gold.

    Data semesteran dan bulanan tetap berada di Silver.
    Data tersebut tidak diagregasi otomatis menjadi tahunan.
    """
    if konteks == "panel":
        seri_diizinkan = {
            ("BPS", "var1373"),
            ("BPS", "var1584"),
            ("BPS", "var1541"),
        }
    elif konteks == "nasional":
        seri_diizinkan = set(RINCIAN_NASIONAL)
    else:
        raise ValueError(
            "konteks harus 'panel' atau 'nasional'"
        )

    kandidat_mask = pd.Series(False, index=data.index)

    for sumber, seri in seri_diizinkan:
        kandidat_mask |= (
            data["sumber"].astype(str).eq(sumber)
            & data["seri_kode"].astype(str).eq(seri)
        )

    kandidat = data.loc[kandidat_mask].copy()
    tahunan_mask = kandidat["jenis_periode"].astype(str).eq("tahun")
    hasil = kandidat.loc[tahunan_mask].copy()

    audit = {
        "konteks": konteks,
        "baris_kandidat": int(len(kandidat)),
        "baris_tahunan_terpilih": int(len(hasil)),
        "baris_non_tahunan_tidak_terpilih": int(
            len(kandidat) - len(hasil)
        ),
    }

    return hasil, audit
