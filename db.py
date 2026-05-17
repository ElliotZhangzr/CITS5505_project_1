from flask import Flask
from models import db
import os


def _ensure_sqlite_writable(path: str):
    directory = os.path.dirname(path)
    if not os.access(directory, os.W_OK):
        raise RuntimeError(f"Database directory is not writable: {directory}")

    if os.path.exists(path):
        # some environments create the file read-only; ensure user write bit is set
        os.chmod(path, os.stat(path).st_mode | 0o600)
        if not os.access(path, os.W_OK):
            raise RuntimeError(f"Database file is not writable: {path}")


def init_db(app: Flask):
    os.makedirs(app.instance_path, exist_ok=True)
    db_path = os.path.join(app.instance_path, 'app.db')
    _ensure_sqlite_writable(db_path)

    app.config['SQLALCHEMY_DATABASE_URI'] = (
        'sqlite:///' + db_path
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
