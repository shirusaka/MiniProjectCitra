import pytesseract
from PIL import Image, ImageFilter, ImageEnhance
import re
from datetime import datetime
from config import Config

# Konfigurasi path tesseract
pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_CMD


def preprocess_image(image_path):
    """Pre-processing gambar: grayscale, contrast, threshold."""
    img = Image.open(image_path)
    # Grayscale
    img = img.convert('L')
    # Tingkatkan kontras
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)
    # Sharpen
    img = img.filter(ImageFilter.SHARPEN)
    return img


def extract_text(image_path):
    """Ekstrak teks dari gambar KK menggunakan Tesseract."""
    img = preprocess_image(image_path)
    # OCR dengan bahasa Indonesia
    text = pytesseract.image_to_string(img, lang='ind')
    print("=== RAW OCR TEXT START ===")
    print(text)
    print("=== RAW OCR TEXT END ===")
    return text


def parse_kk_data(text):
    """
    Parse berdasarkan POLA DATA yang sering muncul di hasil OCR KK.
    Tidak andalkan keyword karena sering meleset.
    """
    lines = text.split('\n')
    lines = [l.strip() for l in lines if l.strip()]

    data = {
        'identitas': {
            'nomor_kk': '',
            'nama_kepala_keluarga': '',
            'alamat': '',
            'rt_rw': '',
            'desa_kelurahan': '',
            'kecamatan': '',
            'kabupaten_kota': '',
            'kode_pos': '',
            'provinsi': '',
        },
        'anggota': []
    }

    # 1. Nomor KK - cari 16 digit
    for line in lines:
        match = re.search(r'\b(\d{16})\b', line)
        if match:
            data['identitas']['nomor_kk'] = match.group(1)
            break

    # 2. Nama - cari baris dengan pola: HURUF KAPITAL + koma + ST/S.Pd/gelar (atau minimal ada koma)
    for line in lines:
        # Pattern: minimal 3 huruf, ada spasi, bisa ada koma dan gelar
        if re.search(r'^[A-Z]{2,}[\sA-Z,\.]+(?:ST|S\.Pd|M\.Si|,\s*ST)?$', line):
            # Pastikan bukan keyword
            if not any(x in line.upper() for x in ['ALAMAT', 'DESA', 'KELURAHAN', 'KARTU', 'LENGKAP']):
                # Pastikan minimal ada 2 kata atau ada koma
                if ' ' in line and len(line) > 8:
                    data['identitas']['nama_kepala_keluarga'] = line.strip()
                    break

    # 3. Alamat - cari pola: KATA, KATA (misal TEGALSARI, DAWUKAN)
    for line in lines:
        # Harus ada koma, huruf kapital, dan tidak terlalu panjang
        if ',' in line and re.match(r'^[A-Z\s,]+$', line.strip()):
            if len(line.split(',')) == 2 and 'YOGYAKARTA' not in line:
                # Pastikan kedua bagian tidak terlalu pendek
                parts = line.split(',')
                if len(parts[0].strip()) > 3 and len(parts[1].strip()) > 3:
                    data['identitas']['alamat'] = line.strip()
                    break

    # 4. RT/RW - cari angka 6-7 digit seperti 0087005 atau pattern digit/digit
    for line in lines:
        # Coba pattern digit/digit dulu
        match = re.search(r'(\d{3})\s*/\s*(\d{3})', line)
        if match:
            data['identitas']['rt_rw'] = f"{match.group(1)}/{match.group(2)}"
            break

    # Jika tidak ketemu, coba angka panjang
    if not data['identitas']['rt_rw']:
        for line in lines:
            # Cari angka 6-7 digit
            match = re.search(r'\b(\d{6,7})\b', line)
            if match:
                num = match.group(1)
                # Ambil 3 digit pertama dan 3 digit terakhir
                if len(num) >= 6:
                    data['identitas']['rt_rw'] = f"{num[:3]}/{num[-3:]}"
                    break

    # 5. Desa/Kelurahan - cari kata panjang huruf kapital (satu kata, > 8 huruf)
    for line in lines:
        clean = line.strip().upper().lstrip('I ').lstrip('L ').lstrip('| ')
        # Satu kata panjang, huruf saja
        if clean.isalpha() and len(clean) > 8:
            # Pastikan bukan keyword
            if clean not in ['KELURAHAN', 'KECAMATAN', 'KABUPATEN']:
                data['identitas']['desa_kelurahan'] = clean
                break

    # 6. Provinsi - cari yang mengandung YOGYAKARTA, JAWA, dll
    for line in lines:
        clean = line.strip().replace(':', '').replace('.', '').strip()
        if any(x in clean.upper() for x in ['YOGYAKARTA', 'JAWA BARAT', 'JAWA TENGAH', 'JAWA TIMUR', 'DAERAH ISTIMEWA']):
            data['identitas']['provinsi'] = clean
            break

    # 7. Kecamatan - cari kata pendek huruf kapital (4-10 huruf, satu kata)
    kecamatan_candidates = []
    for line in lines:
        clean = line.strip().upper()
        if clean.isalpha() and 4 <= len(clean) <= 10:
            if clean not in ['ALAMAT', 'NAMA', 'KARTU', 'KELUARGA', 'TEMPAT', 'LAHIR', 'AGAMA']:
                kecamatan_candidates.append(clean)

    # Ambil kandidat yang belum dipakai untuk desa
    for cand in kecamatan_candidates:
        if cand != data['identitas']['desa_kelurahan']:
            data['identitas']['kecamatan'] = cand
            break

    # 8. Kabupaten/Kota - cari kata pendek (4-8 huruf)
    for line in lines:
        clean = line.strip().upper()
        if clean.isalpha() and 4 <= len(clean) <= 8:
            if clean not in ['ALAMAT', 'PROVINSI', 'KECAMATAN', data['identitas']['desa_kelurahan'], data['identitas']['kecamatan']]:
                data['identitas']['kabupaten_kota'] = clean
                break

    # 9. Kode Pos - cari 5 digit
    for line in lines:
        match = re.search(r'\b(\d{5})\b', line)
        if match and match.group(1) != data['identitas']['nomor_kk'][:5]:
            data['identitas']['kode_pos'] = match.group(1)
            break

    # 10. Anggota - cari NIK lain (16 digit yang bukan nomor KK)
    niks = re.findall(r'\b(\d{16})\b', text)
    for nik in set(niks):
        if nik != data['identitas']['nomor_kk']:
            data['anggota'].append({
                'nama_lengkap': 'HASIL OCR - EDIT MANUAL',
                'nik': nik,
                'jenis_kelamin': '', 'tempat_lahir': '', 'tanggal_lahir': '',
                'agama': '', 'pendidikan': '', 'jenis_pekerjaan': '', 'status_hubungan': ''
            })

    return data
