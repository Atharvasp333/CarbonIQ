import csv
from io import StringIO
from typing import List, Dict, Any

def parse_usage_csv(csv_content: str) -> List[Dict[str, Any]]:
    """
    Parses a CSV string containing runtime, cpu_usage, and region.
    Returns a list of dictionaries with parsed values.
    """
    f = StringIO(csv_content)
    reader = csv.DictReader(f)
    results = []
    
    for row in reader:
        # Strip whitespace from keys and values just in case
        cleaned_row = {k.strip().lower(): v.strip() for k, v in row.items() if k}
        
        runtime = float(cleaned_row.get("runtime", 0))
        cpu_usage = float(cleaned_row.get("cpu_usage", 0))
        region = cleaned_row.get("region", "IN")
        
        results.append({
            "runtime": runtime,
            "cpu_usage": cpu_usage,
            "region": region
        })
        
    return results
