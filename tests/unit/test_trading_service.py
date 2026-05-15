import unittest
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import patch

from models import Stock, StockHolding, StockPrice, StockTransaction, db
from tests.unit.test_auth_forms import create_auth_test_app, create_user
from trading_service import execute_stock_trade, execute_stock_trade_from_payload


def create_stock(symbol="AAPL", name="Apple Inc.", base_price="100.00"):
    stock = Stock(
        symbol=symbol,
        name=name,
        base_price=Decimal(base_price),
        volatility=Decimal("0.010000"),
        drift=Decimal("0.000000"),
        momentum_factor=Decimal("0.200000"),
        mean_reversion_factor=Decimal("0.030000"),
        liquidity=Decimal("500000.00"),
        trade_impact_factor=Decimal("0.500000"),
        min_price=Decimal("1.00"),
    )
    db.session.add(stock)
    db.session.commit()
    return stock


def create_price(stock, price="100.00", seconds=0):
    stock_price = StockPrice(
        stock_id=stock.id,
        price=Decimal(price),
        recorded_at=datetime(2026, 5, 1, 12, 0, 0) + timedelta(seconds=seconds),
    )
    db.session.add(stock_price)
    db.session.commit()
    return stock_price


class TradingServiceTests(unittest.TestCase):
    def setUp(self):
        self.app = create_auth_test_app()
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.user = create_user(username="trader", email="trader@example.com", password="Password1")
        self.user.cash = Decimal("1000.00")
        self.stock = create_stock()
        create_price(self.stock, "100.00", seconds=1)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    @patch("trading_service.apply_trade_impact")
    def test_first_buy_reduces_cash_creates_holding_and_buy_transaction(self, mock_apply_impact):
        portfolio, error = execute_stock_trade(self.user.id, self.stock.id, "BUY", 3)

        self.assertIsNone(error)
        self.assertEqual(portfolio["cash"], 700.0)

        holding = StockHolding.query.filter_by(user_id=self.user.id, stock_id=self.stock.id).one()
        self.assertEqual(holding.quantity, 3)
        self.assertEqual(holding.total_cost, Decimal("300.00"))
        self.assertEqual(holding.average_cost, Decimal("100.00"))

        transaction = StockTransaction.query.filter_by(user_id=self.user.id, stock_id=self.stock.id).one()
        self.assertEqual(transaction.side, "BUY")
        self.assertEqual(transaction.quantity, 3)
        self.assertEqual(transaction.price, Decimal("100.00"))
        self.assertEqual(transaction.gross_amount, Decimal("300.00"))
        self.assertEqual(transaction.realized_profit, Decimal("0.00"))
        self.assertEqual(transaction.cash_balance_after, Decimal("700.00"))
        mock_apply_impact.assert_called_once_with(self.stock.id, "BUY", Decimal("300.00"))

    @patch("trading_service.apply_trade_impact")
    def test_second_buy_increases_quantity_total_cost_and_recalculates_average_cost(self, _mock_apply_impact):
        execute_stock_trade(self.user.id, self.stock.id, "BUY", 2)
        create_price(self.stock, "200.00", seconds=2)

        portfolio, error = execute_stock_trade(self.user.id, self.stock.id, "BUY", 1)

        self.assertIsNone(error)
        self.assertEqual(portfolio["cash"], 600.0)
        holding = StockHolding.query.filter_by(user_id=self.user.id, stock_id=self.stock.id).one()
        self.assertEqual(holding.quantity, 3)
        self.assertEqual(holding.total_cost, Decimal("400.00"))
        self.assertEqual(holding.average_cost, Decimal("133.33"))
        self.assertEqual(StockTransaction.query.filter_by(side="BUY").count(), 2)

    @patch("trading_service.apply_trade_impact")
    def test_buy_fails_when_cash_is_insufficient_and_does_not_create_transaction(self, mock_apply_impact):
        portfolio, error = execute_stock_trade(self.user.id, self.stock.id, "BUY", 11)

        self.assertIsNone(portfolio)
        self.assertEqual(error, "Trade failed: insufficient cash.")
        self.assertEqual(self.user.cash, Decimal("1000.00"))
        self.assertEqual(StockTransaction.query.count(), 0)
        holding = StockHolding.query.filter_by(user_id=self.user.id, stock_id=self.stock.id).one()
        self.assertEqual(holding.quantity, 0)
        self.assertEqual(holding.total_cost, Decimal("0.00"))
        mock_apply_impact.assert_not_called()

    def test_trade_fails_when_stock_does_not_exist(self):
        portfolio, error = execute_stock_trade(self.user.id, 999, "BUY", 1)

        self.assertIsNone(portfolio)
        self.assertEqual(error, "Stock not found.")
        self.assertEqual(StockTransaction.query.count(), 0)

    def test_trade_fails_when_stock_has_no_price(self):
        no_price_stock = create_stock(symbol="MSFT", name="Microsoft", base_price="200.00")

        portfolio, error = execute_stock_trade(self.user.id, no_price_stock.id, "BUY", 1)

        self.assertIsNone(portfolio)
        self.assertEqual(error, "No stock price available.")
        self.assertEqual(StockTransaction.query.count(), 0)

    def test_trade_fails_when_quantity_is_zero(self):
        portfolio, error = execute_stock_trade(self.user.id, self.stock.id, "BUY", 0)

        self.assertIsNone(portfolio)
        self.assertEqual(error, "Quantity must be an integer greater than 0.")
        self.assertEqual(StockTransaction.query.count(), 0)

    @patch("trading_service.apply_trade_impact")
    def test_sell_success_adds_cash_reduces_holding_and_creates_sell_transaction(self, _mock_apply_impact):
        execute_stock_trade(self.user.id, self.stock.id, "BUY", 4)
        create_price(self.stock, "120.00", seconds=2)

        portfolio, error = execute_stock_trade(self.user.id, self.stock.id, "SELL", 2)

        self.assertIsNone(error)
        self.assertEqual(portfolio["cash"], 840.0)
        holding = StockHolding.query.filter_by(user_id=self.user.id, stock_id=self.stock.id).one()
        self.assertEqual(holding.quantity, 2)
        self.assertEqual(holding.total_cost, Decimal("200.00"))

        sell_transaction = StockTransaction.query.filter_by(side="SELL").one()
        self.assertEqual(sell_transaction.quantity, 2)
        self.assertEqual(sell_transaction.price, Decimal("120.00"))
        self.assertEqual(sell_transaction.gross_amount, Decimal("240.00"))
        self.assertEqual(sell_transaction.cash_balance_after, Decimal("840.00"))

    @patch("trading_service.apply_trade_impact")
    def test_sell_all_removes_holding(self, _mock_apply_impact):
        execute_stock_trade(self.user.id, self.stock.id, "BUY", 1)

        portfolio, error = execute_stock_trade(self.user.id, self.stock.id, "SELL", 1)

        self.assertIsNone(error)
        self.assertEqual(portfolio["holdings"], [])
        self.assertIsNone(StockHolding.query.filter_by(user_id=self.user.id, stock_id=self.stock.id).first())

    def test_sell_fails_when_user_has_no_holding(self):
        portfolio, error = execute_stock_trade(self.user.id, self.stock.id, "SELL", 1)

        self.assertIsNone(portfolio)
        self.assertEqual(error, "Sell failed: insufficient AAPL holdings.")
        self.assertEqual(self.user.cash, Decimal("1000.00"))
        self.assertEqual(StockTransaction.query.count(), 0)

    @patch("trading_service.apply_trade_impact")
    def test_sell_fails_when_quantity_exceeds_holding_and_keeps_state(self, _mock_apply_impact):
        execute_stock_trade(self.user.id, self.stock.id, "BUY", 2)
        cash_before = self.user.cash
        holding = StockHolding.query.filter_by(user_id=self.user.id, stock_id=self.stock.id).one()

        portfolio, error = execute_stock_trade(self.user.id, self.stock.id, "SELL", 3)

        self.assertIsNone(portfolio)
        self.assertEqual(error, "Sell failed: insufficient AAPL holdings.")
        self.assertEqual(self.user.cash, cash_before)
        self.assertEqual(holding.quantity, 2)
        self.assertEqual(holding.total_cost, Decimal("200.00"))
        self.assertEqual(StockTransaction.query.filter_by(side="SELL").count(), 0)

    @patch("trading_service.apply_trade_impact")
    def test_realized_profit_is_sell_price_minus_average_cost_times_quantity(self, _mock_apply_impact):
        execute_stock_trade(self.user.id, self.stock.id, "BUY", 4)
        create_price(self.stock, "125.00", seconds=2)

        portfolio, error = execute_stock_trade(self.user.id, self.stock.id, "SELL", 3)

        self.assertIsNone(error)
        sell_transaction = StockTransaction.query.filter_by(side="SELL").one()
        self.assertEqual(sell_transaction.realized_profit, Decimal("75.00"))
        self.assertEqual(portfolio["realizedProfit"], 75.0)

    def test_payload_rejects_non_json_request(self):
        portfolio, error = execute_stock_trade_from_payload(self.user.id, "not-json")

        self.assertIsNone(portfolio)
        self.assertEqual(error, "Trade request must be a JSON object.")

    def test_payload_rejects_missing_stock(self):
        portfolio, error = execute_stock_trade_from_payload(self.user.id, {"side": "BUY", "quantity": 1})

        self.assertIsNone(portfolio)
        self.assertEqual(error, "Stock is required.")

    def test_payload_rejects_missing_quantity(self):
        portfolio, error = execute_stock_trade_from_payload(self.user.id, {"stockId": self.stock.id, "side": "BUY"})

        self.assertIsNone(portfolio)
        self.assertEqual(error, "Quantity is required.")


if __name__ == "__main__":
    unittest.main()
