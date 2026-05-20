"""
Script untuk setup tabel dan import data CSV ke Neon PostgreSQL Cloud.
Jalankan sekali saja dari terminal:
    python setup_neon.py
"""
import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

# ── Baca kredensial dari .env ─────────────────────────────────────────────────
DB_HOST     = os.getenv("DB_HOST")
DB_NAME     = os.getenv("DB_NAME")
DB_USER     = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT     = os.getenv("DB_PORT", "5432")
CSV_PATH    = "backend/data/data_mahasiswa_v2.csv"

def get_conn():
    return psycopg2.connect(
        host=DB_HOST, database=DB_NAME, user=DB_USER,
        password=DB_PASSWORD, port=DB_PORT, sslmode="require"
    )

def create_tables():
    print("📋 Membuat tabel di Neon...")
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS mahasiswa (
            id                SERIAL PRIMARY KEY,
            nim               VARCHAR(20) UNIQUE,
            angkatan          INTEGER NOT NULL,
            semester          INTEGER NOT NULL,
            ipk               FLOAT NOT NULL,
            sks_lulus         INTEGER NOT NULL,
            mengulang         INTEGER NOT NULL DEFAULT 0,
            absensi           FLOAT NOT NULL DEFAULT 0,
            status_pembayaran INTEGER NOT NULL DEFAULT 1,
            status_do         INTEGER NOT NULL DEFAULT 0,
            created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS hasil_prediksi (
            id                SERIAL PRIMARY KEY,
            nim               VARCHAR(20),
            angkatan          INTEGER,
            semester          INTEGER,
            ipk               FLOAT,
            sks_lulus         INTEGER,
            mengulang         INTEGER,
            absensi           FLOAT,
            status_pembayaran INTEGER,
            risiko_persen     FLOAT NOT NULL,
            status_risiko     VARCHAR(20) NOT NULL,
            model_ai          VARCHAR(30) NOT NULL,
            tipe_prediksi     VARCHAR(20) DEFAULT 'individu',
            tanggal_prediksi  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Tabel berhasil dibuat!")

def import_data():
    if not os.path.exists(CSV_PATH):
        print(f"❌ File CSV tidak ditemukan: {CSV_PATH}")
        return

    print(f"📂 Membaca CSV: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH, sep=None, engine='python')
    print(f"   Total baris: {len(df):,}")

    conn = get_conn()
    cur = conn.cursor()

    # Cek data yang sudah ada
    cur.execute("SELECT COUNT(*) FROM mahasiswa")
    existing = cur.fetchone()[0]
    if existing > 0:
        print(f"⚠️  Tabel sudah ada {existing:,} data.")
        jawab = input("   Hapus dan import ulang? (y/n): ").strip().lower()
        if jawab != 'y':
            print("⏭️  Import dibatalkan.")
            cur.close(); conn.close()
            return
        cur.execute("TRUNCATE TABLE mahasiswa RESTART IDENTITY")
        conn.commit()
        print("🗑️  Data lama dihapus.")

    # Import baris per baris
    print("📤 Mengimpor data ke Neon...")
    ok = 0
    for _, row in df.iterrows():
        try:
            cur.execute("""
                INSERT INTO mahasiswa
                    (nim, angkatan, semester, ipk, sks_lulus,
                     mengulang, absensi, status_pembayaran, status_do)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
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
            ok += 1
        except Exception as e:
            print(f"   ⚠️ Baris {ok}: {e}")

    conn.commit()
    cur.close(); conn.close()
    print(f"✅ Berhasil import {ok:,} data ke Neon!")

def verify():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*), COUNT(CASE WHEN status_do=1 THEN 1 END), AVG(ipk) FROM mahasiswa")
    total, do, ipk = cur.fetchone()
    print(f"\n{'='*45}")
    print(f"  ✅ VERIFIKASI DATA DI NEON")
    print(f"{'='*45}")
    print(f"  Total Mahasiswa : {total:,}")
    print(f"  Potensi DO      : {do:,}")
    print(f"  Aman            : {total - do:,}")
    print(f"  Rata-rata IPK   : {ipk:.2f}")
    print(f"{'='*45}\n")
    cur.close(); conn.close()

if __name__ == "__main__":
    print("\n🚀 EduPredict AI — Setup Database Neon\n")
    try:
        print(f"🔗 Koneksi ke: {DB_HOST}")
        create_tables()
        import_data()
        verify()
        print("🎉 Selesai! Data sudah masuk ke Neon.\n")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("   Pastikan file .env sudah berisi kredensial Neon yang benar.\n")
