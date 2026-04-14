import streamlit as st
from supabase import create_client
import datetime

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="DTM Certification System", page_icon="🔐", layout="wide")

# --- INISIALISASI SESSION STATE UNTUK LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# ==========================================
# HALAMAN LOGIN
# ==========================================
if not st.session_state.logged_in:
    # CSS Khusus untuk Halaman Login agar posisinya di tengah
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Titillium+Web:wght@400;600;700&display=swap');
        html, body, [class*="css"] { font-family: 'Titillium Web', sans-serif !important; background-color: #f8fafc; }
        [data-testid="stSidebar"] { display: none; } /* Sembunyikan sidebar saat belum login */
        
        .login-box {
            max-width: 400px; margin: 100px auto; padding: 40px; 
            background-color: white; border-radius: 16px; 
            box-shadow: 0 10px 25px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;
            text-align: center;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    st.markdown("<h1 style='color: #1e3a8a; margin-bottom: 5px;'>🔐 APK DTM</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; margin-bottom: 30px;'>Silakan login untuk mengakses sistem</p>", unsafe_allow_html=True)
    
    username = st.text_input("Username", placeholder="Masukkan username...")
    password = st.text_input("Password", type="password", placeholder="Masukkan password...")
    
    if st.button("Masuk / Login", type="primary", use_container_width=True):
        # --- GANTI USERNAME & PASSWORD DI SINI ---
        if username == "admin" and password == "dtm2026":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("❌ Username atau Password salah!")
            
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop() # Hentikan eksekusi kode di bawahnya jika belum login

# ==========================================
# HALAMAN DASHBOARD (JIKA SUDAH LOGIN)
# ==========================================

# --- KONFIGURASI SUPABASE ---
SUPABASE_URL = "https://ehfpmlwmdnjtxrfqdgkc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVoZnBtbHdtZG5qdHhyZnFkZ2tjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ1MDc1NjMsImV4cCI6MjA5MDA4MzU2M30.LPiPaAIm2MhuywLnmSTegWO0-1gcPuVww8abFhTAin8"

@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_connection()

# --- FUNGSI MENGHITUNG STATISTIK ---
@st.cache_data(ttl=10)
def get_dashboard_stats():
    res_sert = supabase.table('data_sertifikasi').select('*').execute()
    res_tim = supabase.table('data_tim').select('*').execute()
    data_sert = res_sert.data
    data_tim = res_tim.data
    
    jml_tim = sum(1 for t in data_tim if t.get('status') == 'Aktif')
    jml_tersertifikasi = 0
    jml_pembekuan = 0
    jml_dicabut = 0
    jml_survailen = 0
    hari_ini = datetime.date.today()
    
    for s in data_sert:
        status = s.get('status')
        if status == 'Tersertifikasi':
            jml_tersertifikasi += 1
            try:
                tgl_surv = datetime.datetime.strptime(s['tgl_survailen'], '%Y-%m-%d').date()
                if (tgl_surv - hari_ini).days <= 60: jml_survailen += 1
            except: pass
        elif status == 'Dibekukan': jml_pembekuan += 1
        elif status == 'Dicabut': jml_dicabut += 1
            
    return {"tersertifikasi": jml_tersertifikasi, "survailen": jml_survailen, "pembekuan": jml_pembekuan, "dicabut": jml_dicabut, "tim": jml_tim}

stats = get_dashboard_stats()

# --- SUNTIKAN CSS DASHBOARD ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Titillium+Web:wght@300;400;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined');
    html, body, [class*="css"] { font-family: 'Titillium Web', sans-serif !important; }
    
    [data-testid="stSidebar"] { background-color: #1a3673 !important; border-right: none !important; }
    [data-testid="stSidebar"] * { color: white !important; }
    [data-testid="stSidebarNav"]::before {
        content: "✅ APK DTM"; display: block; color: white; font-size: 24px; font-weight: 700;
        padding: 20px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 15px;
    }
    [data-testid="stSidebarNav"] ul li a { font-size: 16px !important; font-weight: 600 !important; color: #cbd5e1 !important; padding: 10px 15px !important; }
    [data-testid="stSidebarNav"] ul li a:hover { background-color: rgba(255, 255, 255, 0.05) !important; color: white !important; }
    [data-testid="stSidebarNav"] ul li a[aria-current="page"] { background-color: rgba(255, 255, 255, 0.1) !important; color: white !important; border-left: 4px solid #60a5fa !important; }
    [data-testid="stSidebarNav"] > div:first-child { display: none; }

    .menu-box {
        background-color: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px;
        text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center;
        height: 140px; text-decoration: none !important; transition: all 0.3s ease; box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .menu-box:hover { border-color: #1e3a8a; box-shadow: 0 4px 8px rgba(30,58,138,0.2); transform: translateY(-4px); }
    .menu-icon { font-size: 45px !important; color: #1e3a8a; margin-bottom: 10px; }
    .menu-text { font-weight: 600; font-size: 16px; color: #1e3a8a; }
</style>
""", unsafe_allow_html=True)

# TOMBOL LOGOUT DI SIDEBAR
with st.sidebar:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    if st.button("🚪 Logout Admin", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

def buat_kartu(icon_name, angka, teks, warna_bg_ikon, warna_teks_ikon):
    return f"""
    <div style="background-color: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border: 1px solid #e2e8f0; height: 150px; display: flex; flex-direction: column; justify-content: space-between;">
        <div style="background-color: {warna_bg_ikon}; width: 45px; height: 45px; border-radius: 10px; display: flex; justify-content: center; align-items: center; color: {warna_teks_ikon};">
            <span class="material-symbols-outlined" style="font-size: 28px;">{icon_name}</span>
        </div>
        <div>
            <h2 style="margin: 0; font-size: 32px; color: #1e293b; font-weight: 700;">{angka}</h2>
            <p style="margin: 0; font-size: 14px; color: #64748b; font-weight: 600;">{teks}</p>
        </div>
    </div>
    """

st.markdown("<h1 style='color: #1e3a8a; font-weight: 700;'>Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)
with col1: st.markdown(buat_kartu("verified", str(stats["tersertifikasi"]), "Tersertifikasi LSUHK", "#dcfce7", "#16a34a"), unsafe_allow_html=True)
with col2: st.markdown(buat_kartu("find_in_page", str(stats["survailen"]), "Survailen LSUHK", "#e0f2fe", "#0284c7"), unsafe_allow_html=True)
with col3: st.markdown(buat_kartu("block", str(stats["pembekuan"]), "Pembekuan LSUHK", "#ffedd5", "#ea580c"), unsafe_allow_html=True)
with col4: st.markdown(buat_kartu("cancel", str(stats["dicabut"]), "Tidak Aktif", "#fee2e2", "#dc2626"), unsafe_allow_html=True)
with col5: st.markdown(buat_kartu("groups", str(stats["tim"]), "Database Tim", "#f3e8ff", "#9333ea"), unsafe_allow_html=True)

st.markdown("<br><hr><br>", unsafe_allow_html=True)
st.markdown("<h3 style='color: #1e3a8a; font-weight: 600;'><span class='material-symbols-outlined' style='vertical-align: middle;'>apps</span> Modul Aplikasi</h3>", unsafe_allow_html=True)

col_m1, col_m2, col_m3, col_m4, col_m5, col_m6, col_m7 = st.columns(7)
with col_m1: st.markdown("""<a href="Kontrak_QA" target="_self" class="menu-box"><span class="material-symbols-outlined menu-icon">description</span><span class="menu-text">Kontrak & QA</span></a>""", unsafe_allow_html=True)
with col_m2: st.markdown("""<a href="Invoice" target="_self" class="menu-box"><span class="material-symbols-outlined menu-icon">payments</span><span class="menu-text">Invoice</span></a>""", unsafe_allow_html=True)
with col_m3: st.markdown("""<a href="Analisa" target="_self" class="menu-box"><span class="material-symbols-outlined menu-icon">analytics</span><span class="menu-text">Analisa</span></a>""", unsafe_allow_html=True)
with col_m4: st.markdown("""<a href="Database" target="_self" class="menu-box"><span class="material-symbols-outlined menu-icon">database</span><span class="menu-text">Database</span></a>""", unsafe_allow_html=True)
with col_m5: st.markdown("""<a href="Surat_Tugas" target="_self" class="menu-box"><span class="material-symbols-outlined menu-icon">assignment</span><span class="menu-text">Surat Tugas</span></a>""", unsafe_allow_html=True)
with col_m6: st.markdown("""<a href="Database_Tim" target="_self" class="menu-box"><span class="material-symbols-outlined menu-icon">groups</span><span class="menu-text">Tim Internal</span></a>""", unsafe_allow_html=True)
with col_m7: st.markdown("""<a href="Status_Klien" target="_self" class="menu-box"><span class="material-symbols-outlined menu-icon">workspace_premium</span><span class="menu-text">Status Klien</span></a>""", unsafe_allow_html=True)