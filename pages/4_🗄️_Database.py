import streamlit as st
import pandas as pd
from supabase import create_client
import requests
import datetime

# --- 1. KONFIGURASI SUPABASE ---
SUPABASE_URL = "https://ehfpmlwmdnjtxrfqdgkc.supabase.co" 
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVoZnBtbHdtZG5qdHhyZnFkZ2tjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ1MDc1NjMsImV4cCI6MjA5MDA4MzU2M30.LPiPaAIm2MhuywLnmSTegWO0-1gcPuVww8abFhTAin8" 

@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_connection()

st.set_page_config(page_title="Database Kontrak", page_icon="🗄️", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Titillium+Web:wght@300;400;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined');
    html, body, [class*="css"] { font-family: 'Titillium Web', sans-serif !important; }
    [data-testid="stSidebar"] { background-color: #1e3a8a !important; }
    [data-testid="stSidebar"] * { color: white !important; }
</style>
""", unsafe_allow_html=True)
st.title("🗄️ Manajemen Database Kontrak")

# --- 2. FUNGSI TARIK DATA (METODE JOIN) ---
# Di sinilah letak Arsitektur Pintarnya. Kita gabung data kontrak dan sertifikasinya.
def load_data():
    # 1. Ambil data kontrak
    res_kontrak = supabase.table('data_kontrak').select("*").order("id", desc=True).execute()
    df_kontrak = pd.DataFrame(res_kontrak.data)
    
    if df_kontrak.empty:
        return pd.DataFrame()

    # 2. Ambil data sertifikasi (untuk numpang lihat Tanggal Terbit, Resi, dll)
    res_sertif = supabase.table('data_sertifikasi').select("id_kontrak, no_sertifikat, tgl_terbit, tgl_survailen, status").execute()
    df_sertif = pd.DataFrame(res_sertif.data)
    
    # 3. GABUNGKAN (Merge). 
    # Sekarang Menu Database bisa melihat 'tgl_terbit' meskipun data aslinya ada di tabel sebelah!
    if not df_sertif.empty:
        df_final = pd.merge(df_kontrak, df_sertif, left_on='id', right_on='id_kontrak', how='left')
    else:
        df_final = df_kontrak
        df_final['tgl_terbit'] = None
        df_final['no_sertifikat'] = None
        
    return df_final

df = load_data()

if df.empty:
    st.info("Database masih kosong.")
    st.stop()

# --- 3. FITUR PENCARIAN (SEARCH) ---
st.subheader("🔍 Cari & Lihat Data")
kata_kunci = st.text_input("Ketik pencarian (Nama PT, Marketing, dll):", "")

if kata_kunci:
    mask = df.astype(str).apply(lambda x: x.str.contains(kata_kunci, case=False)).any(axis=1)
    df_tampil = df[mask]
else:
    df_tampil = df

st.dataframe(df_tampil, use_container_width=True)
st.divider()

# --- 4. FITUR UPDATE SEMUA KOLOM ---
st.subheader("✏️ Edit / Lengkapi Data")

df['label_pilihan'] = df['id'].astype(str) + " - " + df['nama_pt'].astype(str)
pilihan_label = st.selectbox("Pilih Data yang akan diedit:", df['label_pilihan'].tolist())
pilihan_id = int(pilihan_label.split(" - ")[0])
data_terpilih = df[df['id'] == pilihan_id].iloc[0].fillna('')

def set_default_date(tgl_string):
    if not tgl_string or str(tgl_string).strip() in ['-', 'None', 'nan', '']: return None
    try:
        return datetime.datetime.strptime(str(tgl_string).strip(), '%Y-%m-%d').date()
    except ValueError:
        return None

with st.form("form_update_lengkap"):
    st.info(f"🏢 Sedang mengedit: **{data_terpilih.get('nama_pt', '')}**")
    
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
            tgl_kontrak = st.date_input("Tanggal Kontrak", value=set_default_date(data_terpilih.get('Tenggal Kontrak', '')))
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
            tgl_audit = st.date_input("Tanggal Audit", value=set_default_date(data_terpilih.get('Tanggal Audit', '')))
            pelaporan = st.text_input("Pelaporan Audit", value=str(data_terpilih.get('Pelaporan Audit', '')))
        with col6:
            lead_auditor = st.text_input("Lead Auditor", value=str(data_terpilih.get('Lead Auditor', '')))
            auditor = st.text_input("Auditor", value=str(data_terpilih.get('Auditor', '')))
            observer = st.text_input("Observer", value=str(data_terpilih.get('Observer', '')))
            
    with tab4:
        col7, col8 = st.columns(2)
        with col7:
            # ---> KITA BACA DARI 'tgl_terbit' MILIK TABEL SEBELAH (HASIL MERGE/JOIN TADI)
            terbit_sertifikat_view = st.date_input("Tanggal Terbit Sertifikat", value=set_default_date(data_terpilih.get('tgl_terbit', '')))
            tgl_kirim_sertifikat = st.date_input("Tanggal Pengiriman Sertifikat", value=set_default_date(data_terpilih.get('Tanggal Pengiriman Sertifikat', '')))
        with col8:
            no_sertif_view = st.text_input("Nomor Sertifikat", value=str(data_terpilih.get('no_sertifikat', '')))
            no_resi = st.text_input("No Resi Sertifikat", value=str(data_terpilih.get('No resi Sertifikat', '')))

    st.markdown("<br>", unsafe_allow_html=True)
    submit_update = st.form_submit_button("💾 SIMPAN SEMUA PERUBAHAN", use_container_width=True)
    
    if submit_update:
        def proses_tgl(kalender): return kalender.strftime('%Y-%m-%d') if kalender else None
        def bersih(nilai): return None if nilai == "" else nilai

        # 1. SIAPKAN DATA UNTUK TABEL KONTRAK
        data_update_kontrak = {
            "nama_pt": bersih(nama_pt), "PIC": bersih(pic), "No Hp PIC": bersih(no_hp_pic),
            "Alamat lengkap": bersih(alamat), "Lokasi": bersih(lokasi),
            "Tenggal Kontrak": proses_tgl(tgl_kontrak), "Skema": bersih(skema), "Ruang Lingkup": bersih(ruang_lingkup),
            "Harga Sertifikasi Awal": bersih(harga), "Marketing": bersih(marketing), "No Wa Marketing": bersih(no_wa_marketing),
            "Status": bersih(status), "Pembayaran Awal": bersih(pem_awal), "Pembayaran Survailen 1": bersih(pem_surv1),
            "Pembayaran Survailen 2": bersih(pem_surv2), "Kajian": bersih(kajian), "Surat Tugas": bersih(surat_tugas),
            "Tanggal Audit": proses_tgl(tgl_audit), "Pelaporan Audit": bersih(pelaporan),
            "Lead Auditor": bersih(lead_auditor), "Auditor": bersih(auditor), "Observer": bersih(observer),
            "Tanggal Pengiriman Sertifikat": proses_tgl(tgl_kirim_sertifikat), "No resi Sertifikat": bersih(no_resi)
        }
        
        try:
            # EKSEKUSI 1: UPDATE KE TABEL KONTRAK
            supabase.table('data_kontrak').update(data_update_kontrak).eq('id', pilihan_id).execute()

            # EKSEKUSI 2: UPDATE KE TABEL SERTIFIKASI (INI YANG BIKIN JADI SELALU SINKRON!)
            tgl_terbit_str = proses_tgl(terbit_sertifikat_view)
            
            cek_sertif = supabase.table('data_sertifikasi').select('id').eq('id_kontrak', pilihan_id).execute()
            if cek_sertif.data:
                # Jika dia sudah dirilis sertifikatnya, kita update nomor & tanggalnya
                supabase.table('data_sertifikasi').update({
                    'tgl_terbit': tgl_terbit_str,
                    'no_sertifikat': bersih(no_sertif_view)
                }).eq('id_kontrak', pilihan_id).execute()

            # (OPSIONAL): Jika Anda masih menggunakan n8n untuk Spreadsheet
            URL_WEBHOOK_UPDATE = "https://n8n-ihbsb8xa9qan.jkt4.sumopod.my.id/webhook-test/b62cc644-5ee3-4584-a392-72177502ee19"
            data_n8n = data_update_kontrak.copy()
            data_n8n['id'] = pilihan_id 
            data_n8n['tgl_terbit'] = tgl_terbit_str # Informasikan n8n agar Spreadsheet-nya juga tahu
            
            requests.post(URL_WEBHOOK_UPDATE, json=data_n8n)
            
            st.success("✅ Seluruh data di Database dan Status Klien berhasil tersinkronisasi!")
            st.rerun()
            
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")

st.divider()

# --- 5. FITUR HAPUS ---
with st.expander("🗑️ Hapus Data (Danger Zone)"):
    with st.form("form_delete"):
        st.warning("⚠️ Menghapus ini akan menghapus Klien dari SEMUA Database!")
        hapus_label = st.selectbox("Pilih Data yang akan DIHAPUS:", df['label_pilihan'].tolist())
        submit_delete = st.form_submit_button("Hapus Permanen")
        if submit_delete:
            hapus_id = int(hapus_label.split(" - ")[0])
            # Hapus dari tabel sertifikat dulu agar tidak jadi hantu
            supabase.table('data_sertifikasi').delete().eq('id_kontrak', hapus_id).execute()
            # Baru hapus dari tabel kontrak
            supabase.table('data_kontrak').delete().eq('id', hapus_id).execute()
            st.error(f"🗑️ Data PT berhasil dihapus secara permanen!")
            st.rerun()
