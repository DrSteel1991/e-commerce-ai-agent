import os

from fastapi import Header, HTTPException

INTERNAL_API_KEY_HEADER = "X-Internal-API-Key"
USER_ID_HEADER = "X-User-Id"


def get_internal_api_key() -> str:
    api_key = os.environ.get("INTERNAL_SERVICE_API_KEY")
    if not api_key:
        raise RuntimeError("INTERNAL_SERVICE_API_KEY is not configured")
    return api_key


def internal_headers(user_id: str | None = None) -> dict[str, str]:
    headers = {INTERNAL_API_KEY_HEADER: get_internal_api_key()}
    if user_id:
        headers[USER_ID_HEADER] = user_id
    return headers


def require_internal_api_key(
    api_key: str = Header(..., alias=INTERNAL_API_KEY_HEADER),
) -> None:
    expected = os.environ.get("INTERNAL_SERVICE_API_KEY")
    if not expected or api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid internal API key")
