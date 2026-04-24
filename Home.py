import streamlit as st
from supabase import create_client

# Matikan menu sidebar bawaan untuk halaman login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

st.set_page_config(page_title="Login | DTM Systems", layout="centered", initial_sidebar_state="collapsed")

# --- KONFIGURASI SUPABASE ---
SUPABASE_URL = "https://ehfpmlwmdnjtxrfqdgkc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVoZnBtbHdtZG5qdHhyZnFkZ2tjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ1MDc1NjMsImV4cCI6MjA5MDA4MzU2M30.LPiPaAIm2MhuywLnmSTegWO0-1gcPuVww8abFhTAin8"

@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_connection()

# Jika sudah login, bisa tambahkan navigasi atau arahkan (misal, tampilkan pesan atau pindah halaman)
if st.session_state.logged_in:
    st.success("Anda sudah login!")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
    st.stop()

# --- HACK CSS UNTUK MENIRU DESAIN MODERN ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }
    .stApp {
        background-color: #f8fafc; 
    }
    
    header {visibility: hidden;}

    div[data-testid="stForm"] {
        background-color: white;
        padding: 40px;
        border-radius: 16px;
        box-shadow: 0 10px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
        border: 1px solid #e2e8f0;
        max-width: 450px !important;
        margin: 0 auto;
    }

    .stTextInput input {
        border-radius: 8px !important;
        padding: 12px 16px !important;
        border: 1px solid #cbd5e1 !important;
        font-size: 14px !important;
    }
    .stTextInput input:focus {
        border-color: #4f46e5 !important;
        box-shadow: 0 0 0 1px #4f46e5 !important;
    }

    button[kind="primary"] {
        background-color: #4f46e5 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
    }
    button[kind="primary"]:hover {
        background-color: #4338ca !important;
        box-shadow: 0 4px 6px -1px rgb(79 70 229 / 0.4) !important;
    }

    div[data-testid="stAlert"] {
        background-color: #dcfce7 !important;
        color: #166534 !important;
        border: none !important;
        border-radius: 8px !important;
    }

    .login-title {
        text-align: center;
        color: #0f172a;
        font-weight: 800;
        font-size: 24px;
        margin-bottom: 5px;
    }
    .login-subtitle {
        text-align: center;
        color: #64748b;
        font-weight: 600;
        font-size: 13px;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 30px;
    }
    
    .logo-container {
        display: flex;
        justify-content: center;
        margin-bottom: 20px;
        margin-top: 50px;
    }
    .logo-box {
        background-color: #4f46e5;
        color: white;
        font-size: 30px;
        font-weight: 800;
        border-radius: 16px;
        width: 70px;
        height: 70px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 10px 15px -3px rgb(79 70 229 / 0.4);
    }
</style>
""", unsafe_allow_html=True)

# --- TAMPILAN LOGIN ---
st.markdown("""
<div class="logo-container">
    <div class="logo-box">D</div>
</div>
<div class="login-title">DTM Systems</div>
<div class="login-subtitle">CERTIFICATION MANAGER</div>
""", unsafe_allow_html=True)

with st.form("login_form"):
    # Hapus pesan sukses logout karena ini akan tampil saat baru buka
    # st.success("Anda telah berhasil logout.") 
    
    st.markdown("<p style='font-size:12px; font-weight:700; color:#334155; margin-bottom:0px;'>USERNAME</p>", unsafe_allow_html=True)
    username = st.text_input("Username", label_visibility="collapsed", placeholder="Masukkan username")
    
    st.markdown("<p style='font-size:12px; font-weight:700; color:#334155; margin-bottom:0px; margin-top:15px;'>PASSWORD</p>", unsafe_allow_html=True)
    password = st.text_input("Password", type="password", label_visibility="collapsed", placeholder="Masukkan password")
    
    st.markdown("<br>", unsafe_allow_html=True)
    submit = st.form_submit_button("Login Masuk", type="primary")
    
    if submit:
        if username and password:
            try:
                # Karena inputnya username (bukan email), kita asumsikan username dikonversi ke email atau cek tabel lain
                # Kita gunakan Supabase Auth dengan email, format sederhana: username + '@dtmsystems.com'
                # Atau modifikasi sesuai skema Anda.
                email_asumsi = username if "@" in username else f"{username}@dtmsystems.com"
                
                auth_res = supabase.auth.sign_in_with_password({"email": email_asumsi, "password": password})
                
                if auth_res.user:
                    st.session_state.logged_in = True
                    st.success("Login berhasil!")
                    st.rerun()
            except Exception as e:
                # Tangani pesan error secara umum jika salah
                error_msg = str(e)
                if "Invalid login credentials" in error_msg:
                    st.error("Username atau Password salah!")
                else:
                    # Menggunakan dummy check jika Supabase belum disetting untuk user ini
                    if username == "admin" and password == "admin123":
                        st.session_state.logged_in = True
                        st.success("Login berhasil (Admin Bypass)!")
                        st.rerun()
                    else:
                        st.error("Username atau Password salah!")
        else:
            st.warning("Silakan isi Username dan Password terlebih dahulu.")
