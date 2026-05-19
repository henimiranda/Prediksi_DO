"""
Setup Database PostgreSQL untuk EduPredict AI.
Script ini akan:
  1. Membuat database 'prediksi_do' jika belum ada
  2. Membuat tabel 'mahasiswa' dengan skema yang sesuai
  3. Import data dari CSV ke PostgreSQL

Jalankan: python setup_database.py
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import pandas as pd
import os
import sys

# ── Konfigurasi ──────────────────────────────────────────────────────────────
DB_HOST     = "localhost"
DB_PORT     = "5432"
DB_USER     = "postgres"
DB_PASSWORD = "12345"       # Ganti sesuai password PostgreSQL kamu
DB_NAME     = "prediksi_do"
TABLE_NAME  = "mahasiswa"
CSV_PATH    = "backend/data/data_mahasiswa_v2.csv"


def create_database():
    """Membuat database 'prediksi_do' jika belum ada."""
    print("[*] Mengecek apakah database sudah ada...")
    try:
        conn = psycopg2.connect(
            host=DB_HOST, port=DB_PORT,
            user=DB_USER, password=DB_PASSWORD,
            database="postgres"  # Koneksi ke default database dulu
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        # Cek apakah database sudah ada
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
        exists = cur.fetchone()

        if not exists:
            cur.execute(f'CREATE DATABASE "{DB_NAME}"')
            print(f"[+] Database '{DB_NAME}' berhasil dibuat!")
        else:
            print(f"[✓] Database '{DB_NAME}' sudah ada.")

        cur.close()
        conn.close()
    except psycopg2.OperationalError as e:
        print(f"\n[!] GAGAL KONEKSI ke PostgreSQL!")
        print(f"    Error: {e}")
        print(f"\n    Pastikan:")
        print(f"    1. PostgreSQL sudah berjalan di {DB_HOST}:{DB_PORT}")
        print(f"    2. User '{DB_USER}' dan password '{DB_PASSWORD}' sudah benar")
        print(f"    3. Bisa diubah di file config/database.py")
        sys.exit(1)


def create_table():
    """Membuat tabel 'mahasiswa' di PostgreSQL."""
    print(f"[*] Membuat tabel '{TABLE_NAME}'...")
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT,
        user=DB_USER, password=DB_PASSWORD,
        database=DB_NAME
    )
    cur = conn.cursor()

    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id              SERIAL PRIMARY KEY,
            nim             VARCHAR(20) UNIQUE,
            angkatan        INTEGER NOT NULL,
            semester         INTEGER NOT NULL,
            ipk             FLOAT NOT NULL,
            sks_lulus       INTEGER NOT NULL,
            mengulang       INTEGER NOT NULL DEFAULT 0,
            absensi         FLOAT NOT NULL DEFAULT 0,
            status_pembayaran INTEGER NOT NULL DEFAULT 1,
            status_do       INTEGER NOT NULL DEFAULT 0,
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Tabel untuk menyimpan riwayat prediksi
    cur.execute("""
        CREATE TABLE IF NOT EXISTS hasil_prediksi (
            id              SERIAL PRIMARY KEY,
            nim             VARCHAR(20),
            angkatan        INTEGER,
            semester         INTEGER,
            ipk             FLOAT,
            sks_lulus       INTEGER,
            mengulang       INTEGER,
            absensi         FLOAT,
            status_pembayaran INTEGER,
            risiko_persen   FLOAT NOT NULL,
            status_risiko   VARCHAR(20) NOT NULL,
            model_ai        VARCHAR(30) NOT NULL,
            tipe_prediksi   VARCHAR(20) DEFAULT 'individu',
            tanggal_prediksi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    print(f"[+] Tabel '{TABLE_NAME}' berhasil dibuat!")
    print(f"[+] Tabel 'hasil_prediksi' berhasil dibuat!")

    cur.close()
    conn.close()


def import_csv_to_db():
    """Import data dari CSV ke tabel PostgreSQL."""
    if not os.path.exists(CSV_PATH):
        print(f"[!] File CSV tidak ditemukan: {CSV_PATH}")
        return

    print(f"[*] Membaca data dari {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH)
    print(f"    Total baris di CSV: {len(df):,}")

    # Koneksi ke database
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT,
        user=DB_USER, password=DB_PASSWORD,
        database=DB_NAME
    )
    cur = conn.cursor()

    # Cek apakah data sudah ada
    cur.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
    count = cur.fetchone()[0]

    if count > 0:
        print(f"[!] Tabel sudah berisi {count:,} data.")
        jawab = input("    Hapus data lama dan import ulang? (y/n): ").strip().lower()
        if jawab != 'y':
            print("[*] Import dibatalkan.")
            cur.close()
            conn.close()
            return
        cur.execute(f"TRUNCATE TABLE {TABLE_NAME} RESTART IDENTITY")
        conn.commit()
        print("[*] Data lama berhasil dihapus.")

    # Insert data baris per baris
    print("[*] Mengimpor data ke PostgreSQL...")
    inserted = 0
    for _, row in df.iterrows():
        try:
            cur.execute(f"""
                INSERT INTO {TABLE_NAME} (nim, angkatan, semester, ipk, sks_lulus,
                                          mengulang, absensi, status_pembayaran, status_do)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (nim) DO NOTHING
            """, (
                str(row.get('NIM', '')),
                int(row.get('Angkatan', 0)),
                int(row.get('Semester', 0)),
                float(row.get('IPK', 0)),
                int(row.get('SKS_Lulus', 0)),
                int(row.get('Mengulang', 0)),
                float(row.get('Absensi', 0)),
                int(row.get('Status_Pembayaran', 1)),
                int(row.get('Status_DO', 0)),
            ))
            inserted += 1
        except Exception as e:
            print(f"    [!] Error baris {inserted}: {e}")

    conn.commit()
    cur.close()
    conn.close()
    print(f"[+] Berhasil mengimpor {inserted:,} data ke tabel '{TABLE_NAME}'!")


def verify_data():
    """Verifikasi data yang sudah diimpor."""
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT,
        user=DB_USER, password=DB_PASSWORD,
        database=DB_NAME
    )
    cur = conn.cursor()

    cur.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
    total = cur.fetchone()[0]

    cur.execute(f"SELECT COUNT(*) FROM {TABLE_NAME} WHERE status_do = 1")
    total_do = cur.fetchone()[0]

    cur.execute(f"SELECT AVG(ipk) FROM {TABLE_NAME}")
    avg_ipk = cur.fetchone()[0]

    print("\n" + "=" * 50)
    print("  VERIFIKASI DATA DI POSTGRESQL")
    print("=" * 50)
    print(f"  Total Mahasiswa : {total:,}")
    print(f"  Total DO        : {total_do:,}")
    print(f"  Total Aman      : {total - total_do:,}")
    print(f"  Rata-rata IPK   : {avg_ipk:.2f}")
    print("=" * 50)

    # Tampilkan 5 data pertama
    cur.execute(f"SELECT nim, angkatan, semester, ipk, status_do FROM {TABLE_NAME} LIMIT 5")
    rows = cur.fetchall()
    print("\n  5 Data Pertama:")
    print(f"  {'NIM':<12} {'Angkatan':<10} {'Semester':<10} {'IPK':<8} {'Status DO'}")
    print("  " + "-" * 52)
    for r in rows:
        print(f"  {r[0]:<12} {r[1]:<10} {r[2]:<10} {r[3]:<8.2f} {r[4]}")

    cur.close()
    conn.close()
    print("\n[✓] Setup database selesai! Sekarang jalankan: streamlit run app.py\n")


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  EDUPREDICT AI - SETUP DATABASE POSTGRESQL")
    print("=" * 50 + "\n")

    create_database()
    create_table()
    import_csv_to_db()
    verify_data()
