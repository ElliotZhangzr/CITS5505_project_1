import json
import unittest
from datetime import datetime
from unittest.mock import patch

from werkzeug.security import check_password_hash

from models import User, db
from password_reset_service import (
    RESET_CODE_MAX_ATTEMPTS,
    RESET_CODE_TTL_SECONDS,
    confirm_password_reset,
    hash_value,
    normalize_email,
    request_password_reset,
    reset_code_key,
)
from tests.unit.test_auth_forms import create_auth_test_app, create_user


GENERIC_MESSAGE = "If this email exists, a verification code has been sent."


class FakeRedis:
    def __init__(self):
        self.values = {}
        self.ttls = {}

    def get(self, key):
        return self.values.get(key)

    def set(self, key, value, ex=None):
        self.values[key] = value
        self.ttls[key] = ex

    def delete(self, key):
        self.values.pop(key, None)
        self.ttls.pop(key, None)

    def ttl(self, key):
        if key not in self.values:
            return -2
        return self.ttls.get(key) or -1


class PasswordResetServiceTests(unittest.TestCase):
    def setUp(self):
        self.app = create_auth_test_app()
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.redis = FakeRedis()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def redis_json(self, email):
        raw_value = self.redis.values[reset_code_key(email)]
        return json.loads(raw_value)

    def save_reset_data(self, email, code="ABC123", attempts=0, valid=True):
        key = reset_code_key(email)
        data = {
            "code_hash": hash_value(code.upper()),
            "sent_at": datetime.utcnow().isoformat(),
            "attempts": attempts,
            "valid": valid,
        }
        self.redis.set(key, json.dumps(data), ex=RESET_CODE_TTL_SECONDS)
        return data

    def test_normalize_email_strips_spaces_and_lowercases(self):
        self.assertEqual(normalize_email(" Test@Email.COM "), "test@email.com")

    @patch("redis_store.get_redis_client")
    @patch("password_reset_service.get_redis_client")
    @patch("password_reset_service.generate_reset_code", return_value="AB123C")
    @patch("password_reset_service.send_password_reset_email")
    def test_request_password_reset_saves_valid_code_for_existing_email(
        self,
        mock_send_email,
        _mock_code,
        service_redis,
        store_redis,
    ):
        create_user(email="test@email.com")
        service_redis.return_value = self.redis
        store_redis.return_value = self.redis

        success, message = request_password_reset(" Test@Email.COM ")

        self.assertTrue(success)
        self.assertEqual(message, GENERIC_MESSAGE)
        reset_data = self.redis_json("test@email.com")
        self.assertEqual(reset_data["code_hash"], hash_value("AB123C"))
        self.assertEqual(reset_data["attempts"], 0)
        self.assertTrue(reset_data["valid"])
        self.assertEqual(self.redis.ttls[reset_code_key("test@email.com")], RESET_CODE_TTL_SECONDS)
        mock_send_email.assert_called_once_with("test@email.com", "AB123C")

    @patch("redis_store.get_redis_client")
    @patch("password_reset_service.get_redis_client")
    @patch("password_reset_service.send_password_reset_email")
    def test_request_password_reset_for_missing_email_uses_generic_message_and_invalid_code(
        self,
        mock_send_email,
        service_redis,
        store_redis,
    ):
        service_redis.return_value = self.redis
        store_redis.return_value = self.redis

        success, message = request_password_reset("missing@example.com")

        self.assertTrue(success)
        self.assertEqual(message, GENERIC_MESSAGE)
        reset_data = self.redis_json("missing@example.com")
        self.assertEqual(reset_data["code_hash"], "")
        self.assertEqual(reset_data["attempts"], 0)
        self.assertFalse(reset_data["valid"])
        mock_send_email.assert_not_called()

    @patch("redis_store.get_redis_client")
    @patch("password_reset_service.get_redis_client")
    @patch("password_reset_service.send_password_reset_email")
    def test_request_password_reset_too_soon_returns_wait_message(
        self,
        mock_send_email,
        service_redis,
        store_redis,
    ):
        create_user(email="test@email.com")
        service_redis.return_value = self.redis
        store_redis.return_value = self.redis
        self.save_reset_data("test@email.com")

        success, message = request_password_reset("test@email.com")

        self.assertFalse(success)
        self.assertEqual(message, "Please wait before requesting another verification code.")
        mock_send_email.assert_not_called()

    @patch("redis_store.get_redis_client")
    @patch("password_reset_service.get_redis_client")
    def test_confirm_password_reset_with_correct_code_hashes_new_password_and_clears_redis(
        self,
        service_redis,
        store_redis,
    ):
        user = create_user(email="test@email.com", password="OldPass1")
        old_hash = user.password_hash
        service_redis.return_value = self.redis
        store_redis.return_value = self.redis
        self.save_reset_data("test@email.com", code="ABC123")

        success, message = confirm_password_reset("test@email.com", "abc123", "NewPass1", "NewPass1")

        self.assertTrue(success)
        self.assertEqual(message, "Password reset successfully. Please log in.")
        updated_user = User.query.filter_by(email="test@email.com").one()
        self.assertNotEqual(updated_user.password_hash, old_hash)
        self.assertTrue(check_password_hash(updated_user.password_hash, "NewPass1"))
        self.assertNotIn(reset_code_key("test@email.com"), self.redis.values)

    @patch("redis_store.get_redis_client")
    @patch("password_reset_service.get_redis_client")
    def test_confirm_password_reset_with_wrong_code_increments_attempts_and_keeps_password(
        self,
        service_redis,
        store_redis,
    ):
        user = create_user(email="test@email.com", password="OldPass1")
        old_hash = user.password_hash
        service_redis.return_value = self.redis
        store_redis.return_value = self.redis
        self.save_reset_data("test@email.com", code="ABC123")

        success, message = confirm_password_reset("test@email.com", "WRONG1", "NewPass1", "NewPass1")

        self.assertFalse(success)
        self.assertEqual(message, "Verification code is incorrect.")
        reset_data = self.redis_json("test@email.com")
        self.assertEqual(reset_data["attempts"], 1)
        self.assertEqual(User.query.filter_by(email="test@email.com").one().password_hash, old_hash)

    @patch("redis_store.get_redis_client")
    @patch("password_reset_service.get_redis_client")
    def test_confirm_password_reset_clears_code_after_too_many_attempts(self, service_redis, store_redis):
        create_user(email="test@email.com")
        service_redis.return_value = self.redis
        store_redis.return_value = self.redis
        self.save_reset_data("test@email.com", code="ABC123", attempts=RESET_CODE_MAX_ATTEMPTS)

        success, message = confirm_password_reset("test@email.com", "ABC123", "NewPass1", "NewPass1")

        self.assertFalse(success)
        self.assertEqual(message, "Too many incorrect attempts. Please request a new code.")
        self.assertNotIn(reset_code_key("test@email.com"), self.redis.values)

    def test_confirm_password_reset_rejects_mismatched_passwords(self):
        success, message = confirm_password_reset("test@email.com", "ABC123", "NewPass1", "Different1")

        self.assertFalse(success)
        self.assertEqual(message, "Passwords do not match.")

    def test_confirm_password_reset_rejects_short_password(self):
        success, message = confirm_password_reset("test@email.com", "ABC123", "short", "short")

        self.assertFalse(success)
        self.assertEqual(message, "Password must be at least 6 characters.")


if __name__ == "__main__":
    unittest.main()
