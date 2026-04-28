import json
import os
from typing import List, Dict

DATA_FILE = os.path.join(os.path.dirname(__file__), "results.json")

def save_result(result: Dict):
    results = get_results()
    results.append(result)
    with open(DATA_FILE, "w") as f:
        json.dump(results, f, indent=2)

def get_results() -> List[Dict]:
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return []
