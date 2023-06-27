import config
import query
import database
import time
from requests.exceptions import ConnectionError
from pyppeteer.errors import TimeoutError, PageError, BrowserError

config:dict = config.ConfigReader().read() # Read config

crawler = query.Crawler(config)
csv = database.CSV(config)
txt = database.TempFile(config)

csv.write_titles_csv(crawler.data["titles_reduced"])

# backoff strategy
backoff_time = 1

while True:
    try:
        crawler.update_data()
        title_value_pairs = zip(crawler.data["titles_reduced"], crawler.data["values_reduced"])
        production = next((v for t, v in title_value_pairs if t == "Production"), 0)
        consumption = next((v for t, v in title_value_pairs if t == "Consumption"), 0)
        
        csv.write_values_csv(crawler.data["values_reduced"])
        
        net = production - consumption
        txt.write_net_temp([net])
        print(f"Production: {production}, Consumption: {consumption}, Net: {net}")

        # Reset backoff time upon successful connection
        backoff_time = 1

        # Sleep until the next minute
        time_to_next_minute = 60 - time.time() % 60
        time.sleep(time_to_next_minute)

    except (ConnectionError, TimeoutError, PageError, BrowserError) as e:
        print(f"Connection failed due to {str(e)}, retrying in {backoff_time}s...")
        time.sleep(backoff_time)
        # Increase backoff time for the next potential failure
        backoff_time *= 2
        continue
