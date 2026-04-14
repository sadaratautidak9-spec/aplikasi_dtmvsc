import streamlit as st
st.set_page_config(page_title="Generate Invoice", layout="wide")
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
st.title("💰 Generate Invoice (Segera Hadir)")
st.write("Di sini nanti kita akan menarik data dari Google Sheets, lalu membuat form untuk memilih Klien mana yang akan dibuatkan Invoicenya.")
