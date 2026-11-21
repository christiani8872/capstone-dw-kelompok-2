
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "data" / "silver" / "raw_gabungan.parquet"
REPORT_DIR = ROOT / "reports"
IMAGE_DIR = REPORT_DIR / "gambar"

INDIKATOR_UTAMA = ["1373", "1584", "1541"]


def main():
    # 1. Memeriksa file dan folder
    if not INPUT.exists():
        raise FileNotFoundError(f"Data tidak ditemukan: {INPUT}")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    # 2. Membaca data Silver
    df = pd.read_parquet(INPUT)

    kolom_wajib = [
        "kode_indikator",
        "wilayah",
        "tahun",
        "nilai",
        "berkas_raw"
    ]

    for kolom in kolom_wajib:
        if kolom not in df.columns:
            raise ValueError(
                f"Kolom wajib tidak ditemukan: {kolom}"
            )

    df["kode_indikator"] = (
        df["kode_indikator"].astype(str)
    )
    df["tahun"] = pd.to_numeric(
        df["tahun"], errors="coerce"
    )
    df["nilai"] = pd.to_numeric(
        df["nilai"], errors="coerce"
    )

    utama = df[
        df["kode_indikator"].isin(INDIKATOR_UTAMA)
    ].copy()

    utama = utama.dropna(
        subset=["wilayah", "tahun", "nilai"]
    )

    if utama.empty:
        raise ValueError(
            "Tidak ditemukan data untuk ketiga indikator utama."
        )

    # 3. Statistik deskriptif per seri
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
        .reindex(INDIKATOR_UTAMA)
        .reset_index()
    )

    # 4. Statistik deskriptif per provinsi dan seri
    profil_provinsi = (
        utama.groupby(
            ["kode_indikator", "wilayah"]
        )
        .agg(
            jumlah_data=("nilai", "count"),
            tahun_awal=("tahun", "min"),
            tahun_akhir=("tahun", "max"),
            minimum=("nilai", "min"),
            maksimum=("nilai", "max"),
            rata_rata=("nilai", "mean"),
            standar_deviasi=("nilai", "std")
        )
        .reset_index()
        .sort_values(
            ["kode_indikator", "wilayah"]
        )
    )

    # 5. Deteksi kandidat anomali menggunakan IQR
    daftar_anomali = []
    batas_iqr = {}

    for kode in INDIKATOR_UTAMA:
        data_seri = utama[
            utama["kode_indikator"] == kode
        ].copy()

        if data_seri.empty:
            continue

        q1 = data_seri["nilai"].quantile(0.25)
        q3 = data_seri["nilai"].quantile(0.75)
        iqr = q3 - q1

        batas_bawah = q1 - (1.5 * iqr)
        batas_atas = q3 + (1.5 * iqr)

        batas_iqr[kode] = {
            "q1": q1,
            "q3": q3,
            "iqr": iqr,
            "batas_bawah": batas_bawah,
            "batas_atas": batas_atas
        }

        kandidat = data_seri[
            (data_seri["nilai"] < batas_bawah)
            | (data_seri["nilai"] > batas_atas)
        ].copy()

        kandidat["q1"] = q1
        kandidat["q3"] = q3
        kandidat["iqr"] = iqr
        kandidat["batas_bawah"] = batas_bawah
        kandidat["batas_atas"] = batas_atas

        kandidat["alasan"] = kandidat["nilai"].apply(
            lambda nilai:
                (
                    f"Nilai {nilai:.2f} di bawah batas bawah "
                    f"IQR ({batas_bawah:.2f})"
                )
                if nilai < batas_bawah
                else (
                    f"Nilai {nilai:.2f} di atas batas atas "
                    f"IQR ({batas_atas:.2f})"
                )
        )

        daftar_anomali.append(kandidat)

    kolom_anomali = [
        "kode_indikator",
        "wilayah",
        "tahun",
        "nilai",
        "q1",
        "q3",
        "iqr",
        "batas_bawah",
        "batas_atas",
        "alasan"
    ]

    if daftar_anomali:
        anomali = pd.concat(
            daftar_anomali,
            ignore_index=True
        )

        anomali = anomali[kolom_anomali].sort_values(
            ["kode_indikator", "wilayah", "tahun"]
        )
    else:
        anomali = pd.DataFrame(
            columns=kolom_anomali
        )

    # 6. Perubahan tahunan var1541
    persalinan = utama[
        utama["kode_indikator"] == "1541"
    ].sort_values(
        ["wilayah", "tahun"]
    ).copy()

    persalinan["perubahan"] = (
        persalinan.groupby("wilayah")["nilai"].diff()
    )

    persalinan["perubahan_absolut"] = (
        persalinan["perubahan"].abs()
    )

    kandidat_perubahan = (
        persalinan.dropna(subset=["perubahan"])
        .sort_values(
            "perubahan_absolut",
            ascending=False
        )
        .head(5)
        .copy()
    )

    # 7. Pemeriksaan hubungan kematian balita dan bayi
    kematian = utama[
        utama["kode_indikator"].isin(["1373", "1584"])
    ]

    perbandingan = kematian.pivot_table(
        index=["wilayah", "tahun"],
        columns="kode_indikator",
        values="nilai",
        aggfunc="first"
    ).reset_index()

    if (
        "1373" in perbandingan.columns
        and "1584" in perbandingan.columns
    ):
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

    # 8. Boxplot ketiga seri
    fig, ax = plt.subplots(figsize=(9, 6))

    data_boxplot = [
        utama.loc[
            utama["kode_indikator"] == kode,
            "nilai"
        ].dropna()
        for kode in INDIKATOR_UTAMA
    ]

    ax.boxplot(
        data_boxplot,
        tick_labels=INDIKATOR_UTAMA
    )

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

    # 9. Grafik deret waktu masing-masing seri
    nama_file_grafik = {}

    for kode in INDIKATOR_UTAMA:
        data_seri = utama[
            utama["kode_indikator"] == kode
        ].copy()

        fig, ax = plt.subplots(figsize=(12, 7))

        for wilayah, data_wilayah in data_seri.groupby(
            "wilayah"
        ):
            data_wilayah = data_wilayah.sort_values(
                "tahun"
            )

            ax.plot(
                data_wilayah["tahun"],
                data_wilayah["nilai"],
                marker="o",
                linewidth=1,
                alpha=0.55
            )

        # Menandai kandidat anomali pada grafik
        kandidat_seri = anomali[
            anomali["kode_indikator"] == kode
        ]

        if not kandidat_seri.empty:
            ax.scatter(
                kandidat_seri["tahun"],
                kandidat_seri["nilai"],
                marker="x",
                s=80,
                label="Kandidat anomali IQR",
                zorder=5
            )
            ax.legend()

        ax.set_title(
            f"Deret Waktu {kode} pada Seluruh Wilayah"
        )
        ax.set_xlabel("Tahun")
        ax.set_ylabel("Nilai")
        ax.grid(True, alpha=0.3)

        fig.tight_layout()

        nama_gambar = f"deret-waktu-var{kode}.png"
        fig.savefig(
            IMAGE_DIR / nama_gambar,
            dpi=150
        )
        plt.close(fig)

        nama_file_grafik[kode] = nama_gambar

    # 10. Grafik lima perubahan terbesar var1541
    fig, ax = plt.subplots(figsize=(10, 6))

    for wilayah in kandidat_perubahan["wilayah"].unique():
        data_wilayah = persalinan[
            persalinan["wilayah"] == wilayah
        ].sort_values("tahun")

        ax.plot(
            data_wilayah["tahun"],
            data_wilayah["nilai"],
            marker="o",
            label=wilayah
        )

    ax.set_title(
        "Perkembangan var1541 pada Lima Kandidat Perubahan Terbesar"
    )
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

    # 11. Menyimpan tabel hasil ke reports
    profil.to_csv(
        REPORT_DIR / "profil-per-seri.csv",
        index=False
    )

    profil_provinsi.to_csv(
        REPORT_DIR / "profil-per-provinsi.csv",
        index=False
    )

    anomali.to_csv(
        REPORT_DIR / "kandidat-anomali-iqr.csv",
        index=False
    )

    # 12. Membuat laporan Markdown
    laporan = [
        "# Profil Seri Utama",
        "",
        "## 1. Tujuan",
        "Analisis dilakukan terhadap var1373, var1584, "
        "dan var1541 untuk melihat profil statistik, "
        "distribusi, perkembangan waktu, dan kandidat anomali.",
        "",
        "## 2. Ringkasan statistik per seri",
        "```text",
        profil.round(2).to_string(index=False),
        "```",
        "",
        "Tabel lengkap: `profil-per-seri.csv`.",
        "",
        "## 3. Statistik per provinsi",
        "Statistik dihitung untuk setiap kombinasi seri dan wilayah.",
        "Kolom meliputi jumlah data, periode, minimum, maksimum, "
        "rata-rata, dan standar deviasi.",
        "",
        "Tabel lengkap: `profil-per-provinsi.csv`.",
        "",
        "## 4. Metode deteksi kandidat anomali",
        "Deteksi menggunakan metode Interquartile Range (IQR).",
        "",
        "- IQR = Q3 - Q1",
        "- Batas bawah = Q1 - 1.5 x IQR",
        "- Batas atas = Q3 + 1.5 x IQR",
        "",
        "Perhitungan dilakukan secara terpisah untuk setiap seri "
        "dengan menggunakan seluruh observasi pada seri tersebut.",
        "Nilai di bawah batas bawah atau di atas batas atas "
        "ditandai sebagai kandidat anomali.",
        "",
        "Kandidat bukan bukti kesalahan data. Pemeriksaan lanjutan "
        "terhadap wilayah, periode, metadata, dan sumber data tetap diperlukan.",
        "",
        "## 5. Batas IQR setiap seri",
        "```text",
    ]

    for kode, batas in batas_iqr.items():
        laporan.append(
            f"{kode}: Q1={batas['q1']:.2f}, "
            f"Q3={batas['q3']:.2f}, "
            f"IQR={batas['iqr']:.2f}, "
            f"batas bawah={batas['batas_bawah']:.2f}, "
            f"batas atas={batas['batas_atas']:.2f}"
        )

    laporan.extend([
        "```",
        "",
        "## 6. Daftar kandidat anomali",
        f"Jumlah kandidat anomali: {len(anomali)}.",
        "",
        "```text",
        (
            anomali[
                [
                    "kode_indikator",
                    "wilayah",
                    "tahun",
                    "nilai",
                    "alasan"
                ]
            ].round(2).to_string(index=False)
            if not anomali.empty
            else "Tidak ditemukan kandidat anomali berdasarkan batas IQR."
        ),
        "```",
        "",
        "Tabel lengkap: `kandidat-anomali-iqr.csv`.",
        "",
        "## 7. Lima perubahan tahunan terbesar var1541",
        "```text",
        kandidat_perubahan[
            [
                "wilayah",
                "tahun",
                "nilai",
                "perubahan",
                "perubahan_absolut"
            ]
        ].round(2).to_string(index=False),
        "```",
        "",
        "Daftar ini merupakan pemeriksaan perubahan tahunan, "
        "bukan hasil deteksi anomali IQR.",
        "",
        "## 8. Pemeriksaan hubungan kematian balita dan bayi",
        f"Jumlah pasangan wilayah-tahun yang dapat dibandingkan: {len(pasangan)}.",
        f"Jumlah pelanggaran var1373 < var1584: {len(pelanggaran)}.",
        "",
        "```text",
        (
            "Tidak ditemukan pelanggaran."
            if len(pelanggaran) == 0
            else pelanggaran.to_string(index=False)
        ),
        "```",
        "",
        "## 9. Visualisasi",
        "- `gambar/distribusi-seri-utama.png`",
        "- `gambar/perubahan-kandidat-var1541.png`",
    ])

    for kode, nama_gambar in nama_file_grafik.items():
        laporan.append(f"- `gambar/{nama_gambar}`")

    laporan.extend([
        "",
        "## 10. Catatan dan keterbatasan",
        "IQR pada analisis ini membandingkan distribusi seluruh "
        "observasi dalam masing-masing seri. Karena data mencakup "
        "beberapa wilayah dan tahun, nilai ekstrem perlu diperiksa "
        "lebih lanjut dalam konteks wilayah dan periode.",
        "",
        "Tidak ada nilai yang dihapus atau diperbaiki dalam proses "
        "deteksi. Data Silver dan data raw tidak diubah oleh analisis ini."
    ])

    (REPORT_DIR / "profil-seri-utama.md").write_text(
        "\n".join(laporan),
        encoding="utf-8"
    )

    # 13. Menampilkan ringkasan hasil
    print("Profiling berhasil dijalankan.")

    print(f"\nLaporan: {REPORT_DIR / 'profil-seri-utama.md'}")
    print(f"Folder grafik: {IMAGE_DIR}")

    print("\nStatistik per seri:")
    print(profil.round(2).to_string(index=False))

    print("\nJumlah statistik per provinsi:")
    print(len(profil_provinsi))

    print("\nJumlah kandidat anomali:")
    print(
        anomali.groupby("kode_indikator")
        .size()
        .reindex(INDIKATOR_UTAMA, fill_value=0)
        .to_string()
    )

    print("\nDaftar kandidat anomali:")
    if anomali.empty:
        print("Tidak ditemukan kandidat anomali.")
    else:
        print(
            anomali[
                [
                    "kode_indikator",
                    "wilayah",
                    "tahun",
                    "nilai",
                    "alasan"
                ]
            ].round(2).to_string(index=False)
        )

    print(
        f"\nJumlah pelanggaran aturan: {len(pelanggaran)}"
    )


if __name__ == "__main__":
    main()
