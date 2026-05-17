import tempfile
import unittest
from pathlib import Path

from flask_migrate import upgrade
from werkzeug.security import check_password_hash

import seed_data
from models import Stock, StockHolding, StockPrice, StockTransaction, User, db


class SeedDataTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "seed.db"
        app = seed_data.create_seed_app(self.db_path)
        with app.app_context():
            upgrade()

    def tearDown(self):
        self.temp_dir.cleanup()

    def open_seed_app(self):
        return seed_data.create_seed_app(self.db_path)

    def test_seed_database_creates_root_admin_and_trader_users(self):
        seed_data.seed_database(self.db_path)
        app = self.open_seed_app()

        with app.app_context():
            usernames = {user.username for user in User.query.all()}
            root = User.query.filter_by(username="root").one()
            admin = User.query.filter_by(username="admin").one()
            trader = User.query.filter_by(username="trader").one()

            expected_usernames = {data["username"] for data in seed_data.USERS}
            self.assertEqual(usernames, expected_usernames)
            self.assertTrue(root.is_admin)
            self.assertTrue(admin.is_admin)
            self.assertFalse(trader.is_admin)
            self.assertEqual(root.email, "root@example.com")
            self.assertEqual(trader.cash, seed_data.USERS[2]["cash"])

    def test_seed_root_password_is_hashed_and_matches_plain_password(self):
        seed_data.seed_database(self.db_path)
        app = self.open_seed_app()

        with app.app_context():
            root = User.query.filter_by(username="root").one()

            self.assertNotEqual(root.password_hash, "root")
            self.assertTrue(check_password_hash(root.password_hash, "root"))

    def test_seed_database_creates_expected_stocks(self):
        seed_data.seed_database(self.db_path)
        app = self.open_seed_app()

        with app.app_context():
            symbols = {stock.symbol for stock in Stock.query.all()}
            aapl = Stock.query.filter_by(symbol="AAPL").one()
            tsla = Stock.query.filter_by(symbol="TSLA").one()
            nvda = Stock.query.filter_by(symbol="NVDA").one()

            self.assertEqual(symbols, {"AAPL", "TSLA", "NVDA"})
            self.assertEqual(aapl.name, "Apple Inc.")
            self.assertEqual(tsla.name, "Tesla Inc.")
            self.assertEqual(nvda.name, "NVIDIA Corporation")

    def test_seed_database_creates_stock_prices(self):
        seed_data.seed_database(self.db_path)
        app = self.open_seed_app()

        with app.app_context():
            expected_price_count = sum(len(stock["prices"]) for stock in seed_data.STOCKS)
            self.assertEqual(StockPrice.query.count(), expected_price_count)

            aapl = Stock.query.filter_by(symbol="AAPL").one()
            aapl_prices = (
                StockPrice.query
                .filter_by(stock_id=aapl.id)
                .order_by(StockPrice.recorded_at.asc())
                .all()
            )
            self.assertEqual(len(aapl_prices), len(seed_data.STOCKS[0]["prices"]))
            self.assertEqual(str(aapl_prices[0].price), "180.00")

    def test_seed_database_creates_trader_aapl_holding(self):
        seed_data.seed_database(self.db_path)
        app = self.open_seed_app()

        with app.app_context():
            trader = User.query.filter_by(username="trader").one()
            aapl = Stock.query.filter_by(symbol="AAPL").one()
            holding = StockHolding.query.filter_by(user_id=trader.id, stock_id=aapl.id).one()

            self.assertEqual(holding.quantity, 7)
            self.assertEqual(holding.average_cost, seed_data.HOLDINGS[0]["average_cost"])
            self.assertEqual(holding.total_cost, seed_data.HOLDINGS[0]["total_cost"])

    def test_seed_database_creates_trader_buy_transactions(self):
        seed_data.seed_database(self.db_path)
        app = self.open_seed_app()

        with app.app_context():
            trader = User.query.filter_by(username="trader").one()
            transactions = StockTransaction.query.filter_by(user_id=trader.id).all()

            trader_transactions = [t for t in seed_data.TRANSACTIONS if t[0] == "trader"]
            self.assertEqual(len(transactions), len(trader_transactions))
            self.assertTrue(all(transaction.side == "BUY" for transaction in transactions))
            self.assertTrue(all(transaction.quantity == 1 for transaction in transactions))

    def test_seed_database_can_run_twice_without_duplicate_users_or_stocks(self):
        seed_data.seed_database(self.db_path)
        seed_data.seed_database(self.db_path)
        app = self.open_seed_app()

        with app.app_context():
            self.assertEqual(User.query.filter_by(username="root").count(), 1)
            self.assertEqual(User.query.filter_by(username="admin").count(), 1)
            self.assertEqual(User.query.filter_by(username="trader").count(), 1)
            self.assertEqual(Stock.query.filter_by(symbol="AAPL").count(), 1)
            self.assertEqual(Stock.query.filter_by(symbol="TSLA").count(), 1)
            self.assertEqual(Stock.query.filter_by(symbol="NVDA").count(), 1)

    def test_seed_database_can_run_twice_without_duplicate_prices_holdings_or_transactions(self):
        seed_data.seed_database(self.db_path)
        seed_data.seed_database(self.db_path)
        app = self.open_seed_app()

        with app.app_context():
            expected_price_count = sum(len(stock["prices"]) for stock in seed_data.STOCKS)
            trader = User.query.filter_by(username="trader").one()

            trader_transactions = [t for t in seed_data.TRANSACTIONS if t[0] == "trader"]
            self.assertEqual(StockPrice.query.count(), expected_price_count)
            self.assertEqual(StockHolding.query.filter_by(user_id=trader.id).count(), 1)
            self.assertEqual(StockTransaction.query.filter_by(user_id=trader.id).count(), len(trader_transactions))


if __name__ == "__main__":
    unittest.main()
