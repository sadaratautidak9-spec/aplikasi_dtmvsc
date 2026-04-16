import streamlit as st

# --- CEK LOGIN (KEAMANAN) ---
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("🔒 Anda belum login. Silakan kembali ke halaman utama (Home) untuk login.")
    st.stop()

from docxtpl import DocxTemplate
import pandas as pd
from datetime import datetime
from num2words import num2words
import os
import urllib.parse
import requests
from supabase import create_client

# --- KONFIGURASI WEBHOOK n8n & SUPABASE ---
N8N_WEBHOOK_URL = "https://n8n-ihbsb8xa9qan.jkt4.sumopod.my.id/webhook-test/0efd14de-28cc-4582-ac29-dc4cf98bcfda"

SUPABASE_URL = "https://ehfpmlwmdnjtxrfqdgkc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVoZnBtbHdtZG5qdHhyZnFkZ2tjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ1MDc1NjMsImV4cCI6MjA5MDA4MzU2M30.LPiPaAIm2MhuywLnmSTegWO0-1gcPuVww8abFhTAin8"

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# 1. KONFIGURASI HALAMAN & CSS
st.set_page_config(page_title="Kontrak & QA | DTM", page_icon="📄", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Titillium+Web:wght@300;400;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined');
    html, body, [class*="css"] { font-family: 'Titillium Web', sans-serif !important; background-color: #f8fafc; }
    [data-testid="stSidebar"] { background-color: #1a3673 !important; border-right: none !important; }
    [data-testid="stSidebar"] * { color: white !important; }
    .section-title { color: #1e3a8a; font-weight: 700; margin-bottom: 15px; margin-top: 0; font-size: 20px; display: flex; align-items: center; gap: 8px; }
</style>
""", unsafe_allow_html=True)

if 'docs_generated' not in st.session_state:
    st.session_state.docs_generated = False
    st.session_state.path_pks = ""
    st.session_state.path_qa = ""
    st.session_state.wa_url = ""

# 2. FUNGSI PEMBANTU (HELPERS)
def get_hari_indo(dt):
    hari_indo = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
    return hari_indo[dt.weekday()]

def tgl_terbilang(dt):
    tgl_h = num2words(dt.day, lang='id').title() 
    bulan_indo = ["", "Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    thn_h = num2words(dt.year, lang='id').title()
    return tgl_h, bulan_indo[dt.month], thn_h

def to_roman(n):
    return ['0', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII'][n]

def format_wa_number(number):
    number = str(number).replace(" ", "").replace("+", "").replace("-", "")
    if number.startswith("0"): number = "62" + number[1:]
    return number

def format_rupiah(angka):
    return f"Rp. {angka:,.0f}".replace(",", ".")

@st.cache_data(ttl=10)
def get_next_contract_number(tahun_pilih):
    try:
        res = supabase.table('data_kontrak').select('created_at').execute()
        if res.data:
            df = pd.DataFrame(res.data)
            df['year'] = pd.to_datetime(df['created_at']).dt.year
            count_tahun_ini = len(df[df['year'] == tahun_pilih])
            return count_tahun_ini + 1
        return 1
    except Exception as e:
        return 1

# 3. TAMPILAN UTAMA
st.markdown("<h2 style='color: #1e3a8a; font-weight: 700;'><span class='material-symbols-outlined' style='vertical-align: middle; font-size: 35px;'>description</span> Generator Kontrak & QA</h2>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📄 Form Generator", "📊 Database Kontrak", "⚙️ Pengaturan"])

with tab1:
    with st.form("doc_form", clear_on_submit=False):
        
        # --- KARTU 1: SKEMA & RUANG LINGKUP (MENGGUNAKAN NATIVE CONTAINER) ---
        with st.container(border=True):
            st.markdown("<h4 class='section-title'><span class='material-symbols-outlined'>category</span> 1. Skema & Ruang Lingkup</h4>", unsafe_allow_html=True)
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                skema = st.selectbox("Pilih Skema", ["LSUHK", "LSPr", "Non KAN"])
            with col_s2:
                if skema == "LSUHK":
                    scope_pilihan = st.multiselect("Ruang Lingkup (LSUHK)", ["PPIU", "PIHK"], default=["PPIU"])
                elif skema == "LSPr":
                    scope_pilihan = [st.selectbox("Ruang Lingkup (LSPr)", ["Hotel", "Restoran", "BPW"])]
                else:
                    scope_pilihan = [st.selectbox("Ruang Lingkup (Non KAN)", ["Hotel Bintang 1", "Hotel Bintang 2", "Hotel Bintang 3", "Hotel Bintang 4", "Hotel Bintang 5"])]

        # --- KARTU 2: IDENTITAS KLIEN ---
        with st.container(border=True):
            st.markdown("<h4 class='section-title'><span class='material-symbols-outlined'>domain</span> 2. Identitas Klien</h4>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                nama_klien = st.text_input("Nama Klien (PT/CV)")
                alamat_klien = st.text_area("Alamat Lengkap Klien", height=100)
                tlp_klien = st.text_input("No HP/WA Klien")
            with c2:
                nama_ttd = st.text_input("Nama Penandatangan (Direktur)")
                jabatan_raw = st.text_input("Jabatan Penandatangan")
                lokasi = st.text_input("Lokasi Penandatanganan", "Jakarta")
                tgl_dokumen = st.date_input("Tanggal Dokumen", datetime.now())

        # --- KARTU 3: FINANSIAL & MARKETING ---
        with st.container(border=True):
            st.markdown("<h4 class='section-title'><span class='material-symbols-outlined'>payments</span> 3. Finansial & Marketing</h4>", unsafe_allow_html=True)
            c3, c4 = st.columns(2)
            with c3:
                marketing = st.text_input("Nama Marketing")
                tlp_marketing = st.text_input("No HP/WA Marketing (Contoh: 08123456789)")
                harga_awal = st.number_input("Harga Sertifikasi (Rp)", min_value=0, step=500000)
            with c4:
                status_bayar = st.selectbox("Status Pembayaran", ["Belum Terdapat Pembayaran", "DP 30%", "DP 50%", "Telah Lunas"])
                kategori_audit = st.selectbox("Kategori Audit", ["Sertifikasi Awal", "Survailen", "Re-Sertifikasi"])
                status_progres = st.selectbox("Status Progres", ["Kontrak", "Rencana Audit", "Selesai"])
                
            st.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)
            st.markdown("**Kondisi Biaya (Untuk Dokumen QA)**")
            c5, c6 = st.columns(2)
            with c5: status_transportasi = st.selectbox("Biaya Transportasi", ["Belum Termasuk", "Sudah Termasuk"])
            with c6: status_akomodasi = st.selectbox("Biaya Akomodasi", ["Belum Termasuk", "Sudah Termasuk"])

        # --- LOGIKA AUTO-NUMBERING VIA SUPABASE ---
        tahun_pilih = tgl_dokumen.year
        romawi = to_roman(tgl_dokumen.month)
        next_num = get_next_contract_number(tahun_pilih)
        no_urut_auto = f"{next_num:03d}"

        if skema == "LSUHK":
            prev_no_kontrak = f"{no_urut_auto}/DTM/LSUHK/{romawi}/{tahun_pilih}"
            prev_no_qa = f"{no_urut_auto}/QA/LSUHK/{romawi}/{tahun_pilih}"
        elif skema == "LSPr":
            prev_no_kontrak = f"{no_urut_auto}/DTM/LSPR/{romawi}/{tahun_pilih}"
            prev_no_qa = f"{no_urut_auto}/QA/LSPR/{romawi}/{tahun_pilih}"
        else:
            prev_no_kontrak = f"{no_urut_auto}/DTM/NON-KAN/{romawi}/{tahun_pilih}"
            prev_no_qa = f"{no_urut_auto}/QA/NON-KAN/{romawi}/{tahun_pilih}"

        st.info(f"💡 **Penomoran Otomatis:** No Kontrak: `{prev_no_kontrak}` | No QA: `{prev_no_qa}`")

        # TOMBOL SUBMIT BESAR
        submit = st.form_submit_button("🚀 Generate Dokumen (Word) & Kirim ke n8n", type="primary", use_container_width=True)

    # 4. LOGIKA EKSEKUSI (SERVER-READY)
    if submit:
        required_fields = {
            "Nama Klien": nama_klien, "Alamat": alamat_klien, "Nama Direktur": nama_ttd, 
            "Jabatan": jabatan_raw, "Harga": harga_awal, "No WA Marketing": tlp_marketing
        }
        empty_fields = [k for k, v in required_fields.items() if not v or v == 0]

        if empty_fields:
            st.error(f"⚠️ **Gagal!** Data berikut belum lengkap: {', '.join(empty_fields)}")
        elif tlp_klien and not tlp_klien.replace("+", "").isdigit():
            st.error("⚠️ **Gagal!** No HP/WA Klien hanya boleh berisi angka!")
        elif tlp_marketing and not tlp_marketing.replace("+", "").isdigit():
            st.error("⚠️ **Gagal!** No HP/WA Marketing hanya boleh berisi angka!")
        elif skema == "LSUHK" and len(scope_pilihan) == 0:
            st.error("⚠️ **Gagal!** Anda harus memilih minimal satu Ruang Lingkup untuk LSUHK!")
        else:
            with st.spinner("🔄 Sedang memproses dokumen Word dan mengirim ke n8n..."):
                try:
                    hari_nama = get_hari_indo(tgl_dokumen)
                    tgl_h, bln_h, thn_h = tgl_terbilang(tgl_dokumen)
                    scope_label = " & ".join(scope_pilihan)
                    harga_formatted = format_rupiah(harga_awal)

                    context = {
                        'hari': hari_nama, 'tgl_teks': tgl_h, 'bulan': bln_h, 'tahun_teks': thn_h,
                        'tgl_angka': tgl_dokumen.strftime('%d %B %Y'), 'no_kontrak': prev_no_kontrak, 'no_qa': prev_no_qa,
                        'nama_klien': nama_klien, 'alamat_klien': alamat_klien, 'tlp_klien': tlp_klien,
                        'nama_ttd': nama_ttd, 'jabatan': jabatan_raw, 'jabatan_ttd': f"{jabatan_raw} {nama_klien}",
                        'harga': harga_formatted, 'scope': scope_label, 'lokasi': lokasi,
                        'status_transportasi': status_transportasi, 'status_akomodasi': status_akomodasi
                    }

                    pks_template = ""
                    qa_template = ""

                    if skema == "LSUHK":
                        if len(scope_pilihan) == 2: pks_template = "templates/pks_lsuhk_gabungan.docx"
                        elif "PPIU" in scope_pilihan: pks_template = "templates/pks_lsuhk_ppiu.docx"
                        else: pks_template = "templates/pks_lsuhk_pihk.docx"
                        qa_template = "templates/qa_lsuhk.docx"
                    elif skema == "LSPr":
                        if "Hotel" in scope_pilihan: pks_template = "templates/pks_lspr_hotel.docx"
                        elif "Restoran" in scope_pilihan: pks_template = "templates/pks_lspr_restoran.docx"
                        else: pks_template = "templates/pks_lspr_bpw.docx"
                        qa_template = "templates/qa_lspr.docx"
                    else:
                        pks_template = "templates/pks_non_kan.docx"
                        qa_template = "templates/qa_non_kan.docx"

                    os.makedirs("output/word", exist_ok=True)
                    os.makedirs("templates", exist_ok=True)

                    if not os.path.exists(pks_template) or not os.path.exists(qa_template):
                        st.error(f"⚠️ Template tidak ditemukan! Pastikan file `{pks_template}` dan `{qa_template}` sudah ada di folder 'templates/'.")
                        st.stop()

                    # --- PROSES PKS (HANYA WORD) ---
                    doc_pks = DocxTemplate(pks_template)
                    doc_pks.render(context)
                    fname_pks = f"PKS_{prev_no_kontrak.replace('/', '-')}_{nama_klien}.docx"
                    path_pks_docx = f"output/word/{fname_pks}"
                    doc_pks.save(path_pks_docx)

                    # --- PROSES QA (HANYA WORD) ---
                    doc_qa = DocxTemplate(qa_template)
                    doc_qa.render(context)
                    fname_qa = f"QA_{prev_no_qa.replace('/', '-')}_{nama_klien}.docx"
                    path_qa_docx = f"output/word/{fname_qa}"
                    doc_qa.save(path_qa_docx)

                    # --- KIRIM DATA & FILE WORD KE n8n ---
                    try:
                        payload_data = {
                            "no_kontrak": prev_no_kontrak, "nama_klien": nama_klien, "marketing": marketing,
                            "no_wa_marketing": format_wa_number(tlp_marketing), "no_wa_klien": format_wa_number(tlp_klien),
                            "skema": skema, "ruang_lingkup": scope_label, "harga": harga_formatted,
                            "alamat_klien": alamat_klien, "tanggal_dokumen" : str(tgl_dokumen)
                        }
                        files_to_send = {
                            "file_word_pks": (fname_pks, open(path_pks_docx, "rb"), "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
                            "file_word_qa": (fname_qa, open(path_qa_docx, "rb"), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                        }
                        if "MASUKKAN-ID-WEBHOOK" not in N8N_WEBHOOK_URL:
                            response = requests.post(N8N_WEBHOOK_URL, data=payload_data, files=files_to_send)
                            if response.status_code == 200:
                                st.success("🚀 Data dan File Word berhasil dikirim ke n8n!")
                                get_next_contract_number.clear()
                            else:
                                st.warning(f"⚠️ Gagal mengirim ke n8n. Status Code: {response.status_code}")
                    except Exception as e_n8n:
                        st.warning(f"⚠️ Tidak dapat terhubung ke n8n. Pastikan n8n menyala. Error: {e_n8n}")

                    # --- SIAPKAN LINK WHATSAPP ---
                    wa_number = format_wa_number(tlp_marketing)
                    wa_text = (f"Halo {marketing},\n\nDokumen PKS dan QA untuk klien *{nama_klien}* sudah selesai dibuat.\n\n"
                               f"📌 *No Kontrak:* {prev_no_kontrak}\n📌 *Skema:* {skema}\n📌 *Ruang Lingkup:* {scope_label}\n"
                               f"💰 *Harga:* {harga_formatted}\n\nMohon tunggu beberapa saat hingga sistem n8n mengirimkan versi PDF-nya. Terima kasih.")
                    
                    st.session_state.docs_generated = True
                    st.session_state.path_pks = path_pks_docx
                    st.session_state.path_qa = path_qa_docx
                    st.session_state.wa_url = f"https://wa.me/{wa_number}?text={urllib.parse.quote(wa_text)}"

                    st.balloons()
                    st.success(f"✅ Selesai! Dokumen Word terbuat dan Data terkirim ke n8n!")

                except Exception as e:
                    st.error(f"❌ Terjadi kesalahan teknis: {e}")

    if st.session_state.docs_generated:
        with st.container(border=True):
            st.markdown("<h4 style='color: #16a34a; margin-top: 0;'>🎉 Dokumen Word Siap Diunduh!</h4>", unsafe_allow_html=True)
            st.info("💡 Versi PDF akan diproses dan dikirimkan secara otomatis oleh sistem n8n di belakang layar.")
            
            c_dl1, c_dl2 = st.columns(2)
            with c_dl1:
                if os.path.exists(st.session_state.path_pks):
                    with open(st.session_state.path_pks, "rb") as f:
                        st.download_button("📥 Download PKS (Word)", f, file_name=os.path.basename(st.session_state.path_pks), use_container_width=True)
            with c_dl2:
                if os.path.exists(st.session_state.path_qa):
                    with open(st.session_state.path_qa, "rb") as f:
                        st.download_button("📥 Download QA (Word)", f, file_name=os.path.basename(st.session_state.path_qa), use_container_width=True)
            
            st.markdown(
                f"""
                <a href="{st.session_state.wa_url}" target="_blank" style="text-decoration: none;">
                    <button style="background-color: #25D366; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: bold; width: 100%; font-size: 16px; margin-top: 10px;">
                        💬 Kirim Notifikasi WA ke Marketing
                    </button>
                </a>
                """, unsafe_allow_html=True
            )

with tab2:
    with st.container(border=True):
        st.markdown("<h4 class='section-title'><span class='material-symbols-outlined'>database</span> Database Kontrak (Supabase)</h4>", unsafe_allow_html=True)
        
        if st.button("🔄 Refresh Data", type="primary"):
            with st.spinner("Mengambil data dari Supabase..."):
                try:
                    res = supabase.table('data_kontrak').select("*").execute()
                    if res.data:
                        df = pd.DataFrame(res.data)
                        if 'created_at' in df.columns:
                            df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
                        st.dataframe(df, use_container_width=True, hide_index=True)
                    else:
                        st.info("Belum ada data kontrak di Supabase.")
                except Exception as e:
                    st.error(f"Gagal mengambil data: {e}")

with tab3:
    with st.container(border=True):
        st.markdown("<h4 class='section-title'><span class='material-symbols-outlined'>settings</span> Petunjuk Penggunaan</h4>", unsafe_allow_html=True)
        st.markdown("""
        1. Pastikan file template Word (`.docx`) berada di dalam folder `templates/`.
        2. Nama template yang dibutuhkan:
           - **LSUHK:** `pks_lsuhk_gabungan.docx`, `pks_lsuhk_ppiu.docx`, `pks_lsuhk_pihk.docx`, `qa_lsuhk.docx`
           - **LSPr:** `pks_lspr_hotel.docx`, `pks_lspr_restoran.docx`, `pks_lspr_bpw.docx`, `qa_lspr.docx`
           - **Non KAN:** `pks_non_kan.docx`, `qa_non_kan.docx`
        3. Aplikasi ini akan menghasilkan file **Word (.docx)** dan mengirimkannya ke n8n.
        4. **Konversi ke PDF akan dilakukan secara otomatis oleh n8n** di server cloud.
        """)
