import yaml
from pathlib import Path
import sys

def gen_exit():
    sys.exit(1)

class Config():
    '''
        Wrapper class for config yaml dict
    '''
    def __init__(self, config_dict):
        self.config_dict = config_dict

    def __getitem__(self, key):
        if key in self.config_dict:
            return self.config_dict[key]
        else:
            print("{} isn't in config file.".format(key))
            gen_exit()

def load_file(f_path, error=''):
    try:
        target_f = open(f_path)
        return target_f
    except Exception as e:
        print('{}\n{}'.format(error, e))
        gen_exit()

def load_file_text(f_path, error=''):
    target_f = load_file(f_path, error)
    text = target_f.read()
    target_f.close()
    return text

def load_config(config_path):
    print('Loading config file {}'.format(config_path))
    config_t = load_file_text(config_path, error='Unable to open config at: {}'.format(config_path))
    config = yaml.load(config_t)
    return Config(config)