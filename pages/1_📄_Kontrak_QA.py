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
    st.session_state.path_doc = ""
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

# ---> FUNGSI AUTO-NUMBERING TERBARU (100% REALTIME & LEBIH KUAT) <---
def get_next_contract_number(tahun_pilih, skema_klien):
    try:
        # Ambil data langsung dari Supabase
        res = supabase.table('data_kontrak').select('created_at, skema').execute()
        
        if res.data:
            df = pd.DataFrame(res.data)
            
            # Jika kolom skema tidak ditemukan, return 1
            if 'skema' not in df.columns:
                return 1
                
            # 1. Bersihkan spasi tersembunyi agar pencocokan akurat
            df['skema'] = df['skema'].astype(str).str.strip()
            skema_klien_bersih = str(skema_klien).strip()
            
            # 2. Ambil tahun dari tanggal
            df['year'] = pd.to_datetime(df['created_at']).dt.year
            
            # 3. Hitung baris yang TAHUN dan SKEMA-nya sama (Casing-sensitive)
            count_skema_ini = len(df[(df['year'] == tahun_pilih) & (df['skema'] == skema_klien_bersih)])
            
            return count_skema_ini + 1
            
        return 1
    except Exception as e:
        # TAMPILKAN ERROR MERAH JIKA GAGAL (Jangan sembunyikan jadi angka 1)
        st.error(f"⚠️ Error sistem perhitungan nomor: {e}")
        return 1

# 3. TAMPILAN UTAMA
st.markdown("<h2 style='color: #1e3a8a; font-weight: 700;'><span class='material-symbols-outlined' style='vertical-align: middle; font-size: 35px;'>description</span> Generator Kontrak & QA</h2>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📄 Form Generator", "📊 Database Kontrak", "⚙️ Pengaturan"])

with tab1:
    
    # --- KARTU 1: SKEMA & RUANG LINGKUP ---
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

    # --- KARTU 2 & 3 (DI DALAM FORM) ---
    with st.form("doc_form", clear_on_submit=False):
        
        # --- KARTU 2: IDENTITAS KLIEN ---
        with st.container(border=True):
            st.markdown("<h4 class='section-title'><span class='material-symbols-outlined'>domain</span> 2. Identitas Klien</h4>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                nama_klien = st.text_input("Nama Klien Organisasi (PT/CV)")
                # ---> TAMBAHAN FORMLIR BRAND & KATEGORI
                nama_brand = st.text_input("Nama Brand (Opsional)", help="Isi apabila organisasi/PT memiliki nama brand (Misal: Hotel Asoka)")
                alamat_klien = st.text_area("Alamat Lengkap Klien", height=100)
                tlp_klien = st.text_input("No HP/WA Klien")
                email_klien = st.text_input("Email Klien")
            with c2:
                # ---> TAMBAHAN KATEGORI (Dimasukkan disini agar kolom seimbang)
                kategori_brand = st.text_input("Kategori (Opsional)", help="Khusus LSPr. Contoh: Bintang 5, Bintang 3, dll.")
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

        # --- LOGIKA AUTO-NUMBERING ---
        tahun_pilih = tgl_dokumen.year
        romawi = to_roman(tgl_dokumen.month)
        next_num = get_next_contract_number(tahun_pilih, skema)
        no_urut_auto = f"{next_num:03d}"

        prev_no_kontrak = ""
        prev_no_qa = ""

        if skema == "LSUHK":
            if len(scope_pilihan) == 2: # PPIU & PIHK
                prev_no_kontrak = f"{no_urut_auto}/DTM/PIHK/{romawi}/{tahun_pilih}"
                prev_no_qa = f"{no_urut_auto}/QA/PIHK-DTM/{romawi}/{tahun_pilih}"
            elif "PPIU" in scope_pilihan:
                prev_no_kontrak = f"{no_urut_auto}/DTM/PPIU/{romawi}/{tahun_pilih}"
                prev_no_qa = f"{no_urut_auto}/QA/PPIU-DTM/{romawi}/{tahun_pilih}"
            else: # PIHK
                prev_no_kontrak = f"{no_urut_auto}/DTM/PIHK/{romawi}/{tahun_pilih}"
                prev_no_qa = f"{no_urut_auto}/QA/PIHK-DTM/{romawi}/{tahun_pilih}"
        elif skema == "LSPr":
            if "Hotel" in scope_pilihan:
                prev_no_kontrak = f"{no_urut_auto}/DTM/HOTEL/{romawi}/{tahun_pilih}"
                prev_no_qa = f"{no_urut_auto}/QA/HT-DTM/{romawi}/{tahun_pilih}"
            elif "Restoran" in scope_pilihan:
                prev_no_kontrak = f"{no_urut_auto}/DTM/RESTORAN/{romawi}/{tahun_pilih}"
                prev_no_qa = f"{no_urut_auto}/QA/RS-DTM/{romawi}/{tahun_pilih}"
            else: # BPW
                prev_no_kontrak = f"{no_urut_auto}/DTM/BPW/{romawi}/{tahun_pilih}"
                prev_no_qa = f"{no_urut_auto}/QA/BPW-DTM/{romawi}/{tahun_pilih}"
        else: # Non KAN
            prev_no_kontrak = f"{no_urut_auto}/DTM/NON-KAN/{romawi}/{tahun_pilih}"
            prev_no_qa = f"{no_urut_auto}/QA/NON-KAN-DTM/{romawi}/{tahun_pilih}"

        st.info(f"💡 **Penomoran Otomatis:** No Kontrak: `{prev_no_kontrak}` | No QA: `{prev_no_qa}`")

        submit = st.form_submit_button("🚀 Generate Dokumen (Word) & Kirim ke n8n", type="primary", use_container_width=True)

    # 4. LOGIKA EKSEKUSI
    if submit:
        required_fields = {
            "Nama Klien": nama_klien, "Alamat": alamat_klien, "Nama Direktur": nama_ttd, 
            "Jabatan": jabatan_raw, "Harga": harga_awal, "No WA Marketing": tlp_marketing,
            "Email Klien": email_klien
        }
        empty_fields = [k for k, v in required_fields.items() if not v or v == 0]

        if empty_fields:
            st.error(f"⚠️ **Gagal!** Data berikut belum lengkap: {', '.join(empty_fields)}")
        elif tlp_klien and not tlp_klien.replace("+", "").isdigit():
            st.error("⚠️ **Gagal!** No HP/WA Klien hanya boleh berisi angka!")
        elif tlp_marketing and not tlp_marketing.replace("+", "").isdigit():
            st.error("⚠️ **Gagal!** No HP/WA Marketing hanya boleh berisi angka!")
        elif email_klien and "@" not in email_klien:
            st.error("⚠️ **Gagal!** Format Email Klien tidak valid!")
        elif skema == "LSUHK" and len(scope_pilihan) == 0:
            st.error("⚠️ **Gagal!** Anda harus memilih minimal satu Ruang Lingkup untuk LSUHK!")
        else:
            with st.spinner("🔄 Sedang memproses dokumen Word dan mengirim ke n8n..."):
                try:
                    hari_nama = get_hari_indo(tgl_dokumen)
                    tgl_h, bln_h, thn_h = tgl_terbilang(tgl_dokumen)
                    
                    # ---> LOGIKA SCOPE PENDEK (UNTUK DATABASE & NAMA FILE)
                    scope_pendek = " & ".join(scope_pilihan) 
                    
                    # ---> LOGIKA SCOPE PANJANG (KHUSUS UNTUK TEMPLATE WORD)
                    scope_panjang = ""
                    if skema == "LSUHK":
                        if "PPIU" in scope_pilihan and "PIHK" in scope_pilihan:
                            scope_panjang = "Penyelenggara Perjalanan Ibadah Umrah (PPIU) & Penyelenggara Ibadah Haji Khusus (PIHK)"
                        elif "PPIU" in scope_pilihan:
                            scope_panjang = "Penyelenggara Perjalanan Ibadah Umrah (PPIU)"
                        elif "PIHK" in scope_pilihan:
                            scope_panjang = "Penyelenggara Ibadah Haji Khusus (PIHK)"
                    elif skema == "LSPr":
                        if "Hotel" in scope_pilihan:
                            scope_panjang = "Penyediaan Akomodasi (Hotel)"
                        elif "Restoran" in scope_pilihan:
                            scope_panjang = "Jasa makanan dan minuman (Restoran)"
                        elif "BPW" in scope_pilihan:
                            scope_panjang = "Biro Perjalanan Wisata (BPW)"
                    else: # Non KAN
                        scope_panjang = scope_pendek

                    harga_formatted = format_rupiah(harga_awal)
                    bulan_indo_list = ["", "Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
                    tanggal_indo_rapi = f"{tgl_dokumen.day} {bulan_indo_list[tgl_dokumen.month]} {tgl_dokumen.year}"

                    # ---> CONTEXT DOCX (Variabel untuk Word)
                    context = {
                        'hari': hari_nama, 'tgl_teks': tgl_h, 'bulan': bln_h, 'tahun_teks': thn_h,
                        'tgl_angka': tanggal_indo_rapi,
                        'no_kontrak': prev_no_kontrak, 'no_qa': prev_no_qa,
                        'nama_klien': nama_klien, 'alamat_klien': alamat_klien, 'tlp_klien': tlp_klien,
                        'email_klien': email_klien,
                        'nama_brand': nama_brand if nama_brand else "-", # Jika kosong, isi "-"
                        'kategori': kategori_brand if kategori_brand else "-", # Jika kosong, isi "-"
                        'nama_ttd': nama_ttd, 'jabatan': jabatan_raw, 'jabatan_ttd': f"{jabatan_raw} {nama_klien}",
                        'harga': harga_formatted, 
                        'scope': scope_panjang, # <--- DISINI DICETAK PANJANG
                        'lokasi': lokasi,
                        'status_transportasi': status_transportasi, 'status_akomodasi': status_akomodasi
                    }

                    template_path = ""
                    if skema == "LSUHK":
                        if len(scope_pilihan) == 2: template_path = "templates/gabungan_lsuhk_ppiu_pihk.docx"
                        elif "PPIU" in scope_pilihan: template_path = "templates/gabungan_lsuhk_ppiu.docx"
                        else: template_path = "templates/gabungan_lsuhk_pihk.docx"
                    elif skema == "LSPr":
                        if "Hotel" in scope_pilihan: template_path = "templates/gabungan_lspr_hotel.docx"
                        elif "Restoran" in scope_pilihan: template_path = "templates/gabungan_lspr_restoran.docx"
                        else: template_path = "templates/gabungan_lspr_bpw.docx"
                    else:
                        template_path = "templates/gabungan_non_kan.docx"

                    os.makedirs("output/word", exist_ok=True)
                    os.makedirs("templates", exist_ok=True)

                    if not os.path.exists(template_path):
                        st.error(f"⚠️ Template tidak ditemukan! Pastikan file `{template_path}` sudah ada.")
                        st.stop()

                    doc = DocxTemplate(template_path)
                    doc.render(context)
                    
                    fname_doc = f"Perjanjian Kerjasama {scope_pendek} {nama_klien}.docx"
                    path_docx = f"output/word/{fname_doc}"
                    doc.save(path_docx)

                    # --- KIRIM DATA PUSAT KE n8n (SUPABASE & SPREADSHEET) ---
                    try:
                        payload_data = {
                            "no_kontrak": prev_no_kontrak, 
                            "no_qa": prev_no_qa,
                            "nama_klien": nama_klien, 
                            "nama_brand": nama_brand, # Tambahan data ke Supabase opsional
                            "kategori_brand": kategori_brand, # Tambahan data ke Supabase opsional
                            "marketing": marketing,
                            "no_wa_marketing": format_wa_number(tlp_marketing), 
                            "no_wa_klien": format_wa_number(tlp_klien),
                            "email_klien": email_klien, 
                            "skema": skema, 
                            "ruang_lingkup": scope_pendek, # <--- DISINI DIKIRIM PENDEK!
                            "harga": harga_formatted,
                            "alamat_klien": alamat_klien, 
                            "tanggal_dokumen": tanggal_indo_rapi, 
                            "status_bayar": status_bayar,
                            "kategori_audit": kategori_audit,
                            "status_progres": status_progres
                        }
                        files_to_send = {
                            "file_word": (fname_doc, open(path_docx, "rb"), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
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
                               f"📌 *No Kontrak:* {prev_no_kontrak}\n📌 *Skema:* {skema}\n📌 *Ruang Lingkup:* {scope_pendek}\n"
                               f"💰 *Harga:* {harga_formatted}\n\nMohon tunggu beberapa saat hingga sistem n8n memproses versi PDF-nya. Terima kasih.")
                    
                    st.session_state.docs_generated = True
                    st.session_state.path_doc = path_docx
                    st.session_state.wa_url = f"https://wa.me/{wa_number}?text={urllib.parse.quote(wa_text)}"

                    st.balloons()
                    st.success(f"✅ Selesai! Dokumen terbuat dan Data terkirim ke n8n!")

                except Exception as e:
                    st.error(f"❌ Terjadi kesalahan teknis: {e}")

    if st.session_state.docs_generated:
        with st.container(border=True):
            st.markdown("<h4 style='color: #16a34a; margin-top: 0;'>🎉 Dokumen Word Siap Diunduh!</h4>", unsafe_allow_html=True)
            st.info("💡 Versi PDF akan diproses dan disimpan secara otomatis oleh sistem n8n ke Google Drive.")
            
            if os.path.exists(st.session_state.path_doc):
                with open(st.session_state.path_doc, "rb") as f:
                    st.download_button("📥 Download Kontrak & QA (Word)", f, file_name=os.path.basename(st.session_state.path_doc), use_container_width=True)
            
            st.markdown(
                f"""
                <a href="{st.session_state.wa_url}" target="_blank" style="text-decoration: none;">
                    <button style="background-color: #25D366; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: bold; width: 100%; font-size: 16px; margin-top: 10px;">
                        💬 Kirim Notifikasi WA ke Marketing
                    </button>
                </a>
                """, unsafe_allow_html=True
            )

# ... (Tab 2 tetap sama) ...

with tab3:
    with st.container(border=True):
        st.markdown("<h4 class='section-title'><span class='material-symbols-outlined'>settings</span> Petunjuk Penggunaan</h4>", unsafe_allow_html=True)
        st.markdown("""
        1. Pastikan file template Word (`.docx`) berada di dalam folder `templates/`.
        2. Nama template gabungan yang dibutuhkan:
           - **LSUHK:** `gabungan_lsuhk_ppiu_pihk.docx`, `gabungan_lsuhk_ppiu.docx`, `gabungan_lsuhk_pihk.docx`
           - **LSPr:** `gabungan_lspr_hotel.docx`, `gabungan_lspr_restoran.docx`, `gabungan_lspr_bpw.docx`
           - **Non KAN:** `gabungan_non_kan.docx`
        3. Aplikasi ini akan menghasilkan **1 file Word (.docx)** yang berisi Kontrak & QA, lalu mengirimkannya ke n8n.
        4. **Konversi ke PDF akan dilakukan secara otomatis oleh n8n** di server cloud.
        """)
