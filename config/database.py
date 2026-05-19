"""
Konfigurasi koneksi database PostgreSQL untuk EduPredict AI.
Menggunakan SQLAlchemy engine + psycopg2 sebagai driver.
Membaca konfigurasi secara LAZY (di dalam fungsi) agar os.environ
yang sudah diisi dari st.secrets di main.py dapat terbaca.
"""
import os
import psycopg2
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

# Nama tabel utama di PostgreSQL
TABLE_NAME = "mahasiswa"


def _get(key, default=""):
    """Baca dari st.secrets (Cloud) → os.environ (Lokal) → default."""
    try:
        import streamlit as st
        val = st.secrets.get(key, None)
        if val is not None:
            return str(val)
    except Exception:
        pass
    return os.environ.get(key, default)


def get_connection():
    """Mengembalikan koneksi psycopg2 langsung (untuk operasi manual)."""
    return psycopg2.connect(
        host=_get("DB_HOST", "localhost"),
        database=_get("DB_NAME", "prediksi_do"),
        user=_get("DB_USER", "postgres"),
        password=_get("DB_PASSWORD", ""),
        port=_get("DB_PORT", "5432"),
        sslmode="require",
        connect_timeout=10
    )


def get_engine():
    """Mengembalikan SQLAlchemy engine (untuk pandas read_sql / to_sql)."""
    url = (
        f"postgresql+psycopg2://{_get('DB_USER', 'postgres')}:{_get('DB_PASSWORD', '')}"
        f"@{_get('DB_HOST', 'localhost')}:{_get('DB_PORT', '5432')}"
        f"/{_get('DB_NAME', 'prediksi_do')}?sslmode=require"
    )
    return create_engine(url)