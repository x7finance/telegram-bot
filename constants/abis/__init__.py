import json, os

from constants import ca


def read(contract):
    file_path = os.path.join('constants', 'abis', f'{contract}.json')
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
        return data
    

def list(chain): 
    return {
        ca.X7R_LIQ_HUB(chain): {
            "abi": read("x7rliquidityhub")
        },
        ca.X7DAO_LIQ_HUB(chain): {
            "abi": read("x7daoliquidityhub")
        },
        ca.X7100_LIQ_HUB(chain): {
            "abi": read("x7100liquidityhub")
        },
        ca.ECO_SPLITTER(chain): {
            "abi": read("ecosystemsplitter"),
            "recipient": ca.LPOOL_RESERVE(chain)
        },
        ca.TREASURY_SPLITTER(chain): {
            "abi": read("treasurysplitter"),
            "recipient": ca.DAO_MULTI(chain)
        }
    }
