from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

class EmptyForm(FlaskForm):
    pass

class LoginForm(FlaskForm):
    username = StringField("Username or email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(max=80)])
    email = EmailField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")

    def validate_password(self, field):
        if len(field.data) < 8:
            raise ValidationError("Password must be at least 8 characters.")
        if not any(c.isupper() for c in field.data):
            raise ValidationError("Password must contain at least one uppercase letter.")
        if not any(c.isdigit() for c in field.data):
            raise ValidationError("Password must contain at least one number.")

class ForgotPasswordForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    submit = SubmitField("Send verification code")


class ResetPasswordForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    code = StringField("Verification code", validators=[DataRequired(), Length(min=6, max=6)])
    new_password = PasswordField("New password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm password",
        validators=[DataRequired(), EqualTo("new_password", message="Passwords do not match.")],
    )
    submit = SubmitField("Reset password")
