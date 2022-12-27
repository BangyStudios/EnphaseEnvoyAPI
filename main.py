import config
import query
import database
import time
from requests.exceptions import ConnectionError

config:dict = config.ConfigReader().read() # Read config

crawler = query.Crawler(config)
csv = database.CSV(config)
csv.write_titles_csv(crawler.data["titles_reduced"])
while True:
    try:
        crawler.update_page()
        crawler.update_page_data()
        csv.write_values_csv(crawler.data["values_reduced"])
    except (ConnectionError):
        print("Cannot reach host, retrying in 10s...")
        time.sleep(10)
        continue