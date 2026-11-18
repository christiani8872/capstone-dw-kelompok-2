from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "data" / "silver" / "raw_gabungan.parquet"
REPORT_DIR = ROOT / "reports"
IMAGE_DIR = REPORT_DIR / "gambar"

INDIKATOR_UTAMA = ["1373", "1584", "1541"]

def main():
    if not INPUT.exists():
        raise FileNotFoundError(f"Data tidak ditemukan: {INPUT}")

    df = pd.read_parquet(INPUT)

    kolom_wajib = [
        "kode_indikator", "wilayah", "tahun",
        "nilai", "berkas_raw"
    ]

    for kolom in kolom_wajib:
        if kolom not in df.columns:
            raise ValueError(f"Kolom wajib tidak ditemukan: {kolom}")

    df["kode_indikator"] = df["kode_indikator"].astype(str)
    df["tahun"] = pd.to_numeric(df["tahun"], errors="coerce")
    df["nilai"] = pd.to_numeric(df["nilai"], errors="coerce")

    utama = df[df["kode_indikator"].isin(INDIKATOR_UTAMA)].copy()
    utama = utama.dropna(subset=["wilayah", "tahun", "nilai"])

    # 1. Profil statistik setiap seri
    profil = (
        utama.groupby("kode_indikator")
        .agg(
            jumlah_data=("nilai", "count"),
            jumlah_wilayah=("wilayah", "nunique"),
            tahun_awal=("tahun", "min"),
            tahun_akhir=("tahun", "max"),
            minimum=("nilai", "min"),
            maksimum=("nilai", "max"),
            rata_rata=("nilai", "mean"),
            standar_deviasi=("nilai", "std")
        )
        .reset_index()
    )

    # 2. Perubahan tahunan untuk var1541
    persalinan = utama[
        utama["kode_indikator"] == "1541"
    ].sort_values(["wilayah", "tahun"]).copy()

    persalinan["perubahan"] = (
        persalinan.groupby("wilayah")["nilai"].diff()
    )
    persalinan["perubahan_absolut"] = (
        persalinan["perubahan"].abs()
    )

    kandidat = (
        persalinan.dropna(subset=["perubahan"])
        .sort_values("perubahan_absolut", ascending=False)
        .head(5)
        .copy()
    )

    # 3. Pemeriksaan hubungan kematian balita dan bayi
    kematian = utama[
        utama["kode_indikator"].isin(["1373", "1584"])
    ]

    perbandingan = kematian.pivot_table(
        index=["wilayah", "tahun"],
        columns="kode_indikator",
        values="nilai",
        aggfunc="first"
    ).reset_index()

    if "1373" in perbandingan.columns and "1584" in perbandingan.columns:
        pasangan = perbandingan.dropna(
            subset=["1373", "1584"]
        ).copy()

        pasangan["selisih"] = (
            pasangan["1373"] - pasangan["1584"]
        )

        pelanggaran = pasangan[
            pasangan["1373"] < pasangan["1584"]
        ]
    else:
        pasangan = pd.DataFrame()
        pelanggaran = pd.DataFrame()

    # 4. Grafik perubahan lima kandidat var1541
    fig, ax = plt.subplots(figsize=(10, 6))

    for wilayah in kandidat["wilayah"].unique():
        data_wilayah = persalinan[
            persalinan["wilayah"] == wilayah
        ].sort_values("tahun")

        ax.plot(
            data_wilayah["tahun"],
            data_wilayah["nilai"],
            marker="o",
            label=wilayah
        )

    ax.set_title("Perkembangan var1541 pada Lima Kandidat")
    ax.set_xlabel("Tahun")
    ax.set_ylabel("Nilai")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(
        IMAGE_DIR / "perubahan-kandidat-var1541.png",
        dpi=150
    )
    plt.close(fig)

    # 5. Grafik distribusi ketiga seri utama
    fig, ax = plt.subplots(figsize=(9, 6))

    data_boxplot = [
        utama.loc[
            utama["kode_indikator"] == kode, "nilai"
        ].dropna()
        for kode in INDIKATOR_UTAMA
    ]

    ax.boxplot(data_boxplot, tick_labels=INDIKATOR_UTAMA)
    ax.set_title("Distribusi Nilai Tiga Seri Utama")
    ax.set_xlabel("Kode indikator")
    ax.set_ylabel("Nilai")
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(
        IMAGE_DIR / "distribusi-seri-utama.png",
        dpi=150
    )
    plt.close(fig)

    # 6. Membuat laporan Markdown
    laporan = [
        "# Profil Seri Utama",
        "",
        "## Tujuan",
        "Profil statistik dan pemeriksaan awal dilakukan pada "
        "var1373, var1584, dan var1541.",
        "",
        "## Ringkasan statistik",
        "```text",
        profil.round(2).to_string(index=False),
        "```",
        "",
        "## Lima kandidat perubahan terbesar var1541",
        "```text",
        kandidat[
            ["wilayah", "tahun", "nilai", "perubahan",
             "perubahan_absolut"]
        ].round(2).to_string(index=False),
        "```",
        "",
        "Kandidat di atas merupakan perubahan yang perlu ditinjau, "
        "bukan kesalahan data yang sudah terbukti.",
        "",
        "## Pemeriksaan hubungan kematian balita dan bayi",
        f"Jumlah pasangan wilayah-tahun yang dapat dibandingkan: {len(pasangan)}",
        f"Jumlah pelanggaran var1373 < var1584: {len(pelanggaran)}",
        "",
        "```text",
        (
            "Tidak ditemukan pelanggaran."
            if len(pelanggaran) == 0
            else pelanggaran.to_string(index=False)
        ),
        "```",
        "",
        "## Visualisasi",
        "- `gambar/distribusi-seri-utama.png`",
        "- `gambar/perubahan-kandidat-var1541.png`",
        "",
        "## Catatan",
        "Nilai ekstrem dan perubahan besar tidak otomatis merupakan "
        "kesalahan. Pemeriksaan lanjutan terhadap metadata dan sumber "
        "data tetap diperlukan."
    ]

    (REPORT_DIR / "profil-seri-utama.md").write_text(
        "\n".join(laporan),
        encoding="utf-8"
    )

    print("Profiling berhasil dijalankan.")
    print(f"Laporan: {REPORT_DIR / 'profil-seri-utama.md'}")
    print(f"Gambar: {IMAGE_DIR}")
    print("\nRingkasan statistik:")
    print(profil.round(2).to_string(index=False))
    print("\nLima kandidat perubahan terbesar:")
    print(kandidat[
        ["wilayah", "tahun", "nilai", "perubahan"]
    ].round(2).to_string(index=False))
    print(f"\nPelanggaran aturan: {len(pelanggaran)}")

if __name__ == "__main__":
    main()

