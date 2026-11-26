"""Tahap 8 — Validasi Silver dan Gold."""

from pathlib import Path

import pandas as pd

from src.common.manifest import baca
from src.common.skema import periksa_silver


ROOT = Path(__file__).resolve().parents[2]
LAPORAN = ROOT / "reports" / "validasi.md"


def jalankan(silver, gold):
    """Validasi Silver dan tiga tabel Gold."""

    temuan = []

    def cek_kolom(df, kolom, nama):
        kurang = [k for k in kolom if k not in df.columns]
        if kurang:
            temuan.append(f"{nama}: kolom wajib tidak ada: {kurang}")
            return False
        return True

    def cek_tidak_kosong(df, nama):
        if df.empty:
            temuan.append(f"{nama}: tabel kosong")
            return False
        return True

    def cek_kunci(df, kunci, nama):
        if all(k in df.columns for k in kunci):
            jumlah = int(df.duplicated(kunci).sum())
            if jumlah:
                temuan.append(
                    f"{nama}: {jumlah} duplikasi pada kunci {kunci}"
                )

    # 1. Validasi Silver dengan pemeriksa skema starter.
    try:
        manifest = baca()
        hasil_skema = periksa_silver(silver, manifest)
    except Exception as e:
        hasil_skema = [f"Gagal menjalankan pemeriksa skema: {e}"]

    for masalah in hasil_skema:
        temuan.append(f"Silver: {masalah}")

    # 2. Validasi panel provinsi.
    panel = gold["panel_provinsi"]

    kolom_panel = [
        "seri_kode",
        "wilayah_kode",
        "periode",
        "nilai",
        "flag_outlier",
        "flag_patahan",
        "catatan_patahan",
    ]

    if cek_kolom(panel, kolom_panel, "Panel provinsi"):
        cek_tidak_kosong(panel, "Panel provinsi")
        cek_kunci(
            panel,
            ["seri_kode", "periode", "wilayah_kode"],
            "Panel provinsi",
        )

        if panel["flag_outlier"].isna().any():
            temuan.append("Panel provinsi: flag_outlier memiliki nilai kosong")

        if panel["flag_patahan"].isna().any():
            temuan.append("Panel provinsi: flag_patahan memiliki nilai kosong")

        jumlah_outlier = int(panel["flag_outlier"].sum())

        if jumlah_outlier != 3:
            temuan.append(
                "Panel provinsi: jumlah outlier yang ditandai "
                f"{jumlah_outlier}, seharusnya 3 berdasarkan catatan Sprint 1"
            )

    # 3. Validasi tabel nasional long.
    nasional = gold["rekonsiliasi_nasional"]

    kolom_nasional = [
        "sumber",
        "seri_kode",
        "periode",
        "nilai",
        "flag_outlier",
        "flag_patahan",
        "catatan_patahan",
    ]

    if cek_kolom(nasional, kolom_nasional, "Rekonsiliasi nasional"):
        cek_tidak_kosong(nasional, "Rekonsiliasi nasional")
        cek_kunci(
            nasional,
            ["sumber", "seri_kode", "periode"],
            "Rekonsiliasi nasional",
        )

        if nasional["flag_outlier"].isna().any():
            temuan.append(
                "Rekonsiliasi nasional: flag_outlier memiliki nilai kosong"
            )

        if nasional["flag_patahan"].isna().any():
            temuan.append(
                "Rekonsiliasi nasional: flag_patahan memiliki nilai kosong"
            )

    # 4. Validasi tabel nasional wide.
    wide = gold["nasional_periode_x_seri"]

    if cek_kolom(wide, ["periode"], "Nasional wide"):
        cek_tidak_kosong(wide, "Nasional wide")
        cek_kunci(wide, ["periode"], "Nasional wide")

    # 5. Tulis laporan validasi.
    LAPORAN.parent.mkdir(parents=True, exist_ok=True)

    if temuan:
        status = "GAGAL"
    else:
        status = "LOLOS"

    isi = [
        "# Laporan Validasi Silver dan Gold",
        "",
        f"**Status: {status}**",
        "",
        f"- Baris Silver: {len(silver)}",
        f"- Baris panel provinsi: {len(panel)}",
        f"- Baris rekonsiliasi nasional: {len(nasional)}",
        f"- Baris nasional wide: {len(wide)}",
        "",
        "## Pemeriksaan",
        "",
    ]

    if temuan:
        isi.extend(["Pemeriksaan menemukan masalah:", ""])
        isi.extend([f"- {t}" for t in temuan])
    else:
        isi.append("Semua pemeriksaan yang diterapkan berhasil.")

    LAPORAN.write_text(
        "\n".join(isi) + "\n",
        encoding="utf-8",
    )

    print(f"Validasi: {status}")
    print(f"Laporan disimpan: {LAPORAN}")

    if temuan:
        raise ValueError(
            "Validasi menemukan masalah. "
            f"Periksa laporan: {LAPORAN}"
        )

    return {
        "status": status,
        "jumlah_temuan": len(temuan),
    }