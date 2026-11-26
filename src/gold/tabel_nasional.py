import pandas as pd
from pathlib import Path

def buat_tabel_nasional():
    print("=== MEMBUAT TABEL NASIONAL (GOLD) ===")
    
    # 1. Baca data mentah hasil ekstraksi (gabungan)
    file_raw = Path("data/silver/raw_gabungan.parquet")
    if not file_raw.exists():
        print("⚠️ File raw_gabungan.parquet tidak ditemukan. Jalankan ekstraksi dulu.")
        return
        
    df = pd.read_parquet(file_raw)
    
    # 2. Daftar indikator yang diminta di Kartu #27
    seri_utama = ['1373', '1584', '1541']
    seri_pembanding = [
        'MDG_0000000007', 'MDG_0000000026', 'WHOSIS_000003',
        'SH.DYN.MORT', 'SH.STA.MMRT', 'SH.STA.BRTC.ZS'
    ]
    semua_seri = seri_utama + seri_pembanding
    
    # Filter hanya seri yang dibutuhkan
    df = df[df['kode_indikator'].isin(semua_seri)]
    
    hasil_nasional = []
    
    # 3. Proses per seri indikator
    for seri in semua_seri:
        df_seri = df[df['kode_indikator'] == seri]
        
        if df_seri.empty:
            continue
            
        # Kelompokkan berdasarkan tahun
        for tahun, group in df_seri.groupby('tahun'):
            # Cek apakah ada baris yang wilayahnya 'Indonesia' (seperti dari WDI/WHO)
            baris_indonesia = group[group['wilayah'].str.contains('Indonesia', case=False, na=False)]
            
            if not baris_indonesia.empty:
                # Jika sudah ada data Indonesia, pakai itu
                nilai_nasional = baris_indonesia['nilai'].iloc[0]
                asal_angka = "Baris Indonesia (BPS/WDI/WHO)"
                berkas_asal = baris_indonesia['_berkas_raw'].iloc[0]
            else:
                # Jika tidak ada (berarti ini data BPS per provinsi), lakukan agregasi
                # Asumsi: Rata-rata sederhana dari seluruh provinsi
                nilai_nasional = group['nilai'].mean()
                asal_angka = f"Agregat {len(group)} Provinsi (Rata-rata Sederhana)"
                berkas_asal = ", ".join(group['_berkas_raw'].unique())
            
            hasil_nasional.append({
                "tahun": int(tahun) if str(tahun).isdigit() else tahun,
                "seri": seri,
                "tipe_seri": "Utama" if seri in seri_utama else "Pembanding",
                "nilai_nasional": float(nilai_nasional) if pd.notna(nilai_nasional) else None,
                "asal_angka": asal_angka,
                "_berkas_raw": berkas_asal
            })
            
    df_gold = pd.DataFrame(hasil_nasional)
    
    # Urutkan berdasarkan tahun dan seri
    df_gold = df_gold.sort_values(by=['tahun', 'seri']).reset_index(drop=True)
    
    # --- SESUAIKAN DENGAN KESEPAKATAN TIM ---
    output_path = Path("data/gold/nasional.parquet")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_gold.to_parquet(output_path, index=False)
    
    print(f" Berhasil membuat Tabel Nasional. Total baris: {len(df_gold)}")
    print(f"Data disimpan ke: {output_path}")
    print("\n Sampel Tabel Nasional:")
    print(df_gold.head(10).to_string())
    
    return str(output_path)

if __name__ == "__main__":
    buat_tabel_nasional()