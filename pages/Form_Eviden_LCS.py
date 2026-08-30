import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import requests
import base64

st.title(":material/edit_document: Form Input Eviden LCS")
st.markdown("Silakan lengkapi data di bawah ini untuk mengirimkan laporan eviden kegiatan.")

# 1. Koneksi Teks ke Spreadsheet
conn = st.connection("gsheets", type=GSheetsConnection)
url_lapor = st.secrets["connections"]["gsheets"]["form_eviden_lcs"]

# Taruh URL dari Apps Script di sini
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbySh0R9TjYvVL-6qFCuYt9RZj3H4Ef7G883w7YdSauIB3Cb-UKydIUDwt20EsH_HFAb/exec"

# 2. Form Input
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

# 3. Logika Eksekusi Pengiriman
if tombol_kirim:
    if not nama or not nip or not judul_konten or eviden is None:
        st.error("Mohon lengkapi seluruh kolom isian dan unggah file eviden sebelum mengirim.", icon=":material/warning:")
    else:
        with st.spinner("Mengunggah dokumen dan menyimpan data... (Mungkin memakan waktu beberapa detik)"):
            try:
                # A. Ubah file menjadi Base64 lalu kirim ke Apps Script (Webhook)
                file_bytes = eviden.read()
                file_base64 = base64.b64encode(file_bytes).decode('utf-8')
                
                payload = {
                    "fileName": eviden.name,
                    "mimeType": eviden.type,
                    "fileBase64": file_base64
                }
                
                # Menembakkan data ke Apps Script
                response = requests.post(WEBHOOK_URL, json=payload)
                
                # Cek apakah respons dari Google benar-benar JSON
                try:
                    hasil = response.json()
                except ValueError:
                    # Jika bukan JSON, tampilkan teks mentah dari Google untuk melihat error aslinya
                    st.error(f"Gagal membaca respons Webhook. Balasan dari Google: {response.text}", icon=":material/bug_report:")
                    st.stop() # Hentikan proses
                
                if hasil.get("status") == "success":
                    link_drive = hasil.get("url")
                    
                    # B. Tarik dan perbarui data di Spreadsheet
                    df_lama = conn.read(spreadsheet=url_lapor)
                    data_baru = pd.DataFrame([{
                        "Nama": nama,
                        "NIP": nip,
                        "Kabupaten": kabupaten,
                        "Judul Konten": judul_konten,
                        "Nama File Eviden": eviden.name,
                        "Link Eviden": link_drive 
                    }])
                    
                    df_update = pd.concat([df_lama, data_baru], ignore_index=True)
                    conn.update(spreadsheet=url_lapor, data=df_update)
                    
                    st.success(f"Laporan atas nama **{nama}** berhasil disubmit!", icon=":material/check_circle:")
                else:
                    st.error(f"Gagal mengunggah file ke Drive: {hasil.get('message')}", icon=":material/error:")
                
            except Exception as e:
                st.error(f"Terjadi kesalahan saat memproses data: {e}", icon=":material/error:")