import os
import yaml
import pandas as pd

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


def write_csv(data, file_name):
    file_path = os.path.join(DATA_DIRECTORY, file_name)
    df = pd.DataFrame(data, index=[0])
    if not os.path.exists(file_path):
        df.to_csv(file_path, index=False, header=True, mode='a', sep='\t', encoding='utf-8')
    else:
        df.to_csv(file_path, index=False, header=False, mode='a', sep='\t', encoding='utf-8')


def read_csv(file_name):
    file_path = os.path.join(DATA_DIRECTORY, file_name)
    df = pd.read_csv(file_path, sep='\t', encoding='utf-8')
    return df.to_dict(orient='records')
