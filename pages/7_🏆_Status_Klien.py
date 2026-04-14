import streamlit as st
import pandas as pd
from supabase import create_client
import datetime

# --- KONFIGURASI HALAMAN & CSS GLOBAL ---
st.set_page_config(page_title="Status Klien | DTM", page_icon="🏆", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Titillium+Web:wght@300;400;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined');
    html, body, [class*="css"] { font-family: 'Titillium Web', sans-serif !important; }
    [data-testid="stSidebar"] { background-color: #1e3a8a !important; }
    [data-testid="stSidebar"] * { color: white !important; }
    
    .card-container { 
        background-color: white; padding: 25px; border-radius: 12px; 
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border: 1px solid #e2e8f0; margin-bottom: 20px; 
    }
    .table-header {
        background-color: #f0f4f8; padding: 12px 10px; border-radius: 8px;
        color: #1e3a8a; font-weight: 700; font-size: 14px; margin-bottom: 15px; border: 1px solid #e2e8f0;
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

# --- FUNGSI TARIK DATA ---
def load_data_kontrak():
    res = supabase.table('data_kontrak').select("*").execute()
    return res.data

def load_data_sertifikasi():
    res = supabase.table('data_sertifikasi').select("*").execute()
    return res.data

# --- INISIALISASI SESSION STATE ---
if 'show_form_sertifikat' not in st.session_state:
    st.session_state.show_form_sertifikat = False
if 'detail_klien' not in st.session_state:
    st.session_state.detail_klien = None

# --- HEADER ---
st.markdown("<h2 style='color: #1e3a8a; font-weight: 700;'>Status Klien & Survailen</h2>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# --- TAMPILAN KARTU DETAIL KLIEN ---
if st.session_state.detail_klien is not None:
    row = st.session_state.detail_klien
    st.markdown("<div class='card-container' style='border-top: 5px solid #1e3a8a;'>", unsafe_allow_html=True)
    
    col_title, col_close = st.columns([4, 1])
    with col_title:
        st.markdown(f"<h3 style='color: #1e3a8a; margin-top: 0;'><span class='material-symbols-outlined' style='vertical-align: middle;'>corporate_fare</span> {row['nama_pt']}</h3>", unsafe_allow_html=True)
    with col_close:
        if st.button("❌ Tutup Detail", use_container_width=True):
            st.session_state.detail_klien = None
            st.rerun()
            
    st.markdown("<hr style='margin-top: 5px; margin-bottom: 20px;'>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<h5 style='color: #1e3a8a;'>📌 Informasi Perusahaan</h5>", unsafe_allow_html=True)
        # Menambahkan Nama Marketing (Pastikan nama kolom di Supabase sesuai, misal 'Nama Marketing' atau 'nama_marketing')
        st.write(f"**Nama Marketing:** {row.get('Nama Marketing', '-')}") 
        st.write(f"**Alamat:** {row.get('Alamat lengkap', '-')}")
        st.write(f"**Ruang Lingkup:** {row.get('Ruang Lingkup', '-')}")
        st.write(f"**Wakil Manajemen:** {row.get('Wakil Manajemen', '-')}")
        st.write(f"**No Tlp Wakil Manajemen:** {row.get('No Tlp Wakil Manajemen', '-')}")
        
    with c2:
        st.markdown("<h5 style='color: #1e3a8a;'>🏆 Informasi Sertifikasi</h5>", unsafe_allow_html=True)
        st.write(f"**No Sertifikat:** {row.get('no_sertifikat', '-')}")
        st.write(f"**Tanggal Terbit:** {row.get('tgl_terbit', '-')}")
        st.write(f"**Jadwal Survailen:** {row.get('tgl_survailen', '-')}")
        
        # Menampilkan Riwayat Tanggal (Hanya muncul jika datanya ada)
        if row.get('tgl_pembekuan'):
            st.markdown(f"<span style='color: #ea580c;'>**Tgl Pembekuan:** {row.get('tgl_pembekuan')}</span>", unsafe_allow_html=True)
        if row.get('tgl_pengaktifan_kembali'):
            st.markdown(f"<span style='color: #16a34a;'>**Tgl Dipulihkan:** {row.get('tgl_pengaktifan_kembali')}</span>", unsafe_allow_html=True)
        if row.get('tgl_pencabutan'):
            st.markdown(f"<span style='color: #dc2626;'>**Tgl Pencabutan:** {row.get('tgl_pencabutan')}</span>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        status = row.get('status', '-')
        if status == 'Tersertifikasi':
            badge = "<span style='background-color: #dcfce7; color: #16a34a; padding: 5px 15px; border-radius: 12px; font-weight: bold; font-size: 13px;'>Tersertifikasi</span>"
        elif status == 'Dibekukan':
            badge = "<span style='background-color: #ffedd5; color: #ea580c; padding: 5px 15px; border-radius: 12px; font-weight: bold; font-size: 13px;'>Dibekukan</span>"
        else:
            badge = "<span style='background-color: #fee2e2; color: #dc2626; padding: 5px 15px; border-radius: 12px; font-weight: bold; font-size: 13px;'>Dicabut</span>"
        st.markdown(f"**Status Saat Ini:** {badge}", unsafe_allow_html=True)

    st.markdown("<br><h5 style='color: #1e3a8a;'>👥 Tim Audit Terakhir</h5>", unsafe_allow_html=True)
    c3, c4, c5 = st.columns(3)
    c3.info(f"**Lead Auditor:**\n\n{row.get('Lead Auditor', '-')}")
    c4.info(f"**Auditor:**\n\n{row.get('Auditor', '-')}")
    c5.info(f"**Observer:**\n\n{row.get('Observer', '-')}")
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()


# --- AMBIL DATA ---
data_kontrak = load_data_kontrak()
data_sertifikasi = load_data_sertifikasi()

df_gabungan = pd.DataFrame()
if data_sertifikasi:
    df_sertifikasi = pd.DataFrame(data_sertifikasi)
    df_kontrak = pd.DataFrame(data_kontrak)
    df_gabungan = pd.merge(df_sertifikasi, df_kontrak, left_on='id_kontrak', right_on='id')

# --- MEMBUAT 3 TAB (SUBMENU) ---
tab1, tab2, tab3 = st.tabs(["✅ Klien Tersertifikasi", "⏸️ Klien Dibekukan", "❌ Klien Dicabut"])

# ==========================================
# TAB 1: KLIEN TERSERTIFIKASI
# ==========================================
with tab1:
    st.markdown("<div class='card-container'>", unsafe_allow_html=True)
    
    col_title, col_btn = st.columns([4, 1])
    with col_title:
        st.markdown("<h4 style='color: #1e3a8a; margin: 0;'><span class='material-symbols-outlined' style='vertical-align: middle;'>verified_user</span> Klien Tersertifikasi LSUHK</h4>", unsafe_allow_html=True)
    with col_btn:
        if st.button("➕ Klien Baru", use_container_width=True, type="primary"):
            st.session_state.show_form_sertifikat = not st.session_state.show_form_sertifikat
            st.rerun()
            
    st.markdown("<hr style='margin-top: 15px; margin-bottom: 20px;'>", unsafe_allow_html=True)
    
    if st.session_state.show_form_sertifikat:
        st.info("Lengkapi data di bawah ini untuk menerbitkan sertifikat baru.")
        id_sudah_sertifikasi = [s['id_kontrak'] for s in data_sertifikasi] if data_sertifikasi else []
        pt_belum_sertifikasi = [k for k in data_kontrak if k['id'] not in id_sudah_sertifikasi]
        
        if not pt_belum_sertifikasi:
            st.warning("Semua klien di database kontrak sudah memiliki sertifikat.")
        else:
            with st.form("form_sertifikat_baru", clear_on_submit=True):
                pilihan_pt = {f"{k['id']} - {k['nama_pt']}": k['id'] for k in pt_belum_sertifikasi}
                pt_terpilih = st.selectbox("Pilih Klien", list(pilihan_pt.keys()))
                
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    no_sertifikat = st.text_input("Nomor Sertifikat")
                with col_s2:
                    tgl_terbit = st.date_input("Tanggal Terbit Sertifikat")
                
                submit_sertifikat = st.form_submit_button("💾 Simpan & Hitung Jadwal Survailen", type="primary")
                
                if submit_sertifikat:
                    tgl_survailen = tgl_terbit + datetime.timedelta(days=365)
                    
                    # 1. Simpan ke tabel data_sertifikasi
                    supabase.table('data_sertifikasi').insert({
                        "id_kontrak": pilihan_pt[pt_terpilih],
                        "no_sertifikat": no_sertifikat,
                        "tgl_terbit": str(tgl_terbit),
                        "tgl_survailen": str(tgl_survailen),
                        "status": "Tersertifikasi"
                    }).execute()
                    
                    # 2. UPDATE OTOMATIS ke tabel data_kontrak
                    # Ubah format tanggal jadi DD-MM-YYYY agar rapi di database
                    tgl_terbit_str = tgl_terbit.strftime("%d-%m-%Y")
                    supabase.table('data_kontrak').update({
                        "Terbit Sertifikat": tgl_terbit_str
                    }).eq("id", pilihan_pt[pt_terpilih]).execute()
                    
                    st.session_state.show_form_sertifikat = False
                    st.rerun()

    if df_gabungan.empty:
        st.write("Belum ada data klien tersertifikasi.")
    else:
        df_aktif = df_gabungan[df_gabungan['status'] == 'Tersertifikasi']
        if df_aktif.empty:
            st.write("Belum ada data klien tersertifikasi.")
        else:
            st.markdown("""
            <div class='table-header'>
                <div style='display: flex;'>
                    <div style='flex: 2.5;'>Nama Organisasi</div>
                    <div style='flex: 2;'>Skema & No. Sertifikat</div>
                    <div style='flex: 1.5;'>Jadwal Survailen</div>
                    <div style='flex: 1.5;'>Status</div>
                    <div style='flex: 2.5; text-align: center;'>Aksi</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            for index, row in df_aktif.iterrows():
                c1, c2, c3, c4, c5 = st.columns([2.5, 2, 1.5, 1.5, 2.5])
                c1.write(f"**{row['nama_pt']}**")
                c2.write(row['no_sertifikat'])
                
                tgl_surv = datetime.datetime.strptime(row['tgl_survailen'], '%Y-%m-%d').date()
                c3.write(tgl_surv.strftime('%d-%m-%Y'))
                
                c4.markdown("<span style='background-color: #dcfce7; color: #16a34a; padding: 5px 10px; border-radius: 5px; font-weight: bold; font-size: 12px;'>Tersertifikasi</span>", unsafe_allow_html=True)
                
                with c5:
                    btn1, btn2, btn3 = st.columns(3)
                    with btn1:
                        if st.button("🔍", key=f"det_{row['id_x']}", help="Lihat Detail Klien"):
                            st.session_state.detail_klien = row
                            st.rerun()
                    with btn2:
                        if st.button("✅", key=f"surv_{row['id_x']}", help="Survailen Selesai (Perpanjang 1 Tahun)"):
                            tgl_baru = tgl_surv + datetime.timedelta(days=365)
                            supabase.table('data_sertifikasi').update({"tgl_survailen": str(tgl_baru)}).eq("id", row['id_x']).execute()
                            st.rerun()
                    with btn3:
                        if st.button("⏸️", key=f"beku_{row['id_x']}", help="Bekukan Klien"):
                            # OTOMATIS MENCATAT TANGGAL HARI INI SAAT DIBEKUKAN
                            hari_ini = str(datetime.date.today())
                            supabase.table('data_sertifikasi').update({
                                "status": "Dibekukan",
                                "tgl_pembekuan": hari_ini
                            }).eq("id", row['id_x']).execute()
                            st.rerun()
                st.markdown("<hr style='margin-top: 5px; margin-bottom: 5px; border-color: #f1f5f9;'>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ==========================================
# TAB 2: KLIEN DIBEKUKAN
# ==========================================
with tab2:
    st.markdown("<div class='card-container'>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #ea580c; margin-bottom: 20px;'><span class='material-symbols-outlined' style='vertical-align: middle;'>block</span> Klien Dibekukan</h4>", unsafe_allow_html=True)
    
    if df_gabungan.empty:
        st.write("Belum ada data.")
    else:
        df_beku = df_gabungan[df_gabungan['status'] == 'Dibekukan']
        if df_beku.empty:
            st.write("Tidak ada klien yang dibekukan saat ini.")
        else:
            st.markdown("""
            <div class='table-header' style='background-color: #ffedd5; color: #ea580c; border-color: #fdba74;'>
                <div style='display: flex;'>
                    <div style='flex: 2.5;'>Nama Organisasi</div>
                    <div style='flex: 2;'>No. Sertifikat</div>
                    <div style='flex: 1.5;'>Jadwal Survailen</div>
                    <div style='flex: 1.5;'>Status</div>
                    <div style='flex: 2.5; text-align: center;'>Tindak Lanjut</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            for index, row in df_beku.iterrows():
                c1, c2, c3, c4, c5 = st.columns([2.5, 2, 1.5, 1.5, 2.5])
                c1.write(f"**{row['nama_pt']}**")
                c2.write(row['no_sertifikat'])
                
                tgl_surv = datetime.datetime.strptime(row['tgl_survailen'], '%Y-%m-%d').date()
                c3.markdown(f"<span style='color: red; font-weight: bold;'>{tgl_surv.strftime('%d-%m-%Y')}</span>", unsafe_allow_html=True)
                
                c4.markdown("<span style='background-color: #ffedd5; color: #ea580c; padding: 5px 10px; border-radius: 5px; font-weight: bold; font-size: 12px;'>Dibekukan</span>", unsafe_allow_html=True)
                
                with c5:
                    btn1, btn2, btn3 = st.columns(3)
                    with btn1:
                        if st.button("🔍", key=f"det_{row['id_x']}", help="Lihat Detail Klien"):
                            st.session_state.detail_klien = row
                            st.rerun()
                    with btn2:
                        if st.button("✅", key=f"pulih_{row['id_x']}", help="Pulihkan (Survailen Selesai)"):
                            # OTOMATIS MENCATAT TANGGAL PEMULIHAN
                            hari_ini = str(datetime.date.today())
                            tgl_baru = tgl_surv + datetime.timedelta(days=365)
                            supabase.table('data_sertifikasi').update({
                                "status": "Tersertifikasi", 
                                "tgl_survailen": str(tgl_baru),
                                "tgl_pengaktifan_kembali": hari_ini
                            }).eq("id", row['id_x']).execute()
                            st.rerun()
                    with btn3:
                        if st.button("❌", key=f"cabut_{row['id_x']}", help="Cabut Sertifikat Permanen"):
                            # OTOMATIS MENCATAT TANGGAL PENCABUTAN
                            hari_ini = str(datetime.date.today())
                            supabase.table('data_sertifikasi').update({
                                "status": "Dicabut",
                                "tgl_pencabutan": hari_ini
                            }).eq("id", row['id_x']).execute()
                            st.rerun()
                st.markdown("<hr style='margin-top: 5px; margin-bottom: 5px; border-color: #f1f5f9;'>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ==========================================
# TAB 3: KLIEN DICABUT
# ==========================================
with tab3:
    st.markdown("<div class='card-container'>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #dc2626; margin-bottom: 20px;'><span class='material-symbols-outlined' style='vertical-align: middle;'>cancel</span> Klien Dicabut (Tidak Aktif)</h4>", unsafe_allow_html=True)
    
    if df_gabungan.empty:
        st.write("Belum ada data.")
    else:
        df_cabut = df_gabungan[df_gabungan['status'] == 'Dicabut']
        if df_cabut.empty:
            st.write("Tidak ada klien yang dicabut saat ini.")
        else:
            st.markdown("""
            <div class='table-header' style='background-color: #fee2e2; color: #dc2626; border-color: #fca5a5;'>
                <div style='display: flex;'>
                    <div style='flex: 3;'>Nama Organisasi</div>
                    <div style='flex: 3;'>No. Sertifikat</div>
                    <div style='flex: 2;'>Status</div>
                    <div style='flex: 2; text-align: center;'>Aksi</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            for index, row in df_cabut.iterrows():
                c1, c2, c3, c4 = st.columns([3, 3, 2, 2])
                c1.write(f"**{row['nama_pt']}**")
                c2.write(row['no_sertifikat'])
                c3.markdown("<span style='background-color: #fee2e2; color: #dc2626; padding: 5px 10px; border-radius: 5px; font-weight: bold; font-size: 12px;'>Dicabut</span>", unsafe_allow_html=True)
                with c4:
                    if st.button("🔍 Lihat Detail", key=f"det_{row['id_x']}", use_container_width=True):
                        st.session_state.detail_klien = row
                        st.rerun()
                st.markdown("<hr style='margin-top: 5px; margin-bottom: 5px; border-color: #f1f5f9;'>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
