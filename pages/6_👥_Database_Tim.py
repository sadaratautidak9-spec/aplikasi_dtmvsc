import streamlit as st
import pandas as pd
from supabase import create_client, Client

# --- KONFIGURASI HALAMAN & CSS GLOBAL ---
st.set_page_config(page_title="Database Tim | DTM", page_icon="👥", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Titillium+Web:wght@300;400;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined');

    html, body, [class*="css"] { font-family: 'Titillium Web', sans-serif !important; }
    [data-testid="stSidebar"] { background-color: #1e3a8a !important; }
    [data-testid="stSidebar"] * { color: white !important; }
    
    .card-container {
        background-color: white; padding: 25px; border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); border: 1px solid #e2e8f0; margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- KONFIGURASI SUPABASE ---
SUPABASE_URL = "https://ehfpmlwmdnjtxrfqdgkc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVoZnBtbHdtZG5qdHhyZnFkZ2tjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ1MDc1NjMsImV4cCI6MjA5MDA4MzU2M30.LPiPaAIm2MhuywLnmSTegWO0-1gcPuVww8abFhTAin8"

@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_connection()

def load_data_tim():
    response = supabase.table('data_tim').select("*").order("id", desc=False).execute()
    return response.data

st.markdown("<h2 style='color: #1e3a8a; font-weight: 700;'><span class='material-symbols-outlined' style='vertical-align: middle; font-size: 35px;'>groups</span> Manajemen Database Tim</h2>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# --- BAGIAN 1: FORM TAMBAH TIM BARU ---
st.markdown("<div class='card-container'>", unsafe_allow_html=True)
st.markdown("<h4 style='color: #1e3a8a; margin-bottom: 20px;'><span class='material-symbols-outlined' style='vertical-align: middle;'>person_add</span> Form Tambah Tim Baru</h4>", unsafe_allow_html=True)

with st.form("form_tambah_tim", clear_on_submit=True):
    col_f1, col_f2, col_f3 = st.columns([2, 1.5, 1.5])
    with col_f1:
        nama_input = st.text_input("Nama Lengkap (beserta gelar)")
    with col_f2:
        telp_input = st.text_input("No. Telepon / WA") # <-- INPUT BARU
    with col_f3:
        peran_input = st.selectbox("Peran Tim", ["Tim Auditor", "Tim Pengambil Keputusan"])
    
    submit_btn = st.form_submit_button("💾 Simpan Data Tim", type="primary")
    
    if submit_btn:
        if nama_input.strip() == "":
            st.error("Nama lengkap tidak boleh kosong!")
        else:
            try:
                supabase.table('data_tim').insert({
                    "nama_lengkap": nama_input,
                    "no_telp": telp_input, # <-- SIMPAN KE DATABASE
                    "peran": peran_input,
                    "status": "Aktif"
                }).execute()
                st.success(f"Berhasil menambahkan {nama_input}!")
                st.rerun()
            except Exception as e:
                st.error(f"Gagal menyimpan data: {e}")
st.markdown("</div>", unsafe_allow_html=True)

# --- BAGIAN 2: TABEL DATABASE TIM ---
st.markdown("<div class='card-container'>", unsafe_allow_html=True)
st.markdown("<h4 style='color: #1e3a8a; margin-bottom: 20px;'><span class='material-symbols-outlined' style='vertical-align: middle;'>badge</span> Database Tim Internal</h4>", unsafe_allow_html=True)

data_tim = load_data_tim()

if not data_tim:
    st.info("Belum ada data tim. Silakan tambahkan melalui form di atas.")
else:
    col_h1, col_h2, col_h3, col_h4, col_h5, col_h6 = st.columns([0.5, 2.5, 1.5, 1.5, 1, 1.5])
    col_h1.markdown("**No**")
    col_h2.markdown("**Nama Lengkap**")
    col_h3.markdown("**No. Telepon**")
    col_h4.markdown("**Peran**")
    col_h5.markdown("**Status**")
    col_h6.markdown("**Aksi**")
    st.markdown("<hr style='margin-top: 5px; margin-bottom: 10px;'>", unsafe_allow_html=True)

    for index, row in enumerate(data_tim):
        col1, col2, col3, col4, col5, col6 = st.columns([0.5, 2.5, 1.5, 1.5, 1, 1.5])
        
        col1.write(f"{index + 1}")
        col2.write(row['nama_lengkap'])
        col3.write(row.get('no_telp', '-')) # <-- TAMPILKAN NO TELP
        col4.write(row['peran'])
        
        if row['status'] == 'Aktif':
            col5.markdown("<span style='background-color: #dcfce7; color: #16a34a; padding: 5px 10px; border-radius: 20px; font-weight: bold; font-size: 12px;'>Aktif</span>", unsafe_allow_html=True)
            label_tombol, status_baru = "🚫 Nonaktifkan", "Non-Aktif"
        else:
            col5.markdown("<span style='background-color: #fee2e2; color: #dc2626; padding: 5px 10px; border-radius: 20px; font-weight: bold; font-size: 12px;'>Non-Aktif</span>", unsafe_allow_html=True)
            label_tombol, status_baru = "✅ Aktifkan", "Aktif"
            
        if col6.button(label_tombol, key=f"btn_{row['id']}", use_container_width=True):
            supabase.table('data_tim').update({"status": status_baru}).eq("id", row['id']).execute()
            st.rerun()
            
        st.markdown("<hr style='margin-top: 5px; margin-bottom: 5px; border-color: #f1f5f9;'>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
