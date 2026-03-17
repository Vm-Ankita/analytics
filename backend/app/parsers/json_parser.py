import json
from typing import List, Dict, Tuple, Optional


def parse_json(raw_text: str) -> Tuple[Optional[List[str]], Optional[List[Dict[str, str]]]]:
    """
    Parse JSON if it is an array of objects.
    """

    try:
        data = json.loads(raw_text)

        if isinstance(data, list) and data and isinstance(data[0], dict):

            headers = list(data[0].keys())

            rows = [
                {h: str(item.get(h, "")).strip() for h in headers}
                for item in data
            ]

            return headers, rows

    except Exception:
        pass

    return None, None