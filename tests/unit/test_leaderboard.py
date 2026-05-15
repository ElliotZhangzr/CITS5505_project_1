import unittest
from decimal import Decimal
from unittest.mock import patch

from leaderboard import calculate_user_metrics, get_leaderboard_context
from models import db
from tests.unit.test_auth_forms import create_auth_test_app, create_user


class LeaderboardTests(unittest.TestCase):
    def setUp(self):
        self.app = create_auth_test_app()
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def create_rank_users(self):
        low = create_user(username="low", email="low@example.com")
        middle = create_user(username="middle", email="middle@example.com")
        high = create_user(username="high", email="high@example.com")
        return low, middle, high

    def portfolio_map(self, users, values):
        return {
            users[index].id: {
                "cash": values[index]["cash"],
                "totalAssets": values[index]["totalAssets"],
                "totalProfit": values[index]["totalProfit"],
            }
            for index in range(len(users))
        }

    def mock_build_portfolio(self, mapping):
        return patch("leaderboard.build_portfolio", side_effect=lambda user_id: mapping[user_id])

    def test_cash_ranking_orders_highest_cash_first(self):
        users = self.create_rank_users()
        mapping = self.portfolio_map(users, [
            {"cash": 1000.0, "totalAssets": 1000.0, "totalProfit": 0.0},
            {"cash": 5000.0, "totalAssets": 5000.0, "totalProfit": 0.0},
            {"cash": 9000.0, "totalAssets": 9000.0, "totalProfit": 0.0},
        ])

        with self.mock_build_portfolio(mapping):
            context = get_leaderboard_context("cash", "low")

        self.assertEqual([user["username"] for user in context["users"]], ["high", "middle", "low"])
        self.assertEqual(context["title"], "Cash Ranking")
        self.assertEqual(context["value_label"], "Cash")

    def test_assets_ranking_orders_highest_total_assets_first(self):
        users = self.create_rank_users()
        mapping = self.portfolio_map(users, [
            {"cash": 9000.0, "totalAssets": 15000.0, "totalProfit": 0.0},
            {"cash": 5000.0, "totalAssets": 30000.0, "totalProfit": 0.0},
            {"cash": 20000.0, "totalAssets": 20000.0, "totalProfit": 0.0},
        ])

        with self.mock_build_portfolio(mapping):
            context = get_leaderboard_context("assets", "low")

        self.assertEqual([user["username"] for user in context["users"]], ["middle", "high", "low"])
        self.assertEqual(context["title"], "Total Assets Ranking")
        self.assertEqual(context["value_label"], "Total Assets")

    def test_profit_ranking_orders_highest_total_profit_first(self):
        users = self.create_rank_users()
        mapping = self.portfolio_map(users, [
            {"cash": 10000.0, "totalAssets": 10000.0, "totalProfit": -50.0},
            {"cash": 10000.0, "totalAssets": 10000.0, "totalProfit": 300.0},
            {"cash": 10000.0, "totalAssets": 10000.0, "totalProfit": 100.0},
        ])

        with self.mock_build_portfolio(mapping):
            context = get_leaderboard_context("profit", "low")

        self.assertEqual([user["username"] for user in context["users"]], ["middle", "high", "low"])
        self.assertEqual(context["title"], "Profit Ranking")
        self.assertEqual(context["value_label"], "Total Profit")

    def test_return_ranking_orders_highest_return_percent_first(self):
        users = self.create_rank_users()
        mapping = self.portfolio_map(users, [
            {"cash": 10000.0, "totalAssets": 9000.0, "totalProfit": 0.0},
            {"cash": 10000.0, "totalAssets": 11000.0, "totalProfit": 0.0},
            {"cash": 10000.0, "totalAssets": 13000.0, "totalProfit": 0.0},
        ])

        with self.mock_build_portfolio(mapping):
            context = get_leaderboard_context("return", "low")

        self.assertEqual([user["username"] for user in context["users"]], ["high", "middle", "low"])
        self.assertEqual(context["title"], "Return Percentage Ranking")
        self.assertEqual(context["value_label"], "Return %")

    def test_return_percent_uses_initial_cash_baseline_formula(self):
        user = create_user(username="winner", email="winner@example.com")
        mapping = {
            user.id: {
                "cash": 12000.0,
                "totalAssets": 12500.0,
                "totalProfit": 500.0,
            }
        }

        with self.mock_build_portfolio(mapping):
            metrics = calculate_user_metrics(user)

        self.assertEqual(metrics["total_assets"], 12500.0)
        self.assertEqual(metrics["returnPercent"], 25.0)

    def test_rank_values_start_at_one_after_sorting(self):
        users = self.create_rank_users()
        mapping = self.portfolio_map(users, [
            {"cash": 1000.0, "totalAssets": 1000.0, "totalProfit": 0.0},
            {"cash": 3000.0, "totalAssets": 3000.0, "totalProfit": 0.0},
            {"cash": 2000.0, "totalAssets": 2000.0, "totalProfit": 0.0},
        ])

        with self.mock_build_portfolio(mapping):
            context = get_leaderboard_context("cash", "low")

        self.assertEqual(context["users"][0]["username"], "middle")
        self.assertEqual(context["users"][0]["rank"], 1)
        self.assertEqual(context["users"][1]["rank"], 2)
        self.assertEqual(context["users"][2]["rank"], 3)

    def test_empty_user_table_returns_empty_users_without_error(self):
        context = get_leaderboard_context("cash", "missing")

        self.assertEqual(context["users"], [])
        self.assertEqual(context["title"], "Cash Ranking")
        self.assertEqual(context["ranking_type"], "cash")
        self.assertEqual(context["current_username"], "missing")

    def test_leaderboard_output_does_not_include_password_hash(self):
        user = create_user(username="safe", email="safe@example.com")
        user.cash = Decimal("12345.00")
        db.session.commit()
        mapping = {
            user.id: {
                "cash": 12345.0,
                "totalAssets": 12345.0,
                "totalProfit": 0.0,
            }
        }

        with self.mock_build_portfolio(mapping):
            context = get_leaderboard_context("cash", "safe")

        result = context["users"][0]
        self.assertNotIn("password_hash", result)
        self.assertNotIn("passwordHash", result)


if __name__ == "__main__":
    unittest.main()
