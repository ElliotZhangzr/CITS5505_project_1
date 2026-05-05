from datetime import datetime, timedelta
from decimal import Decimal
import random

from sqlalchemy.exc import OperationalError

from models import db, Stock, StockPrice


UPDATE_INTERVAL_SECONDS = 2
PRESSURE_DECAY = Decimal("0.78")
PRESSURE_RELEASE_RATE = Decimal("0.45")
MAX_PRICE_RETURN = Decimal("0.15")
MAX_TRADE_IMPACT = Decimal("0.10")
MIN_PRICE_IMPACT_DAMPENER = Decimal("0.25")
MAX_PRESSURE_DIRECTION_BIAS = Decimal("0.48")
STRONG_PRESSURE_THRESHOLD = Decimal("0.025")
PRESSURE_TREND_WEIGHT = Decimal("1.20")
MAX_PRESSURE_SIZE_BOOST = Decimal("2.50")

STOCK_CONFIGS = {}
SIMULATION_STATE = {}


def money(value):
    return Decimal(value).quantize(Decimal("0.01"))


def decimal_value(value):
    return Decimal(str(value))


def positive_price(value, fallback):
    price = decimal_value(value)

    if price > 0:
        return price

    fallback_price = decimal_value(fallback)
    return fallback_price if fallback_price > 0 else Decimal("1.00")


def load_stock_configs():
    global STOCK_CONFIGS

    stocks = Stock.query.order_by(Stock.symbol).all()
    STOCK_CONFIGS = {
        stock.id: {
            "id": stock.id,
            "symbol": stock.symbol,
            "base_price": decimal_value(stock.base_price),
            "volatility": decimal_value(stock.volatility),
            "drift": decimal_value(stock.drift),
            "mean_reversion_factor": decimal_value(stock.mean_reversion_factor),
            "liquidity": decimal_value(stock.liquidity),
            "trade_impact_factor": decimal_value(stock.trade_impact_factor),
            "min_price": decimal_value(stock.min_price),
        }
        for stock in stocks
    }

    for stock_id in STOCK_CONFIGS:
        get_simulation_state(stock_id)


def get_simulation_state(stock_id):
    if stock_id not in SIMULATION_STATE:
        SIMULATION_STATE[stock_id] = {
            "buy_pressure": Decimal("0"),
            "sell_pressure": Decimal("0"),
            "pending_buy_pressure": Decimal("0"),
            "pending_sell_pressure": Decimal("0"),
        }

    SIMULATION_STATE[stock_id].setdefault("pending_buy_pressure", Decimal("0"))
    SIMULATION_STATE[stock_id].setdefault("pending_sell_pressure", Decimal("0"))
    return SIMULATION_STATE[stock_id]


def generate_next_price(last_price, config, state):
    current_price = positive_price(last_price, config["base_price"])
    release_pending_pressure(state)
    random_noise = decimal_value(random.gauss(0, float(config["volatility"])))
    distance_from_base = (config["base_price"] - current_price) / current_price
    mean_reversion_effect = distance_from_base * config["mean_reversion_factor"]
    base_return = (
        config["drift"]
        + random_noise
        + mean_reversion_effect
    )
    pressure_trend = generate_pressure_trend(config, state)
    total_return = base_return + pressure_trend
    total_return = max(-MAX_PRICE_RETURN, min(MAX_PRICE_RETURN, total_return))

    next_price = current_price * (Decimal("1") + total_return)
    next_price = max(config["min_price"], next_price)

    state["buy_pressure"] *= PRESSURE_DECAY
    state["sell_pressure"] *= PRESSURE_DECAY

    return money(next_price)


def generate_pressure_trend(config, state):
    pressure_signal = state["buy_pressure"] - state["sell_pressure"]

    if pressure_signal == 0:
        return Decimal("0")

    pressure_strength = abs(pressure_signal)
    direction_bias = min(MAX_PRESSURE_DIRECTION_BIAS, pressure_strength * Decimal("10"))
    up_probability = Decimal("0.50")

    if pressure_signal > 0:
        up_probability += direction_bias
    else:
        up_probability -= direction_bias

    if pressure_strength >= STRONG_PRESSURE_THRESHOLD:
        direction = Decimal("1") if pressure_signal > 0 else Decimal("-1")
    else:
        direction = Decimal("1") if Decimal(str(random.random())) < up_probability else Decimal("-1")

    size_boost = Decimal("1") + min(MAX_PRESSURE_SIZE_BOOST, pressure_strength * Decimal("14"))
    trend_size = decimal_value(abs(random.gauss(0, float(config["volatility"] * PRESSURE_TREND_WEIGHT * size_boost))))

    return direction * trend_size


def release_pending_pressure(state):
    buy_release = state["pending_buy_pressure"] * PRESSURE_RELEASE_RATE
    sell_release = state["pending_sell_pressure"] * PRESSURE_RELEASE_RATE

    state["buy_pressure"] += buy_release
    state["sell_pressure"] += sell_release
    state["pending_buy_pressure"] -= buy_release
    state["pending_sell_pressure"] -= sell_release


def generate_initial_prices(base_price, count=400):
    config = {
        "base_price": decimal_value(base_price),
        "volatility": Decimal("0.010000"),
        "drift": Decimal("0.000000"),
        "mean_reversion_factor": Decimal("0.030000"),
        "min_price": Decimal("1.00"),
    }
    state = {
        "buy_pressure": Decimal("0"),
        "sell_pressure": Decimal("0"),
        "pending_buy_pressure": Decimal("0"),
        "pending_sell_pressure": Decimal("0"),
    }
    prices = [money(base_price)]

    for _ in range(1, count):
        prices.append(generate_next_price(prices[-1], config, state))

    return prices


def apply_trade_impact(stock_id, side, gross_amount):
    if not STOCK_CONFIGS:
        load_stock_configs()

    config = STOCK_CONFIGS.get(stock_id)

    if not config:
        return Decimal("0")

    state = get_simulation_state(stock_id)
    trade_size = decimal_value(gross_amount) / config["liquidity"]
    latest_price = get_latest_price(stock_id)
    current_price = (
        positive_price(latest_price.price, config["base_price"])
        if latest_price
        else positive_price(config["base_price"], Decimal("1.00"))
    )
    price_dampener = (config["base_price"] / current_price).sqrt()
    price_dampener = max(MIN_PRICE_IMPACT_DAMPENER, min(Decimal("1"), price_dampener))
    impact = config["trade_impact_factor"] * trade_size.sqrt() * price_dampener
    impact = min(MAX_TRADE_IMPACT, impact)

    if side == "BUY":
        state["pending_buy_pressure"] += impact
    else:
        state["pending_sell_pressure"] += impact

    return impact


def update_prices_if_due():
    if not STOCK_CONFIGS:
        load_stock_configs()

    latest_prices = {}
    now = datetime.utcnow()

    try:
        for stock_id, config in STOCK_CONFIGS.items():
            latest_price = get_latest_price(stock_id)

            if not latest_price:
                initial_price = money(config["base_price"])
                db.session.add(StockPrice(stock_id=stock_id, price=initial_price))
                latest_prices[config["symbol"]] = float(initial_price)
                continue

            next_update_at = latest_price.recorded_at + timedelta(seconds=UPDATE_INTERVAL_SECONDS)

            if next_update_at > now:
                latest_prices[config["symbol"]] = float(latest_price.price)
                continue

            state = get_simulation_state(stock_id)
            new_price = generate_next_price(latest_price.price, config, state)
            db.session.add(StockPrice(stock_id=stock_id, price=new_price))
            latest_prices[config["symbol"]] = float(new_price)

        db.session.commit()
    except OperationalError:
        db.session.rollback()
        latest_prices = get_current_prices()

    return latest_prices


def get_latest_price(stock_id):
    return (
        StockPrice.query
        .filter_by(stock_id=stock_id)
        .order_by(StockPrice.recorded_at.desc(), StockPrice.id.desc())
        .first()
    )


def get_current_prices():
    prices = {}

    if not STOCK_CONFIGS:
        load_stock_configs()

    for stock_id, config in STOCK_CONFIGS.items():
        latest_price = get_latest_price(stock_id)

        if latest_price:
            prices[config["symbol"]] = float(latest_price.price)

    return prices
