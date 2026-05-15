import importlib
import unittest
from decimal import Decimal
from unittest.mock import Mock, patch

from flask import get_flashed_messages
from werkzeug.security import check_password_hash

from models import StockHolding, StockTransaction, User, db
from tests.unit.test_auth_forms import create_auth_test_app, create_user
from tests.unit.test_trading_service import create_stock


with patch("stock_simulator.load_stock_configs"):
    app_module = importlib.import_module("app")


class DeleteAccountTests(unittest.TestCase):
    def setUp(self):
        self.app = create_auth_test_app()
        self.app.add_url_rule("/profile", "profile", lambda: "profile")
        self.app.add_url_rule("/register", "register", lambda: "register")
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.user = create_user(username="delete_me", email="delete@example.com", password="Password1")
        self.stock = create_stock()
        self.holding = StockHolding(
            user_id=self.user.id,
            stock_id=self.stock.id,
            quantity=5,
            average_cost=Decimal("100.00"),
            total_cost=Decimal("500.00"),
        )
        self.transaction = StockTransaction(
            user_id=self.user.id,
            stock_id=self.stock.id,
            side="BUY",
            quantity=5,
            price=Decimal("100.00"),
            gross_amount=Decimal("500.00"),
            realized_profit=Decimal("0.00"),
            cash_balance_after=Decimal("9500.00"),
        )
        db.session.add_all([self.holding, self.transaction])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def call_delete_account(self, password):
        delete_account_business_logic = app_module.delete_account.__wrapped__
        with self.app.test_request_context("/delete_account", method="POST", data={"password": password}):
            with patch.object(app_module, "current_user", self.user), \
                    patch.object(app_module, "logout_user") as mock_logout:
                response = delete_account_business_logic()
                messages = get_flashed_messages()
        return response, messages, mock_logout

    def test_correct_password_deletes_user_holding_and_transaction(self):
        user_id = self.user.id
        holding_id = self.holding.id
        transaction_id = self.transaction.id

        response, messages, mock_logout = self.call_delete_account("Password1")

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith("/register"))
        self.assertEqual(messages, [])
        mock_logout.assert_called_once()
        self.assertIsNone(db.session.get(User, user_id))
        self.assertIsNone(db.session.get(StockHolding, holding_id))
        self.assertIsNone(db.session.get(StockTransaction, transaction_id))

    def test_wrong_password_keeps_user_and_returns_password_confirmation_failed(self):
        user_id = self.user.id
        holding_id = self.holding.id
        transaction_id = self.transaction.id
        password_hash_before = self.user.password_hash

        response, messages, mock_logout = self.call_delete_account("WrongPass1")

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith("/profile"))
        self.assertIn("Password confirmation failed.", messages)
        mock_logout.assert_not_called()

        saved_user = db.session.get(User, user_id)
        self.assertIsNotNone(saved_user)
        self.assertEqual(saved_user.password_hash, password_hash_before)
        self.assertTrue(check_password_hash(saved_user.password_hash, "Password1"))
        self.assertIsNotNone(db.session.get(StockHolding, holding_id))
        self.assertIsNotNone(db.session.get(StockTransaction, transaction_id))

    def test_deleted_account_cannot_log_in_again(self):
        user_id = self.user.id
        self.call_delete_account("Password1")
        self.assertIsNone(db.session.get(User, user_id))

        with self.app.test_request_context(
            "/login",
            method="POST",
            data={"username": "delete_me", "password": "Password1"},
        ):
            with patch.object(app_module, "render_template", return_value="login page") as mock_render, \
                    patch.object(app_module, "login_user") as mock_login:
                result = app_module.login()
                messages = get_flashed_messages()

        self.assertEqual(result, "login page")
        mock_render.assert_called_once()
        mock_login.assert_not_called()
        self.assertIn("Username or password incorrect.", messages)


if __name__ == "__main__":
    unittest.main()
