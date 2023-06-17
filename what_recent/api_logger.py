import os
import json

def api_log(key, data):
    filename = f"logs/{os.getpid()}-{key}.json"
    with open(filename, "w") as f:
        json.dump(data, f)
