import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Dasbor LCS", layout="wide")

# ==============================================================================
# 1. JUDUL & KONEKSI DATA
# ==============================================================================
ikon_svg = """
<svg width="35" height="35" viewBox="0 0 24 24" fill="none" stroke="#d84315" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <line x1="18" y1="20" x2="18" y2="10"></line>
    <line x1="12" y1="20" x2="12" y2="4"></line>
    <line x1="6" y1="20" x2="6" y2="14"></line>
</svg>
"""

st.markdown(
    f"""<div style="display: flex; align-items: center; gap: 15px; margin-bottom: 20px;">
{ikon_svg}
<h1 style="margin: 0; font-size: 2.2rem; font-weight: bold;">Dasbor Pelaporan LCS</h1>
</div>""",
    unsafe_allow_html=True
)

conn = st.connection("gsheets", type=GSheetsConnection)

# Menggunakan nama kunci terbaru sesuai dengan file secrets.toml Anda
url_lapor = st.secrets["connections"]["gsheets"]["spreadsheet_lcs"]
url_total = st.secrets["connections"]["gsheets"]["spreadsheet_penyuluh"]

# Mengambil data dari Google Sheets
df_lapor = conn.read(spreadsheet=url_lapor, ttl=60)
df_total = conn.read(spreadsheet=url_total, ttl=600) 

# ==============================================================================
# 2. LOGIKA PERHITUNGAN (VALIDASI MASTER DATA)
# ==============================================================================
if not df_lapor.empty and not df_total.empty:
    
    # Standarisasi teks NIP agar tidak gagal validasi hanya karena kelebihan spasi
    # Asumsi: Kolom di laporan bernama "NIP", dan di master bernama "Nomor"
    df_lapor["NIP"] = df_lapor["NIP"].astype(str).str.strip()
    df_total["Nomor"] = df_total["Nomor"].astype(str).str.strip()
    df_total["Kabupaten"] = df_total["Kabupaten"].astype(str).str.upper().str.strip()

    # Ambil daftar NIP unik yang sudah masuk ke form laporan
    nip_yang_melapor = df_lapor["NIP"].unique()

    # VALIDASI: Jika Nomor NIP ada di daftar nip_yang_melapor, nilainya True (1), jika tidak False (0)
    df_total["Status_Lapor"] = df_total["Nomor"].isin(nip_yang_melapor).astype(int)

    # Kelompokkan langsung dari data master berdasarkan Kabupaten
    df_dashboard = df_total.groupby("Kabupaten").agg(
        Total_Penyuluh=("Nomor", "count"),      # Hitung total baris pegawai di master
        Jumlah_Lapor=("Status_Lapor", "sum")    # Jumlahkan status yang bernilai 1 (True)
    ).reset_index()

    # Hitung persentase kepatuhan
    df_dashboard["Persentase (%)"] = (df_dashboard["Jumlah_Lapor"] / df_dashboard["Total_Penyuluh"] * 100).round(1)

# ==============================================================================
# 3. VISUALISASI GRAFIK & TABEL
# ==============================================================================
    st.markdown("### Persentase Pelaporan per Kabupaten/Kota")
    
    # Grafik batang
    st.bar_chart(
        data=df_dashboard.set_index("Kabupaten_Clean"), 
        y="Persentase (%)", 
        use_container_width=True
    )

    st.markdown("### Rincian Data")
    
    # Kalkulasi Metrik Global
    total_semua = df_dashboard["Total_Penyuluh"].sum()
    lapor_semua = df_dashboard["Jumlah_Lapor"].sum()
    persen_global = round((lapor_semua / total_semua) * 100, 1) if total_semua > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Penyuluh", f"{total_semua} Orang")
    col2.metric("Total Lapor", f"{lapor_semua} Orang")
    col3.metric("Persentase Kepatuhan Global", f"{persen_global} %")

    # Tabel Rincian
    st.dataframe(
        df_dashboard,
        column_config={
            "Kabupaten_Clean": "Nama Kabupaten / Kota",
            "Total_Penyuluh": "Total Pegawai",
            "Jumlah_Lapor": "Sudah Melapor",
            "Persentase (%)": st.column_config.ProgressColumn(
                "Tingkat Kepatuhan",
                help="Persentase penyuluh yang sudah mengumpulkan eviden",
                format="%f %%",
                min_value=0,
                max_value=100,
            ),
        },
        hide_index=True,
        use_container_width=True
    )

# ==============================================================================
# 4. TABEL RINCIAN KESELURUHAN
# ==============================================================================
    st.markdown("---")
    st.markdown("### Rincian Data Keseluruhan")
    
    total_semua = df_dashboard["Total_Penyuluh"].sum()
    lapor_semua = df_dashboard["Jumlah_Lapor"].sum()
    persen_global = round((lapor_semua / total_semua) * 100, 1) if total_semua > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Penyuluh", f"{total_semua} Orang")
    col2.metric("Total Lapor", f"{lapor_semua} Orang")
    col3.metric("Total Persentase", f"{persen_global} %")

    st.dataframe(
        df_dashboard,
        column_config={
            "Kabupaten": "Nama Kabupaten",
            "Total_Penyuluh": "Total Pegawai",
            "Jumlah_Lapor": "Sudah Melapor",
            "Persentase (%)": st.column_config.ProgressColumn(
                "Persentase",
                format="%f %%",
                min_value=0,
                max_value=100,
            ),
        },
        hide_index=True,
        use_container_width=True
    )
else:
    st.warning("Data belum tersedia atau gagal dimuat dari Google Sheets. Pastikan tabel tidak kosong.")
