from flask import Flask
from config import Config
from app.models import db
import os


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Pastikan folder upload ada
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    from app.routes import main
    app.register_blueprint(main)

    return app
