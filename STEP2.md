# 📋 Work Required for Each Page

## 🔐 Login Page (`login_server.py`)
**Goal**: Verify user credentials and initialize the session cache.

**Work to be completed**:
1. Database query: Verify username/email + password (1 query).
2. Session initialization: After successful login, store `user_id`, `username`, `cash`, and `portfolio` in the session.
3. Routing: `GET/POST /login`, display an error on failure.
4. Reuse: All subsequent pages depend on this session, so repeated login queries are unnecessary.

## 📝 Registration Page (`register_server.py`)
**Goal**: Create a new user and set initial data.

**Work to be completed**:
1. Database check: Verify that the username/email is unique (1 query).
2. Data insertion: Hash the password, set initial cash = 10000, and create the user record (1 write).
3. Session initialization: Automatically log in after successful registration and store session data.
5. Reuse: Store new user data directly in the session for use on subsequent pages.

## 📊 Dashboard Page (`dashboard/dashboard_server.py`)
**Goal**: Display user assets.

**Work to be completed**:
1. Data loading: On first entry, read `portfolio` and `cash` from the session (if missing, show an error indicating the login state is incorrect).
2. Reuse: All transaction data is reused in the session, and remains available when the page is refreshed.

## 🏆 Leaderboard Page (`leaderboard_server.py`)
**Goal**: Display user rankings, sorted by assets.

**Work to be completed**:
1. Cached query: Query all users’ assets (refresh data every five seconds).
2. User marking: Get the current user ID from the session and mark the position as "you".

## 👥 User List Page (`users_server.py`)
**Goal**: Display a paginated list of all users.

**Work to be completed**:
1. Pagination query: Query the database (20 users per page, 1 query).
2. Search function: Optional AJAX search, filtered by username (1 query).









## Session Format
**Goal**: Store user state after login or registration so other pages can reuse it without repeated queries.

**Suggested structure**:
```python
session = {
    "user_id": 1,
    "username": "alice",
    "email": "alice@example.com",
    "cash": 10000.0,
    "portfolio": {
        "AAPL": {
            "quantity": 10,
            "avg_price": 180.5
        }
    },
    "logged_in": True
}
```

**Notes**:
1. `user_id`: current user's unique ID.
2. `username`: current user's username.
3. `email`: current user's email.
4. `cash`: available cash balance.
5. `portfolio`: holdings data, keyed by stock symbol.
6. `logged_in`: login status flag.









## Database Structure

### `user` Table
Stores user account information, login credentials, and account balance.

```sql
CREATE TABLE user (
    id INTEGER NOT NULL,
    username VARCHAR(30) NOT NULL,
    email VARCHAR(120) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN NOT NULL,
    cash FLOAT NOT NULL,
    created_at DATETIME NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (username),
    UNIQUE (email)
);
```

### Field Description
1. `id`: Unique user ID, primary key.
2. `username`: Username, must be unique, maximum 30 characters.
3. `email`: User email, must be unique, maximum 120 characters.
4. `password_hash`: Hashed password, used for authentication.
5. `is_admin`: Indicates whether the user has administrator privileges.
6. `cash`: Current cash balance of the user account.
7. `created_at`: Timestamp of when the user account was created.

