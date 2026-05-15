from datetime import datetime, timedelta
from decimal import Decimal
import random

from sqlalchemy.exc import OperationalError

from memory_store import get_json, get_memory_client, set_json
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

STOCK_CONFIG_IDS_KEY = "stock_simulator:config_ids"


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


def decimal_state_value(state, key):
    return decimal_value(state.get(key, "0"))


def state_to_decimals(state):
    return {
        "buy_pressure": decimal_state_value(state, "buy_pressure"),
        "sell_pressure": decimal_state_value(state, "sell_pressure"),
        "pending_buy_pressure": decimal_state_value(state, "pending_buy_pressure"),
        "pending_sell_pressure": decimal_state_value(state, "pending_sell_pressure"),
    }


def state_to_json(state):
    return {
        "buy_pressure": str(state["buy_pressure"]),
        "sell_pressure": str(state["sell_pressure"]),
        "pending_buy_pressure": str(state["pending_buy_pressure"]),
        "pending_sell_pressure": str(state["pending_sell_pressure"]),
    }


def stock_config_key(stock_id):
    return f"stock_simulator:config:{stock_id}"


def stock_state_key(stock_id):
    return f"stock_simulator:state:{stock_id}"


def load_stock_configs():
    stocks = Stock.query.order_by(Stock.symbol).all()
    memory_client = get_memory_client()
    config_ids = []

    for stock in stocks:
        config = {
            "id": stock.id,
            "symbol": stock.symbol,
            "base_price": str(decimal_value(stock.base_price)),
            "volatility": str(decimal_value(stock.volatility)),
            "drift": str(decimal_value(stock.drift)),
            "mean_reversion_factor": str(decimal_value(stock.mean_reversion_factor)),
            "liquidity": str(decimal_value(stock.liquidity)),
            "trade_impact_factor": str(decimal_value(stock.trade_impact_factor)),
            "min_price": str(decimal_value(stock.min_price)),
        }
        set_json(stock_config_key(stock.id), config)
        config_ids.append(str(stock.id))
        get_simulation_state(stock.id)

    memory_client.delete(STOCK_CONFIG_IDS_KEY)

    if config_ids:
        memory_client.rpush(STOCK_CONFIG_IDS_KEY, *config_ids)


def deserialize_config(config):
    return {
        "id": int(config["id"]),
        "symbol": config["symbol"],
        "base_price": decimal_value(config["base_price"]),
        "volatility": decimal_value(config["volatility"]),
        "drift": decimal_value(config["drift"]),
        "mean_reversion_factor": decimal_value(config["mean_reversion_factor"]),
        "liquidity": decimal_value(config["liquidity"]),
        "trade_impact_factor": decimal_value(config["trade_impact_factor"]),
        "min_price": decimal_value(config["min_price"]),
    }


def get_stock_configs():
    memory_client = get_memory_client()
    config_ids = memory_client.lrange(STOCK_CONFIG_IDS_KEY, 0, -1)

    if not config_ids:
        load_stock_configs()
        config_ids = memory_client.lrange(STOCK_CONFIG_IDS_KEY, 0, -1)

    configs = []

    for stock_id in config_ids:
        config = get_json(stock_config_key(stock_id))

        if config:
            configs.append(deserialize_config(config))

    return configs


def get_stock_config(stock_id):
    config = get_json(stock_config_key(stock_id))

    if not config:
        load_stock_configs()
        config = get_json(stock_config_key(stock_id))

    return deserialize_config(config) if config else None


def get_simulation_state(stock_id):
    state = get_json(stock_state_key(stock_id))

    if not state:
        state = {
            "buy_pressure": "0",
            "sell_pressure": "0",
            "pending_buy_pressure": "0",
            "pending_sell_pressure": "0",
        }
        set_json(stock_state_key(stock_id), state)

    return state_to_decimals(state)


def save_simulation_state(stock_id, state):
    set_json(stock_state_key(stock_id), state_to_json(state))


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
    config = get_stock_config(stock_id)

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

    save_simulation_state(stock_id, state)
    return impact


def update_prices_if_due():
    latest_prices = {}
    now = datetime.utcnow()

    try:
        for config in get_stock_configs():
            stock_id = config["id"]
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
            save_simulation_state(stock_id, state)
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

    for config in get_stock_configs():
        stock_id = config["id"]
        latest_price = get_latest_price(stock_id)

        if latest_price:
            prices[config["symbol"]] = float(latest_price.price)

    return prices
