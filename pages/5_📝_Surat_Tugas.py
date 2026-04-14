import streamlit as st

# --- CEK LOGIN ---
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("🔒 Anda belum login. Silakan kembali ke halaman utama (Home) untuk login.")
    st.stop()

from docxtpl import DocxTemplate
import pandas as pd
from datetime import datetime
from num2words import num2words
import os
import requests
from supabase import create_client

# --- KONFIGURASI WEBHOOK n8n & SUPABASE ---
N8N_WEBHOOK_URL = "http://localhost:5678/webhook/0efd14de-28cc-4582-ac29-dc4cf98bcfda"
SUPABASE_URL = "https://ehfpmlwmdnjtxrfqdgkc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVoZnBtbHdtZG5qdHhyZnFkZ2tjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ1MDc1NjMsImV4cCI6MjA5MDA4MzU2M30.LPiPaAIm2MhuywLnmSTegWO0-1gcPuVww8abFhTAin8"

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

st.set_page_config(page_title="Surat Tugas | DTM", page_icon="📋", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Titillium+Web:wght@300;400;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined');
    html, body, [class*="css"] { font-family: 'Titillium Web', sans-serif !important; background-color: #f8fafc; }
    [data-testid="stSidebar"] { background-color: #1a3673 !important; border-right: none !important; }
    [data-testid="stSidebar"] * { color: white !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='color: #1e3a8a; font-weight: 700;'><span class='material-symbols-outlined' style='vertical-align: middle; font-size: 35px;'>assignment</span> Generator Surat Tugas</h2>", unsafe_allow_html=True)

with st.container(border=True):
    st.markdown("#### Detail Penugasan")
    c1, c2 = st.columns(2)
    with c1:
        nama_klien = st.text_input("Nama Klien (PT/CV)")
        tgl_tugas = st.date_input("Tanggal Pelaksanaan Audit")
    with c2:
        nama_auditor = st.text_input("Nama Auditor yang Ditugaskan")
        peran = st.selectbox("Peran", ["Lead Auditor", "Auditor", "Tenaga Ahli"])
        
    submit = st.button("🚀 Generate Surat Tugas (Word) & Kirim ke n8n", type="primary", use_container_width=True)

if submit:
    if not nama_klien or not nama_auditor:
        st.error("⚠️ Nama Klien dan Nama Auditor wajib diisi!")
    else:
        with st.spinner("Memproses dokumen..."):
            try:
                # Siapkan data untuk template
                context = {
                    'nama_klien': nama_klien,
                    'nama_auditor': nama_auditor,
                    'peran': peran,
                    'tanggal': tgl_tugas.strftime('%d %B %Y')
                }
                
                template_path = "templates/surat_tugas_template.docx"
                os.makedirs("output/word", exist_ok=True)
                
                if not os.path.exists(template_path):
                    st.error(f"⚠️ Template tidak ditemukan di `{template_path}`")
                else:
                    # Generate Word
                    doc = DocxTemplate(template_path)
                    doc.render(context)
                    fname = f"Surat_Tugas_{nama_auditor.replace(' ', '_')}_{nama_klien.replace(' ', '_')}.docx"
                    output_path = f"output/word/{fname}"
                    doc.save(output_path)
                    
                    # Kirim ke n8n
                    try:
                        payload = {"klien": nama_klien, "auditor": nama_auditor, "peran": peran, "tanggal": str(tgl_tugas)}
                        files = {"file_word": (fname, open(output_path, "rb"), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
                        
                        if "MASUKKAN-ID-WEBHOOK" not in N8N_WEBHOOK_URL:
                            requests.post(N8N_WEBHOOK_URL, data=payload, files=files)
                    except:
                        pass # Abaikan error n8n sementara
                        
                    st.success("✅ Surat Tugas berhasil dibuat!")
                    with open(output_path, "rb") as f:
                        st.download_button("📥 Download Surat Tugas (Word)", f, file_name=fname, type="primary", use_container_width=True)
            except Exception as e:
                st.error(f"❌ Error: {e}")
