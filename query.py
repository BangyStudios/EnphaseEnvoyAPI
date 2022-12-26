import config
from requests_html import HTMLSession
from datetime import datetime
import csv

config:dict = config.ConfigReader().read() # Read config

class Crawler():
    def __init__(self):
        """Initiate Crawler"""
        self.host = config.get("host")
        self.session = HTMLSession()
        self.timeout_page = config.get("timeout_page")
        self.path_csv = config.get("path_csv")
        self.data = dict()
        self.data["titles"] = ["Time", "Production", "Production (Lifetime)", 
                  "Consumption", "Consumption (Lifetime)", 
                  "Net Power"] # Titles for data fields
        self.data["titles_reduced"] = ["Time", "Production", "Consumption"] # Reduced titles for data fields"
        
    def update_page(self):
        """Updates class page"""
        self.page = self.session.get("http://" + self.host) # Get page
        self.page.html.render(sleep=self.timeout_page) # Wait for js render
        
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
        
    def write_titles_csv(self):
        """Writes titles and units into csv"""
        self.filename_csv = self.path_csv + "/" + datetime.now().isoformat(timespec="seconds") + ".csv"
        with open(self.filename_csv, "w") as file_csv:
            writer_csv = csv.writer(file_csv)
            writer_csv.writerow(self.data["titles_reduced"])
            file_csv.close()
            
    def write_values_csv(self, filename_csv=None):
        """Writes class page data into csv"""
        if (filename_csv != None):
            filename_csv = self.path_csv + "/" + filename_csv + ".csv"
        else:
            filename_csv = self.filename_csv
        with open(filename_csv, "a") as file_csv:
            if (None not in self.data["values_reduced"]): # Discard empty rows
                writer_csv = csv.writer(file_csv)
                time_values = [datetime.now().isoformat(timespec="seconds")]
                for value in self.data["values_reduced"]: # Append value after Time column
                    time_values.append(value)
                writer_csv.writerow(time_values)
            file_csv.close()
