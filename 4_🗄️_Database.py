import streamlit as st
import pandas as pd
from supabase import create_client, Client

# --- 1. KONFIGURASI SUPABASE ---
# GANTI DENGAN URL DAN KEY MILIK ANDA!
SUPABASE_URL = "https://ehfpmlwmdnjtxrfqdgkc.supabase.co" 
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVoZnBtbHdtZG5qdHhyZnFkZ2tjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ1MDc1NjMsImV4cCI6MjA5MDA4MzU2M30.LPiPaAIm2MhuywLnmSTegWO0-1gcPuVww8abFhTAin8" 

@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_connection()

st.set_page_config(page_title="Database Kontrak", page_icon="🗄️", layout="wide")
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
st.title("🗄️ Manajemen Database Kontrak")

# --- 2. FUNGSI TARIK DATA ---
def load_data():
    # Tarik data dan urutkan dari yang terbaru (ID terbesar)
    response = supabase.table('data_kontrak').select("*").order("id", desc=True).execute()
    return pd.DataFrame(response.data)

df = load_data()

if df.empty:
    st.info("Database masih kosong.")
    st.stop() # Berhenti di sini kalau kosong

# --- 3. FITUR PENCARIAN (SEARCH) ---
st.subheader("🔍 Cari & Lihat Data")
kata_kunci = st.text_input("Ketik pencarian (Nama PT, Marketing, Status, dll):", "")

# Logika Filter Pencarian
if kata_kunci:
    # Mencari kata kunci di SEMUA kolom
    mask = df.astype(str).apply(lambda x: x.str.contains(kata_kunci, case=False)).any(axis=1)
    df_tampil = df[mask]
else:
    df_tampil = df

st.dataframe(df_tampil, use_container_width=True)
st.caption(f"Menampilkan {len(df_tampil)} dari total {len(df)} data kontrak.")

st.divider()

# --- 4. FITUR UPDATE SEMUA KOLOM ---
st.subheader("✏️ Edit / Lengkapi Data")

# Bikin opsi pilihan "ID - Nama PT" biar gampang nyarinya
df['label_pilihan'] = df['id'].astype(str) + " - " + df['nama_pt'].astype(str)
pilihan_label = st.selectbox("Pilih Data yang akan diedit:", df['label_pilihan'].tolist())

# Ekstrak angka ID dari pilihan (mengambil angka sebelum tanda strip)
pilihan_id = int(pilihan_label.split(" - ")[0])

# Ambil data lama berdasarkan ID terpilih
data_terpilih = df[df['id'] == pilihan_id].iloc[0].fillna('')

with st.form("form_update_lengkap"):
    st.info(f"🏢 Sedang mengedit: **{data_terpilih.get('nama_pt', '')}**")
    
    # MENGGUNAKAN TABS AGAR RAPI
    tab1, tab2, tab3, tab4 = st.tabs(["🏢 Info Perusahaan", "📝 Detail Kontrak & Pembayaran", "🕵️ Tim & Jadwal Audit", "📜 Sertifikat"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            nama_pt = st.text_input("Nama PT (nama_pt)", value=str(data_terpilih.get('nama_pt', '')))
            pic = st.text_input("PIC", value=str(data_terpilih.get('PIC', '')))
            no_hp_pic = st.text_input("No Hp PIC", value=str(data_terpilih.get('No Hp PIC', '')))
        with col2:
            alamat = st.text_area("Alamat Lengkap", value=str(data_terpilih.get('Alamat lengkap', '')))
            lokasi = st.text_input("Lokasi", value=str(data_terpilih.get('Lokasi', '')))
            
    with tab2:
        col3, col4 = st.columns(2)
        with col3:
            tgl_kontrak = st.text_input("Tanggal Kontrak", value=str(data_terpilih.get('Tenggal Kontrak', '')))
            skema = st.text_input("Skema", value=str(data_terpilih.get('Skema', '')))
            ruang_lingkup = st.text_area("Ruang Lingkup", value=str(data_terpilih.get('Ruang Lingkup', '')))
            harga = st.text_input("Harga Sertifikasi Awal", value=str(data_terpilih.get('Harga Sertifikasi Awal', '')))
        with col4:
            marketing = st.text_input("Marketing", value=str(data_terpilih.get('Marketing', '')))
            no_wa_marketing = st.text_input("No Wa Marketing", value=str(data_terpilih.get('No Wa Marketing', '')))
            status = st.text_input("Status", value=str(data_terpilih.get('Status', '')))
            pem_awal = st.text_input("Pembayaran Awal", value=str(data_terpilih.get('Pembayaran Awal', '')))
            pem_surv1 = st.text_input("Pembayaran Survailen 1", value=str(data_terpilih.get('Pembayaran Survailen 1', '')))
            pem_surv2 = st.text_input("Pembayaran Survailen 2", value=str(data_terpilih.get('Pembayaran Survailen 2', '')))
            
    with tab3:
        col5, col6 = st.columns(2)
        with col5:
            kajian = st.text_input("Kajian", value=str(data_terpilih.get('Kajian', '')))
            surat_tugas = st.text_input("Surat Tugas", value=str(data_terpilih.get('Surat Tugas', '')))
            tgl_audit = st.text_input("Tanggal Audit", value=str(data_terpilih.get('Tanggal Audit', '')))
            pelaporan = st.text_input("Pelaporan Audit", value=str(data_terpilih.get('Pelaporan Audit', '')))
        with col6:
            lead_auditor = st.text_input("Lead Auditor", value=str(data_terpilih.get('Lead Auditor', '')))
            auditor = st.text_input("Auditor", value=str(data_terpilih.get('Auditor', '')))
            observer = st.text_input("Observer", value=str(data_terpilih.get('Observer', '')))
            
    with tab4:
        col7, col8 = st.columns(2)
        with col7:
            terbit_sertifikat = st.text_input("Terbit Sertifikat", value=str(data_terpilih.get('Terbit Sertifikat', '')))
            tgl_kirim_sertifikat = st.text_input("Tanggal Pengiriman Sertifikat", value=str(data_terpilih.get('Tanggal Pengiriman Sertifikat', '')))
        with col8:
            no_resi = st.text_input("No Resi Sertifikat", value=str(data_terpilih.get('No resi Sertifikat', '')))

    st.markdown("<br>", unsafe_allow_html=True)
    submit_update = st.form_submit_button("💾 SIMPAN SEMUA PERUBAHAN", use_container_width=True)
    
    if submit_update:
        # Fungsi kecil untuk mengubah teks kosong ("") menjadi None (Null) agar SQL tidak error
        def bersihkan_data(nilai):
            return None if nilai == "" else nilai

        # Kumpulkan semua data dari form (NAMA KOLOM SUDAH DISESUAIKAN DENGAN SCREENSHOT)
        data_update = {
            "nama_pt": bersihkan_data(nama_pt),
            "PIC": bersihkan_data(pic),
            "No Hp PIC": bersihkan_data(no_hp_pic),
            "Alamat lengkap": bersihkan_data(alamat),         # <-- Huruf 'l' kecil
            "Lokasi": bersihkan_data(lokasi),
            "Tenggal Kontrak": bersihkan_data(tgl_kontrak),   # <-- Typo 'e' disesuaikan
            "Skema": bersihkan_data(skema),
            "Ruang Lingkup": bersihkan_data(ruang_lingkup),
            "Harga Sertifikasi Awal": bersihkan_data(harga),
            "Marketing": bersihkan_data(marketing),
            "No Wa Marketing": bersihkan_data(no_wa_marketing),
            "Status": bersihkan_data(status),
            "Pembayaran Awal": bersihkan_data(pem_awal),
            "Pembayaran Survailen 1": bersihkan_data(pem_surv1),
            "Pembayaran Survailen 2": bersihkan_data(pem_surv2),
            "Kajian": bersihkan_data(kajian),
            "Surat Tugas": bersihkan_data(surat_tugas),
            "Tanggal Audit": bersihkan_data(tgl_audit),
            "Pelaporan Audit": bersihkan_data(pelaporan),
            "Lead Auditor": bersihkan_data(lead_auditor),
            "Auditor": bersihkan_data(auditor),
            "Observer": bersihkan_data(observer),
            "Terbit Sertifikat": bersihkan_data(terbit_sertifikat),
            "Tanggal Pengiriman Sertifikat": bersihkan_data(tgl_kirim_sertifikat),
            "No resi Sertifikat": bersihkan_data(no_resi)     # <-- Huruf 'r' kecil
        }
        
        # --- JALUR BARU: PYTHON MELAPOR KE n8n ---
        import requests
        
        # GANTI URL INI DENGAN TEST URL DARI WEBHOOK1 (n8n) ANDA!
        URL_WEBHOOK_UPDATE = "http://localhost:5678/webhook/eaab5868-97ca-4de4-a4aa-562ee23dc2d7"
        
        # Kita gabungkan 'id' agar n8n tahu baris mana yang harus diubah
        data_n8n = data_update.copy()
        data_n8n['id'] = pilihan_id 
        
        try:
            # Tembak datanya ke n8n
            response = requests.post(URL_WEBHOOK_UPDATE, json=data_n8n)
            
            if response.status_code == 200:
                st.success("✅ Laporan perubahan berhasil dikirim ke n8n!")
                st.rerun()
            else:
                st.error("Gagal mengirim ke n8n. Cek apakah n8n sedang berjalan.")
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")

st.divider()

# --- 5. FITUR HAPUS (DENGAN PENGAMAN) ---
with st.expander("🗑️ Hapus Data (Danger Zone)"):
    with st.form("form_delete"):
        st.warning("⚠️ Data yang dihapus tidak bisa dikembalikan!")
        hapus_label = st.selectbox("Pilih Data yang akan DIHAPUS:", df['label_pilihan'].tolist())
        hapus_id = int(hapus_label.split(" - ")[0])
        
        submit_delete = st.form_submit_button("Hapus Permanen")
        if submit_delete:
            supabase.table('data_kontrak').delete().eq('id', hapus_id).execute()
            st.error(f"🗑️ Data PT tersebut berhasil dihapus!")
            st.rerun()