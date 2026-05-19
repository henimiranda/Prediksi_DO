"""
Konfigurasi koneksi database PostgreSQL untuk EduPredict AI.
Menggunakan SQLAlchemy engine + psycopg2 sebagai driver.
"""
from sqlalchemy import create_engine
import psycopg2

import os
from dotenv import load_dotenv
import streamlit as st

# Load environment variables from .env file (if it exists)
load_dotenv()

def get_config(key, default_val):
    # Coba baca dari Streamlit Secrets (untuk Cloud)
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    # Jika gagal/tidak ada, baca dari os.getenv (untuk Lokal)
    return os.getenv(key, default_val)

# ── Konfigurasi Database ──────────────────────────────────────────────────────
DB_CONFIG = {
    "host":     get_config("DB_HOST", "localhost"),
    "database": get_config("DB_NAME", "prediksi_do"),
    "user":     get_config("DB_USER", "postgres"),
    "password": get_config("DB_PASSWORD", "12345"),
    "port":     get_config("DB_PORT", "5432"),
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