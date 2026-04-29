from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from decimal import Decimal

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    cash = db.Column(db.Numeric(12, 2), nullable=False, default=Decimal("10000.00"))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'


class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    prices = db.relationship("StockPrice", back_populates="stock", cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Stock {self.symbol}>'


class StockPrice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey("stock.id"), nullable=False)
    price = db.Column(db.Numeric(12, 2), nullable=False)
    recorded_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    stock = db.relationship("Stock", back_populates="prices")

    def __repr__(self):
        return f'<StockPrice {self.stock_id} {self.price}>'
