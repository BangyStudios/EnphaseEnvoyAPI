import logging
from flask import Flask, config, jsonify

from config import ConfigReader
from client import Client

log = logging.getLogger("logger")

config: dict = ConfigReader().read() # Read config

def create_app():
    app = Flask(__name__)
    client = Client(config.get("ee_host"), config.get("ee_token"), verify_ssl=False, cache_ttl=config.get("ee_cache_ttl"))

    @app.route("/")
    def home():
        return "Invalid endpoint, please see readme for more info"
    
    @app.route("/production/total", methods=["GET"])
    def production_total():
        """Get total production"""
        return jsonify(client.get_production().get("production")[0].get("wNow")), 200

    @app.route("/consumption/total", methods=["GET"])
    def consumption_total():
        """Get total consumption"""
        return jsonify(client.get_production().get("consumption")[0].get("wNow")), 200

    @app.route("/consumption/net", methods=["GET"])
    def consumption_net():
        """Get net consumption"""
        return jsonify(client.get_production().get("consumption")[1].get("wNow")), 200

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host=config.get("flask_host"), port=config.get("flask_port"), debug=config.get("flask_debug"))
