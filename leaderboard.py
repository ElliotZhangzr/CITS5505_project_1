from models import User
from trading_service import build_portfolio

INITIAL_CASH = 10000.0

def get_leaderboard_context(ranking_type, current_user):

    users = User.query.all()

    leaderboard_users = []

    for user in users:
        portfolio = build_portfolio(user.id)

        cash = float(portfolio.get("cash", user.cash))
        total_assets = float(portfolio.get("totalAssets", cash))
        total_profit = float(portfolio.get("totalProfit", 0.0))

        if ranking_type == "assets":
            ranking_value = total_assets
        elif ranking_type == "profit":
            ranking_value = total_profit
        elif ranking_type == "return":
            ranking_value = (total_assets - INITIAL_CASH) / INITIAL_CASH * 100
        else:
            ranking_value = cash
            ranking_type

        leaderboard_users.append({
        "username": user.username,
        "email": user.email,
        "cash": cash,
        "total_assets": total_assets,
        "total_profit": total_profit,
        "returnPercent": (total_assets - INITIAL_CASH) / INITIAL_CASH * 100,
        "ranking_value": ranking_value
    })

    leaderboard_users.sort(key=lambda user: user["ranking_value"], reverse=True)

    for index, user in enumerate(leaderboard_users, start=1):
        user["rank"] = index

    if ranking_type == "assets":
        title = "Total Assets Ranking"
        value_label = "Total Assets"
    elif ranking_type == "profit":
        title = "Profit Ranking"
        value_label = "Total Profit"
    elif ranking_type == "return":
        title = "Return Percentage Ranking"
        value_label = "Return %"
    else:
        title = "Cash Ranking"
        value_label = "Cash"

    return {
        "users": leaderboard_users,
        "title": title,
        "ranking_type": ranking_type,
        "value_label": value_label,
        "current_user": current_user
    }