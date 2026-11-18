from pathlib import Path

import pandas as pd


INPUT = Path("data/silver/raw_gabungan.parquet")
OUTPUT = Path("reports/ketersediaan-pembanding.md")

PEMBANDING = {
    "SH.DYN.MORT": "WDI - Angka kematian balita",
    "SH.STA.BRTC.ZS": "WDI - Persalinan dibantu tenaga kesehatan terampil",
    "SH.STA.MMRT": "WDI - Rasio kematian ibu",
    "MDG_0000000007": "WHO - Angka kematian balita",
    "MDG_0000000026": "WHO - Rasio kematian ibu",
    "WHOSIS_000003": "WHO - Angka kematian neonatal",
}

UTAMA = {
    "1373": "BPS var1373 (kematian balita)",
    "1584": "BPS var1584 (kematian bayi)",
    "1541": "BPS var1541 (persalinan di fasilitas kesehatan, kelompok 40% pengeluaran terbawah)",
}


def tahun_tersedia(data):
    return set(data["tahun"].dropna().astype(int).tolist())


def jalankan():
    if not INPUT.exists():
        raise FileNotFoundError(f"Data tidak ditemukan: {INPUT}")

    df = pd.read_parquet(INPUT)

    wajib = {
        "sumber", "kode_indikator", "nama_indikator",
        "wilayah", "tahun", "nilai", "berkas_raw",
        "nilai_bawah", "nilai_atas",
    }
    kurang = wajib - set(df.columns)
    if kurang:
        raise ValueError(f"Kolom wajib tidak ditemukan: {sorted(kurang)}")

    pembanding = df[df["kode_indikator"].isin(PEMBANDING)].copy()
    utama = df[df["kode_indikator"].isin(UTAMA)].copy()

    if pembanding.empty:
        raise ValueError("Tidak ditemukan data seri pembanding.")

    baris = [
        "# Ketersediaan Seri Pembanding",
        "",
        "## Tujuan",
        "",
        "Profil ini merangkum ketersediaan enam seri pembanding nasional, "
        "periode, wilayah, nilai, dan irisan tahun dengan seri utama BPS.",
        "",
        "## Ringkasan enam seri pembanding",
        "",
        "| Sumber | Kode | Indikator | Baris | Nilai tersedia | Wilayah | Tahun awal | Tahun akhir |",
        "|---|---|---|---:|---:|---|---:|---:|",
    ]

    ringkasan = []

    for kode, nama in PEMBANDING.items():
        x = pembanding[pembanding["kode_indikator"] == kode].copy()
        if x.empty:
            continue

        tahun = x["tahun"].dropna().astype(int)
        wilayah = sorted(x["wilayah"].dropna().astype(str).unique())
        ringkasan.append({
            "kode": kode,
            "sumber": x["sumber"].iloc[0],
            "baris": len(x),
            "nilai": int(x["nilai"].count()),
            "wilayah": wilayah,
            "tahun": set(tahun.tolist()),
            "awal": int(tahun.min()) if not tahun.empty else None,
            "akhir": int(tahun.max()) if not tahun.empty else None,
        })

        nama_asli = str(x["nama_indikator"].dropna().iloc[0])
        baris.append(
            f"| {x['sumber'].iloc[0]} | {kode} | {nama_asli} "
            f"| {len(x)} | {x['nilai'].count()} "
            f"| {', '.join(wilayah)} "
            f"| {tahun.min()} | {tahun.max()} |"
        )

    baris += [
        "",
        "## Irisan periode dengan seri utama BPS",
        "",
        "Irisan tahun menunjukkan tahun yang tersedia pada kedua seri. "
        "Irisan periode saja tidak membuktikan bahwa definisi atau metode "
        "pengukuran kedua indikator sama.",
        "",
        "| Seri pembanding | Seri utama | Tahun yang sama | Jumlah tahun |",
        "|---|---|---|---:|",
    ]

    for item in ringkasan:
        for kode_utama, nama_utama in UTAMA.items():
            y = utama[utama["kode_indikator"] == kode_utama]
            irisan = sorted(item["tahun"] & tahun_tersedia(y))
            baris.append(
                f"| {item['kode']} | {nama_utama} "
                f"| {', '.join(map(str, irisan)) if irisan else '-'} "
                f"| {len(irisan)} |"
            )

    baris += [
        "",
        "## Ketersediaan nilai dan dimensi data",
        "",
        "| Kode | Baris | Nilai tersedia | Nilai kosong | Batas bawah tersedia | Batas atas tersedia |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    for item in ringkasan:
        x = pembanding[pembanding["kode_indikator"] == item["kode"]]
        baris.append(
            f"| {item['kode']} | {len(x)} | {x['nilai'].count()} "
            f"| {x['nilai'].isna().sum()} "
            f"| {x['nilai_bawah'].count()} | {x['nilai_atas'].count()} |"
        )

    baris += [
        "",
        "Dimensi yang tersedia pada berkas gabungan ini adalah sumber, "
        "kode dan nama indikator, wilayah, tahun, nilai, berkas sumber, "
        "hash sumber, serta batas bawah dan batas atas jika tersedia. "
        "Kolom rincian tidak tersedia pada skema ekstraksi ini, sehingga "
        "tidak boleh disimpulkan bahwa seluruh dimensi rincian sumber "
        "asli sudah diperiksa.",
        "",
        "## Catatan interpretasi",
        "",
        "- WDI dan WHO merupakan pembanding nasional untuk konteks dan "
        "rekonsiliasi, bukan pengganti otomatis data BPS.",
        "- WDI SH.DYN.MORT dan WHO MDG_0000000007 sama-sama mengukur "
        "kematian balita, tetapi sumber dan metodologinya dapat berbeda.",
        "- WHO WHOSIS_000003 mengukur kematian neonatal, bukan kematian "
        "bayi atau balita secara keseluruhan.",
        "- WDI SH.STA.BRTC.ZS mengukur persalinan dengan tenaga kesehatan "
        "terampil. Ini tidak identik dengan BPS var1541 yang mengukur "
        "persalinan di fasilitas kesehatan pada kelompok pengeluaran "
        "40 persen terbawah.",
        "- WDI SH.STA.MMRT dan WHO MDG_0000000026 mengukur rasio kematian "
        "ibu. Keduanya menjadi konteks kesehatan ibu, bukan ukuran "
        "yang sama dengan var1541.",
        "- Perbedaan nilai antar-sumber tidak otomatis merupakan kesalahan. "
        "Periksa definisi, satuan, periode, dan metode pengumpulan sebelum "
        "menarik kesimpulan.",
        "",
        "## Kesimpulan",
        "",
        f"Profil menemukan {len(ringkasan)} dari 6 seri pembanding yang "
        "diharapkan. Rincian periode dan irisan tahun ditampilkan di atas. "
        "Perbandingan substantif perlu mempertimbangkan kesesuaian definisi "
        "dan metode masing-masing indikator.",
        "",
    ]

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(baris), encoding="utf-8")

    print("Profil pembanding berhasil dibuat.")
    print(f"Laporan: {OUTPUT.resolve()}")
    print("\nRingkasan:")
    for item in ringkasan:
        print(
            f"{item['kode']}: {item['baris']} baris, "
            f"{item['nilai']} nilai tersedia, "
            f"{item['awal']}-{item['akhir']}"
        )


if __name__ == "__main__":
    jalankan()
