import os

class Config:
    # Ganti sesuai PostgreSQL kamu
    POSTGRES_USER     = 'postgres'
    POSTGRES_PASSWORD = 'your_password_here'   # <-- ganti ini
    POSTGRES_HOST     = 'localhost'
    POSTGRES_PORT     = '5432'
    POSTGRES_DB       = 'db_kartu_keluarga'

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
        f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'app', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # max 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    SECRET_KEY = 'kk-ocr-secret-key'

    # Path Tesseract (Sesuaikan jika instalasi berbeda)
    TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
