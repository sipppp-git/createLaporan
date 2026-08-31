import streamlit as st
import requests
import base64

st.title(":material/edit_document: Form Input Eviden LCS")
st.markdown("Silakan lengkapi data di bawah ini untuk mengirimkan laporan eviden kegiatan.")

# Tempelkan URL Webhook Anda (pastikan ekornya /exec)
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbz0COQV-ngjL1Own_u-xeZHmrPppLvA84wfNE-yJrpkvnETKxEMdPtA-rwjr3VWR8folQ/exec"

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

if tombol_kirim:
    if not nama or not nip or not judul_konten or eviden is None:
        st.error("Mohon lengkapi seluruh kolom isian dan unggah file eviden sebelum mengirim.", icon=":material/warning:")
    else:
        with st.spinner("Mengunggah dokumen dan menyimpan data ke sistem..."):
            try:
                file_bytes = eviden.read()
                file_base64 = base64.b64encode(file_bytes).decode('utf-8')
                
                # Payload kini membawa semua atribut teks dan lampiran sekaligus
                payload = {
                    "nama": nama,
                    "nip": nip,
                    "kabupaten": kabupaten,
                    "judulKonten": judul_konten,
                    "fileName": eviden.name,
                    "mimeType": eviden.type,
                    "fileBase64": file_base64
                }
                
                response = requests.post(WEBHOOK_URL, json=payload)
                
                try:
                    hasil = response.json()
                except ValueError:
                    st.error(f"Gagal membaca respons Webhook. Balasan: {response.text}", icon=":material/bug_report:")
                    st.stop()
                
                if hasil.get("status") == "success":
                    st.success(f"Laporan atas nama **{nama}** berhasil disubmit dan diarsipkan!", icon=":material/check_circle:")
                else:
                    st.error(f"Gagal memproses data: {hasil.get('message')}", icon=":material/error:")
                
            except Exception as e:
                st.error(f"Terjadi kesalahan sistem: {e}", icon=":material/error:")