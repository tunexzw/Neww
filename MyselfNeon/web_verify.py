import base64


def encode_verify_slug(target_url: str) -> str:
    payload = target_url.encode("utf-8")
    return base64.urlsafe_b64encode(payload).decode("utf-8").rstrip("=")


def decode_verify_slug(slug: str):
    try:
        padded = slug + "=" * (-len(slug) % 4)
        return base64.urlsafe_b64decode(padded.encode("utf-8")).decode("utf-8")
    except Exception:
        return None
