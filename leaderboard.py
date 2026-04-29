from models import User

def get_leaderboard_context(ranking_type, current_user):

    leaderboard_users = User.query.order_by(User.cash.desc()).all()

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