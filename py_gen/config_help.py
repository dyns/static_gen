import os
import shutil
from pathlib import Path

def write_default_config(abs_path):
	default_config_resource = os.path.join(os.path.dirname(__file__), './res/config.yaml')
	dir_path = os.path.dirname(abs_path)
	# create directories if needed
	Path(dir_path).mkdir(parents=True, exist_ok=True)
	shutil.copy(default_config_resource, abs_path)