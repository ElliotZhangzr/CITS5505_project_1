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

    holdings = db.relationship("StockHolding", back_populates="user", cascade="all, delete-orphan")
    transactions = db.relationship("StockTransaction", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f'<User {self.username}>'


class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    prices = db.relationship("StockPrice", back_populates="stock", cascade="all, delete-orphan")
    holdings = db.relationship("StockHolding", back_populates="stock", cascade="all, delete-orphan")
    transactions = db.relationship("StockTransaction", back_populates="stock", cascade="all, delete-orphan")

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


class StockHolding(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    stock_id = db.Column(db.Integer, db.ForeignKey("stock.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    average_cost = db.Column(db.Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    total_cost = db.Column(db.Numeric(14, 2), nullable=False, default=Decimal("0.00"))
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship("User", back_populates="holdings")
    stock = db.relationship("Stock", back_populates="holdings")

    __table_args__ = (
        db.UniqueConstraint("user_id", "stock_id", name="uq_user_stock_holding"),
    )

    def __repr__(self):
        return f'<StockHolding {self.user_id} {self.stock_id} {self.quantity}>'


class StockTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    stock_id = db.Column(db.Integer, db.ForeignKey("stock.id"), nullable=False)
    side = db.Column(db.String(4), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(12, 2), nullable=False)
    gross_amount = db.Column(db.Numeric(14, 2), nullable=False)
    realized_profit = db.Column(db.Numeric(14, 2), nullable=False, default=Decimal("0.00"))
    average_cost_before = db.Column(db.Numeric(12, 2), nullable=True)
    cash_balance_after = db.Column(db.Numeric(14, 2), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship("User", back_populates="transactions")
    stock = db.relationship("Stock", back_populates="transactions")

    def __repr__(self):
        return f'<StockTransaction {self.user_id} {self.side} {self.stock_id} {self.quantity}>'
