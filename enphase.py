import logging

import httpx

log = logging.getLogger("logger")

LOGIN_URL = "https://enlighten.enphaseenergy.com/login/login.json"
TOKEN_URL = "https://entrez.enphaseenergy.com/tokens"


class TokenError(Exception):
    """Raised when a new token could not be obtained from Enphase."""


async def fetch_token(email: str, password: str, serial_num: str, timeout: float = 15) -> str:
    """Log in to Enlighten and request a fresh Envoy token for the given serial number."""
    try:
        async with httpx.AsyncClient(timeout=timeout) as client_http:
            response_login = await client_http.post(
                url=LOGIN_URL,
                data={"user[email]": email, "user[password]": password},
            )
            response_login.raise_for_status()
            session_id = response_login.json().get("session_id")
            if session_id is None:
                raise TokenError("Enlighten login succeeded but returned no session_id")

            response_token = await client_http.post(
                url=TOKEN_URL,
                json={"session_id": session_id, "serial_num": serial_num, "username": email},
            )
            response_token.raise_for_status()
            token = response_token.text.strip()
    except httpx.HTTPError as e:
        raise TokenError(f"Token request failed: {e}") from e

    if len(token) == 0:
        raise TokenError("Enphase returned an empty token")
    log.info("Obtained new Envoy token")
    return token
