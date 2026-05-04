from datetime import datetime, timedelta
import hashlib
import secrets
import string

from models import db, User
from sendemail import send_password_reset_email


PASSWORD_RESET_CODES = {}
RESET_CODE_LENGTH = 6
RESET_CODE_TTL_MINUTES = 10
RESET_CODE_RESEND_SECONDS = 60
RESET_CODE_MAX_ATTEMPTS = 5


def normalize_email(email):
    return (email or "").strip().lower()


def hash_value(value):
    return hashlib.sha256(value.encode()).hexdigest()


def generate_reset_code():
    alphabet = string.ascii_uppercase + string.digits

    while True:
        code = "".join(secrets.choice(alphabet) for _ in range(RESET_CODE_LENGTH))

        if any(char.isalpha() for char in code) and any(char.isdigit() for char in code):
            return code


def clear_expired_reset_codes():
    now = datetime.utcnow()
    expired_emails = [
        email
        for email, data in PASSWORD_RESET_CODES.items()
        if data["expires_at"] <= now
    ]

    for email in expired_emails:
        PASSWORD_RESET_CODES.pop(email, None)


def clear_reset_code(email):
    PASSWORD_RESET_CODES.pop(normalize_email(email), None)


def get_reset_code_seconds_remaining(email):
    clear_expired_reset_codes()

    reset_data = PASSWORD_RESET_CODES.get(normalize_email(email))

    if not reset_data:
        return 0

    remaining = int((reset_data["expires_at"] - datetime.utcnow()).total_seconds())
    return max(0, remaining)


def request_password_reset(email):
    clear_expired_reset_codes()

    normalized_email = normalize_email(email)

    if not normalized_email:
        return False, "Email is required."

    user = User.query.filter_by(email=normalized_email).first()
    generic_message = "If this email exists, a verification code has been sent."

    if not user:
        return True, generic_message

    now = datetime.utcnow()
    existing_code = PASSWORD_RESET_CODES.get(normalized_email)

    if existing_code and (now - existing_code["sent_at"]).total_seconds() < RESET_CODE_RESEND_SECONDS:
        return False, "Please wait before requesting another verification code."

    code = generate_reset_code()
    reset_data = {
        "code_hash": hash_value(code.upper()),
        "expires_at": now + timedelta(minutes=RESET_CODE_TTL_MINUTES),
        "sent_at": now,
        "attempts": 0,
    }

    try:
        send_password_reset_email(user.email, code)
    except Exception:
        clear_reset_code(normalized_email)
        raise

    PASSWORD_RESET_CODES[normalized_email] = reset_data
    return True, generic_message


def confirm_password_reset(email, code, new_password, confirm_password):
    clear_expired_reset_codes()

    normalized_email = normalize_email(email)
    normalized_code = (code or "").strip().upper()

    if not normalized_email or not normalized_code or not new_password or not confirm_password:
        return False, "All fields are required."

    if new_password != confirm_password:
        return False, "Passwords do not match."

    if len(new_password) < 6:
        return False, "Password must be at least 6 characters."

    reset_data = PASSWORD_RESET_CODES.get(normalized_email)

    if not reset_data:
        return False, "Verification code is invalid or expired."

    if reset_data["expires_at"] <= datetime.utcnow():
        PASSWORD_RESET_CODES.pop(normalized_email, None)
        return False, "Verification code is invalid or expired."

    if reset_data["attempts"] >= RESET_CODE_MAX_ATTEMPTS:
        PASSWORD_RESET_CODES.pop(normalized_email, None)
        return False, "Too many incorrect attempts. Please request a new code."

    if hash_value(normalized_code) != reset_data["code_hash"]:
        reset_data["attempts"] += 1
        return False, "Verification code is incorrect."

    user = User.query.filter_by(email=normalized_email).first()

    if not user:
        PASSWORD_RESET_CODES.pop(normalized_email, None)
        return False, "Verification code is invalid or expired."

    user.password_hash = hash_value(new_password)
    db.session.commit()
    PASSWORD_RESET_CODES.pop(normalized_email, None)

    return True, "Password reset successfully. Please log in."
