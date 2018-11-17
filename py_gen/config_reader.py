from yaml import load, dump
from yaml import Loader, Dumper

def load_config(config_path):
    # config.yaml
    config = load(open(config_path), Loader=Loader)
    return config


