import yaml

def read_yaml(file_path):
    with open(file_path) as file:
        return yaml.load(file, Loader=yaml.FullLoader)


def write_yaml(data, file_path):
    with open(file_path, 'w') as file:
        yaml.dump(data, file)
