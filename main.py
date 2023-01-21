import config
import query
import database
import time
from requests.exceptions import ConnectionError
from pyppeteer.errors import TimeoutError, PageError

config:dict = config.ConfigReader().read() # Read config

crawler = query.Crawler(config)
calculator = query.Calculator()
csv = database.CSV(config)
txt = database.TempFile(config)
# csv.write_titles_csv(crawler.data["titles_reduced"])
while True:
    try:
        crawler.update_data()
        # csv.write_values_csv(crawler.data["values_reduced"])
        net_temp = calculator.get_net(crawler.data)
        txt.write_net_temp([net_temp])
        print(f"Net: {net_temp}")
        time.sleep(25)
    except (ConnectionError, TimeoutError, PageError):
        print("Connection failed, retrying in 10s...")
        time.sleep(10)
        continue