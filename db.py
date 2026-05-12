from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db
import os


def _ensure_sqlite_writable(path: str):
    directory = os.path.dirname(path)
    if not os.access(directory, os.W_OK):
        raise RuntimeError(f"Database directory is not writable: {directory}")

    if os.path.exists(path):
        os.chmod(path, os.stat(path).st_mode | 0o600)
        if not os.access(path, os.W_OK):
            raise RuntimeError(f"Database file is not writable: {path}")


def init_db(app: Flask):
    """Initialize the database, create tables if they do not exist"""
    os.makedirs(app.instance_path, exist_ok=True)
    db_path = os.path.join(app.instance_path, 'app.db')
    _ensure_sqlite_writable(db_path)

    app.config['SQLALCHEMY_DATABASE_URI'] = (
        'sqlite:///' + db_path
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        # Check if database file exists, create tables if not
        if not os.path.exists(db_path):
            db.create_all()
            _ensure_sqlite_writable(db_path)
            print("Database and tables created.")
        else:
            db.create_all()
            print("Database already exists.")
