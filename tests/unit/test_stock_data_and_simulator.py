import unittest
from decimal import Decimal
from unittest.mock import patch

from models import db
from stock_data import get_stock_data
from stock_simulator import (
    MAX_PRICE_RETURN,
    apply_trade_impact,
    generate_next_price,
    positive_price,
)
from tests.unit.test_auth_forms import create_auth_test_app
from tests.unit.test_trading_service import create_price, create_stock


def simulator_config(**overrides):
    config = {
        "id": 1,
        "symbol": "AAPL",
        "base_price": Decimal("100.00"),
        "volatility": Decimal("0.010000"),
        "drift": Decimal("0.000000"),
        "mean_reversion_factor": Decimal("0.000000"),
        "liquidity": Decimal("100000.00"),
        "trade_impact_factor": Decimal("0.500000"),
        "min_price": Decimal("1.00"),
    }
    config.update(overrides)
    return config


def empty_state():
    return {
        "buy_pressure": Decimal("0"),
        "sell_pressure": Decimal("0"),
        "pending_buy_pressure": Decimal("0"),
        "pending_sell_pressure": Decimal("0"),
    }


class StockDataAndSimulatorTests(unittest.TestCase):
    def setUp(self):
        self.app = create_auth_test_app()
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_get_stock_data_returns_stocks_and_market_data(self):
        stock = create_stock(symbol="AAPL", name="Apple Inc.")
        create_price(stock, "100.00", seconds=1)

        data = get_stock_data()

        self.assertIn("stocks", data)
        self.assertIn("marketData", data)
        self.assertEqual(data["stocks"][0]["symbol"], "AAPL")
        self.assertEqual(data["stocks"][0]["name"], "Apple Inc.")
        self.assertEqual(data["marketData"]["AAPL"], [100.0])

    def test_get_stock_data_returns_price_history_from_old_to_new(self):
        stock = create_stock(symbol="AAPL", name="Apple Inc.")
        create_price(stock, "100.00", seconds=1)
        create_price(stock, "101.00", seconds=2)
        create_price(stock, "102.00", seconds=3)

        data = get_stock_data()

        self.assertEqual(data["marketData"]["AAPL"], [100.0, 101.0, 102.0])

    def test_get_stock_data_limit_returns_only_requested_number_of_latest_prices(self):
        stock = create_stock(symbol="AAPL", name="Apple Inc.")
        create_price(stock, "100.00", seconds=1)
        create_price(stock, "101.00", seconds=2)
        create_price(stock, "102.00", seconds=3)

        data = get_stock_data(limit=2)

        self.assertEqual(data["marketData"]["AAPL"], [101.0, 102.0])

    def test_positive_price_uses_fallback_when_value_is_not_positive(self):
        self.assertEqual(positive_price("0", "25.00"), Decimal("25.00"))
        self.assertEqual(positive_price("-5", "25.00"), Decimal("25.00"))

    def test_positive_price_returns_one_when_value_and_fallback_are_not_positive(self):
        self.assertEqual(positive_price("0", "0"), Decimal("1.00"))
        self.assertEqual(positive_price("-5", "-10"), Decimal("1.00"))

    @patch("stock_simulator.generate_pressure_trend", return_value=Decimal("0"))
    @patch("stock_simulator.random.gauss", return_value=0)
    def test_generate_next_price_returns_decimal_with_two_places(self, _mock_gauss, _mock_pressure):
        price = generate_next_price(Decimal("100.00"), simulator_config(), empty_state())

        self.assertIsInstance(price, Decimal)
        self.assertEqual(price, Decimal("100.00"))
        self.assertEqual(price.as_tuple().exponent, -2)

    @patch("stock_simulator.generate_pressure_trend", return_value=Decimal("0"))
    @patch("stock_simulator.random.gauss", return_value=10)
    def test_generate_next_price_caps_single_step_increase_at_fifteen_percent(self, _mock_gauss, _mock_pressure):
        price = generate_next_price(Decimal("100.00"), simulator_config(volatility=Decimal("1.000000")), empty_state())

        self.assertEqual(MAX_PRICE_RETURN, Decimal("0.15"))
        self.assertEqual(price, Decimal("115.00"))

    @patch("stock_simulator.generate_pressure_trend", return_value=Decimal("0"))
    @patch("stock_simulator.random.gauss", return_value=-10)
    def test_generate_next_price_does_not_go_below_minimum_price(self, _mock_gauss, _mock_pressure):
        price = generate_next_price(
            Decimal("10.00"),
            simulator_config(volatility=Decimal("1.000000"), min_price=Decimal("9.00")),
            empty_state(),
        )

        self.assertEqual(price, Decimal("9.00"))

    @patch("stock_simulator.save_simulation_state")
    @patch("stock_simulator.get_latest_price", return_value=None)
    @patch("stock_simulator.get_simulation_state")
    @patch("stock_simulator.get_stock_config")
    def test_apply_trade_impact_buy_adds_pending_buy_pressure(
        self,
        mock_config,
        mock_state,
        _mock_latest_price,
        mock_save_state,
    ):
        state = empty_state()
        mock_config.return_value = simulator_config()
        mock_state.return_value = state

        impact = apply_trade_impact(1, "BUY", Decimal("1000.00"))

        self.assertGreater(impact, Decimal("0"))
        self.assertEqual(state["pending_buy_pressure"], impact)
        self.assertEqual(state["pending_sell_pressure"], Decimal("0"))
        mock_save_state.assert_called_once_with(1, state)

    @patch("stock_simulator.save_simulation_state")
    @patch("stock_simulator.get_latest_price", return_value=None)
    @patch("stock_simulator.get_simulation_state")
    @patch("stock_simulator.get_stock_config")
    def test_apply_trade_impact_sell_adds_pending_sell_pressure(
        self,
        mock_config,
        mock_state,
        _mock_latest_price,
        mock_save_state,
    ):
        state = empty_state()
        mock_config.return_value = simulator_config()
        mock_state.return_value = state

        impact = apply_trade_impact(1, "SELL", Decimal("1000.00"))

        self.assertGreater(impact, Decimal("0"))
        self.assertEqual(state["pending_buy_pressure"], Decimal("0"))
        self.assertEqual(state["pending_sell_pressure"], impact)
        mock_save_state.assert_called_once_with(1, state)

    @patch("stock_simulator.get_stock_config", return_value=None)
    def test_apply_trade_impact_returns_zero_when_stock_config_is_missing(self, _mock_config):
        impact = apply_trade_impact(1, "BUY", Decimal("1000.00"))

        self.assertEqual(impact, Decimal("0"))


if __name__ == "__main__":
    unittest.main()
