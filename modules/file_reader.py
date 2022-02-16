import os
import yaml

from pathlib import Path


DATA_DIRECTORY =  os.path.join(Path(__file__).parent.parent, 'data')


def read_yaml(file_path):
    with open(file_path) as file:
        return yaml.load(file, Loader=yaml.FullLoader)


def write_yaml(data, file_path):
    with open(file_path, 'w') as file:
        yaml.dump(data, file)


def write_data(data, file_name):
    file_path = os.path.join(DATA_DIRECTORY, f'{file_name}.yml')
    write_yaml(data, file_path)


def read_data(file_name):
    file_path = os.path.join(DATA_DIRECTORY, f'{file_name}.yml')
    if(not os.path.exists(file_path)):
        return {}
    return read_yaml(file_path)