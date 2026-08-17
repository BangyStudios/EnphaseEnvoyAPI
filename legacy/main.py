from config import ConfigReader
from client import Client
import legacy.database as database
import time

config: dict = ConfigReader().read() # Read config

client = Client(config.get("host"), config.get("token"), verify_ssl=False)
csv = database.CSV(config)
txt = database.TempFile(config)

# csv.write_titles_csv(crawler.data["titles_reduced"])
while True:
    try:
        print(client.get_production())

        # csv.write_values_csv(crawler.data["values_reduced"])
        time.sleep(25)
    except (ConnectionError, TimeoutError):
        print("Connection failed, retrying in 10s...")
        time.sleep(10)
        continue