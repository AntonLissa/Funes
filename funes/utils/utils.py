import json

def print_json(data):
    obj = json.loads(data)

    print(json.dumps(obj, indent=2))