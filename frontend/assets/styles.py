"""
CSS Styles untuk EduPredict AI — Midnight Premium (Stable Version)
"""

LOGIN_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Space+Grotesk:wght@300;500;700&display=swap');

.stApp {
    background: linear-gradient(135deg, #0a0f1a 0%, #111827 40%, #1e1b4b 100%);
    font-family: 'Outfit', sans-serif;
}
[data-testid="stHeader"], #MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 2rem !important; }

/* Custom Login Card Styling */
.login-card {
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 1.5rem;
    padding: 3rem 2rem;
    text-align: center;
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4);
    margin: 0 auto;
}
.login-logo {
    font-size: 3.5rem;
    margin-bottom: 0.5rem;
    line-height: 1;
}
.login-title {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 800;
    font-size: 2.2rem;
    color: #ffffff;
    margin: 0 0 0.5rem 0;
    letter-spacing: -0.5px;
}
.login-subtitle {
    color: #94a3b8;
    font-size: 0.95rem;
    margin-bottom: 2.5rem;
}
.google-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background-color: #ffffff;
    color: #1f2937;
    font-weight: 600;
    padding: 12px 24px;
    border-radius: 50px;
    text-decoration: none;
    font-family: 'Outfit', sans-serif;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transition: all 0.2s ease;
    width: 100%;
    max-width: 280px;
}
.google-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    background-color: #f8fafc;
}
</style>
"""

MAIN_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Space+Grotesk:wght@300;500;700&display=swap');

/* ── Global Setup ── */
.stApp {
    background: #0b0e14;
    font-family: 'Outfit', sans-serif;
}

/* Sembunyikan elemen sampah di Header tapi biarkan tombol Sidebar tetap ada */
header[data-testid="stHeader"] {
    background: rgba(0,0,0,0) !important;
}
/* Menyembunyikan tombol Deploy dan elemen kanan lainnya */
[data-testid="stHeader"] > div:first-child > div:nth-child(2) {
    display: none !important;
}
#MainMenu, footer { visibility: hidden; }

/* Pastikan tombol panah sidebar terlihat jelas */
button[data-testid="stSidebarCollapseButton"] {
    color: white !important;
    background: rgba(255,255,255,0.05) !important;
    border-radius: 50% !important;
}

/* 👑 Admin Badge Top Right */
.admin-badge {
    position: fixed;
    top: 1rem;
    right: 1.5rem;
    z-index: 999999;
    background: rgba(255,255,255,0.03);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.08);
    padding: 0.5rem 1.2rem;
    border-radius: 50px;
    color: #94a3b8;
    font-size: 0.85rem;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 8px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}
.admin-badge b { color: #818cf8; }

/* ── Sidebar Container ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #020617 100%) !important;
    border-right: 1px solid rgba(99,102,241,0.1) !important;
    width: 320px !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 0rem !important;
}

/* ── Premium Brand ── */
.sidebar-brand {
    text-align: center;
    padding: 0.5rem 1rem 0.5rem 1rem;
    margin-bottom: 0.2rem;
}
.sidebar-brand .icon {
    font-size: 2.2rem;
    display: block;
    margin-bottom: 0.2rem;
}
.sidebar-brand h1 {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 800;
    font-size: 1.5rem;
    line-height: 1.2;
    background: linear-gradient(135deg, #818cf8 0%, #c084fc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}
.sidebar-brand p {
    color: #475569;
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
    background: rgba(255,255,255,0.03) !important;
    color: #94a3b8 !important;
    border: 1px solid rgba(255,255,255,0.05) !important;
    border-radius: 0.85rem !important;
    padding: 0.7rem 1.2rem !important;
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
    background: rgba(99,102,241,0.1) !important;
    color: #e2e8f0 !important;
    border-color: rgba(99,102,241,0.3) !important;
    transform: translateX(5px) !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
}
.active-nav button {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
    color: white !important;
    border: none !important;
    box-shadow: 0 10px 20px rgba(79,70,229,0.3) !important;
}

/* ── Content Cards ── */
.metric-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 1.2rem; padding: 1.5rem; text-align: center;
    transition: all 0.3s ease;
}
.metric-card:hover { transform: translateY(-5px); border-color: rgba(99,102,241,0.3); }
.metric-value { font-size:2.2rem; font-weight:800; color:white; }
.metric-label { font-size:0.75rem; color:#64748b; text-transform:uppercase; letter-spacing:0.1em; }

.section-card {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 1.5rem; padding: 2rem; margin-bottom: 1.5rem;
}

.page-header {
    margin-bottom: 2rem;
}
.page-header h1 {
    font-size: 2rem;
    font-weight: 700;
    color: white;
    margin-bottom: 0.2rem;
}
.page-header p {
    color: #94a3b8;
    font-size: 1rem;
}

.result-card {
    background: rgba(255,255,255,0.03);
    border-radius: 1.5rem;
    padding: 2.5rem;
    text-align: center;
    margin-bottom: 2rem;
}
.result-pct { font-size: 4rem; font-weight: 800; }
.result-label { font-size: 1.5rem; font-weight: 700; margin: 0.5rem 0; }
.result-sub { font-size: 0.9rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.1em; }

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

/* Hide all text inputs and buttons inside 3-column layouts when in main app (to target ghost PIN inputs and buttons) */
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2):nth-last-child(2) div[data-testid="stTextInput"],
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2):nth-last-child(2) button {
    display: none !important;
}
</style>
"""
