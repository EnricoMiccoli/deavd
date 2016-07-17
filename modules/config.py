import yaml

CONF_PATH = 'config.yaml'

with open(CONF_PATH, 'r') as infile:
    conf = yaml.safe_load(infile)

#TODO: check if config.yaml has been update every time conf is accessed
