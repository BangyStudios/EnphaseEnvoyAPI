import json

template_config = {
    "host" : "[hostname]", 
    "sleep_page" : 5, 
    "timeout_page" : 20, 
    "path_csv" : "data",
    "path_temp" : "data"
}

class ConfigReader:
    """
    Class to read the global JSON configuration file.
    """
    def __init__(self):
        """Initiate defaults for ConfigReader"""
        self.path_config = "config.json" # Path to config file
    def read(self):
        """Reads config into dict"""
        self.open("r")
        config = json.load(self.config)
        self.close()
        return config
    def create(self):
        """Create a new configuration template"""
        self.open("w")
        json.dump(template_config, self.config)
        self.close()
    def open(self, mode):
        """Opens config with specified mode"""
        self.config = open(self.path_config, mode)
    def close(self):
        """Closes config"""
        self.config.close()