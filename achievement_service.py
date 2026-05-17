from sqlalchemy import func

from achievement_definitions import ACHIEVEMENTS
from models import Stock, StockHolding, StockTransaction, User
from trading_service import build_portfolio


# evaluates a single achievement condition using an operator string from its definition
def compare_metric(value, operator, target):
    if operator == ">=":
        return value >= target
    if operator == ">":
        return value > target
    if operator == "<=":
        return value <= target
    if operator == "<":
        return value < target
    if operator == "==":
        return value == target
    if operator == "truthy":
        return bool(value)
    raise ValueError(f"Unsupported achievement operator: {operator}")


# full-table scan — builds a portfolio for every user; called once per profile load
def get_total_assets_rank(user_id):
    ranked_users = []

    for user in User.query.all():
        portfolio = build_portfolio(user.id)
        ranked_users.append(
            {
                "user_id": user.id,
                "total_assets": float(portfolio.get("totalAssets", user.cash)),
            }
        )

    ranked_users.sort(key=lambda item: item["total_assets"], reverse=True)

    for index, item in enumerate(ranked_users, start=1):
        if item["user_id"] == user_id:
            return index

    return None


def build_achievement_metrics(user):
    portfolio = build_portfolio(user.id)
    holding_count = (
        StockHolding.query
        .filter(StockHolding.user_id == user.id, StockHolding.quantity > 0)
        .count()
    )
    stock_count = Stock.query.count()

    trade_counts = dict(
        StockTransaction.query
        .with_entities(StockTransaction.side, func.count(StockTransaction.id))
        .filter_by(user_id=user.id)
        .group_by(StockTransaction.side)
        .all()
    )

    return {
        "trade_count": sum(trade_counts.values()),
        "buy_count": trade_counts.get("BUY", 0),
        "sell_count": trade_counts.get("SELL", 0),
        "has_bio": bool((user.bio or "").strip()),
        "has_avatar": bool((user.avatar_url or "").strip()),
        "holding_count": holding_count,
        "stock_count": stock_count,
        "total_profit": float(portfolio.get("totalProfit", 0)),
        "total_assets": float(portfolio.get("totalAssets", user.cash)),
        "total_assets_rank": get_total_assets_rank(user.id),
        "holds_all_stocks": stock_count > 0 and holding_count >= stock_count,
    }


def get_user_achievements(user):
    metrics = build_achievement_metrics(user)
    achievements = []

    for definition in ACHIEVEMENTS:
        current_value = metrics.get(definition["metric"])
        unlocked = compare_metric(
            current_value,
            definition["operator"],
            definition["target"],
        )
        achievements.append(
            {
                **definition,
                "current_value": current_value,
                "unlocked": unlocked,
            }
        )

    return achievements
