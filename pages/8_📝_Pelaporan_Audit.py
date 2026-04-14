import streamlit as st
import pandas as pd

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Pelaporan Audit | DTM", page_icon="📝", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Titillium+Web:wght@300;400;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined');
    html, body, [class*="css"] { font-family: 'Titillium Web', sans-serif !important; background-color: #f8fafc; }
    [data-testid="stSidebar"] { background-color: #1e3a8a !important; }
    [data-testid="stSidebar"] * { color: white !important; }
    
    .audit-card {
        background-color: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; margin-bottom: 20px;
        border-left: 5px solid #3b82f6;
    }
    .question-title { font-size: 18px; font-weight: 600; color: #1e293b; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='color: #1e3a8a; font-weight: 700;'><span class='material-symbols-outlined' style='vertical-align: middle; font-size: 35px;'>fact_check</span> E-Audit Checklist</h2>", unsafe_allow_html=True)
st.write("Formulir pelaporan audit digital terintegrasi.")
st.markdown("<hr>", unsafe_allow_html=True)

# --- SIMULASI DATA BANK SOAL (Nanti bisa diperbanyak) ---
bank_soal = {
    "PPIU": [
        "1. Apakah biro perjalanan wisata memiliki izin resmi sebagai PPIU dari Kementerian Agama?",
        "2. Apakah PPIU memiliki kantor tetap dan fasilitas pelayanan yang memadai?",
        "3. Apakah terdapat SOP tertulis mengenai pendaftaran dan pemberangkatan jamaah umrah?"
    ],
    "Hotel": [
        "1. Apakah hotel memiliki area lobi yang sesuai dengan standar bintang yang diajukan?",
        "2. Apakah kebersihan kamar dan kamar mandi dikelola dengan SOP yang jelas?",
        "3. Apakah fasilitas keamanan (APAR, Jalur Evakuasi) tersedia dan berfungsi baik?"
    ]
}

# --- STEP 1: PILIH KLIEN ---
st.markdown("<div class='audit-card'>", unsafe_allow_html=True)
st.markdown("#### 🏢 Informasi Klien & Penugasan")
col1, col2 = st.columns(2)
with col1:
    # Simulasi pilihan klien (Nanti ditarik dari Supabase)
    klien_terpilih = st.selectbox("Pilih Klien yang Diaudit", ["-- Pilih Klien --", "PT Amanah Perkasa (PPIU)", "Hotel Grand Melia (Hotel)"])
with col2:
    nama_auditor = st.text_input("Nama Auditor", "Budi Cahyono")
    tgl_audit = st.date_input("Tanggal Pelaksanaan Audit")
st.markdown("</div>", unsafe_allow_html=True)

# --- STEP 2: MUNCULKAN CHECKLIST OTOMATIS ---
if klien_terpilih != "-- Pilih Klien --":
    # Deteksi ruang lingkup dari nama klien (Simulasi)
    ruang_lingkup = "PPIU" if "PPIU" in klien_terpilih else "Hotel"
    
    st.markdown(f"<h3 style='color: #1e3a8a; margin-top: 30px;'>📋 Daftar Periksa: {ruang_lingkup}</h3>", unsafe_allow_html=True)
    
    # Ambil soal sesuai ruang lingkup
    soal_audit = bank_soal[ruang_lingkup]
    
    # Form Audit
    with st.form("form_audit"):
        jawaban_auditor = {} # Untuk menyimpan semua jawaban
        
        for i, soal in enumerate(soal_audit):
            st.markdown(f"<div class='audit-card' style='border-left-color: #f59e0b;'>", unsafe_allow_html=True)
            st.markdown(f"<div class='question-title'>{soal}</div>", unsafe_allow_html=True)
            
            c_nilai, c_catatan = st.columns([1, 2])
            with c_nilai:
                nilai = st.radio(
                    "Hasil Penilaian:", 
                    ["Sesuai (S)", "Minor (Mi)", "Mayor (Ma)", "Observasi (OB)", "N/A"], 
                    key=f"nilai_{i}",
                    horizontal=True
                )
            with c_catatan:
                catatan = st.text_area("Catatan / Bukti Obyektif:", key=f"catatan_{i}", height=68, placeholder="Tuliskan bukti dokumen atau temuan lapangan...")
            
            # Simpan ke dictionary
            jawaban_auditor[f"soal_{i}"] = {"pertanyaan": soal, "nilai": nilai, "catatan": catatan}
            st.markdown("</div>", unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        submit_audit = st.form_submit_button("💾 Simpan Laporan Audit", type="primary", use_container_width=True)
        
        if submit_audit:
            st.success("✅ Laporan Audit berhasil disimpan ke Database!")
            # Di sini nanti kita masukkan script untuk mengirim 'jawaban_auditor' ke Supabase
            st.json(jawaban_auditor) # Menampilkan format data yang akan dikirim ke database
