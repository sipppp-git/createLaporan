import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Import fungsi dari helpers.py
from helpers import konversi_ke_direct_link, buat_tabel_kegiatan_html, buat_grid_eviden_html

st.set_page_config(page_title="Cetak SKP LCS Agustus", layout="wide")

# Muat CSS
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Koneksi ke GSheets
conn = st.connection("gsheets", type=GSheetsConnection)
url_spreadsheet = st.secrets["connections"]["gsheets"]["spreadsheet"]
df = conn.read(spreadsheet=url_spreadsheet, ttl=60)
df["Tanggal"] = df["Tanggal"].astype(str)

st.sidebar.title("🎮 Panel Kontrol")
daftar_penyuluh = df["Nama"].unique()
nama_terpilih = st.sidebar.selectbox("Pilih Nama Penyuluh:", daftar_penyuluh)

# Filter Data (Bisa menghasilkan lebih dari 1 baris jika ada beberapa tanggal)
df_penyuluh = df[df["Nama"] == nama_terpilih]

if not df_penyuluh.empty:
    # Ambil info identitas dari baris pertama saja
    info = df_penyuluh.iloc[0]

    # --- KOP SURAT ---
    st.markdown(
        """
        <div style="text-align: center; font-family: 'Times New Roman', serif; line-height: 1.5;">
            <h3 style="margin: 0; font-size: 16pt; font-weight: bold;">LAPORAN KEGIATAN</h3>
            <h3 style="margin: 0; font-size: 14pt; font-weight: bold;">TUGAS JABATAN PENYULUH PERTANIAN SESUAI JENJANG</h3>
            <h3 style="margin: 0; font-size: 14pt; font-weight: bold;">PENDERASAN MATERI DAN INFORMASI PEMBANGUNAN PERTANIAN</h3>
            <h4 style="margin: 0; font-size: 12pt; font-weight: bold;">PERIODE AGUSTUS 2026</h4>
        </div>
        <hr style="border: 1.5px solid black; margin-top: 15px; margin-bottom: 20px;">
        """,
        unsafe_allow_html=True,
    )

    # --- IDENTITAS (Format tabel tanpa garis) ---
    st.markdown(
        f"""
        <table style="width: 100%; font-family: 'Times New Roman', serif; font-size: 12pt; border: none; margin-bottom: 20px;">
            <tr><td style="width: 150px; border: none; padding: 3px;">Nama</td><td style="width: 10px; border: none;">:</td><td style="border: none;">{info['Nama']}</td></tr>
            <tr><td style="border: none; padding: 3px;">NIP</td><td style="border: none;">:</td><td style="border: none;">{info['NIP']}</td></tr>
            <tr><td style="border: none; padding: 3px;">Kabupaten</td><td style="border: none;">:</td><td style="border: none;">{info.get('Kabupaten', '-')}</td></tr>
        </table>
        """,
        unsafe_allow_html=True
    )

    # --- LOOPING EVIDEN PER TANGGAL ---
    # Looping setiap baris di dataframe yang sudah difilter
    for index, row in df_penyuluh.iterrows():
        tanggal_kegiatan = row['Tanggal']
        
        # Panggil fungsi pembuat grid 10 kotak dari helpers.py
        grid_html = buat_grid_eviden_html(row, tanggal_kegiatan)
        st.markdown(grid_html, unsafe_allow_html=True)

    # --- LEMBAR TANDA TANGAN ---
    st.write("")
    st.write("")
    col_kosong, col_ttd = st.columns([2, 1])
    with col_ttd:
        st.markdown(
            f"""
            <div style="font-family: 'Times New Roman', serif; font-size: 12pt; text-align: left; page-break-inside: avoid;">
                Papua Pegunungan, 31 Agustus 2026<br>
                Penyuluh Pertanian,<br><br><br><br><br>
                <b><u>{info['Nama']}</u></b><br>
                NIP. {info['NIP']}
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
    st.error("Data tidak ditemukan.")
