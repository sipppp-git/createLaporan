import re
import pandas as pd

def konversi_ke_direct_link(url):
    """Mengubah link share Google Drive menjadi format thumbnail resolusi tinggi."""
    if not isinstance(url, str) or pd.isna(url):
        return None
    
    match = re.search(r"(?:id=|/d/|open\?id=)([\w-]+)", url)
    if match:
        file_id = match.group(1)
        return f"https://drive.google.com/thumbnail?id={file_id}&sz=w800"
    return None

def buat_tabel_kegiatan_html(df_penyuluh):
    """Menghasilkan HTML tabel formal dari DataFrame penyuluh."""
    html_tabel = """
    <table class="tabel-laporan">
        <thead>
            <tr>
                <th style="width: 5%;">No</th>
                <th style="width: 15%;">Tanggal</th>
                <th style="width: 45%;">Rincian Kegiatan</th>
                <th style="width: 15%;">Volume / Satuan</th>
                <th style="width: 20%;">Keterangan</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for idx, row in df_penyuluh.reset_index(drop=True).iterrows():
        tgl = row.get('Tanggal', '-')
        kegiatan = row.get('Kegiatan', row.get('Uraian', '-'))
        volume = row.get('Volume', '1 Berkas')
        ket = row.get('Keterangan', 'Terlaksana')

        html_tabel += f"""
            <tr>
                <td class="center">{idx + 1}</td>
                <td class="center">{tgl}</td>
                <td>{kegiatan}</td>
                <td class="center">{volume}</td>
                <td>{ket}</td>
            </tr>
        """
    html_tabel += "</tbody></table>"
    return html_tabel
