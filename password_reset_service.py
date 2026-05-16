from datetime import datetime
import hashlib
import secrets
import string

from werkzeug.security import generate_password_hash

from memory_store import get_json, get_memory_client, set_json
from models import db, User
from sendemail import send_password_reset_email


RESET_CODE_LENGTH = 6
RESET_CODE_TTL_SECONDS = 10 * 60
RESET_CODE_RESEND_SECONDS = 60
RESET_CODE_MAX_ATTEMPTS = 5


def normalize_email(email):
    return (email or "").strip().lower()


def reset_code_key(email):
    return f"password_reset:{normalize_email(email)}"


def hash_value(value):
    return hashlib.sha256(value.encode()).hexdigest()


def generate_reset_code():
    alphabet = string.ascii_uppercase + string.digits

    while True:
        code = "".join(secrets.choice(alphabet) for _ in range(RESET_CODE_LENGTH))

        if any(char.isalpha() for char in code) and any(char.isdigit() for char in code):
            return code


def clear_reset_code(email):
    get_memory_client().delete(reset_code_key(email))


def get_reset_data(email):
    return get_json(reset_code_key(email))


def save_reset_data(email, reset_data):
    set_json(reset_code_key(email), reset_data, ex=RESET_CODE_TTL_SECONDS)


def get_reset_code_seconds_remaining(email):
    ttl = get_memory_client().ttl(reset_code_key(email))
    return max(0, ttl)


def get_reset_code_resend_seconds_remaining(email):
    reset_data = get_reset_data(email)

    if not reset_data:
        return 0

    sent_at = datetime.fromisoformat(reset_data["sent_at"])
    elapsed = int((datetime.utcnow() - sent_at).total_seconds())
    return max(0, RESET_CODE_RESEND_SECONDS - elapsed)


def request_password_reset(email):
    normalized_email = normalize_email(email)

    if not normalized_email:
        return False, "Email is required."

    user = User.query.filter_by(email=normalized_email).first()
    generic_message = "If this email exists, a verification code has been sent."

    existing_code = get_reset_data(normalized_email)

    if existing_code:
        sent_at = datetime.fromisoformat(existing_code["sent_at"])

        if (datetime.utcnow() - sent_at).total_seconds() < RESET_CODE_RESEND_SECONDS:
            return False, "Please wait before requesting another verification code."

    if not user:
        save_reset_data(normalized_email, {
            "code_hash": "",
            "sent_at": datetime.utcnow().isoformat(),
            "attempts": 0,
            "valid": False,
        })
        return True, generic_message

    code = generate_reset_code()
    reset_data = {
        "code_hash": hash_value(code.upper()),
        "sent_at": datetime.utcnow().isoformat(),
        "attempts": 0,
        "valid": True,
    }

    try:
        send_password_reset_email(user.email, code)
    except Exception:
        clear_reset_code(normalized_email)
        raise

    save_reset_data(normalized_email, reset_data)
    return True, generic_message


def confirm_password_reset(email, code, new_password, confirm_password):
    normalized_email = normalize_email(email)
    normalized_code = (code or "").strip().upper()

    if not normalized_email or not normalized_code or not new_password or not confirm_password:
        return False, "All fields are required."

    if new_password != confirm_password:
        return False, "Passwords do not match."

    if len(new_password) < 6:
        return False, "Password must be at least 6 characters."

    reset_data = get_reset_data(normalized_email)

    if not reset_data:
        return False, "Verification code is invalid or expired."

    if not reset_data.get("valid", True):
        return False, "Verification code is invalid or expired."

    if int(reset_data.get("attempts", 0)) >= RESET_CODE_MAX_ATTEMPTS:
        clear_reset_code(normalized_email)
        return False, "Too many incorrect attempts. Please request a new code."

    if hash_value(normalized_code) != reset_data["code_hash"]:
        reset_data["attempts"] = int(reset_data.get("attempts", 0)) + 1
        remaining_ttl = get_reset_code_seconds_remaining(normalized_email)

        if remaining_ttl > 0:
            set_json(reset_code_key(normalized_email), reset_data, ex=remaining_ttl)

        return False, "Verification code is incorrect."

    user = User.query.filter_by(email=normalized_email).first()

    if not user:
        clear_reset_code(normalized_email)
        return False, "Verification code is invalid or expired."

    user.password_hash = generate_password_hash(new_password, method="pbkdf2:sha256")
    db.session.commit()
    clear_reset_code(normalized_email)

    return True, "Password reset successfully. Please log in."
