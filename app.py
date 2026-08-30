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

url_lapor = st.secrets["connections"]["gsheets"]["spreadsheet_lapor"]
url_total = st.secrets["connections"]["gsheets"]["spreadsheet_total"]

df_lapor = conn.read(spreadsheet=url_lapor, ttl=60)
df_total = conn.read(spreadsheet=url_total, ttl=600) 

# ==============================================================================
# 2. LOGIKA PERHITUNGAN (VALIDASI MASTER DATA)
# ==============================================================================
if not df_lapor.empty and not df_total.empty:
    
    # Standarisasi teks NIP agar tidak gagal validasi hanya karena kelebihan spasi
    df_lapor["NIP"] = df_lapor["NIP"].astype(str).str.strip()
    df_total["Nomor"] = df_total["Nomor"].astype(str).str.strip()
    df_total["Kabupaten"] = df_total["Kabupaten"].astype(str).str.upper().str.strip()

    # Ambil daftar NIP unik yang sudah masuk ke form laporan
    nip_yang_melapor = df_lapor["NIP"].unique()

    # VALIDASI: Jika Nomor NIP ada di daftar nip_yang_melapor, nilainya True (1), jika tidak False (0)
    df_total["Status_Lapor"] = df_total["Nomor"].isin(nip_yang_melapor).astype(int)

    # Kelompokkan langsung dari data master berdasarkan Kabupaten
    df_dashboard = df_total.groupby("Kabupaten").agg(
        Total_Penyuluh=("Nomor", "count"),      # Hitung total baris pegawai
        Jumlah_Lapor=("Status_Lapor", "sum")    # Jumlahkan status yang bernilai 1 (True)
    ).reset_index()

    # Hitung persentase kepatuhan
    df_dashboard["Persentase (%)"] = (df_dashboard["Jumlah_Lapor"] / df_dashboard["Total_Penyuluh"] * 100).round(1)

# ==============================================================================
# 3. VISUALISASI DASBOR (HORIZONTAL BAR CHART)
# ==============================================================================
    st.markdown("### Status Pelaporan per Kabupaten")
    
    # Daftar 4 kabupaten target
    target_kabupaten = [
        "KAB. PEGUNUNGAN BINTANG",
        "KAB. JAYAWIJAYA",
        "KAB. YAHUKIMO",
        "KAB. MAMBERAMO TENGAH"
    ]
    
    # Filter data hanya untuk 4 kabupaten tersebut
    df_chart = df_dashboard[df_dashboard["Kabupaten"].isin(target_kabupaten)].copy()
    
    if not df_chart.empty:
        # Bersihkan nama kabupaten dari kata "KAB. " agar lebih rapi di grafik
        df_chart["Kab_Label"] = df_chart["Kabupaten"].str.replace("KAB. ", "")
        
        # Urutkan data berdasarkan persentase (dari kecil ke besar agar yang tertinggi di atas)
        df_chart = df_chart.sort_values("Persentase (%)", ascending=True)
        
        # Gabungkan teks keterangan untuk ditampilkan di dalam grafik
        df_chart["Teks_Label"] = df_chart["Jumlah_Lapor"].astype(str) + " dari " + df_chart["Total_Penyuluh"].astype(str) + " Orang (" + df_chart["Persentase (%)"].astype(str) + "%)"

        # Buat Grafik Batang Horizontal
        fig = go.Figure(go.Bar(
            x=df_chart["Persentase (%)"],
            y=df_chart["Kab_Label"],
            orientation='h',
            text=df_chart["Teks_Label"],
            textposition='inside',
            insidetextanchor='middle',
            textfont=dict(color='white', size=14, weight='bold'),
            marker=dict(color='#d84315') # Warna oranye khas
        ))

        # Atur tata letak grafik agar bersih dari garis bantu
        fig.update_layout(
            xaxis=dict(range=[0, 100], showgrid=False, visible=False), 
            yaxis=dict(showgrid=False, tickfont=dict(size=14, color='#333', weight='bold')),
            margin=dict(l=10, r=10, t=10, b=10),
            height=250,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )

        # Render grafik ke layar
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    else:
        st.info("Data untuk kabupaten target belum tersedia.")

# ==============================================================================
# 4. TABEL RINCIAN KESELURUHAN (Sempat tertimpa)
# ==============================================================================
    st.markdown("---")
    st.markdown("### Rincian Data Keseluruhan")
    
    total_semua = df_dashboard["Total_Penyuluh"].sum()
    lapor_semua = df_dashboard["Jumlah_Lapor"].sum()
    persen_global = round((lapor_semua / total_semua) * 100, 1) if total_semua > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Penyuluh", f"{total_semua} Orang")
    col2.metric("Total Lapor", f"{lapor_semua} Orang")
    col3.metric("Kepatuhan Global", f"{persen_global} %")

    st.dataframe(
        df_dashboard,
        column_config={
            "Kabupaten": "Nama Kabupaten",
            "Total_Penyuluh": "Total Pegawai",
            "Jumlah_Lapor": "Sudah Melapor",
            "Persentase (%)": st.column_config.ProgressColumn(
                "Tingkat Kepatuhan",
                format="%f %%",
                min_value=0,
                max_value=100,
            ),
        },
        hide_index=True,
        use_container_width=True
    )
else:
    st.warning("Data belum tersedia atau gagal dimuat dari Google Sheets.")
