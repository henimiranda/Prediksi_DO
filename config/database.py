"""
Konfigurasi koneksi database PostgreSQL untuk EduPredict AI.
Menggunakan SQLAlchemy engine + psycopg2 sebagai driver.
"""
from sqlalchemy import create_engine
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables from .env file (jika ada, untuk lokal)
load_dotenv()

# Nama tabel utama di PostgreSQL
TABLE_NAME = "mahasiswa"


def _get_config(key, default_val):
    """Baca konfigurasi: coba st.secrets (Cloud) lalu os.getenv (Lokal)."""
    try:
        import streamlit as st
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key, default_val)


def get_connection():
    """Mengembalikan koneksi psycopg2 langsung (untuk operasi manual)."""
    conn = psycopg2.connect(
        host=_get_config("DB_HOST", "localhost"),
        database=_get_config("DB_NAME", "prediksi_do"),
        user=_get_config("DB_USER", "postgres"),
        password=_get_config("DB_PASSWORD", "12345"),
        port=_get_config("DB_PORT", "5432"),
        sslmode="require"  # Wajib untuk koneksi Neon
    )
    return conn


def get_engine():
    """Mengembalikan SQLAlchemy engine (untuk pandas read_sql / to_sql)."""
    host     = _get_config("DB_HOST", "localhost")
    database = _get_config("DB_NAME", "prediksi_do")
    user     = _get_config("DB_USER", "postgres")
    password = _get_config("DB_PASSWORD", "12345")
    port     = _get_config("DB_PORT", "5432")
    url = (
        f"postgresql+psycopg2://{user}:{password}"
        f"@{host}:{port}/{database}?sslmode=require"
    )
    return create_engine(url)