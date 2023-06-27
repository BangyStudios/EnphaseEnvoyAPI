import config
from requests_html import HTMLSession

class Crawler():
    def __init__(self, config=config.ConfigReader().read()):
        """Initiate Crawler"""
        self.host = config.get("host")
        self.timeout_page = config.get("timeout_page")
        self.sleep_page = config.get("sleep_page")
        self.data = dict()
        self.data["titles"] = ["Production", "Production (Lifetime)", 
                  "Consumption", "Consumption (Lifetime)", 
                  "Net Power"] # Titles for data fields
        self.data["titles_reduced"] = ["Production", "Consumption"] # Reduced titles for data fields"
        self.session = HTMLSession()

    def get_data(self):
        """Return the latest data from updated page"""
        return self.data

    def update_page(self):
        """Updates js values on class page"""
        self.page = self.session.get("http://" + self.host) # Get page
        self.page.html.render(sleep=self.sleep_page, timeout=self.timeout_page) # Wait for js render

    def update_page_data(self):
        """Update class page data into a dict"""
        units_elements = self.page.html.find("span.units") # Search units in html
        values_elements = self.page.html.find("span.value") # Search value in html
        values_elements = [values_elements[i] for i in range(len(units_elements))] # Prune end values.

        self.data["units"], self.data["values"] = [], []
        for unit, value in zip(units_elements, values_elements):
            self.data["units"].append(unit.text)
            value_float = float(value.text)
            if "kW" in unit.text:
                value_float *= 1000
            elif "MW" in unit.text:
                value_float *= 1000000
            self.data["values"].append(int(value_float))

    def update_reduced_data(self):
        """Update reduced data"""
        self.data["values_reduced"] = [v for t, v in zip(self.data["titles"], self.data["values"]) if t in self.data["titles_reduced"]]

    def update_data(self):
        """Reload page and update data from it."""
        self.update_page()
        self.update_page_data()
        self.update_reduced_data()
        self.page.close()