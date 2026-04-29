from models import User

def get_users_paginated(page=1, per_page=5):
    users = User.query.order_by(User.created_at.asc()).paginate(page=page, per_page=per_page)

    return {
        "users": [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "joinTime": user.created_at.strftime("%d %b %Y, %I:%M %p"),
            }
            for user in users.items
        ],
        "has_next": users.has_next,
        "has_prev": users.has_prev,
        "page": page
    }