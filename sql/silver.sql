-- ============================================================================
-- DDL Tabel Silver - Kasus 02 (Kematian Anak dan Ibu)
-- Basis Data Target : DuckDB
-- Mengacu pada kontrak skema baku: src/common/skema.py
-- ============================================================================

CREATE TABLE IF NOT EXISTS silver (
    sumber        VARCHAR NOT NULL,
    seri_kode     VARCHAR NOT NULL,
    wilayah_kode  INTEGER NOT NULL, -- 9999 = Nasional (Indonesia), Provinsi = kode BPS x 100
    nama_wilayah  VARCHAR NOT NULL,
    periode       VARCHAR NOT NULL,
    jenis_periode VARCHAR NOT NULL CHECK (jenis_periode IN ('tahun', 'semester', 'triwulan', 'bulan')),
    rincian       VARCHAR NOT NULL,
    nilai         DOUBLE  NOT NULL, -- Silver hanya memuat observasi valid yang memiliki nilai
    satuan        VARCHAR NOT NULL,
    _berkas_raw   VARCHAR NOT NULL,
    _sha256_raw   VARCHAR NOT NULL,

    -- Kunci primer komposit sesuai KUNCI di src/common/skema.py
    PRIMARY KEY (sumber, seri_kode, wilayah_kode, periode, rincian, _berkas_raw)
);
