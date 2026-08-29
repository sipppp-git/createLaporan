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
    Menghasilkan grid gambar secara dinamis per tanggal.
    Hanya akan membuat sel (kotak) sejumlah gambar yang benar-benar diunggah.
    """
    # Kumpulkan hanya link eviden yang ada isinya (valid)
    links_valid = []
    for i in range(1, 11):
        col = f"Ev{i}"
        if col in row.index:
            url = row.get(col, None)
            if pd.notna(url) and str(url).strip().lower() != "nan":
                direct = konversi_ke_direct_link(url)
                if direct:
                    links_valid.append(direct)
                    
    # Jika tidak ada gambar sama sekali di tanggal tersebut
    if len(links_valid) == 0:
        return f"<div style='margin-top: 20px;'><h4 style='font-family: \"Times New Roman\", serif; font-weight: bold;'>Tanggal: {tanggal}</h4><p style='font-family: \"Times New Roman\", serif; font-size: 11pt; font-style: italic;'>(Tidak ada lampiran gambar)</p></div>"

    # Jika ada gambar, buat tabel gridnya
    html = f"<div style='margin-top: 20px;'><h4 style='font-family: \"Times New Roman\", serif; font-weight: bold;'>Tanggal: {tanggal}</h4>"
    html += '<table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">'
    
    # Looping berdasarkan jumlah gambar yang ada, dilompati 2 per 2 (karena 2 kolom)
    for i in range(0, len(links_valid), 2):
        html += "<tr>"
        
        # Kolom 1 (Kiri) - Pasti ada karena kita mulai dari index i
        img_kiri = links_valid[i]
        html += f'<td style="width: 50%; border: 1px solid black; padding: 8px; text-align: center; height: 350px; vertical-align: middle;"><img src="{img_kiri}" style="max-width: 100%; max-height: 330px; object-fit: contain;"></td>'
        
        # Kolom 2 (Kanan) - Cek apakah masih ada gambar tersisa untuk kolom kanan
        if i + 1 < len(links_valid):
            img_kanan = links_valid[i+1]
            html += f'<td style="width: 50%; border: 1px solid black; padding: 8px; text-align: center; height: 350px; vertical-align: middle;"><img src="{img_kanan}" style="max-width: 100%; max-height: 330px; object-fit: contain;"></td>'
        else:
            # Jika ganjil (gambar terakhir sendirian di kiri), kolom kanan dibuat kosong tanpa border
            html += '<td style="width: 50%; border: none;"></td>'
            
        html += "</tr>"
        
    html += "</table></div>"
    return html
