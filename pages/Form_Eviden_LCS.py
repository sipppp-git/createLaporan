import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.title(":material/edit_document: Form Input Eviden LCS")
st.markdown("Silakan lengkapi data di bawah ini untuk mengirimkan laporan eviden kegiatan.")

# Membangun koneksi ke Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)
url_lapor = st.secrets["connections"]["gsheets"]["spreadsheet_lcs"]

# Membuat form input
with st.form(key="form_eviden", clear_on_submit=True):
    nama = st.text_input("Nama Lengkap", placeholder="Masukkan nama lengkap")
    nip = st.text_input("NIP", placeholder="Masukkan NIP (18 Digit)")
    
    daftar_kabupaten = [
        "KAB. PEGUNUNGAN BINTANG", 
        "KAB. JAYAWIJAYA", 
        "KAB. YAHUKIMO", 
        "KAB. MAMBERAMO TENGAH"
    ]
    kabupaten = st.selectbox("Kabupaten Tugas", daftar_kabupaten)
    
    judul_konten = st.text_input("Judul Konten", placeholder="Contoh: Laporan Penyuluhan Pertanian Desa X")
    eviden = st.file_uploader("Unggah Eviden (Foto/PDF)", type=["png", "jpg", "jpeg", "pdf"])
    
    tombol_kirim = st.form_submit_button("Kirim Data")

# Logika ketika tombol ditekan
if tombol_kirim:
    if not nama or not nip or not judul_konten or eviden is None:
        st.error("Mohon lengkapi seluruh kolom isian dan unggah file eviden sebelum mengirim.", icon=":material/warning:")
    else:
        with st.spinner("Menyimpan data ke *database*..."):
            try:
                # 1. Tarik data lama dari spreadsheet
                df_lama = conn.read(spreadsheet=url_lapor)
                
                # 2. Siapkan baris data baru
                data_baru = pd.DataFrame([{
                    "Nama": nama,
                    "NIP": nip,
                    "Kabupaten": kabupaten,
                    "Judul Konten": judul_konten,
                    "Nama File Eviden": eviden.name
                }])
                
                # 3. Gabungkan data lama dan baru, lalu perbarui Google Sheets
                df_update = pd.concat([df_lama, data_baru], ignore_index=True)
                conn.update(spreadsheet=url_lapor, data=df_update)
                
                st.success(f"Laporan atas nama **{nama}** berhasil dikirim!", icon=":material/check_circle:")
                st.info(f"File {eviden.name} siap diproses lebih lanjut.", icon=":material/info:")
                
            except Exception as e:
                st.error(f"Terjadi kesalahan saat menyimpan data: {e}", icon=":material/error:")