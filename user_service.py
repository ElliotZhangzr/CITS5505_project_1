from models import db, User

def get_users_paginated(page=1, per_page=5, search=""):
    search = (search or "").strip()
    query = User.query

    if search:
        filters = [User.username.ilike(f"%{search}%")]

        if search.isdigit():
            filters.append(User.id == int(search))

        query = query.filter(db.or_(*filters))

    users = query.order_by(User.created_at.asc()).paginate(page=page, per_page=per_page)

    return {
        "users": [
            {
                "id": user.id,
                "username": user.username,
                "joinTime": user.created_at.strftime("%d %b %Y, %I:%M %p"),
            }
            for user in users.items
        ],
        "has_next": users.has_next,
        "has_prev": users.has_prev,
        "page": page,
        "search": search,
    }
