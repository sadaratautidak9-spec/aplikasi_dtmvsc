import streamlit as st
import pandas as pd
from supabase import create_client, Client
from docxtpl import DocxTemplate
import os
import requests

# --- 1. KONFIGURASI SUPABASE & n8n ---
SUPABASE_URL = "https://ehfpmlwmdnjtxrfqdgkc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVoZnBtbHdtZG5qdHhyZnFkZ2tjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ1MDc1NjMsImV4cCI6MjA5MDA4MzU2M30.LPiPaAIm2MhuywLnmSTegWO0-1gcPuVww8abFhTAin8"

# MASUKKAN URL WEBHOOK n8n ANDA DI SINI
URL_WEBHOOK_N8N = "http://localhost:5678/webhook-test/MASUKKAN-ID-WEBHOOK-ANDA-DISINI"

@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_connection()

st.set_page_config(page_title="Surat Tugas & Pemberitahuan", page_icon="📝", layout="wide")
# --- SUNTIKAN CSS DESAIN GLOBAL ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Titillium+Web:wght@300;400;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined');

    html, body, [class*="css"] {
        font-family: 'Titillium Web', sans-serif !important;
    }
    
    /* Paksa Sidebar berwarna Biru Tua */
    [data-testid="stSidebar"] {
        background-color: #1e3a8a !important;
    }
    
    /* Paksa tulisan di Sidebar berwarna Putih */
    [data-testid="stSidebar"] * {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)
st.title("📝 Generator Surat Tugas & Pemberitahuan")

# --- 2. AMBIL DATA DARI DATABASE ---
@st.cache_data(ttl=600)
def load_data_kontrak(_client):
    response = _client.table('data_kontrak').select("*").order("id", desc=True).execute()
    return pd.DataFrame(response.data)

def load_data_surat(_client, id_kontrak):
    response = _client.table('data_surat').select("*").eq("id_kontrak", id_kontrak).execute()
    if response.data:
        return response.data[0] # Ambil data surat jika sudah ada
    return {} # Kosong jika belum pernah dibuat

df = load_data_kontrak(supabase)

if st.button("🔄 Refresh Data Database"):
    load_data_kontrak.clear()
    st.rerun()

if df.empty:
    st.warning("Database masih kosong.")
    st.stop()

# --- 3. PILIH PERUSAHAAN ---
st.subheader("1. Pilih Perusahaan")
df['label_pilihan'] = df['id'].astype(str) + " - " + df['nama_pt'].astype(str)
pilihan_label = st.selectbox("Pilih PT yang akan dibuatkan surat:", df['label_pilihan'].tolist())

pilihan_id = int(pilihan_label.split(" - ")[0])
data_terpilih = df[df['id'] == pilihan_id].iloc[0].fillna('-')

# Ambil data surat dari tabel kedua (data_surat) berdasarkan id_kontrak
data_surat = load_data_surat(supabase, pilihan_id)

st.divider()

# --- 4. FORM EDIT DATA & GENERATE ---
st.subheader("2. Lengkapi Data & Buat Dokumen")

# A. Data Paten (Tabel data_kontrak - Terkunci)
st.markdown("**Data Perusahaan (Terkunci)**")
col_pt1, col_pt2 = st.columns(2)
with col_pt1:
    st.text_input("Nama PT", value=data_terpilih.get('nama_pt', '-'), disabled=True)
with col_pt2:
    st.text_input("Alamat Lengkap", value=data_terpilih.get('Alamat lengkap', '-'), disabled=True)

st.markdown("<br>", unsafe_allow_html=True)

# B. Data Tim Audit (Tabel data_kontrak - Bisa Diedit)
st.markdown("**Data Tim Audit & Wakil Manajemen (Bisa Diedit)**")

# --- LOGIKA MENGAMBIL DATA TIM DARI DATABASE ---
@st.cache_data(ttl=60)
def get_pilihan_auditor():
    # Ambil data dari tabel data_tim yang perannya "Tim Auditor" dan statusnya "Aktif"
    res = supabase.table('data_tim').select("*").eq('peran', 'Tim Auditor').eq('status', 'Aktif').execute()
    pilihan = ["-"] # Default kosong
    for t in res.data:
        telp = t.get('no_telp', '')
        if telp:
            pilihan.append(f"{t['nama_lengkap']} [{telp}]")
        else:
            pilihan.append(t['nama_lengkap'])
    return pilihan

daftar_auditor = get_pilihan_auditor()

# Fungsi bantu untuk mencari index default di dropdown
def cari_index(nilai_dicari, daftar_pilihan):
    if nilai_dicari in daftar_pilihan:
        return daftar_pilihan.index(nilai_dicari)
    return 0

col_edit1, col_edit2 = st.columns(2)
with col_edit1:
    # SEKARANG MENGGUNAKAN SELECTBOX (DROPDOWN) BUKAN TEXT_INPUT
    val_lead = data_terpilih.get('Lead Auditor', '-')
    lead_auditor_input = st.selectbox("Lead Auditor", daftar_auditor, index=cari_index(val_lead, daftar_auditor))
    
    val_auditor = data_terpilih.get('Auditor', '-')
    auditor_input = st.selectbox("Auditor", daftar_auditor, index=cari_index(val_auditor, daftar_auditor))
    
    val_observer = data_terpilih.get('Observer', '-')
    observer_input = st.selectbox("Observer", daftar_auditor, index=cari_index(val_observer, daftar_auditor))

with col_edit2:
    wakil_manajemen_input = st.text_input("Wakil Manajemen", value=data_surat.get('Wakil Manajemen', ''))
    no_tlp_wm_input = st.text_input("No Tlp Wakil Manajemen", value=data_surat.get('No Tlp Wakil Manajemen', ''))

st.markdown("<br>", unsafe_allow_html=True)

# C. Data Surat (Tabel data_surat)
with st.expander("Data Detail Surat (Nomor, Tanggal, Zoom, dll)", expanded=True):
    col_a, col_b = st.columns(2)
    with col_a:
        no_surat_input = st.text_input("Nomor Surat Tugas", value=data_surat.get('no_surat_tugas', '025/STTA/III/25'))
        no_surat_pemberitahuan_input = st.text_input("Nomor Surat Pemberitahuan", value=data_surat.get('no_surat_pemberitahuan', '026/SP/III/25'))
        tipe_audit_input = st.text_input("Tipe Audit", value=data_surat.get('tipe_audit', 'Sertifikasi Awal'))
        kategori_risiko_input = st.text_input("Kategori Risiko", value=data_surat.get('kategori_risiko', 'Tinggi'))
        
        # Logika untuk menampilkan pilihan default dropdown
        pilihan_pelaksanaan = ["☑ Audit Lapangan (on-site)   ☐ Audit Jarak Jauh", "☐ Audit Lapangan (on-site)   ☑ Audit Jarak Jauh"]
        index_pelaksanaan = 0 if data_surat.get('pelaksanaan', '') == pilihan_pelaksanaan[0] else 1 if data_surat.get('pelaksanaan', '') == pilihan_pelaksanaan[1] else 0
        pelaksanaan_input = st.selectbox("Pelaksanaan Audit", pilihan_pelaksanaan, index=index_pelaksanaan)
        
    with col_b:
        tgl_surat_input = st.text_input("Tanggal Surat (Bawah)", value=data_surat.get('tgl_surat', '03 Maret 2025'))
        tgl_audit1_input = st.text_input("Tanggal Mulai", value=data_surat.get('tgl_mulai', '10 Maret 2025'))
        tgl_audit2_input = st.text_input("Tanggal Selesai", value=data_surat.get('tgl_selesai', '11 Maret 2025'))
        hari_audit_input = st.text_input("Jumlah Hari", value=data_surat.get('jumlah_hari', '2'))
        
    st.markdown("**Data Zoom (Kosongkan jika On-site):**")
    col_z1, col_z2, col_z3 = st.columns(3)
    with col_z1: link_zoom_input = st.text_input("Link Zoom", value=data_surat.get('link_zoom', '-'))
    with col_z2: id_zoom_input = st.text_input("Meeting ID", value=data_surat.get('id_zoom', '-'))
    with col_z3: pass_zoom_input = st.text_input("Passcode", value=data_surat.get('pass_zoom', '-'))

st.markdown("<br>", unsafe_allow_html=True)

# --- 5. TOMBOL AKSI UTAMA ---
col_btn1, col_btn2 = st.columns(2)
os.makedirs("output/word", exist_ok=True)
os.makedirs("output/pdf", exist_ok=True) # Folder baru untuk PDF

# Import library untuk PDF (Taruh di sini agar aman)
import pythoncom
from docx2pdf import convert

with col_btn1:
    if st.button("💾 Simpan Data & Generate Surat Tugas", use_container_width=True, type="primary"):
        try:
            # 1. UPDATE TABEL data_kontrak
            data_update_kontrak = {
                "Lead Auditor": lead_auditor_input,
                "Auditor": auditor_input,
                "Observer": observer_input
            }
            supabase.table('data_kontrak').update(data_update_kontrak).eq('id', pilihan_id).execute()
            
            # 2. SIMPAN/UPDATE TABEL data_surat
            data_update_surat = {
                "id_kontrak": pilihan_id,
                "Wakil Manajemen": wakil_manajemen_input,
                "No Tlp Wakil Manajemen": no_tlp_wm_input,
                "no_surat_tugas": no_surat_input,
                "no_surat_pemberitahuan": no_surat_pemberitahuan_input,
                "tipe_audit": tipe_audit_input,
                "kategori_risiko": kategori_risiko_input,
                "tgl_mulai": tgl_audit1_input,
                "tgl_selesai": tgl_audit2_input,
                "jumlah_hari": hari_audit_input,
                "pelaksanaan": pelaksanaan_input,
                "link_zoom": link_zoom_input,
                "id_zoom": id_zoom_input,
                "pass_zoom": pass_zoom_input,
                "tgl_surat": tgl_surat_input
            }
            
            cek_surat = supabase.table('data_surat').select("id").eq("id_kontrak", pilihan_id).execute()
            if cek_surat.data:
                supabase.table('data_surat').update(data_update_surat).eq("id_kontrak", pilihan_id).execute()
            else:
                supabase.table('data_surat').insert(data_update_surat).execute()

            # 3. LAPOR KE n8n
            try:
                data_n8n = data_update_kontrak.copy()
                data_n8n['id'] = pilihan_id
                requests.post(URL_WEBHOOK_N8N, json=data_n8n)
            except:
                pass 
                
            load_data_kontrak.clear()

            # 4. GENERATE WORD SURAT TUGAS
            doc = DocxTemplate("templates/surat_tugas_template.docx")
            context = {
                "no_surat": no_surat_input,
                "lead_auditor": lead_auditor_input,
                "auditor": auditor_input,
                "observer": observer_input,
                "nama_pt": data_terpilih.get('nama_pt', '-'),
                "alamat": data_terpilih.get('Alamat lengkap', '-'),
                "pic": wakil_manajemen_input, 
                "no_hp_pic": no_tlp_wm_input, 
                "tipe_audit": tipe_audit_input,
                "ruang_lingkup": data_terpilih.get('Ruang Lingkup', '-'),
                "kategori_risiko": kategori_risiko_input,
                "tanggal_audit1": tgl_audit1_input,
                "tanggal_audit2": tgl_audit2_input,
                "hari_audit": hari_audit_input,
                "pelaksanaan_audit": pelaksanaan_input,
                "link_zoom": link_zoom_input,
                "id_zoom": id_zoom_input,
                "password_zoom": pass_zoom_input,
                "tanggal_surat": tgl_surat_input
            }
            doc.render(context)
            nama_file_word = f"Surat_Tugas_{data_terpilih['nama_pt']}.docx"
            nama_file_pdf = f"Surat_Tugas_{data_terpilih['nama_pt']}.pdf"
            path_word = f"output/word/{nama_file_word}"
            path_pdf = f"output/pdf/{nama_file_pdf}"
            
            doc.save(path_word) # Simpan Word
            
            # 5. CONVERT KE PDF
            with st.spinner('Mengubah ke PDF... Mohon tunggu sebentar...'):
                pythoncom.CoInitialize() # Wajib untuk Windows
                convert(path_word, path_pdf)
            
            st.success("✅ Surat Tugas Berhasil Dibuat (Word & PDF)!")
            
            # 6. TOMBOL DOWNLOAD
            col_dw1, col_dw2 = st.columns(2)
            with col_dw1:
                with open(path_word, "rb") as file:
                    st.download_button("⬇️ Download Word", data=file, file_name=nama_file_word, use_container_width=True)
            with col_dw2:
                with open(path_pdf, "rb") as file:
                    st.download_button("⬇️ Download PDF", data=file, file_name=nama_file_pdf, mime="application/pdf", use_container_width=True)
                    
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")

with col_btn2:
    if st.button("📢 Generate Surat Pemberitahuan", use_container_width=True):
        try:
            doc = DocxTemplate("templates/pemberitahuan_template.docx")
            # Menyuntikkan data yang sama persis ke template yang berbeda!
            context = {
                "no_surat_pemberitahuan": no_surat_pemberitahuan_input,
                "nama_pt": data_terpilih.get('nama_pt', '-'),
                "alamat": data_terpilih.get('Alamat lengkap', '-'),
                "ruang_lingkup": data_terpilih.get('Ruang Lingkup', '-'),
                "kategori_risiko": kategori_risiko_input,
                "tipe_audit": tipe_audit_input,
                "tanggal_audit": f"{tgl_audit1_input} s/d {tgl_audit2_input}",
                "lead_auditor": lead_auditor_input,
                "auditor": auditor_input,
                "observer": observer_input,
                "tanggal_surat": tgl_surat_input
            }
            doc.render(context)
            nama_file_word = f"Pemberitahuan_{data_terpilih['nama_pt']}.docx"
            nama_file_pdf = f"Pemberitahuan_{data_terpilih['nama_pt']}.pdf"
            path_word = f"output/word/{nama_file_word}"
            path_pdf = f"output/pdf/{nama_file_pdf}"
            
            doc.save(path_word)
            
            # CONVERT KE PDF
            with st.spinner('Mengubah ke PDF... Mohon tunggu sebentar...'):
                pythoncom.CoInitialize()
                convert(path_word, path_pdf)
                
            st.success("✅ Surat Pemberitahuan Berhasil Dibuat (Word & PDF)!")
            
            col_dw1, col_dw2 = st.columns(2)
            with col_dw1:
                with open(path_word, "rb") as file:
                    st.download_button("⬇️ Download Word", data=file, file_name=nama_file_word, use_container_width=True)
            with col_dw2:
                with open(path_pdf, "rb") as file:
                    st.download_button("⬇️ Download PDF", data=file, file_name=nama_file_pdf, mime="application/pdf", use_container_width=True)
                    
        except Exception as e:
            st.error(f"Gagal membuat surat: {e}")