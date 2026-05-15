import importlib
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from flask import get_flashed_messages


with patch("stock_simulator.load_stock_configs"):
    app_module = importlib.import_module("app")


class AdminLogicTests(unittest.TestCase):
    def test_admin_required_allows_admin_user_to_call_view(self):
        admin_user = SimpleNamespace(is_authenticated=True, is_admin=True)

        def protected_view():
            return "admin content"

        wrapped_view = app_module.admin_required(protected_view)

        with app_module.app.test_request_context("/admin"):
            with patch.object(app_module, "current_user", admin_user):
                result = wrapped_view()

        self.assertEqual(result, "admin content")

    def test_admin_required_redirects_normal_user_to_dashboard(self):
        normal_user = SimpleNamespace(is_authenticated=True, is_admin=False)

        def protected_view():
            return "admin content"

        wrapped_view = app_module.admin_required(protected_view)

        with app_module.app.test_request_context("/admin"):
            with patch.object(app_module, "current_user", normal_user):
                response = wrapped_view()
                messages = get_flashed_messages()

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith("/dashboard"))
        self.assertIn("Admin access required.", messages)

    def test_admin_required_redirects_unauthenticated_user_to_login(self):
        anonymous_user = SimpleNamespace(is_authenticated=False, is_admin=False)

        def protected_view():
            return "admin content"

        wrapped_view = app_module.admin_required(protected_view)

        with app_module.app.test_request_context("/admin"):
            with patch.object(app_module, "current_user", anonymous_user):
                response = wrapped_view()

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith("/login"))

    def test_build_admin_user_rows_labels_admin_and_normal_users(self):
        current_user = SimpleNamespace(id=1)
        admin = SimpleNamespace(id=1, is_admin=True)
        normal = SimpleNamespace(id=2, is_admin=False)

        with patch.object(app_module, "current_user", current_user):
            rows = app_module.build_admin_user_rows([admin, normal])

        self.assertEqual(rows[0]["role_label"], "Admin")
        self.assertEqual(rows[0]["action_label"], "Remove Admin")
        self.assertEqual(rows[1]["role_label"], "Normal User")
        self.assertEqual(rows[1]["action_label"], "Make Admin")

    def test_build_admin_user_rows_marks_current_user(self):
        current_user = SimpleNamespace(id=10)
        current = SimpleNamespace(id=10, is_admin=True)
        other = SimpleNamespace(id=20, is_admin=False)

        with patch.object(app_module, "current_user", current_user):
            rows = app_module.build_admin_user_rows([current, other])

        self.assertTrue(rows[0]["is_current_user"])
        self.assertFalse(rows[1]["is_current_user"])

    def test_build_admin_user_rows_sets_other_user_action_labels(self):
        current_user = SimpleNamespace(id=1)
        other_admin = SimpleNamespace(id=2, is_admin=True)
        other_normal = SimpleNamespace(id=3, is_admin=False)

        with patch.object(app_module, "current_user", current_user):
            rows = app_module.build_admin_user_rows([other_admin, other_normal])

        self.assertFalse(rows[0]["is_current_user"])
        self.assertEqual(rows[0]["action_label"], "Remove Admin")
        self.assertFalse(rows[1]["is_current_user"])
        self.assertEqual(rows[1]["action_label"], "Make Admin")

    def test_toggle_admin_flips_other_user_admin_status(self):
        current_user = SimpleNamespace(id=1, is_authenticated=True, is_admin=True)
        target_user = SimpleNamespace(id=2, is_admin=False)
        fake_query = SimpleNamespace(get_or_404=Mock(return_value=target_user))
        toggle_admin_business_logic = app_module.toggle_admin_role.__wrapped__.__wrapped__

        with app_module.app.test_request_context("/admin/users/2/toggle-admin", method="POST"):
            with patch.object(app_module, "current_user", current_user), \
                    patch.object(app_module.User, "query", fake_query), \
                    patch.object(app_module.db.session, "commit") as mock_commit:
                response = toggle_admin_business_logic(2)
                messages = get_flashed_messages()

        self.assertTrue(target_user.is_admin)
        fake_query.get_or_404.assert_called_once_with(2)
        mock_commit.assert_called_once()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith("/admin/users"))
        self.assertIn("User role updated successfully.", messages)

    def test_toggle_admin_does_not_allow_current_user_to_change_own_admin_role(self):
        current_user = SimpleNamespace(id=1, is_authenticated=True, is_admin=True)
        fake_query = SimpleNamespace(get_or_404=Mock())
        toggle_admin_business_logic = app_module.toggle_admin_role.__wrapped__.__wrapped__

        with app_module.app.test_request_context("/admin/users/1/toggle-admin", method="POST"):
            with patch.object(app_module, "current_user", current_user), \
                    patch.object(app_module.User, "query", fake_query), \
                    patch.object(app_module.db.session, "commit") as mock_commit:
                response = toggle_admin_business_logic(1)
                messages = get_flashed_messages()

        fake_query.get_or_404.assert_not_called()
        mock_commit.assert_not_called()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith("/admin/users"))
        self.assertIn("You cannot change your own admin role.", messages)


if __name__ == "__main__":
    unittest.main()
