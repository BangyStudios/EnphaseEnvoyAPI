
from datetime import datetime
import csv

class CSV:
    def __init__(self, config):
        self.path_csv = config.get("path_csv")
        
    def write_titles_csv(self, titles):
        """Writes titles and creates csv"""
        self.filename_csv = f"{self.path_csv}/{datetime.now().strftime('%Y%m%d-%H%M%S')}.csv"
        time_titles = ["Time"]
        for title in titles: # Append title after Time column
            time_titles.append(title)
        with open(self.filename_csv, "w") as file_csv:
            writer_csv = csv.writer(file_csv)
            writer_csv.writerow(time_titles)
            file_csv.close()
            
    def write_values_csv(self, values, filename_csv=None):
        """Writes class page data into csv"""
        if (filename_csv != None):
            filename_csv = f"{self.path_csv}/{filename_csv}.csv"
        else:
            filename_csv = self.filename_csv
        with open(filename_csv, "a") as file_csv:
            if ("" not in values): # Discard empty rows
                writer_csv = csv.writer(file_csv)
                time_values = [datetime.now().strftime("%Y-%m-%dT%H:%M:%S")]
                for value in values: # Append value after Time column
                    time_values.append(value)
                writer_csv.writerow(time_values)
            file_csv.close()
            
class TempFile:
    def __init__(self, config):
        self.path_temp = config.get("path_temp")
    
    def write_net_temp(self, net, filename_temp=None):
        """Writes class page data into csv"""
        filename_txt = f"{self.path_temp}/net.txt"
        with open(filename_txt, "w") as file_txt:
            writer_csv = csv.writer(file_txt)
            writer_csv.writerow(net)
            file_txt.close()