import streamlit as st
import os
import sys
import requests
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

# ── Anti-flicker: paksa background gelap sebelum CSS Streamlit dimuat ────────
st.markdown("""
<style>
html, body, [data-testid="stApp"] {
    background-color: #0b0e14 !important;
    transition: none !important;
}
</style>
""", unsafe_allow_html=True)

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

from frontend.assets.styles import MAIN_CSS
from frontend.views.ui_pages import (
    page_dashboard, page_data, page_predict, 
    page_batch, page_history
)
from backend.core.ml_logic import (
    MLEngine, load_from_db, save_to_db, 
    save_prediction_to_db, load_prediction_history
)

# ── Preload Database in Background Thread ────────────────────────────────────
import threading
def preload_db():
    try:
        load_from_db()
        load_prediction_history()
    except Exception:
        pass

if 'db_preloaded' not in st.session_state:
    st.session_state.db_preloaded = True
    threading.Thread(target=preload_db, daemon=True).start()

# ── CONFIG ────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="EduPredict AI", page_icon="🎓", layout="wide")

# ── Helper: ambil config dari st.secrets atau os.environ ─────────────────────
def _cfg(key, default=""):
    try:
        return st.secrets.get(key, os.environ.get(key, default))
    except Exception:
        return os.environ.get(key, default)

# ── Check Database Availability (cached 5 menit agar tidak jalan tiap klik) ──
@st.cache_resource(ttl=300)
def check_db_connection():
    try:
        import psycopg2 as _pg2
        _conn = _pg2.connect(
            host=_cfg("DB_HOST", "localhost"),
            database=_cfg("DB_NAME", "prediksi_do"),
            user=_cfg("DB_USER", "postgres"),
            password=_cfg("DB_PASSWORD", ""),
            port=_cfg("DB_PORT", "5432"),
            sslmode="require",
            connect_timeout=10
        )
        # Buat tabel users_auth jika belum ada
        _cur = _conn.cursor()
        _cur.execute("""
            CREATE TABLE IF NOT EXISTS users_auth (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                pin VARCHAR(6) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        _conn.commit()
        _cur.close()
        _conn.close()
        return True, None
    except Exception as e:
        return False, str(e)

DB_AVAILABLE, DB_ERROR = check_db_connection()

# ── Helper Autentikasi Pengguna & PIN ────────────────────────────────────────
import json

def get_user_pin(email):
    email = email.lower().strip()
    if DB_AVAILABLE:
        try:
            import psycopg2 as _pg2
            _conn = _pg2.connect(
                host=_cfg("DB_HOST", "localhost"),
                database=_cfg("DB_NAME", "prediksi_do"),
                user=_cfg("DB_USER", "postgres"),
                password=_cfg("DB_PASSWORD", ""),
                port=_cfg("DB_PORT", "5432"),
                sslmode="require",
                connect_timeout=10
            )
            _cur = _conn.cursor()
            _cur.execute("SELECT pin FROM users_auth WHERE email = %s", (email,))
            row = _cur.fetchone()
            _cur.close()
            _conn.close()
            if row:
                return row[0]
        except Exception:
            pass

    # Fallback ke penyimpanan offline lokal jika DB tidak tersedia
    offline_file = "backend/data/users_offline.json"
    if os.path.exists(offline_file):
        try:
            with open(offline_file, "r") as f:
                users = json.load(f)
                return users.get(email)
        except Exception:
            pass
    return None

def save_user_pin(email, pin):
    email = email.lower().strip()
    pin = pin.strip()
    saved = False
    if DB_AVAILABLE:
        try:
            import psycopg2 as _pg2
            _conn = _pg2.connect(
                host=_cfg("DB_HOST", "localhost"),
                database=_cfg("DB_NAME", "prediksi_do"),
                user=_cfg("DB_USER", "postgres"),
                password=_cfg("DB_PASSWORD", ""),
                port=_cfg("DB_PORT", "5432"),
                sslmode="require",
                connect_timeout=10
            )
            _cur = _conn.cursor()
            _cur.execute("""
                INSERT INTO users_auth (email, pin)
                VALUES (%s, %s)
                ON CONFLICT (email) DO UPDATE SET pin = EXCLUDED.pin
            """, (email, pin))
            _conn.commit()
            _cur.close()
            _conn.close()
            saved = True
        except Exception:
            pass

    # Selalu simpan salinan cadangan di lokal / jika DB gagal
    offline_file = "backend/data/users_offline.json"
    os.makedirs(os.path.dirname(offline_file), exist_ok=True)
    users = {}
    if os.path.exists(offline_file):
        try:
            with open(offline_file, "r") as f:
                users = json.load(f)
        except Exception:
            pass
    users[email] = pin
    try:
        with open(offline_file, "w") as f:
            json.dump(users, f, indent=4)
        saved = True
    except Exception:
        pass
    return saved

# ── ML ENGINE ─────────────────────────────────────────────────────────────────
@st.cache_resource
def get_engine():
    return MLEngine()

# ── SESSION STATE ─────────────────────────────────────────────────────────────
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'active_page' not in st.session_state: st.session_state.active_page = "Dashboard"
if 'user_email' not in st.session_state: st.session_state.user_email = None

MENU_ITEMS = [
    ("📊","Dashboard"),
    ("📋","Data & Pelatihan"),
    ("🧠","Prediksi Individu"),
    ("📂","Prediksi Batch"),
    ("📜","Riwayat Prediksi"),
]

# ── LOGIN PAGE ────────────────────────────────────────────────────────────────
if not st.session_state.logged_in:
    _, col_c, _ = st.columns([1, 1.8, 1])
    with col_c:
        st.markdown("<div style='height:8vh'></div>", unsafe_allow_html=True)
        
        with st.container(border=True):
            st.markdown("""
            <div style="text-align: center; margin-bottom: 2rem;">
                <div style="font-size: 3.5rem; margin-bottom: 0.5rem;">🎓</div>
                <h2 style="margin: 0 0 0.5rem 0; color: white; font-weight: 800; font-family: sans-serif;">EduPredict AI</h2>
                <p style="color: #94a3b8; font-size: 0.95rem; margin: 0;">Sistem Prediksi Risiko Drop Out Mahasiswa</p>
            </div>
            """, unsafe_allow_html=True)
            
            # --- Kredensial Google OAuth Asli ---
            CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "").strip()
            CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()
            REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8501/").strip()            
            # State Management
            if 'oauth_email' not in st.session_state:
                st.session_state.oauth_email = None

            query_params = st.query_params
            
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
                    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
                    token_res = requests.post(token_url, data=data, headers=headers, verify=False, timeout=30)
                    token_json = token_res.json()
                    if "access_token" in token_json:
                        access_token = token_json["access_token"]
                        user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
                        headers = {"Authorization": f"Bearer {access_token}"}
                        user_res = requests.get(user_info_url, headers=headers, verify=False, timeout=30)
                        user_json = user_res.json()
                        
                        if "email" in user_json:
                            user_email = user_json["email"]
                            # Perbolehkan semua email login
                            st.session_state.oauth_email = user_email
                    else:
                        st.error(f"Gagal mendapatkan akses dari Google. Detail: {token_json}")
                except Exception as e:
                    st.error(f"Terjadi kesalahan koneksi OAuth: {e}")
                
                st.query_params.clear()

            if not st.session_state.oauth_email:
                auth_url = (
                    "https://accounts.google.com/o/oauth2/v2/auth?"
                    f"client_id={CLIENT_ID}&"
                    f"redirect_uri={urllib.parse.quote(REDIRECT_URI)}&"
                    "response_type=code&"
                    "scope=openid%20email%20profile&"
                    "prompt=select_account"
                )
                
                st.markdown(f"""
                <div style="display:flex; justify-content:center; margin-top: 1.5rem; margin-bottom: 0.5rem;">
                    <a href="{auth_url}" target="_blank" style="
                        display: inline-flex;
                        align-items: center;
                        justify-content: center;
                        background-color: #ffffff;
                        color: #1f2937;
                        font-weight: 600;
                        padding: 12px 24px;
                        border-radius: 8px;
                        text-decoration: none;
                        width: 100%;
                        max-width: 280px;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                        border: 1px solid #e2e8f0;
                        font-family: sans-serif;
                    ">
                        <img src="https://www.svgrepo.com/show/475656/google-color.svg" width="20" height="20" style="margin-right:10px;">
                        Lanjutkan dengan Google
                    </a>
                </div>
                <div style="text-align:center; margin-bottom: 1.5rem;">
                    <code style="color: #64748b; font-size: 0.75rem; background: rgba(255,255,255,0.05); padding: 2px 6px; border-radius: 4px;">Redirect URI: {REDIRECT_URI}</code>
                </div>
                """, unsafe_allow_html=True)
                
            else:
                email = st.session_state.oauth_email
                saved_pin = get_user_pin(email)
                
                if saved_pin is None:
                    # User belum punya PIN, arahkan buat PIN baru
                    st.markdown(f"<p style='text-align:center; color:#94a3b8; font-size:0.9rem; margin-bottom: 0.5rem;'>Masuk sebagai: <b>{email}</b></p>", unsafe_allow_html=True)
                    st.markdown("<h4 style='text-align:center; color:white; margin-top: 0.5rem; margin-bottom: 1rem;'>Buat PIN Baru</h4>", unsafe_allow_html=True)
                    st.markdown("<p style='text-align:center; color:#94a3b8; font-size:0.8rem; margin-bottom: 1rem;'>Silakan buat PIN 6 digit angka untuk login berikutnya.</p>", unsafe_allow_html=True)
                    
                    new_pin = st.text_input("PIN Baru (6 Digit)", type="password", placeholder="••••••", max_chars=6)
                    confirm_pin = st.text_input("Konfirmasi PIN Baru (6 Digit)", type="password", placeholder="••••••", max_chars=6)
                    
                    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        btn_batal = st.button("⬅ Batal", use_container_width=True)
                    with col_btn2:
                        btn_simpan = st.button("💾 Simpan & Masuk", use_container_width=True)
                        
                    if btn_batal:
                        st.session_state.oauth_email = None
                        st.rerun()
                        
                    if btn_simpan:
                        if not new_pin or len(new_pin) != 6 or not new_pin.isdigit():
                            st.error("❌ PIN harus berupa 6 digit angka!")
                        elif new_pin != confirm_pin:
                            st.error("❌ Konfirmasi PIN tidak cocok!")
                        else:
                            if save_user_pin(email, new_pin):
                                st.session_state.logged_in = True
                                st.session_state.user_email = email
                                st.session_state.oauth_email = None
                                st.success("✅ PIN berhasil disimpan!")
                                st.rerun()
                            else:
                                st.error("❌ Gagal menyimpan PIN! Silakan coba lagi.")
                else:
                    # User sudah punya PIN, tampilkan input PIN
                    st.markdown(f"<p style='text-align:center; color:#94a3b8; font-size:0.9rem; margin-bottom: 0.5rem;'>Masuk sebagai: <b>{email}</b></p>", unsafe_allow_html=True)
                    st.markdown("<h4 style='text-align:center; color:white; margin-top: 0.5rem; margin-bottom: 1rem;'>Masukkan PIN</h4>", unsafe_allow_html=True)
                    
                    input_pin = st.text_input("PIN 6 Digit", type="password", placeholder="••••••", max_chars=6, label_visibility="collapsed")
                    
                    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        btn_batal = st.button("⬅ Batal", use_container_width=True)
                    with col_btn2:
                        btn_buka = st.button("🔓 Buka Kunci", use_container_width=True)
                    
                    if btn_batal:
                        st.session_state.oauth_email = None
                        st.rerun()
                    
                    if btn_buka or (input_pin and len(input_pin) == 6):
                        if input_pin == saved_pin:
                            st.session_state.logged_in = True
                            st.session_state.user_email = email
                            st.session_state.oauth_email = None
                            st.rerun()
                        else:
                            st.error("❌ PIN Salah!")
                                
        st.markdown("<p style='text-align:center;color:#475569;font-size:0.75rem;margin-top:2rem'>© 2026 EduPredict AI • v2.0</p>", unsafe_allow_html=True)

# ── MAIN APP WITH SIDEBAR ─────────────────────────────────────────────────────
else:
    st.markdown(MAIN_CSS, unsafe_allow_html=True)
    engine = get_engine()

    # 👑 PINDAH KE POJOK KANAN ATAS (Floating Badge)
    user_display = st.session_state.get('user_email', 'Admin')
    st.markdown(f"""<div class='admin-badge'>
        <span>👤</span> Pengguna: <b>{user_display}</b>
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
                # Tidak perlu st.rerun() eksplisit — Streamlit auto-rerun setelah state change
            
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
