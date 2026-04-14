import streamlit as st

# --- CEK LOGIN ---
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("🔒 Anda belum login. Silakan kembali ke halaman utama (Home) untuk login.")
    st.stop()

import pandas as pd
from supabase import create_client
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

    html, body, [class*="css"] { font-family: 'Titillium Web', sans-serif !important; }
    [data-testid="stSidebar"] { background-color: #1a3673 !important; border-right: none !important; }
    [data-testid="stSidebar"] * { color: white !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='color: #1e3a8a; font-weight: 700;'><span class='material-symbols-outlined' style='vertical-align: middle; font-size: 35px;'>assignment</span> Generator Surat Tugas & Pemberitahuan</h2>", unsafe_allow_html=True)

# --- 2. AMBIL DATA DARI DATABASE ---
@st.cache_data(ttl=600)
def load_data_kontrak():
    response = supabase.table('data_kontrak').select("*").order("id", desc=True).execute()
    return pd.DataFrame(response.data)

def load_data_surat(id_kontrak):
    response = supabase.table('data_surat').select("*").eq("id_kontrak", id_kontrak).execute()
    if response.data:
        return response.data[0] # Ambil data surat jika sudah ada
    return {} # Kosong jika belum pernah dibuat

df = load_data_kontrak()

if st.button("🔄 Refresh Data Database"):
    load_data_kontrak.clear()
    st.rerun()

if df.empty:
    st.warning("Database masih kosong.")
    st.stop()

# --- 3. PILIH PERUSAHAAN ---
with st.container(border=True):
    st.markdown("#### 1. Pilih Perusahaan")
    # Karena di Supabase nama kolomnya mungkin berbeda, kita sesuaikan
    # Asumsi kolom nama klien di Supabase adalah 'nama_klien' atau 'nama_pt'
    col_nama = 'nama_klien' if 'nama_klien' in df.columns else 'nama_pt' if 'nama_pt' in df.columns else None
    
    if col_nama:
        df['label_pilihan'] = df['id'].astype(str) + " - " + df[col_nama].astype(str)
        pilihan_label = st.selectbox("Pilih PT yang akan dibuatkan surat:", df['label_pilihan'].tolist())

        pilihan_id = int(pilihan_label.split(" - ")[0])
        data_terpilih = df[df['id'] == pilihan_id].iloc[0].fillna('-')

        # Ambil data surat dari tabel kedua (data_surat) berdasarkan id_kontrak
        data_surat = load_data_surat(pilihan_id)
    else:
        st.error("Kolom nama klien tidak ditemukan di database.")
        st.stop()

st.markdown("<br>", unsafe_allow_html=True)

# --- 4. FORM EDIT DATA & GENERATE ---
with st.container(border=True):
    st.markdown("#### 2. Lengkapi Data & Buat Dokumen")

    # A. Data Paten (Tabel data_kontrak - Terkunci)
    st.markdown("**Data Perusahaan (Terkunci)**")
    col_pt1, col_pt2 = st.columns(2)
    with col_pt1:
        st.text_input("Nama PT", value=data_terpilih.get(col_nama, '-'), disabled=True)
    with col_pt2:
        # Asumsi kolom alamat di Supabase adalah 'alamat_klien' atau 'Alamat lengkap'
        col_alamat = 'alamat_klien' if 'alamat_klien' in data_terpilih else 'Alamat lengkap' if 'Alamat lengkap' in data_terpilih else '-'
        st.text_input("Alamat Lengkap", value=data_terpilih.get(col_alamat, '-'), disabled=True)

    st.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)

    # B. Data Tim Audit (Tabel data_kontrak - Bisa Diedit)
    st.markdown("**Data Tim Audit & Wakil Manajemen (Bisa Diedit)**")

    # --- LOGIKA MENGAMBIL DATA TIM DARI DATABASE ---
    @st.cache_data(ttl=60)
    def get_pilihan_auditor():
        res = supabase.table('data_tim').select("*").eq('peran', 'Tim Auditor').eq('status', 'Aktif').execute()
        pilihan = ["-"]
        for t in res.data:
            telp = t.get('no_telp', '')
            if telp:
                pilihan.append(f"{t['nama_lengkap']} [{telp}]")
            else:
                pilihan.append(t['nama_lengkap'])
        return pilihan

    daftar_auditor = get_pilihan_auditor()

    def cari_index(nilai_dicari, daftar_pilihan):
        if nilai_dicari in daftar_pilihan:
            return daftar_pilihan.index(nilai_dicari)
        return 0

    col_edit1, col_edit2 = st.columns(2)
    with col_edit1:
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

# --- 5. TOMBOL AKSI UTAMA ---
col_btn1, col_btn2 = st.columns(2)
os.makedirs("output/word", exist_ok=True)

# Asumsi kolom ruang lingkup
col_ruang_lingkup = 'ruang_lingkup' if 'ruang_lingkup' in data_terpilih else 'Ruang Lingkup' if 'Ruang Lingkup' in data_terpilih else '-'

with col_btn1:
    if st.button("💾 Simpan Data & Generate Surat Tugas (Word)", use_container_width=True, type="primary"):
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
                if "MASUKKAN-ID-WEBHOOK" not in URL_WEBHOOK_N8N:
                    requests.post(URL_WEBHOOK_N8N, json=data_n8n)
            except:
                pass 
                
            load_data_kontrak.clear()

            # 4. GENERATE WORD SURAT TUGAS
            template_path = "templates/surat_tugas_template.docx"
            if not os.path.exists(template_path):
                st.error(f"⚠️ Template tidak ditemukan di `{template_path}`")
            else:
                doc = DocxTemplate(template_path)
                context = {
                    "no_surat": no_surat_input,
                    "lead_auditor": lead_auditor_input,
                    "auditor": auditor_input,
                    "observer": observer_input,
                    "nama_pt": data_terpilih.get(col_nama, '-'),
                    "alamat": data_terpilih.get(col_alamat, '-'),
                    "pic": wakil_manajemen_input, 
                    "no_hp_pic": no_tlp_wm_input, 
                    "tipe_audit": tipe_audit_input,
                    "ruang_lingkup": data_terpilih.get(col_ruang_lingkup, '-'),
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
                nama_file_word = f"Surat_Tugas_{data_terpilih.get(col_nama, 'Klien')}.docx"
                path_word = f"output/word/{nama_file_word}"
                
                doc.save(path_word) # Simpan Word
                
                st.success("✅ Data Tersimpan & Surat Tugas (Word) Berhasil Dibuat!")
                
                with open(path_word, "rb") as file:
                    st.download_button("⬇️ Download Surat Tugas (Word)", data=file, file_name=nama_file_word, use_container_width=True)
                    
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")

with col_btn2:
    if st.button("📢 Generate Surat Pemberitahuan (Word)", use_container_width=True):
        try:
            template_path = "templates/pemberitahuan_template.docx"
            if not os.path.exists(template_path):
                st.error(f"⚠️ Template tidak ditemukan di `{template_path}`")
            else:
                doc = DocxTemplate(template_path)
                context = {
                    "no_surat_pemberitahuan": no_surat_pemberitahuan_input,
                    "nama_pt": data_terpilih.get(col_nama, '-'),
                    "alamat": data_terpilih.get(col_alamat, '-'),
                    "ruang_lingkup": data_terpilih.get(col_ruang_lingkup, '-'),
                    "kategori_risiko": kategori_risiko_input,
                    "tipe_audit": tipe_audit_input,
                    "tanggal_audit": f"{tgl_audit1_input} s/d {tgl_audit2_input}",
                    "lead_auditor": lead_auditor_input,
                    "auditor": auditor_input,
                    "observer": observer_input,
                    "tanggal_surat": tgl_surat_input
                }
                doc.render(context)
                nama_file_word = f"Pemberitahuan_{data_terpilih.get(col_nama, 'Klien')}.docx"
                path_word = f"output/word/{nama_file_word}"
                
                doc.save(path_word)
                
                st.success("✅ Surat Pemberitahuan (Word) Berhasil Dibuat!")
                
                with open(path_word, "rb") as file:
                    st.download_button("⬇️ Download Surat Pemberitahuan (Word)", data=file, file_name=nama_file_word, use_container_width=True)
                    
        except Exception as e:
            st.error(f"Gagal membuat surat: {e}")
