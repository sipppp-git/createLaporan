import plotly.graph_objects as go
import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Dasbor LCS", layout="wide")
# Siapkan kode SVG Anda (ini contoh ikon grafik batang sederhana)
ikon_svg = """
<svg width="35" height="35" viewBox="0 0 24 24" fill="none" stroke="#d84315" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <line x1="18" y1="20" x2="18" y2="10"></line>
    <line x1="12" y1="20" x2="12" y2="4"></line>
    <line x1="6" y1="20" x2="6" y2="14"></line>
</svg>
"""

# Render SVG dan teks berdampingan menggunakan st.markdown
st.markdown(
f"""<div style="display: flex; align-items: center; gap: 15px; margin-bottom: 20px;">
{ikon_svg}
<h1 style="margin: 0; font-size: 2.2rem; font-weight: bold;">Dasbor Pelaporan LCS</h1>
</div>""",
    unsafe_allow_html=True
)

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
# 2. LOGIKA PERHITUNGAN (VALIDASI MASTER DATA)
# ==============================================================================
    # Standarisasi teks NIP agar tidak gagal validasi hanya karena kelebihan spasi
    df_lapor["NIP"] = df_lapor["NIP"].astype(str).str.strip()
    df_total["Nomor"] = df_total["Nomor"].astype(str).str.strip()
    df_total["Kabupaten"] = df_total["Kabupaten"].astype(str).str.upper().str.strip()

    # Ambil daftar NIP unik yang sudah masuk ke form laporan
    nip_yang_melapor = df_lapor["NIP"].unique()

    # VALIDASI: Buat kolom baru di data master. 
    # Jika Nomor NIP ada di daftar nip_yang_melapor, nilainya True (1), jika tidak False (0)
    df_total["Status_Lapor"] = df_total["Nomor"].isin(nip_yang_melapor).astype(int)

    # Kelompokkan langsung dari data master berdasarkan Kabupaten
    df_dashboard = df_total.groupby("Kabupaten").agg(
        Total_Penyuluh=("Nomor", "count"),      # Hitung total baris pegawai
        Jumlah_Lapor=("Status_Lapor", "sum")    # Jumlahkan status yang bernilai 1 (True)
    ).reset_index()

    # Hitung persentase kepatuhan
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
            margin=dict(t=5, b=5, l=5, r=5),
            height=200,
            # Menambahkan teks persentase tebal di tengah lubang
            annotations=[dict(text=f"<b>{persen:g}%</b>", x=0.5, y=0.5, font_size=24, font_color="#d84315", showarrow=False)]
        )

        # Menampilkan ke dalam kolom Streamlit masing-masing
        with kolom_grafik[i]:
            # 1. RENDER DIAGRAM LINGKARAN DI ATAS
            st.plotly_chart(
                fig, 
                use_container_width=True, 
                config={'displayModeBar': False},
                key=kab
            )
            
            # 2. NAMA KABUPATEN DI BAWAH DIAGRAM
            st.markdown(f"<h5 style='text-align: center; color: #d84315; font-size: 15px; font-weight: bold; margin-bottom: 0px; margin-top: -15px;'>{kab.replace('KAB. ', '')}</h5>", unsafe_allow_html=True)
            
            # 3. KETERANGAN JUMLAH DI BAGIAN PALING BAWAH
            st.markdown(f"<p style='text-align: center; color: #555; font-weight: bold; font-size: 14px; margin-top: 2px;'>{lapor} (dari {total})</p>", unsafe_allow_html=True)

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
