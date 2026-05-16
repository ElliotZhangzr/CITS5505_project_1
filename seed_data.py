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
        "avatar_url": "/static/uploads/avatars/user_1.png",
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
    {"username": "user01", "email": "user01@example.com", "password": "User01pwd", "is_admin": False, "cash": Decimal("99100.00"), "bio": "", "avatar_url": "", "hide_holdings": False, "created_at": BASE_TIME + timedelta(minutes=20)},
    {"username": "user02", "email": "user02@example.com", "password": "User02pwd", "is_admin": False, "cash": Decimal("99370.00"), "bio": "", "avatar_url": "", "hide_holdings": False, "created_at": BASE_TIME + timedelta(minutes=25)},
    {"username": "user03", "email": "user03@example.com", "password": "User03pwd", "is_admin": False, "cash": Decimal("98300.00"), "bio": "", "avatar_url": "", "hide_holdings": False, "created_at": BASE_TIME + timedelta(minutes=30)},
    {"username": "user04", "email": "user04@example.com", "password": "User04pwd", "is_admin": False, "cash": Decimal("98200.00"), "bio": "", "avatar_url": "", "hide_holdings": False, "created_at": BASE_TIME + timedelta(minutes=35)},
    {"username": "user05", "email": "user05@example.com", "password": "User05pwd", "is_admin": False, "cash": Decimal("98950.00"), "bio": "", "avatar_url": "", "hide_holdings": False, "created_at": BASE_TIME + timedelta(minutes=40)},
    {"username": "user06", "email": "user06@example.com", "password": "User06pwd", "is_admin": False, "cash": Decimal("99150.00"), "bio": "", "avatar_url": "", "hide_holdings": False, "created_at": BASE_TIME + timedelta(minutes=45)},
    {"username": "user07", "email": "user07@example.com", "password": "User07pwd", "is_admin": False, "cash": Decimal("98140.00"), "bio": "", "avatar_url": "", "hide_holdings": False, "created_at": BASE_TIME + timedelta(minutes=50)},
    {"username": "user08", "email": "user08@example.com", "password": "User08pwd", "is_admin": False, "cash": Decimal("98310.00"), "bio": "", "avatar_url": "", "hide_holdings": False, "created_at": BASE_TIME + timedelta(minutes=55)},
    {"username": "user09", "email": "user09@example.com", "password": "User09pwd", "is_admin": False, "cash": Decimal("96910.00"), "bio": "", "avatar_url": "", "hide_holdings": False, "created_at": BASE_TIME + timedelta(minutes=60)},
    {"username": "user10", "email": "user10@example.com", "password": "User10pwd", "is_admin": False, "cash": Decimal("98920.00"), "bio": "", "avatar_url": "", "hide_holdings": False, "created_at": BASE_TIME + timedelta(minutes=65)},
    {"username": "user11", "email": "user11@example.com", "password": "User11pwd", "is_admin": False, "cash": Decimal("99160.00"), "bio": "", "avatar_url": "", "hide_holdings": False, "created_at": BASE_TIME + timedelta(minutes=70)},
    {"username": "user12", "email": "user12@example.com", "password": "User12pwd", "is_admin": False, "cash": Decimal("97450.00"), "bio": "", "avatar_url": "", "hide_holdings": False, "created_at": BASE_TIME + timedelta(minutes=75)},
    {"username": "user13", "email": "user13@example.com", "password": "User13pwd", "is_admin": False, "cash": Decimal("97300.00"), "bio": "", "avatar_url": "", "hide_holdings": False, "created_at": BASE_TIME + timedelta(minutes=80)},
    {"username": "user14", "email": "user14@example.com", "password": "User14pwd", "is_admin": False, "cash": Decimal("98530.00"), "bio": "", "avatar_url": "", "hide_holdings": False, "created_at": BASE_TIME + timedelta(minutes=85)},
    {"username": "user15", "email": "user15@example.com", "password": "User15pwd", "is_admin": False, "cash": Decimal("98250.00"), "bio": "", "avatar_url": "", "hide_holdings": False, "created_at": BASE_TIME + timedelta(minutes=90)},
    {"username": "user16", "email": "user16@example.com", "password": "User16pwd", "is_admin": False, "cash": Decimal("99280.00"), "bio": "", "avatar_url": "", "hide_holdings": False, "created_at": BASE_TIME + timedelta(minutes=95)},
    {"username": "user17", "email": "user17@example.com", "password": "User17pwd", "is_admin": False, "cash": Decimal("98740.00"), "bio": "", "avatar_url": "", "hide_holdings": False, "created_at": BASE_TIME + timedelta(minutes=100)},
    {"username": "user18", "email": "user18@example.com", "password": "User18pwd", "is_admin": False, "cash": Decimal("97670.00"), "bio": "", "avatar_url": "", "hide_holdings": False, "created_at": BASE_TIME + timedelta(minutes=105)},
    {"username": "user19", "email": "user19@example.com", "password": "User19pwd", "is_admin": False, "cash": Decimal("96400.00"), "bio": "", "avatar_url": "", "hide_holdings": False, "created_at": BASE_TIME + timedelta(minutes=110)},
    {"username": "user20", "email": "user20@example.com", "password": "User20pwd", "is_admin": False, "cash": Decimal("98760.00"), "bio": "", "avatar_url": "", "hide_holdings": False, "created_at": BASE_TIME + timedelta(minutes=115)},
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
    {"username": "user01", "symbol": "AAPL", "quantity": 5,  "average_cost": Decimal("180.00"), "total_cost": Decimal("900.00"),  "updated_at": BASE_TIME + timedelta(hours=2)},
    {"username": "user02", "symbol": "TSLA", "quantity": 3,  "average_cost": Decimal("210.00"), "total_cost": Decimal("630.00"),  "updated_at": BASE_TIME + timedelta(hours=2)},
    {"username": "user03", "symbol": "NVDA", "quantity": 2,  "average_cost": Decimal("850.00"), "total_cost": Decimal("1700.00"), "updated_at": BASE_TIME + timedelta(hours=2)},
    {"username": "user04", "symbol": "AAPL", "quantity": 10, "average_cost": Decimal("180.00"), "total_cost": Decimal("1800.00"), "updated_at": BASE_TIME + timedelta(hours=2)},
    {"username": "user05", "symbol": "TSLA", "quantity": 5,  "average_cost": Decimal("210.00"), "total_cost": Decimal("1050.00"), "updated_at": BASE_TIME + timedelta(hours=2)},
    {"username": "user06", "symbol": "NVDA", "quantity": 1,  "average_cost": Decimal("850.00"), "total_cost": Decimal("850.00"),  "updated_at": BASE_TIME + timedelta(hours=2)},
    {"username": "user07", "symbol": "AAPL", "quantity": 8,  "average_cost": Decimal("180.00"), "total_cost": Decimal("1440.00"), "updated_at": BASE_TIME + timedelta(hours=2)},
    {"username": "user07", "symbol": "TSLA", "quantity": 2,  "average_cost": Decimal("210.00"), "total_cost": Decimal("420.00"),  "updated_at": BASE_TIME + timedelta(hours=2)},
    {"username": "user08", "symbol": "TSLA", "quantity": 4,  "average_cost": Decimal("210.00"), "total_cost": Decimal("840.00"),  "updated_at": BASE_TIME + timedelta(hours=2)},
    {"username": "user08", "symbol": "NVDA", "quantity": 1,  "average_cost": Decimal("850.00"), "total_cost": Decimal("850.00"),  "updated_at": BASE_TIME + timedelta(hours=2)},
    {"username": "user09", "symbol": "AAPL", "quantity": 3,  "average_cost": Decimal("180.00"), "total_cost": Decimal("540.00"),  "updated_at": BASE_TIME + timedelta(hours=2)},
    {"username": "user09", "symbol": "NVDA", "quantity": 3,  "average_cost": Decimal("850.00"), "total_cost": Decimal("2550.00"), "updated_at": BASE_TIME + timedelta(hours=2)},
    {"username": "user10", "symbol": "AAPL", "quantity": 6,  "average_cost": Decimal("180.00"), "total_cost": Decimal("1080.00"), "updated_at": BASE_TIME + timedelta(hours=2)},
    {"username": "user11", "symbol": "TSLA", "quantity": 4,  "average_cost": Decimal("210.00"), "total_cost": Decimal("840.00"),  "updated_at": BASE_TIME + timedelta(hours=2)},
    {"username": "user12", "symbol": "NVDA", "quantity": 3,  "average_cost": Decimal("850.00"), "total_cost": Decimal("2550.00"), "updated_at": BASE_TIME + timedelta(hours=2)},
    {"username": "user13", "symbol": "AAPL", "quantity": 15, "average_cost": Decimal("180.00"), "total_cost": Decimal("2700.00"), "updated_at": BASE_TIME + timedelta(hours=2)},
    {"username": "user14", "symbol": "TSLA", "quantity": 7,  "average_cost": Decimal("210.00"), "total_cost": Decimal("1470.00"), "updated_at": BASE_TIME + timedelta(hours=2)},
    {"username": "user15", "symbol": "NVDA", "quantity": 1,  "average_cost": Decimal("850.00"), "total_cost": Decimal("850.00"),  "updated_at": BASE_TIME + timedelta(hours=2)},
    {"username": "user15", "symbol": "AAPL", "quantity": 5,  "average_cost": Decimal("180.00"), "total_cost": Decimal("900.00"),  "updated_at": BASE_TIME + timedelta(hours=2)},
    {"username": "user16", "symbol": "AAPL", "quantity": 4,  "average_cost": Decimal("180.00"), "total_cost": Decimal("720.00"),  "updated_at": BASE_TIME + timedelta(hours=2)},
    {"username": "user17", "symbol": "TSLA", "quantity": 6,  "average_cost": Decimal("210.00"), "total_cost": Decimal("1260.00"), "updated_at": BASE_TIME + timedelta(hours=2)},
    {"username": "user18", "symbol": "NVDA", "quantity": 2,  "average_cost": Decimal("850.00"), "total_cost": Decimal("1700.00"), "updated_at": BASE_TIME + timedelta(hours=2)},
    {"username": "user18", "symbol": "TSLA", "quantity": 3,  "average_cost": Decimal("210.00"), "total_cost": Decimal("630.00"),  "updated_at": BASE_TIME + timedelta(hours=2)},
    {"username": "user19", "symbol": "AAPL", "quantity": 20, "average_cost": Decimal("180.00"), "total_cost": Decimal("3600.00"), "updated_at": BASE_TIME + timedelta(hours=2)},
    {"username": "user20", "symbol": "NVDA", "quantity": 1,  "average_cost": Decimal("850.00"), "total_cost": Decimal("850.00"),  "updated_at": BASE_TIME + timedelta(hours=2)},
    {"username": "user20", "symbol": "TSLA", "quantity": 1,  "average_cost": Decimal("210.00"), "total_cost": Decimal("210.00"),  "updated_at": BASE_TIME + timedelta(hours=2)},
    {"username": "user20", "symbol": "AAPL", "quantity": 1,  "average_cost": Decimal("180.00"), "total_cost": Decimal("180.00"),  "updated_at": BASE_TIME + timedelta(hours=2)},
]


TRANSACTIONS = [
    ("trader", "AAPL", "BUY", 1, "136.59", "136.59", "0.00", None,     "9863.41",  1),
    ("trader", "AAPL", "BUY", 1, "137.21", "137.21", "0.00", "136.59", "9726.20",  2),
    ("trader", "AAPL", "BUY", 1, "137.21", "137.21", "0.00", "136.90", "9588.99",  3),
    ("trader", "AAPL", "BUY", 1, "134.86", "134.86", "0.00", "137.00", "9454.13",  4),
    ("trader", "AAPL", "BUY", 1, "134.86", "134.86", "0.00", "136.47", "9319.27",  5),
    ("trader", "AAPL", "BUY", 1, "134.86", "134.86", "0.00", "136.15", "9184.41",  6),
    ("trader", "AAPL", "BUY", 1, "134.86", "134.86", "0.00", "135.93", "9049.55",  7),
    # user01–user06: single-stock purchases
    ("user01", "AAPL", "BUY",  5, "180.00",  "900.00", "0.00", None, "99100.00", 100),
    ("user02", "TSLA", "BUY",  3, "210.00",  "630.00", "0.00", None, "99370.00", 101),
    ("user03", "NVDA", "BUY",  2, "850.00", "1700.00", "0.00", None, "98300.00", 102),
    ("user04", "AAPL", "BUY", 10, "180.00", "1800.00", "0.00", None, "98200.00", 103),
    ("user05", "TSLA", "BUY",  5, "210.00", "1050.00", "0.00", None, "98950.00", 104),
    ("user06", "NVDA", "BUY",  1, "850.00",  "850.00", "0.00", None, "99150.00", 105),
    # user07: AAPL then TSLA
    ("user07", "AAPL", "BUY",  8, "180.00", "1440.00", "0.00", None, "98560.00", 106),
    ("user07", "TSLA", "BUY",  2, "210.00",  "420.00", "0.00", None, "98140.00", 107),
    # user08: TSLA then NVDA
    ("user08", "TSLA", "BUY",  4, "210.00",  "840.00", "0.00", None, "99160.00", 108),
    ("user08", "NVDA", "BUY",  1, "850.00",  "850.00", "0.00", None, "98310.00", 109),
    # user09: AAPL then NVDA
    ("user09", "AAPL", "BUY",  3, "180.00",  "540.00", "0.00", None, "99460.00", 110),
    ("user09", "NVDA", "BUY",  3, "850.00", "2550.00", "0.00", None, "96910.00", 111),
    # user10–user14: single-stock purchases
    ("user10", "AAPL", "BUY",  6, "180.00", "1080.00", "0.00", None, "98920.00", 112),
    ("user11", "TSLA", "BUY",  4, "210.00",  "840.00", "0.00", None, "99160.00", 113),
    ("user12", "NVDA", "BUY",  3, "850.00", "2550.00", "0.00", None, "97450.00", 114),
    ("user13", "AAPL", "BUY", 15, "180.00", "2700.00", "0.00", None, "97300.00", 115),
    ("user14", "TSLA", "BUY",  7, "210.00", "1470.00", "0.00", None, "98530.00", 116),
    # user15: NVDA then AAPL
    ("user15", "NVDA", "BUY",  1, "850.00",  "850.00", "0.00", None, "99150.00", 117),
    ("user15", "AAPL", "BUY",  5, "180.00",  "900.00", "0.00", None, "98250.00", 118),
    # user16–user17: single-stock purchases
    ("user16", "AAPL", "BUY",  4, "180.00",  "720.00", "0.00", None, "99280.00", 119),
    ("user17", "TSLA", "BUY",  6, "210.00", "1260.00", "0.00", None, "98740.00", 120),
    # user18: NVDA then TSLA
    ("user18", "NVDA", "BUY",  2, "850.00", "1700.00", "0.00", None, "98300.00", 121),
    ("user18", "TSLA", "BUY",  3, "210.00",  "630.00", "0.00", None, "97670.00", 122),
    # user19: single large AAPL purchase
    ("user19", "AAPL", "BUY", 20, "180.00", "3600.00", "0.00", None, "96400.00", 123),
    # user20: NVDA, TSLA, then AAPL
    ("user20", "NVDA", "BUY",  1, "850.00",  "850.00", "0.00", None, "99150.00", 124),
    ("user20", "TSLA", "BUY",  1, "210.00",  "210.00", "0.00", None, "98940.00", 125),
    ("user20", "AAPL", "BUY",  1, "180.00",  "180.00", "0.00", None, "98760.00", 126),
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
    user.password_hash = generate_password_hash(data["password"], method="pbkdf2:sha256")
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