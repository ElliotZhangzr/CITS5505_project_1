from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db, User
import os

def init_db(app: Flask):
    """Initialize the database, create tables if they do not exist"""
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        # Check if database file exists, create tables if not
        if not os.path.exists('app.db'):
            db.create_all()
            print("Database and tables created.")
        else:
            print("Database already exists.")