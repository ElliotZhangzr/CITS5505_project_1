from datetime import datetime, timedelta
from decimal import Decimal
import random

from sqlalchemy.exc import OperationalError

from models import db, StockPrice


UPDATE_INTERVAL_SECONDS = 2


def generate_next_price(last_price):
    change_percent = Decimal(str((random.random() - 0.5) * 0.04))
    next_price = Decimal(str(last_price)) * (Decimal("1") + change_percent)
    return next_price.quantize(Decimal("0.01"))


def generate_initial_prices(base_price, count=400):
    prices = [Decimal(base_price)]

    for _ in range(1, count):
        prices.append(generate_next_price(prices[-1]))

    return prices


def update_prices_if_due(stocks):
    latest_prices = {}
    now = datetime.utcnow()

    try:
        for stock in stocks:
            latest_price = get_latest_price(stock.id)

            if not latest_price:
                continue

            next_update_at = latest_price.recorded_at + timedelta(seconds=UPDATE_INTERVAL_SECONDS)

            if next_update_at > now:
                latest_prices[stock.symbol] = float(latest_price.price)
                continue

            new_price = generate_next_price(latest_price.price)
            db.session.add(StockPrice(stock_id=stock.id, price=new_price))
            latest_prices[stock.symbol] = float(new_price)

        db.session.commit()
    except OperationalError:
        db.session.rollback()
        latest_prices = get_current_prices(stocks)

    return latest_prices


def get_latest_price(stock_id):
    return (
        StockPrice.query
        .filter_by(stock_id=stock_id)
        .order_by(StockPrice.recorded_at.desc(), StockPrice.id.desc())
        .first()
    )


def get_current_prices(stocks):
    prices = {}

    for stock in stocks:
        latest_price = get_latest_price(stock.id)

        if latest_price:
            prices[stock.symbol] = float(latest_price.price)

    return prices
