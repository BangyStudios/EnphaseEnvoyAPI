import asyncio
import logging
from datetime import datetime, timezone

from quart import Quart, jsonify

from client import Client
from config import ConfigReader

log = logging.getLogger("logger")

config: dict = ConfigReader().read() # Read config

def create_app() -> Quart:
    app = Quart(__name__)
    credentials = None
    if config.get("enlighten_email") and config.get("enlighten_password") and config.get("ee_serial"):
        credentials = {
            "email": config["enlighten_email"],
            "password": config["enlighten_password"],
            "serial_num": config["ee_serial"],
        }

    host = config.get("ee_host")
    if host is None:
        raise ValueError("'ee_host' is missing from the config")
    token = config.get("ee_token")
    timeout = config.get("ee_timeout")
    if timeout is None or timeout <= 0:
        raise ValueError(f"'ee_timeout' must be a positive number of seconds, got {timeout!r}")
    poll_interval = config.get("ee_poll_interval")
    if poll_interval is None or poll_interval <= 0:
        raise ValueError(f"'ee_poll_interval' must be a positive number of seconds, got {poll_interval!r}")
    backoff_max = config.get("ee_backoff_max")
    if backoff_max is None or backoff_max < poll_interval:
        raise ValueError(f"'ee_backoff_max' must be at least 'ee_poll_interval' ({poll_interval!r}), got {backoff_max!r}")

    async def save_token(token: str) -> None:
        config["ee_token"] = token
        await asyncio.to_thread(ConfigReader().update, values={"ee_token": token})

    client = Client(host=host, token=token, verify_ssl=False,
                    poll_interval=poll_interval, backoff_max=backoff_max, timeout=timeout,
                    credentials=credentials, on_token_refresh=save_token)

    @app.before_serving
    async def start_poller() -> None:
        await client.start()

    @app.after_serving
    async def stop_poller() -> None:
        await client.stop()

    def get_production_watts(section: str, index: int) -> tuple:
        """Serve from the cache only; 503 until the first successful poll."""
        if client.production is None:
            return jsonify(error="No data cached yet", detail=client.error_poll), 503, {"Retry-After": "1"}
        readings = client.production.get(section)
        watts = readings[index].get("wNow")
        return jsonify(watts), 200

    @app.route("/")
    async def home() -> str:
        return "Invalid endpoint, please see readme for more info"

    @app.route("/production/total", methods=["GET"])
    async def production_total() -> tuple:
        """Get total production"""
        return get_production_watts(section="production", index=0)

    @app.route("/consumption/total", methods=["GET"])
    async def consumption_total() -> tuple:
        """Get total consumption"""
        return get_production_watts(section="consumption", index=0)

    @app.route("/consumption/net", methods=["GET"])
    async def consumption_net() -> tuple:
        """Get net consumption"""
        return get_production_watts(section="consumption", index=1)

    @app.route("/cache/age", methods=["GET"])
    async def cache_age() -> tuple:
        """Get the age of the cached data"""
        datetime_now = datetime.now(timezone.utc)
        age_seconds = client.get_production_age_datetime(datetime_now=datetime_now)
        datetime_updated = None
        if client.production_datetime is not None:
            datetime_updated = client.production_datetime.isoformat()
        return jsonify(age_seconds=age_seconds, datetime_updated=datetime_updated, error=client.error_poll), 200

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host=config.get("flask_host"), port=config.get("flask_port"), debug=config.get("flask_debug"))
