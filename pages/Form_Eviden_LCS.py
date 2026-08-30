import streamlit as st

st.set_page_config(page_title="Input Eviden LCS", page_icon="📝", layout="centered")

st.markdown("### 📝 Form Input Eviden LCS")
st.markdown("Silakan lengkapi data di bawah ini untuk mengirimkan laporan eviden kegiatan.")

# Membuat form agar halaman tidak termuat ulang sebelum tombol submit ditekan
with st.form(key="form_eviden", clear_on_submit=True):
    # 1. Input Teks
    nama = st.text_input("Nama Lengkap", placeholder="Masukkan nama lengkap")
    nip = st.text_input("NIP", placeholder="Masukkan NIP (18 Digit)")
    
    # 2. Dropdown Kabupaten
    daftar_kabupaten = [
        "KAB. PEGUNUNGAN BINTANG", 
        "KAB. JAYAWIJAYA", 
        "KAB. YAHUKIMO", 
        "KAB. MAMBERAMO TENGAH"
    ]
    kabupaten = st.selectbox("Kabupaten Tugas", daftar_kabupaten)
    
    # 3. Input Judul Konten
    judul_konten = st.text_input("Judul Konten", placeholder="Contoh: Laporan Penyuluhan Pertanian Desa X")
    
    # 4. Upload Eviden (Mendukung gambar dan dokumen PDF)
    eviden = st.file_uploader("Unggah Eviden (Foto/PDF)", type=["png", "jpg", "jpeg", "pdf"])
    
    # 5. Tombol Submit
    tombol_kirim = st.form_submit_button("Kirim Data Eviden")

# Logika pemrosesan setelah tombol ditekan
if tombol_kirim:
    # Validasi kelengkapan data
    if not nama or not nip or not judul_konten or eviden is None:
        st.error("⚠️ Mohon lengkapi seluruh kolom isian dan unggah file eviden sebelum mengirim.")
    else:
        st.success(f"✅ Data atas nama {nama} berhasil divalidasi!")
        st.info(f"File siap diproses: {eviden.name} (Ukuran: {eviden.size / 1024:.2f} KB)")
        
        # Objek file 'eviden' ini nantinya bisa dikonversi menjadi buffer/base64 
        # untuk diteruskan ke handler Apps Script dan dirutekan ke folder Google Drive
        # berdasarkan spesifikasi NIP penyuluh.