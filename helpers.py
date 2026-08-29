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

def buat_grid_eviden_html(row, tanggal):
    """
    Menghasilkan grid 10 kotak (5 baris x 2 kolom) untuk eviden per tanggal.
    Kotak akan tetap dirender meskipun kosong.
    """
    html = f"<div style='margin-top: 30px;'><h4 style='font-family: \"Times New Roman\", serif; font-weight: bold;'>Tanggal: {tanggal}</h4>"
    html += '<table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">'
    
    # Kumpulkan 10 status link eviden
    links = []
    for i in range(1, 11):
        col = f"Ev{i}"
        url = row.get(col, None)
        if pd.notna(url) and str(url).strip().lower() != "nan":
            direct = konversi_ke_direct_link(url)
            links.append(direct if direct else "")
        else:
            links.append("")
            
    # Buat 5 baris, masing-masing 2 kolom
    for r in range(5):
        html += "<tr>"
        for c in range(2):
            idx = r * 2 + c
            img_url = links[idx]
            if img_url:
                # Sel berisi gambar
                html += f'<td style="width: 50%; border: 1px solid black; padding: 8px; text-align: center; height: 350px; vertical-align: middle;"><img src="{img_url}" style="max-width: 100%; max-height: 330px; object-fit: contain;"></td>'
            else:
                # Sel kosong
                html += f'<td style="width: 50%; border: 1px solid black; padding: 8px; text-align: center; height: 350px; vertical-align: middle; background-color: #f9f9f9; color: #999; font-family: \'Times New Roman\', serif;">(Tidak ada lampiran {idx+1})</td>'
        html += "</tr>"
        
    html += "</table></div>"
    return html
