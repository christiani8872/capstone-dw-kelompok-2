-- ============================================================================
-- DDL Tabel Gold - Kasus 02 (Kematian Anak dan Ibu)
-- Basis Data Target : DuckDB (data/gold/capstone.duckdb)
-- ============================================================================

CREATE TABLE IF NOT EXISTS panel_provinsi (
    seri_kode            VARCHAR NOT NULL,
    periode              VARCHAR NOT NULL,
    wilayah_kode         VARCHAR NOT NULL,
    nama_wilayah         VARCHAR NOT NULL,
    nilai                DOUBLE,
    satuan               VARCHAR,
    _berkas_raw          VARCHAR,
    _sha256_raw          VARCHAR,
    flag_outlier         BOOLEAN NOT NULL,
    flag_patahan         BOOLEAN NOT NULL,
    catatan_patahan      VARCHAR,
    status_ketersediaan  VARCHAR NOT NULL,

    PRIMARY KEY (seri_kode, periode, wilayah_kode)
);

CREATE TABLE IF NOT EXISTS tabel_nasional (
    kelompok_rekonsiliasi  VARCHAR NOT NULL,
    peran_seri             VARCHAR NOT NULL,
    sumber                 VARCHAR NOT NULL,
    seri_kode              VARCHAR NOT NULL,
    ukuran                 VARCHAR NOT NULL,
    wilayah_kode           INTEGER NOT NULL,
    nama_wilayah           VARCHAR NOT NULL,
    periode                VARCHAR NOT NULL,
    nilai                  DOUBLE  NOT NULL,
    satuan                 VARCHAR NOT NULL,
    satuan_baku            VARCHAR NOT NULL,
    rincian                VARCHAR NOT NULL,
    flag_outlier           BOOLEAN NOT NULL,
    flag_patahan           BOOLEAN NOT NULL,
    catatan_patahan        VARCHAR NOT NULL,
    _berkas_raw            VARCHAR NOT NULL,
    _sha256_raw            VARCHAR NOT NULL,

    PRIMARY KEY (sumber, seri_kode, periode)
);

CREATE TABLE IF NOT EXISTS rekonsiliasi (
    kode_pasangan        VARCHAR NOT NULL,
    periode              VARCHAR NOT NULL,
    seri_utama           VARCHAR NOT NULL,
    sumber_utama         VARCHAR NOT NULL,
    nilai_utama          DOUBLE,
    satuan_utama         VARCHAR NOT NULL,
    seri_pembanding      VARCHAR NOT NULL,
    sumber_pembanding    VARCHAR NOT NULL,
    nilai_pembanding     DOUBLE,
    satuan_pembanding    VARCHAR NOT NULL,
    selisih              DOUBLE,
    status_pasangan      VARCHAR NOT NULL CHECK (status_pasangan IN ('berpasangan', 'hanya_utama', 'hanya_pembanding')),
    kategori_penjelasan  VARCHAR CHECK (
        kategori_penjelasan IS NULL OR kategori_penjelasan IN (
            'definisi berbeda',
            'metode berbeda',
            'vintage berbeda',
            'cakupan berbeda',
            'belum terjelaskan'
        )
    ),
    catatan_penjelasan   VARCHAR NOT NULL,

    PRIMARY KEY (kode_pasangan, periode)
);