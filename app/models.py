from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class IdentitasKK(db.Model):
    __tablename__ = 'tbl_identitasKK'
    nomor_kk = db.Column(db.String(20), primary_key=True)
    nama_kepala_keluarga = db.Column(db.String(100))
    alamat = db.Column(db.String(255))
    rt_rw = db.Column(db.String(20))
    desa_kelurahan = db.Column(db.String(100))
    kecamatan = db.Column(db.String(100))
    kabupaten_kota = db.Column(db.String(100))
    kode_pos = db.Column(db.String(10))
    provinsi = db.Column(db.String(100))

    # Relationship to members
    anggota = db.relationship('AnggotaKeluargaKK', backref='identitas', cascade='all, delete-orphan')

class AnggotaKeluargaKK(db.Model):
    __tablename__ = 'tbl_anggotaKeluargaKK'
    id = db.Column(db.Integer, primary_key=True)
    nomor_kk = db.Column(db.String(20), db.ForeignKey('tbl_identitasKK.nomor_kk'), nullable=False)
    nama_lengkap = db.Column(db.String(100))
    nik = db.Column(db.String(20), unique=True)
    jenis_kelamin = db.Column(db.String(20))
    tempat_lahir = db.Column(db.String(100))
    tanggal_lahir = db.Column(db.Date)
    agama = db.Column(db.String(50))
    pendidikan = db.Column(db.String(100))
    jenis_pekerjaan = db.Column(db.String(100))
    status_hubungan = db.Column(db.String(50))
