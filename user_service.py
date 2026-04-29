from models import User


def get_all_users():
    users = User.query.order_by(User.created_at.desc()).all()

    return [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "joinTime": user.created_at.strftime("%d %b %Y, %I:%M %p"),
        }
        for user in users
    ]
