import os


def load_local_env():
    if not os.path.exists(".env"):
        return

    with open(".env", encoding="utf-8") as env_file:
        for line in env_file:
            line = line.strip()

            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()

            if key.startswith("RESEND_"):
                os.environ[key] = value.strip()


def send_password_reset_email(to_email, code):
    import resend

    load_local_env()
    resend.api_key = os.environ.get("RESEND_API_KEY")

    if not resend.api_key:
        raise RuntimeError("RESEND_API_KEY is not configured.")

    from_email = os.environ.get("RESEND_FROM_EMAIL")

    if not from_email:
        raise RuntimeError("RESEND_FROM_EMAIL is not configured.")

    resend.Emails.send({
        "from": from_email,
        "to": to_email,
        "subject": "Password reset verification code",
        "html": (
            "<p>Your password reset verification code is "
            f"<strong>{code}</strong>.</p>"
            "<p>This code will expire in 10 minutes.</p>"
            "<p>If you did not request a password reset, you can ignore this email.</p>"
        ),
    })
