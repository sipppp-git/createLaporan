import streamlit as st

# 1. Konfigurasi Global (Akan diterapkan ke semua halaman)
st.set_page_config(
    page_title="Sistem Pelaporan LCS", 
    page_icon=":material/agriculture:", 
    layout="wide"
)

# 2. Definisikan Setiap Halaman dan Ikon Materialnya
halaman_dasbor = st.Page(
    "pages/dashboard.py", 
    title="Dasbor Utama", 
    icon=":material/dashboard:", 
    default=True
)

halaman_form = st.Page(
    "pages/Form_Eviden_LCS.py", 
    title="Input Eviden", 
    icon=":material/edit_document:"
)

halaman_preview = st.Page(
    "pages/preview.py", 
    title="Pratinjau Data", 
    icon=":material/visibility:"
)

# 3. Kelompokkan ke dalam Navigasi
# Anda bisa menggunakan list biasa, atau dictionary untuk membuat kategori menu/dropdown
navigasi = st.navigation(
    {
        "Laporan & Visualisasi": [halaman_dasbor, halaman_preview],
        "Input Data": [halaman_form]
    }
)

# 4. Jalankan Halaman
navigasi.run()