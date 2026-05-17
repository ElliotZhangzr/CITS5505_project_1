from decimal import Decimal

from models import db, Stock, StockTransaction


def _money(value):
    return Decimal(value).quantize(Decimal("0.01"))


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
            "id": t.id,
            "stockId": t.stock_id,
            "symbol": t.stock.symbol,
            "side": t.side,
            "quantity": t.quantity,
            "price": float(_money(t.price)),
            "grossAmount": float(_money(t.gross_amount)),
            "realizedProfit": float(_money(t.realized_profit)),
            "averageCostBefore": (
                float(_money(t.average_cost_before))
                if t.average_cost_before is not None
                else None
            ),
            "cashBalanceAfter": float(_money(t.cash_balance_after)),
            "createdAt": t.created_at.isoformat(),
        }
        for t in transactions
    ]
