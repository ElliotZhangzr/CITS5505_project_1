from models import User
from trading_service import build_portfolio

INITIAL_CASH = 10000.0

def calculate_user_metrics(user):
    portfolio = build_portfolio(user.id)

    cash = float(portfolio.get("cash", user.cash))
    total_assets = float(portfolio.get("totalAssets", cash))
    total_profit = float(portfolio.get("totalProfit", 0.0))
    return_percent = (total_assets - INITIAL_CASH) / INITIAL_CASH * 100
    
    return {
        "username": user.username,
        "email": user.email,
        "cash": cash,
        "total_assets": total_assets,
        "total_profit": total_profit,  
        "returnPercent": return_percent
    }

def get_ranking_value(user_data, ranking_type):
    if ranking_type == "assets":
        return user_data["total_assets"]
    elif ranking_type == "profit":
        return user_data["total_profit"]
    elif ranking_type == "return":
        return user_data["returnPercent"]
    else:
        return user_data["cash"]
    
def get_leaderboard_context(ranking_type, current_username):

    users = User.query.all()

    leaderboard_users = []

    for user in users:

        user_data = calculate_user_metrics(user)
        
        user_data["ranking_value"] = get_ranking_value(user_data, ranking_type)

        leaderboard_users.append(user_data)

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
        "current_username": current_username
    }
