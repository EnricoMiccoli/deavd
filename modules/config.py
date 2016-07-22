import yaml

CONF_PATH = 'config.yaml'

class Config(dict):
    def __init__(self, filename):
        with open(filename, 'r') as infile:
            self.conf = yaml.safe_load(infile)

    def __getitem__(self, key):
        value = self.conf[key]
        return value

conf = Config(CONF_PATH)
#TODO: check if config.yaml has been update every time conf is accessed
