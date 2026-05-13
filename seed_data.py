from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = BASE_DIR / "instance" / "app.db"


USERS = [
    (
        1,
        "ellang",
        "example@doooy.cn",
        "3cea35c661bd7dd54b456c6224b903780825aa219c726ea772d678ade062b285",
        1,
        9999999999,
        "",
        "",
        0,
        "2026-05-04 16:13:26.838215",
    ),
    (
        2,
        "root",
        "ellir@gmail.com",
        "4813494d137e1631bba301d5acab6e7bb7aa74ce1185d456565ef51d737677b2",
        0,
        9049.55,
        "",
        "",
        0,
        "2026-05-04 16:32:52.351358",
    ),
]


STOCKS = [
    (1, "AAPL", "Apple Inc.", "2026-04-28 08:35:28.641540", 150, 0.006, 0.0002, 0.15, 0, 1000000, 0.25, 1),
    (2, "TSLA", "Tesla Inc.", "2026-04-28 08:35:28.643347", 200, 0.025, 0.0001, 0.55, 0, 300000, 0.8, 1),
    (3, "NVDA", "NVIDIA Corporation", "2026-04-28 08:35:28.645040", 900, 0.015, 0.0006, 0.4, 0, 600000, 0.5, 1),
]


STOCK_PRICES = [
    (1, 1, 180, "2026-04-28 08:35:28.644162"),
    (2, 1, 176.55, "2026-04-28 08:35:28.644164"),
    (3, 1, 176.41, "2026-04-28 08:35:28.644165"),
    (4, 1, 178.41, "2026-04-28 08:35:28.644166"),
    (5, 1, 180.57, "2026-04-28 08:35:28.644167"),
    (6, 1, 176.97, "2026-04-28 08:35:28.644167"),
    (7, 1, 178.99, "2026-04-28 08:35:28.644168"),
    (8, 1, 177.56, "2026-04-28 08:35:28.644169"),
    (9, 1, 175.95, "2026-04-28 08:35:28.644169"),
    (10, 1, 177.66, "2026-04-28 08:35:28.644170"),
    (11, 2, 210, "2026-04-28 08:35:28.645231"),
    (12, 2, 207.95, "2026-04-28 08:35:28.645233"),
    (13, 2, 208.14, "2026-04-28 08:35:28.645234"),
    (14, 2, 204.2, "2026-04-28 08:35:28.645234"),
    (15, 2, 204.56, "2026-04-28 08:35:28.645235"),
    (16, 2, 206.58, "2026-04-28 08:35:28.645236"),
    (17, 2, 207.33, "2026-04-28 08:35:28.645237"),
    (18, 2, 210.37, "2026-04-28 08:35:28.645237"),
    (19, 2, 209.51, "2026-04-28 08:35:28.645238"),
    (20, 2, 212.14, "2026-04-28 08:35:28.645239"),
    (21, 3, 800, "2026-04-28 08:35:28.645817"),
    (22, 3, 807.47, "2026-04-28 08:35:28.645819"),
    (23, 3, 816.19, "2026-04-28 08:35:28.645819"),
    (24, 3, 823.06, "2026-04-28 08:35:28.645820"),
    (25, 3, 810.81, "2026-04-28 08:35:28.645821"),
    (26, 3, 821.56, "2026-04-28 08:35:28.645822"),
    (27, 3, 825.27, "2026-04-28 08:35:28.645822"),
    (28, 3, 840.96, "2026-04-28 08:35:28.645823"),
    (29, 3, 856.63, "2026-04-28 08:35:28.645824"),
    (30, 3, 872.87, "2026-04-28 08:35:28.645824"),
]


STOCK_HOLDINGS = [
    (1, 2, 1, 7, 135.78, 950.45, "2026-05-04 17:00:24.538000"),
]


STOCK_TRANSACTIONS = [
    (1, 2, 1, "BUY", 1, 136.59, 136.59, 0, 0, 9863.41, "2026-05-04 17:00:18.107135"),
    (2, 2, 1, "BUY", 1, 137.21, 137.21, 0, 136.59, 9726.2, "2026-05-04 17:00:23.097008"),
    (3, 2, 1, "BUY", 1, 137.21, 137.21, 0, 136.9, 9588.99, "2026-05-04 17:00:23.931190"),
    (4, 2, 1, "BUY", 1, 134.86, 134.86, 0, 137, 9454.13, "2026-05-04 17:00:24.088792"),
    (5, 2, 1, "BUY", 1, 134.86, 134.86, 0, 136.47, 9319.27, "2026-05-04 17:00:24.270243"),
    (6, 2, 1, "BUY", 1, 134.86, 134.86, 0, 136.15, 9184.41, "2026-05-04 17:00:24.403579"),
    (7, 2, 1, "BUY", 1, 134.86, 134.86, 0, 135.93, 9049.55, "2026-05-04 17:00:24.539481"),
]


CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS "user" (
    id INTEGER NOT NULL PRIMARY KEY,
    username VARCHAR(30) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN NOT NULL,
    cash NUMERIC(12, 2) NOT NULL,
    bio VARCHAR(200),
    avatar_url VARCHAR(500),
    hide_holdings BOOLEAN NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS stock (
    id INTEGER NOT NULL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL UNIQUE,
    name VARCHAR(120) NOT NULL,
    created_at DATETIME NOT NULL,
    base_price NUMERIC(12, 2) NOT NULL DEFAULT 100.00,
    volatility NUMERIC(8, 6) NOT NULL DEFAULT 0.010000,
    drift NUMERIC(8, 6) NOT NULL DEFAULT 0.000000,
    momentum_factor NUMERIC(8, 6) NOT NULL DEFAULT 0.200000,
    mean_reversion_factor NUMERIC(8, 6) NOT NULL DEFAULT 0.030000,
    liquidity NUMERIC(14, 2) NOT NULL DEFAULT 500000.00,
    trade_impact_factor NUMERIC(8, 6) NOT NULL DEFAULT 0.500000,
    min_price NUMERIC(12, 2) NOT NULL DEFAULT 1.00
);

CREATE TABLE IF NOT EXISTS stock_price (
    id INTEGER NOT NULL PRIMARY KEY,
    stock_id INTEGER NOT NULL,
    price NUMERIC(12, 2) NOT NULL,
    recorded_at DATETIME NOT NULL,
    FOREIGN KEY (stock_id) REFERENCES stock (id)
);

CREATE TABLE IF NOT EXISTS stock_holding (
    id INTEGER NOT NULL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    stock_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    average_cost NUMERIC(12, 2) NOT NULL,
    total_cost NUMERIC(14, 2) NOT NULL,
    updated_at DATETIME NOT NULL,
    CONSTRAINT uq_user_stock_holding UNIQUE (user_id, stock_id),
    FOREIGN KEY (user_id) REFERENCES "user" (id),
    FOREIGN KEY (stock_id) REFERENCES stock (id)
);

CREATE TABLE IF NOT EXISTS stock_transaction (
    id INTEGER NOT NULL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    stock_id INTEGER NOT NULL,
    side VARCHAR(4) NOT NULL,
    quantity INTEGER NOT NULL,
    price NUMERIC(12, 2) NOT NULL,
    gross_amount NUMERIC(14, 2) NOT NULL,
    realized_profit NUMERIC(14, 2) NOT NULL DEFAULT 0.00,
    average_cost_before NUMERIC(12, 2),
    cash_balance_after NUMERIC(14, 2) NOT NULL,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES "user" (id),
    FOREIGN KEY (stock_id) REFERENCES stock (id)
);
"""


def seed_database(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript(CREATE_TABLES_SQL)

        user_columns = {
            row[1] for row in conn.execute('PRAGMA table_info("user")').fetchall()
        }
        if {"bio", "avatar_url", "hide_holdings"}.issubset(user_columns):
            conn.executemany(
                """
                INSERT INTO "user"
                (id, username, email, password_hash, is_admin, cash, bio, avatar_url,
                 hide_holdings, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    username = excluded.username,
                    email = excluded.email,
                    password_hash = excluded.password_hash,
                    is_admin = excluded.is_admin,
                    cash = excluded.cash,
                    bio = excluded.bio,
                    avatar_url = excluded.avatar_url,
                    hide_holdings = excluded.hide_holdings,
                    created_at = excluded.created_at
                """,
                USERS,
            )
        else:
            legacy_users = [user[:6] + (user[9],) for user in USERS]
            conn.executemany(
                """
                INSERT INTO "user"
                (id, username, email, password_hash, is_admin, cash, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    username = excluded.username,
                    email = excluded.email,
                    password_hash = excluded.password_hash,
                    is_admin = excluded.is_admin,
                    cash = excluded.cash,
                    created_at = excluded.created_at
                """,
                legacy_users,
            )
        conn.executemany(
            """
            INSERT OR IGNORE INTO stock
            (id, symbol, name, created_at, base_price, volatility, drift,
             momentum_factor, mean_reversion_factor, liquidity,
             trade_impact_factor, min_price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            STOCKS,
        )
        conn.executemany(
            """
            INSERT OR IGNORE INTO stock_price
            (id, stock_id, price, recorded_at)
            VALUES (?, ?, ?, ?)
            """,
            STOCK_PRICES,
        )
        conn.executemany(
            """
            INSERT OR IGNORE INTO stock_holding
            (id, user_id, stock_id, quantity, average_cost, total_cost, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            STOCK_HOLDINGS,
        )
        conn.executemany(
            """
            INSERT OR IGNORE INTO stock_transaction
            (id, user_id, stock_id, side, quantity, price, gross_amount,
             realized_profit, average_cost_before, cash_balance_after, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            STOCK_TRANSACTIONS,
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Insert standalone seed data into a SQLite database.")
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB_PATH,
        help=f"SQLite database path. Default: {DEFAULT_DB_PATH}",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    seed_database(args.db)
    print(f"Seed data inserted into {args.db}")
