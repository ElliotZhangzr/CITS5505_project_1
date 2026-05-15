import unittest
from decimal import Decimal

from models import StockHolding, StockTransaction, db
from tests.unit.test_auth_forms import create_auth_test_app, create_user
from tests.unit.test_trading_service import create_price, create_stock
from trading_service import build_portfolio


def create_holding(user, stock, quantity=1, average_cost="100.00", total_cost=None):
    if total_cost is None:
        total_cost = Decimal(average_cost) * quantity

    holding = StockHolding(
        user_id=user.id,
        stock_id=stock.id,
        quantity=quantity,
        average_cost=Decimal(average_cost),
        total_cost=Decimal(total_cost),
    )
    db.session.add(holding)
    db.session.commit()
    return holding


def create_sell_transaction(user, stock, realized_profit="0.00"):
    transaction = StockTransaction(
        user_id=user.id,
        stock_id=stock.id,
        side="SELL",
        quantity=1,
        price=Decimal("100.00"),
        gross_amount=Decimal("100.00"),
        realized_profit=Decimal(realized_profit),
        average_cost_before=Decimal("100.00"),
        cash_balance_after=Decimal(user.cash),
    )
    db.session.add(transaction)
    db.session.commit()
    return transaction


class PortfolioTests(unittest.TestCase):
    def setUp(self):
        self.app = create_auth_test_app()
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.user = create_user(username="portfolio", email="portfolio@example.com")
        self.user.cash = Decimal("1000.00")
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_portfolio_without_holdings_returns_empty_holdings_zero_stock_value_and_total_assets_equal_cash(self):
        portfolio = build_portfolio(self.user.id)

        self.assertEqual(portfolio["holdings"], [])
        self.assertEqual(portfolio["stockValue"], 0.0)
        self.assertEqual(portfolio["unrealizedProfit"], 0.0)
        self.assertEqual(portfolio["realizedProfit"], 0.0)
        self.assertEqual(portfolio["totalProfit"], 0.0)
        self.assertEqual(portfolio["cash"], 1000.0)
        self.assertEqual(portfolio["totalAssets"], 1000.0)

    def test_portfolio_with_holding_calculates_market_value_from_current_price_times_quantity(self):
        stock = create_stock(symbol="AAPL", name="Apple Inc.")
        create_price(stock, "120.00")
        create_holding(self.user, stock, quantity=3, average_cost="100.00", total_cost="300.00")

        portfolio = build_portfolio(self.user.id)

        holding = portfolio["holdings"][0]
        self.assertEqual(holding["symbol"], "AAPL")
        self.assertEqual(holding["quantity"], 3)
        self.assertEqual(holding["currentPrice"], 120.0)
        self.assertEqual(holding["marketValue"], 360.0)
        self.assertEqual(portfolio["stockValue"], 360.0)
        self.assertEqual(portfolio["totalAssets"], 1360.0)

    def test_portfolio_calculates_unrealized_profit_from_current_price_minus_average_cost_times_quantity(self):
        stock = create_stock(symbol="AAPL", name="Apple Inc.")
        create_price(stock, "125.00")
        create_holding(self.user, stock, quantity=4, average_cost="100.00", total_cost="400.00")

        portfolio = build_portfolio(self.user.id)

        holding = portfolio["holdings"][0]
        self.assertEqual(holding["unrealizedProfit"], 100.0)
        self.assertEqual(portfolio["unrealizedProfit"], 100.0)
        self.assertEqual(portfolio["totalProfit"], 100.0)

    def test_portfolio_realized_profit_is_sum_of_sell_transaction_profit(self):
        stock = create_stock(symbol="AAPL", name="Apple Inc.")
        create_price(stock, "100.00")
        create_sell_transaction(self.user, stock, realized_profit="20.00")
        create_sell_transaction(self.user, stock, realized_profit="35.50")
        create_sell_transaction(self.user, stock, realized_profit="-5.25")

        portfolio = build_portfolio(self.user.id)

        self.assertEqual(portfolio["realizedProfit"], 50.25)
        self.assertEqual(portfolio["totalProfit"], 50.25)

    def test_portfolio_uses_zero_current_price_when_stock_has_no_price_and_does_not_crash(self):
        stock = create_stock(symbol="MSFT", name="Microsoft", base_price="200.00")
        create_holding(self.user, stock, quantity=2, average_cost="50.00", total_cost="100.00")

        portfolio = build_portfolio(self.user.id)

        holding = portfolio["holdings"][0]
        self.assertEqual(holding["currentPrice"], 0.0)
        self.assertEqual(holding["marketValue"], 0.0)
        self.assertEqual(holding["unrealizedProfit"], -100.0)
        self.assertEqual(portfolio["stockValue"], 0.0)
        self.assertEqual(portfolio["totalAssets"], 1000.0)
        self.assertEqual(portfolio["totalProfit"], -100.0)

    def test_portfolio_output_does_not_expose_email_or_password_hash(self):
        stock = create_stock(symbol="AAPL", name="Apple Inc.")
        create_price(stock, "120.00")
        create_holding(self.user, stock, quantity=1, average_cost="100.00")

        portfolio = build_portfolio(self.user.id)

        self.assertNotIn("email", portfolio)
        self.assertNotIn("password_hash", portfolio)
        self.assertNotIn("passwordHash", portfolio)

        holding = portfolio["holdings"][0]
        self.assertNotIn("email", holding)
        self.assertNotIn("password_hash", holding)
        self.assertNotIn("passwordHash", holding)


if __name__ == "__main__":
    unittest.main()
