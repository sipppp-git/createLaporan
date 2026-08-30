import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseUpload
import io

st.title(":material/edit_document: Form Input Eviden LCS")
st.markdown("Silakan lengkapi data di bawah ini untuk mengirimkan laporan eviden kegiatan.")

# 1. Koneksi Teks ke Spreadsheet Lapor Baru
conn = st.connection("gsheets", type=GSheetsConnection)
url_lapor = st.secrets["connections"]["gsheets"]["form_eviden_lcs"]

# 2. Fungsi Unggah ke Google Drive
def unggah_ke_drive(file_buffer, nama_file, tipe_mime):
    kredensial_dict = st.secrets["gcp_service_account"]
    folder_id = st.secrets["DRIVE_FOLDER_ID"]
    
    # Membangun otentikasi
    creds = service_account.Credentials.from_service_account_info(
        kredensial_dict, scopes=['https://www.googleapis.com/auth/drive.file']
    )
    service = build('drive', 'v3', credentials=creds)
    
    # Membungkus file dari RAM Streamlit agar bisa dibaca API
    media = MediaIoBaseUpload(io.BytesIO(file_buffer), mimetype=tipe_mime, resumable=True)
    metadata_file = {
        'name': nama_file,
        'parents': [folder_id]
    }
    
    # Eksekusi unggah
    file_terkirim = service.files().create(body=metadata_file, media_body=media, fields='id, webViewLink').execute()
    return file_terkirim.get('webViewLink')

# 3. Form Input
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

# 4. Logika Eksekusi Pengiriman
if tombol_kirim:
    if not nama or not nip or not judul_konten or eviden is None:
        st.error("Mohon lengkapi seluruh kolom isian dan unggah file eviden sebelum mengirim.", icon=":material/warning:")
    else:
        with st.spinner("Mengunggah dokumen dan menyimpan data..."):
            try:
                # A. Terbangkan file ke Google Drive terlebih dahulu
                file_bytes = eviden.read()
                link_drive = unggah_ke_drive(file_bytes, eviden.name, eviden.type)
                
                # B. Tarik data lama dari spreadsheet khusus form
                df_lama = conn.read(spreadsheet=url_lapor)
                
                # C. Siapkan baris data baru (tambahkan kolom Link Eviden)
                data_baru = pd.DataFrame([{
                    "Nama": nama,
                    "NIP": nip,
                    "Kabupaten": kabupaten,
                    "Judul Konten": judul_konten,
                    "Nama File Eviden": eviden.name,
                    "Link Eviden": link_drive # Menyimpan URL agar mudah diakses panitia
                }])
                
                # D. Perbarui Google Sheets
                df_update = pd.concat([df_lama, data_baru], ignore_index=True)
                conn.update(spreadsheet=url_lapor, data=df_update)
                
                st.success(f"Laporan atas nama **{nama}** berhasil disubmit!", icon=":material/check_circle:")
                
            except Exception as e:
                st.error(f"Terjadi kesalahan saat memproses data: {e}", icon=":material/error:")