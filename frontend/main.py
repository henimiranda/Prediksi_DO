import streamlit as st
import os
import sys
import requests
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

# ── Inject Streamlit Secrets ke os.environ (untuk Streamlit Cloud) ────────────
# Ini memastikan config.database bisa membaca variabel via os.getenv()
try:
    for _k, _v in st.secrets.items():
        if _k not in os.environ:
            os.environ[_k] = str(_v)
except Exception:
    pass  # Tidak apa-apa jika berjalan di lokal tanpa secrets

# Add root directory to sys.path to allow imports from backend and config
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from frontend.assets.styles import LOGIN_CSS, MAIN_CSS
from frontend.views.ui_pages import (
    page_dashboard, page_data, page_predict, 
    page_batch, page_history
)
from backend.core.ml_logic import (
    MLEngine, load_from_db, save_to_db, 
    save_prediction_to_db, load_prediction_history
)

# ── CONFIG ────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="EduPredict AI", page_icon="🎓", layout="wide")

# ── Helper: ambil config dari st.secrets atau os.environ ─────────────────────
def _cfg(key, default=""):
    try:
        return st.secrets.get(key, os.environ.get(key, default))
    except Exception:
        return os.environ.get(key, default)

# ── Check Database Availability (langsung pakai psycopg2, bypass database.py) ─
DB_ERROR = None
DB_HOST_USED = _cfg("DB_HOST", "localhost")
try:
    import psycopg2 as _pg2
    _conn = _pg2.connect(
        host=DB_HOST_USED,
        database=_cfg("DB_NAME", "prediksi_do"),
        user=_cfg("DB_USER", "postgres"),
        password=_cfg("DB_PASSWORD", ""),
        port=_cfg("DB_PORT", "5432"),
        sslmode="require",
        connect_timeout=10
    )
    DB_AVAILABLE = True
    _conn.close()
except Exception as e:
    DB_AVAILABLE = False
    DB_ERROR = str(e)

# ── ML ENGINE ─────────────────────────────────────────────────────────────────
@st.cache_resource
def get_engine():
    return MLEngine()

# ── SESSION STATE ─────────────────────────────────────────────────────────────
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'active_page' not in st.session_state: st.session_state.active_page = "Dashboard"

MENU_ITEMS = [
    ("📊","Dashboard"),
    ("📋","Data & Pelatihan"),
    ("🧠","Prediksi Individu"),
    ("📂","Prediksi Batch"),
    ("📜","Riwayat Prediksi"),
]

# ── LOGIN PAGE ────────────────────────────────────────────────────────────────
if not st.session_state.logged_in:
    st.markdown(LOGIN_CSS, unsafe_allow_html=True)
    st.markdown("""<div class='login-bg'>
        <div class='orb orb-1'></div><div class='orb orb-2'></div><div class='orb orb-3'></div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <style>
    /* Ubah kolom tengah menjadi sebuah 'Card' atau kotak besar */
    div[data-testid="stHorizontalBlock"]:first-of-type > div[data-testid="column"]:nth-child(2) {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 1.5rem;
        padding: 3rem 2rem;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)

    _, col_c, _ = st.columns([1, 1.5, 1])
    with col_c:
        st.markdown("<div style='height:2vh'></div>", unsafe_allow_html=True)
        
        # --- Konfigurasi Admin ---
        ALLOWED_EMAIL = "henimiranda9@gmail.com" # Ganti dengan Email Google Asli Anda
        CORRECT_PIN = "123456" # Ganti dengan PIN 6 digit pilihan Anda
        
        # --- Kredensial Google OAuth Asli ---
        CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
        CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
        REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8501/") 
        
        # State Management
        if 'oauth_email' not in st.session_state:
            st.session_state.oauth_email = None

        query_params = st.query_params
        
        # Jika ada parameter 'code' dari Google, tukarkan dengan token (Real Flow)
        if "code" in query_params and not st.session_state.oauth_email:
            auth_code = query_params["code"]
            token_url = "https://oauth2.googleapis.com/token"
            data = {
                "code": auth_code,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "redirect_uri": REDIRECT_URI,
                "grant_type": "authorization_code"
            }
            try:
                # 1. Dapatkan Token
                headers = {'Content-Type': 'application/x-www-form-urlencoded'}
                token_res = requests.post(token_url, data=data, headers=headers, verify=False, timeout=30)
                token_json = token_res.json()
                if "access_token" in token_json:
                    access_token = token_json["access_token"]
                    # 2. Ambil Info User
                    user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
                    headers = {"Authorization": f"Bearer {access_token}"}
                    user_res = requests.get(user_info_url, headers=headers, verify=False, timeout=30)
                    user_json = user_res.json()
                    
                    if "email" in user_json:
                        user_email = user_json["email"]
                        if user_email.lower() == ALLOWED_EMAIL.lower():
                            st.session_state.oauth_email = user_email
                        else:
                            st.error(f"❌ Email '{user_email}' tidak terdaftar sebagai Administrator!")
                else:
                    st.error(f"Gagal mendapatkan akses dari Google. Detail: {token_json}")
            except Exception as e:
                st.error(f"Terjadi kesalahan koneksi OAuth: {e}")
            
            # Bersihkan URL parameter
            st.query_params.clear()

        # Render Konten Card (Logo & Judul)
        st.markdown(f"""
        <div style="text-align: center;">
            <div class="login-logo">🎓</div>
            <h1 class="login-title">EduPredict AI</h1>
            <p class="login-subtitle">Sistem Prediksi Risiko Drop Out Mahasiswa</p>
        </div>
        """, unsafe_allow_html=True)

        if not st.session_state.oauth_email:
            # Buat URL Otorisasi Asli
            auth_url = (
                "https://accounts.google.com/o/oauth2/v2/auth?"
                f"client_id={CLIENT_ID}&"
                f"redirect_uri={urllib.parse.quote(REDIRECT_URI)}&"
                "response_type=code&"
                "scope=openid%20email%20profile&"
                "prompt=select_account"
            )
            
            # Tombol Login Google
            st.markdown(f"""
            <div style="display:flex; justify-content:center; margin-top: 2rem;">
                <a href="{auth_url}" target="_blank" class="google-btn">
                    <img src="https://www.svgrepo.com/show/475656/google-color.svg" width="20" height="20" style="margin-right:10px;">
                    Lanjutkan dengan Google
                </a>
            </div>
            """, unsafe_allow_html=True)
            
        else:
            # PIN Mode UI
            st.markdown(f"<p style='text-align:center; color:#94a3b8; font-size:0.9rem; margin-top:-1.5rem;'>Masuk sebagai: <b>{st.session_state.oauth_email}</b></p>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align:center; color:white; letter-spacing: 2px; margin-top: 1rem; margin-bottom:1rem;'>Masukkan PIN</h3>", unsafe_allow_html=True)
            
            _, pin_col, _ = st.columns([1, 4, 1])
            with pin_col:
                input_pin = st.text_input("PIN 6 Digit", type="password", placeholder="••••••", max_chars=6, label_visibility="collapsed")
                
                st.markdown("<br>", unsafe_allow_html=True)
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("⬅ Batal", use_container_width=True):
                        st.session_state.oauth_email = None
                        st.rerun()
                with col_btn2:
                    if st.button("🔓 Buka Kunci", use_container_width=True):
                        if input_pin == CORRECT_PIN:
                            st.session_state.logged_in = True
                            st.rerun()
                        else:
                            st.error("❌ PIN Salah!")
                            
    st.markdown("<p style='text-align:center;color:#475569;font-size:0.75rem;margin-top:2rem'>© 2026 EduPredict AI • v2.0</p>", unsafe_allow_html=True)

# ── MAIN APP WITH SIDEBAR ─────────────────────────────────────────────────────
else:
    st.markdown(MAIN_CSS, unsafe_allow_html=True)
    engine = get_engine()

    # 👑 PINDAH KE POJOK KANAN ATAS (Floating Badge)
    st.markdown("""<div class='admin-badge'>
        <span>👤</span> Administrator: <b>Admin</b>
    </div>""", unsafe_allow_html=True)

    with st.sidebar:
        # Sidebar Brand
        st.markdown("""<div class='sidebar-brand'>
            <span class='icon'>🎓</span>
            <h1>EduPredict<br>AI</h1>
            <p>Predictive Analytics System</p>
        </div>""", unsafe_allow_html=True)

        # Navigasi
        st.markdown("<div class='nav-container'>", unsafe_allow_html=True)
        for icon, label in MENU_ITEMS:
            is_active = st.session_state.active_page == label
            if is_active:
                st.markdown("<div class='active-nav'>", unsafe_allow_html=True)
            
            if st.button(f"{icon}  {label}", key=f"nav_{label}", use_container_width=True):
                st.session_state.active_page = label
                st.rerun()
            
            if is_active:
                st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # 🟢 KEMBALI KE BAWAH: Logout & PostgreSQL
        st.markdown("<div style='position: fixed; bottom: 10px; width: 280px; padding: 1rem;'>", unsafe_allow_html=True)
        st.markdown("---")
        if st.button("🚪 Logout", key="btn_logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
        
        if DB_AVAILABLE: st.success("🐘 PostgreSQL Connected")
        else: st.warning("📄 CSV Mode (Offline)")
        st.markdown("</div>", unsafe_allow_html=True)

    # ── PAGE ROUTING ──────────────────────────────────────────────────────────
    pg = st.session_state.active_page
    if pg == "Dashboard":
        page_dashboard(load_from_db, DB_AVAILABLE)
    elif pg == "Data & Pelatihan":
        page_data(engine, load_from_db, save_to_db, DB_AVAILABLE)
    elif pg == "Prediksi Individu":
        page_predict(engine, save_prediction_to_db)
    elif pg == "Prediksi Batch":
        page_batch(engine, save_prediction_to_db)
    elif pg == "Riwayat Prediksi":
        page_history(load_prediction_history, DB_AVAILABLE)
