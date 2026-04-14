import streamlit as st
import pandas as pd
from supabase import create_client
import plotly.express as px

# --- KONFIGURASI HALAMAN & CSS GLOBAL ---
st.set_page_config(page_title="Dashboard Analisa | DTM", page_icon="📊", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Titillium+Web:wght@300;400;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined');
    html, body, [class*="css"] { font-family: 'Titillium Web', sans-serif !important; background-color: #f8fafc; }
    [data-testid="stSidebar"] { background-color: #1e3a8a !important; }
    [data-testid="stSidebar"] * { color: white !important; }
    
    /* Hilangkan padding atas bawaan Streamlit agar lebih rapat */
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }

    /* Desain Kartu Metrik (Sesuai Referensi) */
    .metric-card {
        background-color: white; padding: 25px; border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.03); border: 1px solid #f1f5f9;
        height: 100%; display: flex; flex-direction: column; justify-content: space-between;
    }
    .icon-circle {
        width: 45px; height: 45px; border-radius: 50%;
        display: flex; justify-content: center; align-items: center; margin-bottom: 15px;
    }
    .metric-title { font-size: 15px; color: #0f172a; font-weight: 600; margin-bottom: 5px; }
    .metric-value { font-size: 32px; color: #0f172a; font-weight: 700; margin: 0; line-height: 1.2; }
    .metric-subtitle { font-size: 13px; color: #64748b; margin-top: 5px; }

    /* Desain Kartu Akses Cepat (Sesuai Referensi) */
    .quick-access-card {
        border-radius: 16px; padding: 20px; display: flex; align-items: center; justify-content: space-between;
        margin-bottom: 15px; text-decoration: none !important; transition: transform 0.2s;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    .quick-access-card:hover { transform: translateY(-3px); }
    .qa-icon-wrapper {
        background: rgba(255,255,255,0.2); width: 40px; height: 40px; border-radius: 10px;
        display: flex; justify-content: center; align-items: center; margin-right: 15px;
    }
    .qa-title { font-weight: 700; font-size: 16px; margin: 0; }
    .qa-subtitle { font-size: 13px; margin: 0; opacity: 0.9; font-weight: 300; }

    /* Kontainer Umum */
    .white-container {
        background-color: white; padding: 25px; border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.03); border: 1px solid #f1f5f9; margin-bottom: 20px;
    }
    .section-header { font-size: 16px; color: #64748b; font-weight: 600; margin-bottom: 20px; border-bottom: 1px solid #f1f5f9; padding-bottom: 10px;}
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
@st.cache_data(ttl=10)
def load_data():
    res_kontrak = supabase.table('data_kontrak').select("*").execute()
    res_sert = supabase.table('data_sertifikasi').select("*").execute()
    res_tim = supabase.table('data_tim').select("*").execute()
    return res_kontrak.data, res_sert.data, res_tim.data

data_kontrak, data_sertifikasi, data_tim = load_data()

df_kontrak = pd.DataFrame(data_kontrak) if data_kontrak else pd.DataFrame()
df_sert = pd.DataFrame(data_sertifikasi) if data_sertifikasi else pd.DataFrame()
df_tim = pd.DataFrame(data_tim) if data_tim else pd.DataFrame()

# --- HEADER (Sesuai Referensi) ---
st.markdown("<h2 style='color: #1e293b; font-weight: 700; margin-bottom: 25px;'>Selamat Datang, DTM Certification</h2>", unsafe_allow_html=True)

# --- ROW 1: 4 KARTU METRIK (Sesuai Referensi) ---
c1, c2, c3, c4 = st.columns(4)

jml_klien = len(df_kontrak)
jml_auditor = len(df_tim[df_tim['status'] == 'Aktif']) if not df_tim.empty else 0
jml_sert = len(df_sert[df_sert['status'] == 'Tersertifikasi']) if not df_sert.empty else 0
jml_masalah = len(df_sert[df_sert['status'].isin(['Dibekukan', 'Dicabut'])]) if not df_sert.empty else 0

with c1:
    st.markdown(f"""
    <div class='metric-card'>
        <div>
            <div class='icon-circle' style='background-color: #3b82f6;'><span class='material-symbols-outlined' style='color: white;'>corporate_fare</span></div>
            <div class='metric-title'>Jumlah Klien</div>
            <div class='metric-value'>{jml_klien}</div>
        </div>
        <div class='metric-subtitle'>Klien Terdaftar di Sistem</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class='metric-card'>
        <div>
            <div class='icon-circle' style='background-color: #f59e0b;'><span class='material-symbols-outlined' style='color: white;'>groups</span></div>
            <div class='metric-title'>Jumlah Auditor</div>
            <div class='metric-value'>{jml_auditor}</div>
        </div>
        <div class='metric-subtitle'>Auditor Internal Aktif</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class='metric-card'>
        <div>
            <div class='icon-circle' style='background-color: #10b981;'><span class='material-symbols-outlined' style='color: white;'>verified</span></div>
            <div class='metric-title'>Klien Tersertifikasi</div>
            <div class='metric-value'>{jml_sert}</div>
        </div>
        <div class='metric-subtitle'>Sertifikat Aktif</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class='metric-card'>
        <div>
            <div class='icon-circle' style='background-color: #a855f7;'><span class='material-symbols-outlined' style='color: white;'>warning</span></div>
            <div class='metric-title'>Perlu Perhatian</div>
            <div class='metric-value'>{jml_masalah}</div>
        </div>
        <div class='metric-subtitle'>Klien Dibekukan / Dicabut</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- ROW 2: GRAFIK KIRI & AKSES CEPAT KANAN (Sesuai Referensi) ---
col_left, col_right = st.columns([2.2, 1])

with col_left:
    st.markdown("<div class='white-container' style='height: 100%;'>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>Performa Sertifikasi Berdasarkan Skema</div>", unsafe_allow_html=True)
    
    if not df_kontrak.empty and 'Skema' in df_kontrak.columns:
        # Mengelompokkan data berdasarkan Skema
        skema_data = df_kontrak['Skema'].value_counts().reset_index()
        skema_data.columns = ['Skema', 'Jumlah']
        
        # Membuat Bar Chart ala Referensi (Warna Biru/Ungu)
        fig_bar = px.bar(skema_data, x='Skema', y='Jumlah', text_auto=True, color='Skema',
                         color_discrete_sequence=['#6366f1', '#8b5cf6', '#3b82f6'])
        
        fig_bar.update_layout(
            margin=dict(t=10, b=10, l=0, r=0), 
            xaxis_title="", yaxis_title="", 
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", 
            height=300, showlegend=False
        )
        fig_bar.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f1f5f9')
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Data tidak cukup untuk menampilkan grafik.")
    st.markdown("</div>", unsafe_allow_html=True)

with col_right:
    st.markdown("<div style='font-size: 16px; color: #64748b; font-weight: 600; margin-bottom: 15px;'><span class='material-symbols-outlined' style='vertical-align: middle; font-size: 20px; color: #3b82f6;'>bolt</span> Akses Cepat Modul</div>", unsafe_allow_html=True)
    
    # Tombol 1: Biru Tua
    st.markdown("""
    <a href="Kontrak_QA" target="_self" class="quick-access-card" style="background-color: #1e293b; color: white;">
        <div style="display: flex; align-items: center;">
            <div class="qa-icon-wrapper"><span class="material-symbols-outlined" style="color: white;">description</span></div>
            <div><p class="qa-title">Kontrak & QA</p><p class="qa-subtitle">Buat dokumen baru</p></div>
        </div>
        <span class="material-symbols-outlined" style="color: rgba(255,255,255,0.5);">arrow_forward</span>
    </a>
    """, unsafe_allow_html=True)
    
    # Tombol 2: Oranye
    st.markdown("""
    <a href="Database_Tim" target="_self" class="quick-access-card" style="background-color: #f59e0b; color: white;">
        <div style="display: flex; align-items: center;">
            <div class="qa-icon-wrapper"><span class="material-symbols-outlined" style="color: white;">groups</span></div>
            <div><p class="qa-title">Auditor</p><p class="qa-subtitle">Kelola data auditor</p></div>
        </div>
        <span class="material-symbols-outlined" style="color: rgba(255,255,255,0.5);">arrow_forward</span>
    </a>
    """, unsafe_allow_html=True)
    
    # Tombol 3: Ungu Muda (Teks Gelap)
    st.markdown("""
    <a href="Status_Klien" target="_self" class="quick-access-card" style="background-color: #e2e8f0; color: #0f172a;">
        <div style="display: flex; align-items: center;">
            <div class="qa-icon-wrapper" style="background: rgba(0,0,0,0.05);"><span class="material-symbols-outlined" style="color: #0f172a;">verified</span></div>
            <div><p class="qa-title">Status Klien</p><p class="qa-subtitle">Daftar klien tersertifikasi</p></div>
        </div>
        <span class="material-symbols-outlined" style="color: rgba(0,0,0,0.3);">arrow_forward</span>
    </a>
    """, unsafe_allow_html=True)

# --- ROW 3: TABEL PENGGANTI PETA (Tetap Fungsional) ---
st.markdown("<div class='white-container'>", unsafe_allow_html=True)
col_t1, col_t2 = st.columns([3, 1])
with col_t1:
    st.markdown("<div class='section-header' style='border: none; margin: 0; padding: 0;'>Sebaran Data Klien Keseluruhan</div>", unsafe_allow_html=True)
with col_t2:
    search_query = st.text_input("🔍 Cari Klien / Skema...", placeholder="Ketik nama PT...", label_visibility="collapsed")

if not df_kontrak.empty:
    if not df_sert.empty:
        df_merged = pd.merge(df_kontrak, df_sert, left_on='id', right_on='id_kontrak', how='left')
    else:
        df_merged = df_kontrak.copy()
        df_merged['status'] = 'Belum Sertifikasi'
        df_merged['no_sertifikat'] = '-'
        df_merged['tgl_survailen'] = '-'

    kolom_tampil = ['nama_pt', 'Skema', 'Ruang Lingkup', 'status', 'no_sertifikat', 'tgl_survailen']
    kolom_tampil = [col for col in kolom_tampil if col in df_merged.columns]
    df_display = df_merged[kolom_tampil].fillna('-')

    df_display.rename(columns={
        'nama_pt': 'Nama Klien', 'status': 'Status Sertifikasi',
        'no_sertifikat': 'No. Sertifikat', 'tgl_survailen': 'Jadwal Survailen'
    }, inplace=True)

    if search_query:
        mask = df_display.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)
        df_display = df_display[mask]

    st.dataframe(df_display, use_container_width=True, hide_index=True, height=300)
else:
    st.info("Belum ada data klien.")
st.markdown("</div>", unsafe_allow_html=True)