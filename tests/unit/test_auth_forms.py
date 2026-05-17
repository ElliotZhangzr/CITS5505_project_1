import unittest
from decimal import Decimal

from flask import Flask
from flask_migrate import Migrate, upgrade
from werkzeug.security import check_password_hash, generate_password_hash

from forms import LoginForm, RegisterForm, ResetPasswordForm
from models import User, db


def create_auth_test_app():
    app = Flask(__name__)
    app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret",
        WTF_CSRF_ENABLED=False,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    db.init_app(app)
    Migrate(app, db)

    with app.app_context():
        upgrade()

    return app


def create_user(username="existing", email="existing@example.com", password="Password1"):
    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        cash=Decimal("10000.00"),
    )
    db.session.add(user)
    db.session.commit()
    return user


class AuthFormsTests(unittest.TestCase):
    def setUp(self):
        self.app = create_auth_test_app()
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def build_register_form(self, username="newuser", email="new@example.com", password="Password1"):
        with self.app.test_request_context(method="POST"):
            return RegisterForm(username=username, email=email, password=password)

    def build_reset_form(
        self,
        email="new@example.com",
        code="ABC123",
        new_password="Password1",
        confirm_password="Password1",
    ):
        with self.app.test_request_context(method="POST"):
            return ResetPasswordForm(
                email=email,
                code=code,
                new_password=new_password,
                confirm_password=confirm_password,
            )

    def test_register_form_accepts_valid_unique_user(self):
        form = self.build_register_form()

        self.assertTrue(form.validate())
        self.assertEqual(form.errors, {})

    def test_register_form_allows_duplicate_username_for_route_message(self):
        create_user(username="taken", email="first@example.com")
        form = self.build_register_form(username="taken", email="second@example.com")

        self.assertTrue(form.validate())
        self.assertEqual(form.username.errors, [])
        self.assertEqual(form.email.errors, [])

    def test_register_form_allows_duplicate_email_for_route_message(self):
        create_user(username="first", email="taken@example.com")
        form = self.build_register_form(username="second", email="taken@example.com")

        self.assertTrue(form.validate())
        self.assertEqual(form.email.errors, [])
        self.assertEqual(form.username.errors, [])

    def test_register_form_rejects_password_shorter_than_eight_characters(self):
        form = self.build_register_form(password="Abc123")

        self.assertFalse(form.validate())
        self.assertIn("Password must be at least 8 characters.", form.password.errors)

    def test_register_form_rejects_password_without_uppercase_letter(self):
        form = self.build_register_form(password="password1")

        self.assertFalse(form.validate())
        self.assertIn("Password must contain at least one uppercase letter.", form.password.errors)

    def test_register_form_rejects_password_without_number(self):
        form = self.build_register_form(password="Password")

        self.assertFalse(form.validate())
        self.assertIn("Password must contain at least one number.", form.password.errors)

    def test_reset_password_form_accepts_matching_passwords(self):
        form = self.build_reset_form()

        self.assertTrue(form.validate())
        self.assertEqual(form.errors, {})

    def test_reset_password_form_rejects_mismatched_confirmation(self):
        form = self.build_reset_form(confirm_password="Different1")

        self.assertFalse(form.validate())
        self.assertIn("Passwords do not match.", form.confirm_password.errors)

    def test_login_form_accepts_username_and_password_fields(self):
        with self.app.test_request_context(method="POST"):
            form = LoginForm(username="existing", password="Password1")

        self.assertTrue(form.validate())

    def test_login_form_rejects_missing_username_or_password(self):
        with self.app.test_request_context(method="POST"):
            missing_username = LoginForm(username="", password="Password1")
            missing_password = LoginForm(username="existing", password="")

        self.assertFalse(missing_username.validate())
        self.assertFalse(missing_password.validate())

    def test_register_logic_saves_hashed_password_and_initial_cash(self):
        form = self.build_register_form(username="saved", email="saved@example.com", password="Password1")
        self.assertTrue(form.validate())

        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data),
            cash="10000.00",
        )
        db.session.add(user)
        db.session.commit()

        saved_user = User.query.filter_by(username="saved").one()
        self.assertEqual(saved_user.email, "saved@example.com")
        self.assertEqual(saved_user.cash, Decimal("10000.00"))
        self.assertNotEqual(saved_user.password_hash, "Password1")
        self.assertTrue(check_password_hash(saved_user.password_hash, "Password1"))

    def test_login_logic_finds_user_by_username_or_email_and_checks_password(self):
        create_user(username="loginuser", email="login@example.com", password="Password1")

        by_username = User.query.filter(
            (User.username == "loginuser") | (User.email == "loginuser")
        ).first()
        by_email = User.query.filter(
            (User.username == "login@example.com") | (User.email == "login@example.com")
        ).first()

        self.assertIsNotNone(by_username)
        self.assertIsNotNone(by_email)
        self.assertTrue(check_password_hash(by_username.password_hash, "Password1"))
        self.assertTrue(check_password_hash(by_email.password_hash, "Password1"))

    def test_login_logic_rejects_wrong_password_and_unknown_user(self):
        create_user(username="loginuser", email="login@example.com", password="Password1")

        user = User.query.filter(
            (User.username == "loginuser") | (User.email == "loginuser")
        ).first()
        unknown = User.query.filter(
            (User.username == "missing") | (User.email == "missing")
        ).first()

        self.assertFalse(check_password_hash(user.password_hash, "WrongPass1"))
        self.assertIsNone(unknown)


if __name__ == "__main__":
    unittest.main()
