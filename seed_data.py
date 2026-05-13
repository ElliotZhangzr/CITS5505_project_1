from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

from flask import Flask
from werkzeug.security import generate_password_hash

from models import db, Stock, StockHolding, StockPrice, StockTransaction, User


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = BASE_DIR / "instance" / "app.db"
BASE_TIME = datetime(2026, 5, 4, 16, 0, 0)


USERS = [
    {
        "username": "root",
        "email": "root@example.com",
        "password": "root",
        "is_admin": True,
        "cash": Decimal("100000.00"),
        "bio": "Seeded root admin account.",
        "avatar_url": "",
        "hide_holdings": False,
        "created_at": BASE_TIME,
    },
    {
        "username": "admin",
        "email": "admin@example.com",
        "password": "Admin123",
        "is_admin": True,
        "cash": Decimal("100000.00"),
        "bio": "Seeded admin account.",
        "avatar_url": "",
        "hide_holdings": False,
        "created_at": BASE_TIME,
    },
    {
        "username": "trader",
        "email": "trader@example.com",
        "password": "Trader123",
        "is_admin": False,
        "cash": Decimal("9049.55"),
        "bio": "Seeded trader account.",
        "avatar_url": "",
        "hide_holdings": False,
        "created_at": BASE_TIME + timedelta(minutes=10),
    },
]


STOCKS = [
    {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "base_price": Decimal("150.00"),
        "volatility": Decimal("0.006000"),
        "drift": Decimal("0.000200"),
        "momentum_factor": Decimal("0.150000"),
        "mean_reversion_factor": Decimal("0.030000"),
        "liquidity": Decimal("1000000.00"),
        "trade_impact_factor": Decimal("0.250000"),
        "min_price": Decimal("1.00"),
        "created_at": BASE_TIME,
        "prices": ["180.00", "176.55", "176.41", "178.41", "180.57", "176.97", "178.99", "177.56", "175.95", "177.66"],
    },
    {
        "symbol": "TSLA",
        "name": "Tesla Inc.",
        "base_price": Decimal("200.00"),
        "volatility": Decimal("0.025000"),
        "drift": Decimal("0.000100"),
        "momentum_factor": Decimal("0.550000"),
        "mean_reversion_factor": Decimal("0.030000"),
        "liquidity": Decimal("300000.00"),
        "trade_impact_factor": Decimal("0.800000"),
        "min_price": Decimal("1.00"),
        "created_at": BASE_TIME + timedelta(minutes=1),
        "prices": ["210.00", "207.95", "208.14", "204.20", "204.56", "206.58", "207.33", "210.37", "209.51", "212.14"],
    },
    {
        "symbol": "NVDA",
        "name": "NVIDIA Corporation",
        "base_price": Decimal("900.00"),
        "volatility": Decimal("0.015000"),
        "drift": Decimal("0.000600"),
        "momentum_factor": Decimal("0.400000"),
        "mean_reversion_factor": Decimal("0.030000"),
        "liquidity": Decimal("600000.00"),
        "trade_impact_factor": Decimal("0.500000"),
        "min_price": Decimal("1.00"),
        "created_at": BASE_TIME + timedelta(minutes=2),
        "prices": ["800.00", "807.47", "816.19", "823.06", "810.81", "821.56", "825.27", "840.96", "856.63", "872.87"],
    },
]


HOLDINGS = [
    {
        "username": "trader",
        "symbol": "AAPL",
        "quantity": 7,
        "average_cost": Decimal("135.78"),
        "total_cost": Decimal("950.45"),
        "updated_at": BASE_TIME + timedelta(hours=1),
    },
]


TRANSACTIONS = [
    ("trader", "AAPL", "BUY", 1, "136.59", "136.59", "0.00", None, "9863.41", 1),
    ("trader", "AAPL", "BUY", 1, "137.21", "137.21", "0.00", "136.59", "9726.20", 2),
    ("trader", "AAPL", "BUY", 1, "137.21", "137.21", "0.00", "136.90", "9588.99", 3),
    ("trader", "AAPL", "BUY", 1, "134.86", "134.86", "0.00", "137.00", "9454.13", 4),
    ("trader", "AAPL", "BUY", 1, "134.86", "134.86", "0.00", "136.47", "9319.27", 5),
    ("trader", "AAPL", "BUY", 1, "134.86", "134.86", "0.00", "136.15", "9184.41", 6),
    ("trader", "AAPL", "BUY", 1, "134.86", "134.86", "0.00", "135.93", "9049.55", 7),
]


def create_seed_app(db_path: Path) -> Flask:
    app = Flask(__name__, instance_path=str(db_path.parent))
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + str(db_path)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    return app


def upsert_user(data: dict) -> User:
    user = User.query.filter_by(username=data["username"]).first()
    if user is None:
        user = User(username=data["username"])
        db.session.add(user)

    user.email = data["email"]
    user.password_hash = generate_password_hash(data["password"])
    user.is_admin = data["is_admin"]
    user.cash = data["cash"]
    user.bio = data["bio"]
    user.avatar_url = data["avatar_url"]
    user.hide_holdings = data["hide_holdings"]
    user.created_at = data["created_at"]
    return user


def upsert_stock(data: dict) -> Stock:
    stock = Stock.query.filter_by(symbol=data["symbol"]).first()
    if stock is None:
        stock = Stock(symbol=data["symbol"])
        db.session.add(stock)

    stock.name = data["name"]
    stock.base_price = data["base_price"]
    stock.volatility = data["volatility"]
    stock.drift = data["drift"]
    stock.momentum_factor = data["momentum_factor"]
    stock.mean_reversion_factor = data["mean_reversion_factor"]
    stock.liquidity = data["liquidity"]
    stock.trade_impact_factor = data["trade_impact_factor"]
    stock.min_price = data["min_price"]
    stock.created_at = data["created_at"]
    return stock


def seed_prices(stocks_by_symbol: dict[str, Stock]) -> None:
    for stock_data in STOCKS:
        stock = stocks_by_symbol[stock_data["symbol"]]
        for index, price in enumerate(stock_data["prices"]):
            recorded_at = stock_data["created_at"] + timedelta(seconds=index)
            existing = StockPrice.query.filter_by(stock_id=stock.id, recorded_at=recorded_at).first()
            if existing is None:
                existing = StockPrice(stock_id=stock.id, recorded_at=recorded_at)
                db.session.add(existing)
            existing.price = Decimal(price)


def seed_holdings(users_by_name: dict[str, User], stocks_by_symbol: dict[str, Stock]) -> None:
    for data in HOLDINGS:
        user = users_by_name[data["username"]]
        stock = stocks_by_symbol[data["symbol"]]
        holding = StockHolding.query.filter_by(user_id=user.id, stock_id=stock.id).first()
        if holding is None:
            holding = StockHolding(user_id=user.id, stock_id=stock.id)
            db.session.add(holding)

        holding.quantity = data["quantity"]
        holding.average_cost = data["average_cost"]
        holding.total_cost = data["total_cost"]
        holding.updated_at = data["updated_at"]


def seed_transactions(users_by_name: dict[str, User], stocks_by_symbol: dict[str, Stock]) -> None:
    for username, symbol, side, quantity, price, gross, profit, avg_before, cash_after, offset in TRANSACTIONS:
        user = users_by_name[username]
        stock = stocks_by_symbol[symbol]
        created_at = BASE_TIME + timedelta(hours=1, seconds=offset)
        transaction = StockTransaction.query.filter_by(
            user_id=user.id,
            stock_id=stock.id,
            side=side,
            quantity=quantity,
            created_at=created_at,
        ).first()

        if transaction is None:
            transaction = StockTransaction(
                user_id=user.id,
                stock_id=stock.id,
                side=side,
                quantity=quantity,
                created_at=created_at,
            )
            db.session.add(transaction)

        transaction.price = Decimal(price)
        transaction.gross_amount = Decimal(gross)
        transaction.realized_profit = Decimal(profit)
        transaction.average_cost_before = Decimal(avg_before) if avg_before is not None else None
        transaction.cash_balance_after = Decimal(cash_after)


def seed_database(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    app = create_seed_app(db_path)

    with app.app_context():
        db.create_all()
        users_by_name = {data["username"]: upsert_user(data) for data in USERS}
        stocks_by_symbol = {data["symbol"]: upsert_stock(data) for data in STOCKS}
        db.session.flush()

        seed_prices(stocks_by_symbol)
        seed_holdings(users_by_name, stocks_by_symbol)
        seed_transactions(users_by_name, stocks_by_symbol)
        db.session.commit()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Insert model-based seed data into the SQLite database.")
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB_PATH,
        help=f"SQLite database path. Default: {DEFAULT_DB_PATH}",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    seed_database(args.db)
    print(f"Seed data inserted into {args.db}")
