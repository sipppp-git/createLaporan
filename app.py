import plotly.graph_objects as go
import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Dasbor LCS", layout="wide")
st.title("📊 Dasbor Kepatuhan Pelaporan LCS")

# ==============================================================================
# 1. KONEKSI DATA
# ==============================================================================
conn = st.connection("gsheets", type=GSheetsConnection)
df_lapor = conn.read(spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet_lcs"], ttl=60)
df_total = conn.read(spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet_penyuluh"], ttl=600) 

if not df_lapor.empty and not df_total.empty:
    
    # Samakan format teks agar proses penggabungan presisi (huruf besar & tanpa spasi lebih)
    df_lapor["Kabupaten"] = df_lapor["Kabupaten"].astype(str).str.upper().str.strip()
    df_total["Kabupaten"] = df_total["Kabupaten"].astype(str).str.upper().str.strip()

# ==============================================================================
# 2. LOGIKA PERHITUNGAN NIP BERDASARKAN KABUPATEN
# ==============================================================================
    # Hitung total target dari master (asumsi 1 baris = 1 penyuluh)
    target_per_kab = df_total.groupby("Kabupaten").size().reset_index(name="Total_Penyuluh")

    # Hitung jumlah pelapor berdasarkan NIP unik yang masuk di sheet laporan
    lapor_per_kab = df_lapor.groupby("Kabupaten")["NIP"].nunique().reset_index(name="Jumlah_Lapor")

    # Gabungkan kedua perhitungan
    df_dashboard = pd.merge(target_per_kab, lapor_per_kab, on="Kabupaten", how="left")
    df_dashboard["Jumlah_Lapor"] = df_dashboard["Jumlah_Lapor"].fillna(0).astype(int)
    
    # Hitung persentase
    df_dashboard["Persentase (%)"] = (df_dashboard["Jumlah_Lapor"] / df_dashboard["Total_Penyuluh"] * 100).round(1)

# ==============================================================================
# 3. VISUALISASI DASBOR (PLOTLY DONUT CHARTS)
# ==============================================================================
    st.markdown("### Status Pelaporan per Kabupaten")
    
    # Daftar 4 kabupaten target sesuai permintaan
    target_kabupaten = [
        "KAB. PEGUNUNGAN BINTANG",
        "KAB. JAYAWIJAYA",
        "KAB. YAHUKIMO",
        "KAB. MAMBERAMO TENGAH"
    ]
    
    # Membuat 4 kolom sejajar
    kolom_grafik = st.columns(4)
    
    for i, kab in enumerate(target_kabupaten):
        # Ambil data spesifik untuk kabupaten ini
        df_kab = df_dashboard[df_dashboard["Kabupaten"] == kab]
        
        if not df_kab.empty:
            lapor = int(df_kab["Jumlah_Lapor"].values[0])
            total = int(df_kab["Total_Penyuluh"].values[0])
            persen = df_kab["Persentase (%)"].values[0]
        else:
            lapor, total, persen = 0, 0, 0.0
            
        belum_lapor = max(total - lapor, 0)
        
        # Pengaturan warna: Oranye untuk yang sudah lapor, Abu-abu terang untuk sisanya
        warna_chart = ['#f57c00', '#e5e7eb'] 

        # Membuat grafik Donut
        fig = go.Figure(data=[go.Pie(
            values=[lapor, belum_lapor],
            labels=["Sudah Lapor", "Belum Lapor"],
            hole=0.75, # Ukuran lubang tengah
            textinfo='none', # Menyembunyikan teks bawaan pie chart
            marker=dict(colors=warna_chart),
            hoverinfo="label+value"
        )])

        fig.update_layout(
            showlegend=False,
            margin=dict(t=10, b=10, l=10, r=10),
            height=200,
            # Menambahkan teks persentase tebal di tengah lubang
            annotations=[dict(text=f"<b>{persen:g}%</b>", x=0.5, y=0.5, font_size=24, font_color="#d84315", showarrow=False)]
        )

        # Menampilkan ke dalam kolom Streamlit masing-masing
        with kolom_grafik[i]:
            # Judul Kabupaten (Warna Oranye)
            st.markdown(f"<h5 style='text-align: center; color: #d84315; font-size: 16px; font-weight: bold;'>{kab.replace('KAB. ', '')}</h5>", unsafe_allow_html=True)
            
            # Render Grafik
            st.plotly_chart(
                fig, 
                use_container_width=True, 
                config={'displayModeBar': False},
                key=kab
            )
            
            # Subtitle Jumlah (dari Total)
            st.markdown(f"<p style='text-align: center; color: #555; font-weight: bold; margin-top: -15px;'>{lapor} (dari {total})</p>", unsafe_allow_html=True)

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
            "Persentase (%)": st.column_config.ProgressColumn("Tingkat Kepatuhan", format="%f %%", min_value=0, max_value=100),
        },
        hide_index=True,
        use_container_width=True
    )
else:
    st.warning("Data gagal dimuat.")
