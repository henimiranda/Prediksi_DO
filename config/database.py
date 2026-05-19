"""
Konfigurasi koneksi database PostgreSQL untuk EduPredict AI.
Menggunakan SQLAlchemy engine + psycopg2 sebagai driver.
"""
from sqlalchemy import create_engine
import psycopg2

import os
from dotenv import load_dotenv

# Load environment variables from .env file (if it exists)
load_dotenv()

# ── Konfigurasi Database ──────────────────────────────────────────────────────
DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "prediksi_do"),
    "user":     os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "12345"),
    "port":     os.getenv("DB_PORT", "5432"),
}

# Nama tabel utama di PostgreSQL
TABLE_NAME = "mahasiswa"


def get_connection():
    """Mengembalikan koneksi psycopg2 langsung (untuk operasi manual)."""
    conn = psycopg2.connect(
        host=DB_CONFIG["host"],
        database=DB_CONFIG["database"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        port=DB_CONFIG["port"],
        sslmode="require"  # Wajib untuk koneksi Neon
    )
    return conn


def get_engine():
    """Mengembalikan SQLAlchemy engine (untuk pandas read_sql / to_sql)."""
    url = (
        f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?sslmode=require"
    )
    return create_engine(url)