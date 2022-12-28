
from datetime import datetime
import csv

class CSV:
    def __init__(self, config):
        self.path_csv = config.get("path_csv")
        
    def write_titles_csv(self, titles):
        """Writes titles and creates csv"""
        self.filename_csv = self.path_csv + "/" + datetime.now().isoformat(timespec="seconds") + ".csv"
        with open(self.filename_csv, "w") as file_csv:
            writer_csv = csv.writer(file_csv)
            writer_csv.writerow(titles)
            file_csv.close()
            
    def write_values_csv(self, values, filename_csv=None):
        """Writes class page data into csv"""
        if (filename_csv != None):
            filename_csv = self.path_csv + "/" + filename_csv + ".csv"
        else:
            filename_csv = self.filename_csv
        with open(filename_csv, "a") as file_csv:
            if ("" not in values): # Discard empty rows
                writer_csv = csv.writer(file_csv)
                time_values = [datetime.now().isoformat(timespec="seconds")]
                for value in values: # Append value after Time column
                    time_values.append(value)
                writer_csv.writerow(time_values)
            file_csv.close()
            
class TempFile:
    def __init__(self, config):
        self.path_temp = config.get("path_temp")
    
    def write_net_temp(self, net, filename_temp=None):
        """Writes class page data into csv"""
        filename_txt = self.path_temp + "/" + "temp.txt"
        with open(filename_txt, "w") as file_txt:
            writer_csv = csv.writer(file_txt)
            writer_csv.writerow(net)
            file_txt.close()