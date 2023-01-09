import config
from requests_html import HTMLSession

class Crawler():
    def __init__(self, config=config.ConfigReader().read()):
        """Initiate Crawler"""
        self.host = config.get("host")
        self.timeout_page = config.get("timeout_page")
        self.sleep_page = config.get("sleep_page")
        self.data = dict()
        self.data["titles"] = ["Time", "Production", "Production (Lifetime)", 
                  "Consumption", "Consumption (Lifetime)", 
                  "Net Power"] # Titles for data fields
        self.data["titles_reduced"] = ["Time", "Production", "Consumption"] # Reduced titles for data fields"
    
    def get_data(self):
        """Return the latest data from updated page"""
        return self.data
    
    def update_page(self):
        """Updates js values on class page"""
        self.session = HTMLSession()
        self.page = self.session.get("http://" + self.host) # Get page
        self.page.html.render(sleep=self.sleep_page, timeout=self.timeout_page) # Wait for js render
        self.session.close()
        
    def update_page_data(self):
        """Update class page data into a dict"""
        units_elements = self.page.html.find("span.units") # Search units in html
        self.data["units"] = [element.text for element in units_elements] # Parse units into list
        values_elements = self.page.html.find("span.value") # Search value in html
        values = [element.text for element in values_elements] # Parse values into list
        values = values[0:len(self.data["units"])] # Eliminate unnecessary items
        values = [float(value) for value in values] # Casts values to floats
        for i in range(len(self.data["units"])): # Change kW, MW, ..., to W
            if ("kW" in self.data["units"][i]):
                values[i] *= 1000
            elif ("MW" in self.data["units"][i]):
                values[i] *= 1000000
        self.data["values"] = [int(value) for value in values] # Casts values to ints
        self.data["values_reduced"] = list()
        for i in range(len(self.data["values"])): # Eliminate unnecessary value columns
            if (self.data["titles"][i + 1] in self.data["titles_reduced"]):
                self.data["values_reduced"].append(self.data["values"][i])
                
    def update_data(self):
        """Reload page and update data from it."""
        self.update_page()
        self.update_page_data()

class Calculator():
    def __init__(self):
        """Initiate calculator"""
        self.net = 0
    def get_net(self, data):
        """Return the surplus electricity from data in watts or 0 if error"""
        if (len(data["titles_reduced"]) - 1 != len(data["values_reduced"])):
            return self.net
        for i in range(len(data["titles_reduced"])):
            if (data["titles_reduced"][i] == "Production"):
                production = data["values_reduced"][i - 1]
            if (data["titles_reduced"][i] == "Consumption"):
                consumption = data["values_reduced"][i - 1]
        self.net = production - consumption
        return self.net