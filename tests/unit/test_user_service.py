import unittest
from datetime import datetime, timedelta

from models import db
from tests.unit.test_auth_forms import create_auth_test_app, create_user
from user_service import get_users_paginated


class UserServiceTests(unittest.TestCase):
    def setUp(self):
        self.app = create_auth_test_app()
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def create_users(self, count):
        base_time = datetime(2026, 5, 1, 10, 0, 0)
        users = []

        for index in range(count):
            user = create_user(
                username=f"user{index + 1}",
                email=f"user{index + 1}@example.com",
            )
            user.created_at = base_time + timedelta(minutes=index)
            users.append(user)

        db.session.commit()
        return users

    def test_user_pagination_returns_requested_number_of_users_per_page(self):
        self.create_users(6)

        page_one = get_users_paginated(page=1, per_page=2)

        self.assertEqual(len(page_one["users"]), 2)
        self.assertEqual([user["username"] for user in page_one["users"]], ["user1", "user2"])
        self.assertEqual(page_one["page"], 1)

    def test_has_next_is_true_when_more_users_exist_after_current_page(self):
        self.create_users(6)

        page_one = get_users_paginated(page=1, per_page=5)

        self.assertTrue(page_one["has_next"])
        self.assertFalse(page_one["has_prev"])

    def test_has_prev_is_true_on_second_page(self):
        self.create_users(6)

        page_two = get_users_paginated(page=2, per_page=5)

        self.assertTrue(page_two["has_prev"])
        self.assertFalse(page_two["has_next"])
        self.assertEqual(len(page_two["users"]), 1)
        self.assertEqual(page_two["users"][0]["username"], "user6")

    def test_join_time_is_string_ready_for_template_display(self):
        self.create_users(1)

        result = get_users_paginated(page=1, per_page=5)

        join_time = result["users"][0]["joinTime"]
        self.assertIsInstance(join_time, str)
        self.assertEqual(join_time, "01 May 2026, 10:00 AM")

    def test_user_search_filters_by_username_across_database(self):
        self.create_users(12)

        result = get_users_paginated(page=1, per_page=5, search="user12")

        self.assertEqual([user["username"] for user in result["users"]], ["user12"])
        self.assertFalse(result["has_next"])
        self.assertEqual(result["search"], "user12")

    def test_user_search_filters_by_user_id(self):
        users = self.create_users(3)

        result = get_users_paginated(page=1, per_page=5, search=str(users[1].id))

        self.assertEqual([user["id"] for user in result["users"]], [users[1].id])

    def test_user_dict_does_not_return_email(self):
        self.create_users(1)

        result = get_users_paginated(page=1, per_page=5)

        self.assertNotIn("email", result["users"][0])

    def test_user_dict_does_not_return_password_hash(self):
        self.create_users(1)

        result = get_users_paginated(page=1, per_page=5)

        self.assertNotIn("password_hash", result["users"][0])
        self.assertNotIn("passwordHash", result["users"][0])


if __name__ == "__main__":
    unittest.main()
