import query
import time
from requests.exceptions import ConnectionError

crawler = query.Crawler()
crawler.write_titles_csv()
while True:
    try:
        crawler.update_page()
        crawler.update_page_data()
    except (ConnectionError):
        print("Cannot reach host, retrying in 10s...")
        time.sleep(10)
        continue
    crawler.write_values_csv()