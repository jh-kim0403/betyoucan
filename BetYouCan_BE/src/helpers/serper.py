import logging

import requests
from src.config import settings

SERP_SEARCH_PATH = "/search.json"
DEFAULT_TIMEOUT_SECONDS = 20
LENS_ENGINE = "google_lens"
_session = requests.Session()
SERP_API_KEY = settings.serp_api_key
SERP_BASE_URL = settings.serp_base_url

class SerperError(Exception):
    pass


def _serp_url() -> str:
    return f"{SERP_BASE_URL.rstrip('/')}{SERP_SEARCH_PATH}"

def reverse_image_search(image_url: str, timeout: int = DEFAULT_TIMEOUT_SECONDS) -> dict:
    if not SERP_API_KEY:
        raise SerperError("SERP_API_KEY is not configured")

    try:
        response = _session.get(
            _serp_url(),
            params={
                "engine": LENS_ENGINE,
                "url": image_url,
                "type": "exact_matches",
                "api_key": SERP_API_KEY
            }
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise SerperError(f"Serper request failed: {exc}") from exc

    try:
        return response.json()
    except ValueError as exc:
        raise SerperError("Serper response was not valid JSON") from exc
