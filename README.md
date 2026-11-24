# Mini Project: OCR Kartu Keluarga

Aplikasi web untuk membaca data Kartu Keluarga (KK) menggunakan OCR (Optical Character Recognition) berbasis Tesseract.

## Fitur
- Upload gambar KK
- Ekstraksi data otomatis menggunakan Tesseract OCR
- Halaman konfirmasi dengan form editable untuk koreksi data
- CRUD (Create, Read, Update, Delete) untuk data KK dan anggota keluarga
- Database PostgreSQL

## Stack Teknologi
- **Backend**: Python Flask
- **OCR**: Tesseract OCR dengan pytesseract
- **Database**: PostgreSQL
- **Frontend**: HTML, CSS (Bootstrap), JavaScript

## Instalasi

### Prerequisites
1. Python 3.8+
2. PostgreSQL
3. Tesseract OCR

### Install Tesseract OCR
**Windows:**
Download dari [https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)

Install dan pastikan path: `C:\Program Files\Tesseract-OCR\tesseract.exe`

Download bahasa Indonesia (`ind.traineddata`) dari [https://github.com/tesseract-ocr/tessdata](https://github.com/tesseract-ocr/tessdata) dan taruh di folder `tessdata`.

### Setup Project

1. Clone repository:
```bash
git clone <repository-url>
cd MiniProjectCitra
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Setup database PostgreSQL:
```sql
CREATE DATABASE db_kartu_keluarga;
```

4. Edit `config.py`:
```python
POSTGRES_USER = 'postgres'
POSTGRES_PASSWORD = 'your_password'
TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

5. Jalankan aplikasi:
```bash
python run.py
```

Buka browser: `http://localhost:5000`

## Struktur Database

### tbl_identitasKK
- nomor_kk (PK)
- nama_kepala_keluarga
- alamat
- rt_rw
- desa_kelurahan
- kecamatan
- kabupaten_kota
- kode_pos
- provinsi

### tbl_anggotaKeluargaKK
- id (PK)
- nomor_kk (FK)
- nama_lengkap
- nik
- jenis_kelamin
- tempat_lahir
- tanggal_lahir
- agama
- pendidikan
- jenis_pekerjaan
- status_hubungan

## Workflow
1. User upload foto KK
2. Pre-processing gambar (grayscale, contrast, sharpen)
3. OCR ekstrak teks
4. Parsing data ke format JSON
5. Halaman konfirmasi untuk koreksi manual
6. Simpan ke database
7. Halaman penelusuran dan detail KK

## Catatan
- Akurasi OCR tergantung kualitas gambar
- Gunakan foto dengan pencahayaan baik dan tidak blur
- Halaman konfirmasi memungkinkan koreksi manual jika OCR tidak akurat
