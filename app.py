import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Import fungsi dari file helpers.py
from helpers import konversi_ke_direct_link, buat_tabel_kegiatan_html

st.set_page_config(page_title="Cetak SKP LCS Agustus", layout="wide")

# Membaca file CSS eksternal dan menerapkannya
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Koneksi & Ambil Data
conn = st.connection("gsheets", type=GSheetsConnection)
url_spreadsheet = st.secrets["connections"]["gsheets"]["spreadsheet"]
df = conn.read(spreadsheet=url_spreadsheet, ttl=60)
df["Tanggal"] = df["Tanggal"].astype(str)

# Sidebar
st.sidebar.title("🎮 Panel Kontrol Admin")
daftar_penyuluh = df["Nama"].unique()
nama_terpilih = st.sidebar.selectbox("Pilih Nama Penyuluh:", daftar_penyuluh)

st.sidebar.warning("💡 Tekan **Ctrl + P** untuk cetak PDF. Pastikan 'Background graphics' dicentang!")

# Filter Data
df_penyuluh = df[df["Nama"] == nama_terpilih]

if not df_penyuluh.empty:
    row = df_penyuluh.iloc[0]

    # Kop Surat
    st.markdown(
        """
        <div style="text-align: center; font-family: 'Times New Roman', serif; line-height: 1.6;">
            <h3 style="margin: 0; font-size: 18pt; font-weight: bold;">LAPORAN KEGIATAN</h3>
            <h3 style="margin: 0; font-size: 14pt; font-weight: bold;">PENDERASAN MATERI DAN INFORMASI PEMBANGUNAN PERTANIAN</h3>
            <h4 style="margin: 0; font-size: 12pt; font-weight: bold;">PERIODE: AGUSTUS 2026</h4>
        </div>
        <hr style="border: 1px solid black; margin-top: 10px; margin-bottom: 20px;">
        """,
        unsafe_allow_html=True,
    )

    # Identitas
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Nama Penyuluh:** {row['Nama']}")
        st.markdown(f"**NIP:** {row['NIP']}")
    with col2:
        st.markdown(f"**Kabupaten/Wilayah:** {row.get('Kabupaten', '-')}")
        st.markdown(f"**Tanggal Cetak:** {row['Tanggal']}")

    # Tabel Rincian (Memanggil fungsi dari helpers.py)
    st.markdown("#### B. RINCIAN PELAKSANAAN TUGAS")
    st.markdown(buat_tabel_kegiatan_html(df_penyuluh), unsafe_allow_html=True)

    # Filter Eviden Foto
    list_eviden = []
    for i in range(1, 11):
        col_name = f"Ev{i}"
        if col_name in df.columns:
            url_foto = row[col_name]
            if pd.notna(url_foto) and str(url_foto).strip().lower() != "nan":
                direct_url = konversi_ke_direct_link(url_foto)
                if direct_url:
                    list_eviden.append(direct_url)

    # Galeri Eviden
    st.markdown("#### LAMPIRAN EVIDEN LCS")
    if list_eviden:
        grid = st.columns(2)
        for idx, url in enumerate(list_eviden):
            with grid[idx % 2]:
                st.markdown(
                    f"""
                    <div style="margin-bottom: 20px; border: 1px solid #ddd; padding: 10px; text-align: center;">
                        <img src="{url}" style="width: 100%; max-height: 400px; object-fit: contain;">
                        <p style="margin-top: 8px; font-family: 'Times New Roman', serif;">Eviden ke-{idx + 1}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.info("Tidak ada lampiran gambar eviden.")
else:
    st.error("Data tidak ditemukan.")
