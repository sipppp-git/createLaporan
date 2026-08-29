import re
import pandas as pd
import streamlit as st

# ==============================================================================
# 1. ATUR HALAMAN & TAMPILAN CETAK (CSS CUSTOM)
# ==============================================================================
st.set_page_config(page_title="Cetak SKP LCS Agustus", layout="wide")

# CSS ini berfungsi menyembunyikan tombol navigasi Streamlit saat halaman dicetak (Ctrl+P)
# sehingga hasil cetakan PDF bersih seperti dokumen resmi.
st.markdown(
    """
    <style>
    @media print {
        header, [data-testid="stSidebar"], [data-testid="stToolbar"], button {
            display: none !important;
        }
        .main .block-container {
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==============================================================================
# 2. FUNGSI BANTUAN (HELPER)
# ==============================================================================
def konversi_ke_direct_link(url):
    """Mengubah link share Google Drive menjadi link gambar langsung."""
    if not isinstance(url, str) or pd.isna(url):
        return None
    match = re.search(r"(?:id=|/d/|open\?id=)([\w-]+)", url)
    if match:
        file_id = match.group(1)
        return f"https://google.com{file_id}"
    return None


# ==============================================================================
# 3. CONTOH SIMULASI DATAFRAME (Hapus bagian ini jika df Anda sudah di-load)
# ==============================================================================
# Jika df sudah di-load dari file excel sebelumnya, abaikan baris simulasi ini.
if "df" not in locals() and "df" not in globals():
    data = {
        "Tanggal": ["2026-08-21 20:14:02.238"],
        "Nama": ["Agustinus Tekege, A.Md"],
        "NIP": ["197308072006051003"],
        "Kabupaten": ["Provinsi"],
        "Ev1": ["https://google.com..."],
        "Ev2": ["https://google.com..."],
        "Ev3": [None],
        "Ev4": [None],
        "Ev5": [None],
        "Ev6": [None],
        "Ev7": [None],
        "Ev8": [None],
        "Ev9": [None],
        "Ev10": [None],
    }
    df = pd.DataFrame(data)

# ==============================================================================
# 4. SIDEBAR PANEL KONTROL ADMIN
# ==============================================================================
st.sidebar.title("🎮 Panel Kontrol Admin")
st.sidebar.write("Gunakan panel ini untuk memfilter data penyuluh.")

# Ambil daftar nama unik penyuluh dari DataFrame Anda
daftar_penyuluh = df["Nama"].unique()
nama_terpilih = st.sidebar.selectbox("Pilih Nama Penyuluh:", daftar_penyuluh)

st.sidebar.warning(
    "💡 **Tips Cetak:** Setelah data muncul, tekan **Ctrl + P** di keyboard Anda. Pilih 'Save as PDF' dan pastikan centang opsi 'Background graphics' agar tata letak rapi!"
)

# ==============================================================================
# 5. PEMROSESAN DATA & TAMPILAN DOKUMEN SKP (SIAP CETAK)
# ==============================================================================
# Filter data berdasarkan penyuluh yang dipilih
df_penyuluh = df[df["Nama"] == nama_terpilih]

if not df_penyuluh.empty:
    # Mengambil baris pertama data penyuluh tersebut
    row = df_penyuluh.iloc[0]

    # --- KOP SURAT / JUDUL LAPORAN ---
    st.markdown(
        """
        <div style="text-align: center; font-family: 'Times New Roman', serif; line-height: 1.6;">
            <h3 style="margin: 0; font-size: 16pt; font-weight: bold;">LAPORAN SKP PENDERASAN INFORMASI PEMBANGUNAN PERTANIAN</h3>
            <h3 style="margin: 0; font-size: 14pt; font-weight: bold;">LIGHTHOUSE COMMAND CENTER (LCS)</h3>
            <h4 style="margin: 0; font-size: 12pt; font-weight: bold; text-transform: uppercase;">PERIODE: AGUSTUS 2026</h4>
        </div>
        <hr style="border: 1px solid black; margin-top: 10px; margin-bottom: 20px;">
        """,
        unsafe_allow_html=True,
    )

    # --- IDENTITAS PENYULUH ---
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.markdown(f"**Nama Penyuluh:** {row['Nama']}")
        st.markdown(f"**NIP:** {row['NIP']}")
    with col_info2:
        st.markdown(f"**Kabupaten/Wilayah:** {row['Kabupaten']}")
        st.markdown(f"**Tanggal Rekam Data:** {row['Tanggal']}")

    st.write("")

    # --- PROSES FILTER EVIDEN (MENGABAIKAN NAN) ---
    list_eviden_bersih = []
    kolom_eviden = [
        "Ev1",
        "Ev2",
        "Ev3",
        "Ev4",
        "Ev5",
        "Ev6",
        "Ev7",
        "Ev8",
        "Ev9",
        "Ev10",
    ]

    for col in kolom_eviden:
        if col in df.columns:
            url_foto = row[col]
            # Validasi: Jika ada isinya dan bukan NaN, masukkan ke list galeri
            if pd.notna(url_foto) and str(url_foto).strip().lower() != "nan":
                direct_url = konversi_ke_direct_link(url_foto)
                if direct_url:
                    list_eviden_bersih.append(direct_url)

    # --- GALERI TAMPILAN FOTO DINAMIS (OTOMATIS BERTAMBAH KOTAKNYA) ---
    st.markdown("#### 📸 LAMPIRAN BUKTI DOKUMENTASI LCS")

    if len(list_eviden_bersih) > 0:
        # Membuat grid 2 kolom secara dinamis ke bawah
        grid_kolom = st.columns(2)

        for indeks, url_langsung in enumerate(list_eviden_bersih):
            # Membagi foto selang-seling ke kolom kiri (0) dan kanan (1)
            target_kolom = indeks % 2
            with grid_kolom[target_kolom]:
                # Menampilkan gambar dengan caption nomor urut eviden
                st.image(
                    url_langsung,
                    caption=f"Eviden Dokumentasi ke-{indeks + 1}",
                    use_container_width=True,
                )
    else:
        st.info("Tidak ada lampiran gambar eviden untuk bulan ini.")

    # --- LEMBAR TANDA TANGAN ---
    st.write("")
    st.write("")
    col_ttd1, col_ttd2 = st.columns([2, 1])
    with col_ttd2:
        st.markdown(
            f"""
            <div style="font-family: 'Times New Roman', serif; font-size: 11pt; text-align: left;">
                Papua Pegunungan, Agustus 2026<br>
                Penyuluh Pertanian,<br><br><br><br><br>
                <b><u>{row['Nama']}</u></b><br>
                NIP. {row['NIP']}
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
    st.error("Data penyuluh tidak ditemukan dalam sistem.")
