import requests
import time

class Client:
    def __init__(self, host, token, verify_ssl=False, cache_ttl=5):
        self.host = host.rstrip("/")
        self.token = token
        self.session = requests.Session()
        self.session.verify = verify_ssl  # Set to True if SSL cert is valid
        self.session_id = None

        # Caching setup
        self.cache_ttl = cache_ttl  # seconds
        self._last_production_response = None
        self._last_production_timestamp = 0

    def get_production(self):
        now = time.time()

        # Serve cached result if still valid
        if (
            self._last_production_response is not None
            and now - self._last_production_timestamp < self.cache_ttl
        ):
            return self._last_production_response

        url = f"https://{self.host}/production.json"
        response = self.session.get(url)

        if response.status_code == 200:
            data = response.json()
            self._last_production_response = data
            self._last_production_timestamp = now
            return data

        elif response.status_code == 401:
            # Authenticate and retry
            self.authenticate()
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            self._last_production_response = data
            self._last_production_timestamp = now
            return data

        else:
            response.raise_for_status()

    def authenticate(self):
        auth_url = f"https://{self.host}/auth/check_jwt"
        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.session.get(auth_url, headers=headers)
        response.raise_for_status()

        # Extract Set-Cookie header
        cookies = response.headers.get("Set-Cookie", "")
        for part in cookies.split(";"):
            if part.strip().startswith("sessionId="):
                self.session_id = part.strip().split("=")[1]
                break

        if not self.session_id:
            raise RuntimeError("Authentication failed: sessionId not found in Set-Cookie")

        # Store cookie in session for next requests
        self.session.cookies.set("sessionId", self.session_id)
