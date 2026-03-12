import json


def parse_json(raw_text: str):
    """Return (headers, rows) if JSON is array-of-objects, else (None, None)."""
    try:
        data = json.loads(raw_text)
        if isinstance(data, list) and data and isinstance(data[0], dict):
            headers = list(data[0].keys())
            rows = [{h: str(item.get(h, "")) for h in headers} for item in data]
            return headers, rows
    except Exception:
        pass
    return None, None
