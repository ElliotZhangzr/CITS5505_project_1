import base64
import importlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from models import User, db
from tests.unit.test_auth_forms import create_auth_test_app, create_user


with patch("stock_simulator.load_stock_configs"):
    app_module = importlib.import_module("app")


class ProfileLogicTests(unittest.TestCase):
    def setUp(self):
        self.app = create_auth_test_app()
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.user = create_user(username="profile", email="profile@example.com")

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def call_profile_json_route(self, route_func, path, payload):
        with self.app.test_request_context(path, method="POST", json=payload):
            with patch.object(app_module, "current_user", self.user):
                return route_func.__wrapped__()

    def response_json_and_status(self, response):
        if isinstance(response, tuple):
            flask_response, status_code = response
            return flask_response.get_json(), status_code
        return response.get_json(), response.status_code

    def test_update_bio_saves_bio_and_returns_ok_true(self):
        response = self.call_profile_json_route(
            app_module.update_bio,
            "/profile/update_bio",
            {"bio": "I like long term investing."},
        )
        data, status_code = self.response_json_and_status(response)
        updated_user = User.query.get(self.user.id)

        self.assertEqual(status_code, 200)
        self.assertEqual(data, {"ok": True})
        self.assertEqual(updated_user.bio, "I like long term investing.")

    def test_update_bio_rejects_more_than_200_characters(self):
        response = self.call_profile_json_route(
            app_module.update_bio,
            "/profile/update_bio",
            {"bio": "x" * 201},
        )
        data, status_code = self.response_json_and_status(response)

        self.assertEqual(status_code, 400)
        self.assertEqual(data, {"ok": False, "error": "Bio must be 200 characters or less."})

    def test_update_hide_holdings_true_sets_database_value_true(self):
        response = self.call_profile_json_route(
            app_module.update_hide_holdings,
            "/profile/update_hide_holdings",
            {"hide_holdings": True},
        )
        data, status_code = self.response_json_and_status(response)
        updated_user = User.query.get(self.user.id)

        self.assertEqual(status_code, 200)
        self.assertEqual(data, {"ok": True})
        self.assertTrue(updated_user.hide_holdings)

    def test_update_hide_holdings_false_sets_database_value_false(self):
        self.user.hide_holdings = True
        db.session.commit()

        response = self.call_profile_json_route(
            app_module.update_hide_holdings,
            "/profile/update_hide_holdings",
            {"hide_holdings": False},
        )
        data, status_code = self.response_json_and_status(response)
        updated_user = User.query.get(self.user.id)

        self.assertEqual(status_code, 200)
        self.assertEqual(data, {"ok": True})
        self.assertFalse(updated_user.hide_holdings)

    def test_update_avatar_accepts_png_data_saves_user_png_and_database_url(self):
        png_bytes = b"\x89PNG\r\n\x1a\nunit-test-image"
        avatar_data = "data:image/png;base64," + base64.b64encode(png_bytes).decode("ascii")

        with tempfile.TemporaryDirectory() as temp_dir:
            upload_dir = Path(temp_dir) / "avatars"

            with patch.object(app_module, "AVATAR_UPLOAD_DIR", upload_dir):
                response = self.call_profile_json_route(
                    app_module.update_avatar,
                    "/profile/update_avatar",
                    {"avatar_data": avatar_data},
                )

            data, status_code = self.response_json_and_status(response)
            avatar_file = upload_dir / f"user_{self.user.id}.png"
            updated_user = User.query.get(self.user.id)

            self.assertEqual(status_code, 200)
            self.assertTrue(data["ok"])
            self.assertEqual(data["avatar_url"], f"/static/uploads/avatars/user_{self.user.id}.png")
            self.assertEqual(updated_user.avatar_url, f"/static/uploads/avatars/user_{self.user.id}.png")
            self.assertTrue(avatar_file.exists())
            self.assertEqual(avatar_file.read_bytes(), png_bytes)

    def test_update_avatar_rejects_empty_avatar_data(self):
        response = self.call_profile_json_route(
            app_module.update_avatar,
            "/profile/update_avatar",
            {"avatar_data": ""},
        )
        data, status_code = self.response_json_and_status(response)

        self.assertEqual(status_code, 400)
        self.assertEqual(data, {"ok": False, "error": "Avatar image data is required."})

    def test_update_avatar_rejects_non_png_image_data(self):
        jpeg_data = "data:image/jpeg;base64," + base64.b64encode(b"jpeg-data").decode("ascii")

        response = self.call_profile_json_route(
            app_module.update_avatar,
            "/profile/update_avatar",
            {"avatar_data": jpeg_data},
        )
        data, status_code = self.response_json_and_status(response)

        self.assertEqual(status_code, 400)
        self.assertEqual(data, {"ok": False, "error": "Avatar must be saved as PNG."})

    def test_update_avatar_rejects_invalid_base64_encoding(self):
        response = self.call_profile_json_route(
            app_module.update_avatar,
            "/profile/update_avatar",
            {"avatar_data": "data:image/png;base64,not-valid-base64"},
        )
        data, status_code = self.response_json_and_status(response)

        self.assertEqual(status_code, 400)
        self.assertEqual(data, {"ok": False, "error": "Invalid avatar encoding."})


if __name__ == "__main__":
    unittest.main()
