from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import func

from models import db, Stock, StockHolding, StockTransaction, User
from stock_simulator import apply_trade_impact, get_latest_price


def money(value):
    return Decimal(value).quantize(Decimal("0.01"))


def get_current_stock_price(stock_id):
    latest_price = get_latest_price(stock_id)

    if not latest_price:
        return None

    return money(latest_price.price)


def get_or_create_holding(user_id, stock_id):
    holding = StockHolding.query.filter_by(user_id=user_id, stock_id=stock_id).first()

    if holding:
        return holding

    holding = StockHolding(
        user_id=user_id,
        stock_id=stock_id,
        quantity=0,
        average_cost=Decimal("0.00"),
        total_cost=Decimal("0.00"),
    )
    db.session.add(holding)
    return holding


def execute_stock_trade_from_payload(user_id, payload):
    if not isinstance(payload, dict):
        return None, "Trade request must be a JSON object."

    stock_id = payload.get("stockId", payload.get("stock_id"))
    side = payload.get("side", "")
    quantity = payload.get("quantity")

    if stock_id in (None, ""):
        return None, "Stock is required."

    if quantity in (None, ""):
        return None, "Quantity is required."

    try:
        stock_id = int(stock_id)
    except (TypeError, ValueError):
        return None, "Stock must be a valid number."

    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        return None, "Quantity must be a valid number."

    return execute_stock_trade(user_id, stock_id, side, quantity)


def execute_stock_trade(user_id, stock_id, side, quantity):
    side = side.upper()

    if side not in ("BUY", "SELL"):
        return None, "Trade side must be BUY or SELL."

    if not isinstance(quantity, int) or quantity <= 0:
        return None, "Quantity must be an integer greater than 0."

    user = db.session.get(User, user_id)
    stock = db.session.get(Stock, stock_id)

    if not user:
        return None, "User not found."

    if not stock:
        return None, "Stock not found."

    price = get_current_stock_price(stock_id)

    if price is None:
        return None, "No stock price available."

    gross_amount = money(price * quantity)
    holding = StockHolding.query.filter_by(user_id=user_id, stock_id=stock_id).first()

    if side == "BUY":
        holding = holding or get_or_create_holding(user_id, stock_id)
    elif not holding:
        return None, f"Sell failed: insufficient {stock.symbol} holdings."

    average_cost_before = money(holding.average_cost)
    realized_profit = Decimal("0.00")

    if side == "BUY":
        if money(user.cash) < gross_amount:
            return None, "Trade failed: insufficient cash."

        new_quantity = holding.quantity + quantity
        new_total_cost = money(holding.total_cost + gross_amount)

        user.cash = money(user.cash - gross_amount)
        holding.quantity = new_quantity
        holding.total_cost = new_total_cost
        holding.average_cost = money(new_total_cost / new_quantity)
        holding.updated_at = datetime.now(timezone.utc)
    else:
        if holding.quantity < quantity:
            return None, f"Sell failed: insufficient {stock.symbol} holdings."

        realized_profit = money((price - holding.average_cost) * quantity)
        user.cash = money(user.cash + gross_amount)

        remaining_quantity = holding.quantity - quantity

        if remaining_quantity == 0:
            db.session.delete(holding)
        else:
            remaining_cost = money(holding.total_cost - holding.average_cost * quantity)
            holding.quantity = remaining_quantity
            holding.total_cost = remaining_cost
            holding.average_cost = money(remaining_cost / remaining_quantity)
            holding.updated_at = datetime.now(timezone.utc)

    transaction = StockTransaction(
        user_id=user_id,
        stock_id=stock_id,
        side=side,
        quantity=quantity,
        price=price,
        gross_amount=gross_amount,
        realized_profit=realized_profit,
        average_cost_before=average_cost_before,
        cash_balance_after=money(user.cash),
    )
    db.session.add(transaction)
    db.session.commit()
    apply_trade_impact(stock_id, side, gross_amount)

    return build_portfolio(user_id), None


def build_portfolio(user_id):
    user = db.session.get(User, user_id)
    holdings = (
        StockHolding.query
        .filter_by(user_id=user_id)
        .join(Stock)
        .order_by(Stock.symbol)
        .all()
    )

    holding_rows = []
    stock_value = Decimal("0.00")
    unrealized_profit = Decimal("0.00")

    for holding in holdings:
        current_price = get_current_stock_price(holding.stock_id)

        if current_price is None:
            current_price = Decimal("0.00")

        market_value = money(current_price * holding.quantity)
        holding_profit = money((current_price - holding.average_cost) * holding.quantity)

        stock_value += market_value
        unrealized_profit += holding_profit

        holding_rows.append({
            "stockId": holding.stock_id,
            "symbol": holding.stock.symbol,
            "name": holding.stock.name,
            "quantity": holding.quantity,
            "averageCost": float(money(holding.average_cost)),
            "currentPrice": float(current_price),
            "marketValue": float(market_value),
            "unrealizedProfit": float(holding_profit),
        })

    realized_profit = (
        db.session.query(func.coalesce(func.sum(StockTransaction.realized_profit), 0))
        .filter_by(user_id=user_id, side="SELL")
        .scalar()
    )
    realized_profit = money(realized_profit)
    cash = money(user.cash)
    stock_value = money(stock_value)
    unrealized_profit = money(unrealized_profit)
    total_assets = money(cash + stock_value)

    return {
        "cash": float(cash),
        "stockValue": float(stock_value),
        "totalAssets": float(total_assets),
        "realizedProfit": float(realized_profit),
        "unrealizedProfit": float(unrealized_profit),
        "totalProfit": float(realized_profit + unrealized_profit),
        "holdings": holding_rows,
    }


def get_transaction_history(user_id, limit=50):
    transactions = (
        StockTransaction.query
        .filter_by(user_id=user_id)
        .join(Stock)
        .order_by(StockTransaction.created_at.desc(), StockTransaction.id.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": transaction.id,
            "stockId": transaction.stock_id,
            "symbol": transaction.stock.symbol,
            "side": transaction.side,
            "quantity": transaction.quantity,
            "price": float(money(transaction.price)),
            "grossAmount": float(money(transaction.gross_amount)),
            "realizedProfit": float(money(transaction.realized_profit)),
            "averageCostBefore": (
                float(money(transaction.average_cost_before))
                if transaction.average_cost_before is not None
                else None
            ),
            "cashBalanceAfter": float(money(transaction.cash_balance_after)),
            "createdAt": transaction.created_at.isoformat(),
        }
        for transaction in transactions
    ]
