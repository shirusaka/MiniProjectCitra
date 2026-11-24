from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from app.models import db, IdentitasKK, AnggotaKeluargaKK
from app.ocr_engine import extract_text, parse_kk_data
import os
from werkzeug.utils import secure_filename
from datetime import datetime

main = Blueprint('main', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@main.route('/')
def index():
    """Halaman penelusuran tabel KK saja."""
    list_kk = IdentitasKK.query.all()
    return render_template('index.html', list_kk=list_kk)

@main.route('/upload', methods=['GET', 'POST'])
def upload():
    """Halaman input gambar KK."""
    if request.method == 'POST':
        if 'image' not in request.files:
            flash('Tidak ada file bagian')
            return redirect(request.url)

        file = request.files['image']
        if file.filename == '':
            flash('Tidak ada file dipilih')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # OCR Processing
            try:
                raw_text = extract_text(filepath)
                kk_data = parse_kk_data(raw_text)
                # Tampilkan halaman konfirmasi
                return render_template('konfirmasi.html', data=kk_data)
            except Exception as e:
                flash(f'Error OCR: {str(e)}')
                return redirect(request.url)

    return render_template('upload.html')

@main.route('/simpan', methods=['POST'])
def simpan():
    """Simpan data dari form konfirmasi ke database."""
    # Data Identitas KK
    nomor_kk = request.form.get('nomor_kk')

    # Cek duplicate
    exists = IdentitasKK.query.get(nomor_kk)
    if exists:
        flash('Nomor KK sudah ada di database!')
        return redirect(url_for('main.index'))

    new_kk = IdentitasKK(
        nomor_kk=nomor_kk,
        nama_kepala_keluarga=request.form.get('nama_kepala_keluarga'),
        alamat=request.form.get('alamat'),
        rt_rw=request.form.get('rt_rw'),
        desa_kelurahan=request.form.get('desa_kelurahan'),
        kecamatan=request.form.get('kecamatan'),
        kabupaten_kota=request.form.get('kabupaten_kota'),
        kode_pos=request.form.get('kode_pos'),
        provinsi=request.form.get('provinsi')
    )
    db.session.add(new_kk)

    # Data Anggota (multi-row)
    names = request.form.getlist('nama_lengkap[]')
    niks = request.form.getlist('nik[]')
    jk = request.form.getlist('jenis_kelamin[]')
    tl = request.form.getlist('tempat_lahir[]')
    tgl = request.form.getlist('tanggal_lahir[]')
    agm = request.form.getlist('agama[]')
    pend = request.form.getlist('pendidikan[]')
    pkj = request.form.getlist('jenis_pekerjaan[]')
    hub = request.form.getlist('status_hubungan[]')

    for i in range(len(names)):
        # Konversi string tanggal ke object date python
        tgl_obj = None
        if tgl[i]:
            try:
                tgl_obj = datetime.strptime(tgl[i], '%Y-%m-%d').date()
            except:
                pass

        new_anggota = AnggotaKeluargaKK(
            nomor_kk=nomor_kk,
            nama_lengkap=names[i],
            nik=niks[i],
            jenis_kelamin=jk[i],
            tempat_lahir=tl[i],
            tanggal_lahir=tgl_obj,
            agama=agm[i],
            pendidikan=pend[i],
            jenis_pekerjaan=pkj[i],
            status_hubungan=hub[i]
        )
        db.session.add(new_anggota)

    db.session.commit()
    flash('Data KK berhasil disimpan!')
    return redirect(url_for('main.index'))

@main.route('/detail/<nomor_kk>')
def detail(nomor_kk):
    """Lihat detail anggota keluarga pada sebuah KK."""
    kk = IdentitasKK.query.get_or_404(nomor_kk)
    return render_template('detail.html', kk=kk)

@main.route('/edit_kk/<nomor_kk>', methods=['GET', 'POST'])
def edit_kk(nomor_kk):
    """Update data identitas KK."""
    kk = IdentitasKK.query.get_or_404(nomor_kk)
    if request.method == 'POST':
        kk.nama_kepala_keluarga = request.form.get('nama_kepala_keluarga')
        kk.alamat = request.form.get('alamat')
        kk.rt_rw = request.form.get('rt_rw')
        kk.desa_kelurahan = request.form.get('desa_kelurahan')
        kk.kecamatan = request.form.get('kecamatan')
        kk.kabupaten_kota = request.form.get('kabupaten_kota')
        kk.kode_pos = request.form.get('kode_pos')
        kk.provinsi = request.form.get('provinsi')
        db.session.commit()
        flash('Data Identitas KK diperbarui!')
        return redirect(url_for('main.detail', nomor_kk=nomor_kk))
    return render_template('edit_kk.html', kk=kk)

@main.route('/delete_kk/<nomor_kk>')
def delete_kk(nomor_kk):
    """Delete data KK (otomatis delete anggota via cascade)."""
    kk = IdentitasKK.query.get_or_404(nomor_kk)
    db.session.delete(kk)
    db.session.commit()
    flash('Data KK berhasil dihapus!')
    return redirect(url_for('main.index'))

@main.route('/edit_anggota/<int:id>', methods=['GET', 'POST'])
def edit_anggota(id):
    """Update data anggota keluarga."""
    agt = AnggotaKeluargaKK.query.get_or_404(id)
    if request.method == 'POST':
        agt.nama_lengkap = request.form.get('nama_lengkap')
        agt.nik = request.form.get('nik')
        agt.jenis_kelamin = request.form.get('jenis_kelamin')
        agt.tempat_lahir = request.form.get('tempat_lahir')
        tgl = request.form.get('tanggal_lahir')
        if tgl:
            agt.tanggal_lahir = datetime.strptime(tgl, '%Y-%m-%d').date()
        agt.agama = request.form.get('agama')
        agt.pendidikan = request.form.get('pendidikan')
        agt.jenis_pekerjaan = request.form.get('jenis_pekerjaan')
        agt.status_hubungan = request.form.get('status_hubungan')
        db.session.commit()
        flash('Data Anggota diperbarui!')
        return redirect(url_for('main.detail', nomor_kk=agt.nomor_kk))
    return render_template('edit_anggota.html', agt=agt)

@main.route('/delete_anggota/<int:id>')
def delete_anggota(id):
    """Delete data anggota keluarga."""
    agt = AnggotaKeluargaKK.query.get_or_404(id)
    nomor_kk = agt.nomor_kk
    db.session.delete(agt)
    db.session.commit()
    flash('Anggota keluarga dihapus!')
    return redirect(url_for('main.detail', nomor_kk=nomor_kk))
