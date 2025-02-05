import json, os


def read(contract):
    file_path = os.path.join('constants', 'abis', f'{contract}.json')
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
        return data
