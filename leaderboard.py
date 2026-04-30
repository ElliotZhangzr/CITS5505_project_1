from models import User
from trading_service import build_portfolio

def get_leaderboard_context(ranking_type, current_user):

    users = User.query.all()

    leaderboard_users = []

    for user in users:
        if ranking_type == "assets":
            portfolio = build_portfolio(user.id)
            ranking_value = portfolio["total_assets"]
        else:
            ranking_value = float(user.cash)

    
        leaderboard_users.append({
        "username": user.username,
        "email": user.email,
        "cash": float(user.cash),
        "ranking_value": ranking_value
    })

    leaderboard_users.sort(key=lambda user: user["ranking_value"], reverse=True)

    if ranking_type == "assets":
        title = "Total Assets Ranking"
        value_label = "Total Assets"
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