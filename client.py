import asyncio
import logging
from collections.abc import Awaitable, Callable
from datetime import datetime, timezone

import httpx

from enphase import TokenError, fetch_token

log = logging.getLogger("logger")


class AuthenticationError(Exception):
    """Raised when the Envoy rejects or fails to complete authentication."""


class Client:
    """
    Polls the Envoy in the background and caches the latest production.json in memory.
    One request in flight at a time; failures back off exponentially up to backoff_max.
    """
    backoff_factor = 2

    def __init__(self, host: str, token: str | None, verify_ssl: bool, poll_interval: float, backoff_max: float,
                 timeout: float, credentials: dict | None,
                 on_token_refresh: Callable[[str], Awaitable[None]] | None) -> None:
        self.host = host.rstrip("/")
        self.token = token
        self.verify_ssl = verify_ssl  # Set to True if SSL cert is valid
        self.poll_interval = poll_interval  # Seconds between poll starts, must be positive
        self.backoff_max = backoff_max  # Seconds, upper bound on delay after failures
        self.timeout = timeout
        self.credentials = credentials  # dict: email, password, serial_num
        self.on_token_refresh = on_token_refresh  # async callback(token) to persist
        self.session: httpx.AsyncClient | None = None
        self.task_poll: asyncio.Task | None = None

        # Cache
        self.production: dict | None = None  # None until the first successful poll
        self.production_datetime: datetime | None = None
        self.error_poll: str | None = None  # Cleared on the next successful poll

    # ==========================================================================
    # Independent helpers, alphabetical
    # ==========================================================================

    def get_production_age_datetime(self, datetime_now: datetime) -> float | None:
        """Seconds between the cached production and datetime_now, or None if nothing is cached."""
        if self.production_datetime is None:
            return None
        age = datetime_now - self.production_datetime
        return age.total_seconds()

    async def stop(self) -> None:
        if self.task_poll is not None:
            self.task_poll.cancel()
            try:
                await self.task_poll
            except asyncio.CancelledError:
                pass
        if self.session is not None:
            await self.session.aclose()

    # ==========================================================================
    # Core class functions, in dependency order
    # ==========================================================================

    async def refresh_token(self) -> None:
        """Fetch a new token from Enphase using stored credentials."""
        c = self.credentials
        try:
            self.token = await fetch_token(email=c["email"], password=c["password"], serial_num=c["serial_num"])
        except TokenError as e:
            raise AuthenticationError(str(e)) from e
        if self.on_token_refresh is not None:
            await self.on_token_refresh(self.token)

    async def authenticate(self, is_retry: bool = True) -> None:
        auth_url = f"https://{self.host}/auth/check_jwt"
        headers = {"Authorization": f"Bearer {self.token}"}
        response = await self.session.get(url=auth_url, headers=headers)
        if response.status_code in (401, 403):
            if is_retry and self.credentials is not None:
                await self.refresh_token()
                await self.authenticate(is_retry=False)
                return
            raise AuthenticationError(
                f"Envoy rejected the token ({response.status_code}); it may be invalid or expired"
            )
        response.raise_for_status()

        session_id = response.cookies.get("sessionId")
        if session_id is None:
            raise AuthenticationError("sessionId not found in Set-Cookie")

        # Store cookie in session for next requests
        self.session.cookies.set("sessionId", session_id)

    async def pull_production(self) -> dict:
        """Raises httpx.HTTPError or AuthenticationError; the caller handles both."""
        url = f"https://{self.host}/production.json"
        response = await self.session.get(url=url)
        if response.status_code == 401:
            # Authenticate and retry once
            await self.authenticate()
            response = await self.session.get(url=url)
        response.raise_for_status()
        return response.json()

    async def run_poll(self) -> None:
        """Runs until cancelled; never raises on upstream failure."""
        loop = asyncio.get_running_loop()
        delay_backoff = self.poll_interval
        while True:
            time_start = loop.time()
            try:
                production = await self.pull_production()
            except asyncio.CancelledError:
                raise
            except Exception as e:
                self.error_poll = f"{type(e).__name__}: {e}"
                delay_backoff = delay_backoff * self.backoff_factor
                delay_backoff = min(delay_backoff, self.backoff_max)
                log.warning("Envoy poll failed (%s); retrying in %.0fs", self.error_poll, delay_backoff)
                await asyncio.sleep(delay_backoff)
                continue

            self.production = production
            self.production_datetime = datetime.now(timezone.utc)
            self.error_poll = None
            delay_backoff = self.poll_interval

            time_elapsed = loop.time() - time_start
            delay = self.poll_interval - time_elapsed
            delay = max(delay, 0.0)
            await asyncio.sleep(delay)

    async def start(self) -> None:
        self.session = httpx.AsyncClient(verify=self.verify_ssl, timeout=self.timeout)
        self.task_poll = asyncio.create_task(self.run_poll(), name="envoy-poller")
