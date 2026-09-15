import hmac
import hashlib
import os

SECRET_KEY = os.getenv("SECRET_PROVIDER_KEY", "secret123")


def sign(e164: str) -> str | None:
    if e164.endswith("8"):
        return None

    return hmac.new(
        SECRET_KEY.encode("utf-8"),
        e164.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
