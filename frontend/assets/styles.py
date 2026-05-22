"""
CSS Styles untuk EduPredict AI — Midnight Premium (Stable Version)
"""

LOGIN_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Space+Grotesk:wght@300;500;700&display=swap');

.stApp {
    background: radial-gradient(circle at 50% 50%, #111827 0%, #030712 100%) !important;
    font-family: 'Outfit', sans-serif;
}
[data-testid="stHeader"], #MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; }

/* Custom Login Card Styling */
.login-card {
    background: rgba(15, 23, 42, 0.45);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 1.5rem;
    padding: 1.5rem 2rem;
    text-align: center;
    box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.5), 0 0 35px rgba(99, 102, 241, 0.12);
    margin: 0 auto;
    max-width: 420px;
}
.login-logo {
    font-size: 2.8rem;
    margin-bottom: 0.4rem;
    filter: drop-shadow(0 0 10px rgba(99, 102, 241, 0.4));
    animation: float_logo 3s infinite ease-in-out;
}
@keyframes float_logo {
    0%, 100% { transform: translateY(0) scale(1); }
    50% { transform: translateY(-5px) scale(1.02); }
}
.login-title {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 800;
    font-size: 2rem;
    background: linear-gradient(135deg, #ffffff 0%, #a5b4fc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 0.2rem 0;
    letter-spacing: -0.5px;
}
.login-subtitle {
    color: #94a3b8;
    font-size: 0.85rem;
    margin-bottom: 1.5rem;
}
</style>
"""

MAIN_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Space+Grotesk:wght@300;500;700&display=swap');

/* ── Global Setup ── */
.stApp {
    background: radial-gradient(circle at 10% 20%, #0f172a 0%, #020617 90%) !important;
    font-family: 'Outfit', sans-serif;
}

/* Sembunyikan elemen sampah di Header tapi biarkan tombol Sidebar tetap ada */
[data-testid="stHeader"] {
    visibility: visible !important;
    background: rgba(0,0,0,0) !important;
}
/* Pastikan kontrol pembuka sidebar terlihat */
div[data-testid="collapsedSidebarControl"] {
    visibility: visible !important;
    display: flex !important;
}
/* Sembunyikan tombol Deploy dan MainMenu secara spesifik tanpa mengganggu tombol sidebar */
div[data-testid="stConnectionStatus"],
button[data-testid="stHeaderDeployButton"],
.stDeployButton,
#MainMenu,
footer {
    display: none !important;
    visibility: hidden !important;
}

/* Sembunyikan hanya tombol CLOSE (panah lipat) di dalam sidebar */
[data-testid="stSidebar"] button[data-testid="stSidebarCollapseButton"] {
    display: none !important;
}

/* Jika sidebar tertutup (karena localStorage browser), tampilkan tombol buka dengan aksen warna mencolok */
button[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedSidebarControl"] button {
    background-color: #4f46e5 !important;
    color: white !important;
    border: 1px solid #818cf8 !important;
    box-shadow: 0 4px 15px rgba(79,70,229,0.4) !important;
    display: inline-flex !important;
    visibility: visible !important;
    z-index: 999999 !important;
}

/* 👑 Admin Badge Top Right */
.admin-badge {
    position: fixed;
    top: 1rem;
    right: 1.5rem;
    z-index: 999999;
    background: rgba(15, 23, 42, 0.6);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.08);
    padding: 0.5rem 1.2rem;
    border-radius: 50px;
    color: #94a3b8;
    font-size: 0.85rem;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 8px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
.admin-badge b { color: #818cf8; }

/* ── Sidebar Container ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #090d16 0%, #030712 100%) !important;
    border-right: 1px solid rgba(99,102,241,0.15) !important;
    width: 320px !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 0rem !important;
    padding-bottom: 120px !important; /* Beri ruang agar tidak tertutup footer */
}

/* ── Premium Brand ── */
.sidebar-brand {
    text-align: center;
    padding: 1.5rem 1rem 1rem 1rem;
    margin-bottom: 1rem;
}
.sidebar-brand .icon {
    font-size: 2.5rem;
    display: block;
    margin-bottom: 0.2rem;
    filter: drop-shadow(0 0 10px rgba(99,102,241,0.4));
}
.sidebar-brand h1 {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 800;
    font-size: 1.6rem;
    line-height: 1.2;
    background: linear-gradient(135deg, #818cf8 0%, #c084fc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    letter-spacing: -0.5px;
}
.sidebar-brand p {
    color: #64748b;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.2em;
    margin-top: 0.5rem;
}

/* ── Navigation List ── */
.nav-container {
    padding: 0 1rem;
}
.stButton > button {
    background: rgba(255,255,255,0.02) !important;
    color: #94a3b8 !important;
    border: 1px solid rgba(255,255,255,0.05) !important;
    border-radius: 0.85rem !important;
    padding: 0.75rem 1.2rem !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    width: 100% !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    text-align: left !important;
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;
    margin-bottom: 0.6rem !important;
}
.stButton > button:hover {
    background: rgba(99,102,241,0.12) !important;
    color: #f1f5f9 !important;
    border-color: rgba(99,102,241,0.35) !important;
    border-bottom: 3px solid rgba(192, 132, 252, 0.6) !important;
    transform: translateX(5px) !important;
    box-shadow: 0 4px 15px rgba(99,102,241,0.1) !important;
}
.active-nav button {
    background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%) !important;
    color: white !important;
    border-left: 4px solid #818cf8 !important;
    border-bottom: 4px solid #c084fc !important; /* Bottom-nya berwarna (colored bottom border) */
    box-shadow: 0 8px 20px rgba(99,102,241,0.2) !important;
}

/* ── Sidebar Footer ── */
.sidebar-footer {
    position: fixed;
    bottom: 0px;
    left: 0px;
    width: 320px;
    padding: 1rem 1.5rem;
    background: #030712;
    border-top: 1px solid rgba(99,102,241,0.2) !important;
    z-index: 100;
}

/* ── Content Cards & Glassmorphism ── */
.metric-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 1.2rem;
    padding: 1.5rem;
    text-align: center;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
}
.metric-card:hover {
    transform: translateY(-5px);
    border-color: rgba(99,102,241,0.4);
    background: rgba(99,102,241,0.03);
    box-shadow: 0 10px 30px rgba(99,102,241,0.15);
}
.metric-value { font-size:2.2rem; font-weight:800; color:white; }
.metric-label { font-size:0.75rem; color:#64748b; text-transform:uppercase; letter-spacing:0.1em; }

.section-card {
    background: rgba(15, 23, 42, 0.3);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 1.5rem;
    padding: 2rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.page-header {
    margin-bottom: 2.5rem;
    border-left: 4px solid #818cf8;
    padding-left: 1rem;
}
.page-header h1 {
    font-size: 2.2rem;
    font-weight: 800;
    color: white;
    margin-bottom: 0.2rem;
    letter-spacing: -0.5px;
}
.page-header p {
    color: #94a3b8;
    font-size: 1rem;
}

.result-card {
    background: rgba(255, 255, 255, 0.02);
    border-radius: 2rem;
    padding: 2.5rem;
    text-align: center;
    margin-bottom: 2rem;
    backdrop-filter: blur(12px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
}
.result-pct { font-size: 4.5rem; font-weight: 900; }
.result-label { font-size: 1.6rem; font-weight: 800; margin: 0.5rem 0; }
.result-sub { font-size: 0.9rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.1em; }

/* ── Modern Form Controls Override ── */
div[data-testid="stForm"] {
    background: rgba(15, 23, 42, 0.25) !important;
    backdrop-filter: blur(10px) !important;
    border: 1px solid rgba(255, 255, 255, 0.06) !important;
    border-radius: 1.5rem !important;
    padding: 2rem !important;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2) !important;
}

/* Style Inputs, Selectboxes, Slider, & Text Areas globally for premium dark UI */
input, select, textarea, div[data-baseweb="select"] {
    background-color: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 0.8rem !important;
    color: white !important;
    transition: all 0.25s ease !important;
}
input:focus, select:focus, div[data-baseweb="select"]:focus-within {
    border-color: #818cf8 !important;
    box-shadow: 0 0 12px rgba(129, 140, 248, 0.25) !important;
    background-color: rgba(255, 255, 255, 0.05) !important;
}

/* Modernise Streamlit Status Alert Dialogs */
div[data-testid="stNotification"] {
    border-radius: 1rem !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.15) !important;
}

/* Reset the login card styling on columns if any style leaked from previous runs */
div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
    background: none !important;
    backdrop-filter: none !important;
    border: none !important;
    box-shadow: none !important;
}

/* Hide login background and all login page elements instantly when entering main dashboard */
.login-bg, .orb, .login-logo, .login-title, .login-subtitle, .login-user-info, .login-pin-header, .login-footer {
    display: none !important;
}

/* Force hide any column containing login components to remove the ghost PIN form and buttons (bypassing Streamlit layout wrapper changes) */
div[data-testid="column"]:has(.login-logo),
div[data-testid="column"]:has(.login-title),
div[data-testid="column"]:has(.login-user-info),
div[data-testid="column"]:has(.login-pin-header) {
    display: none !important;
}
</style>
"""
