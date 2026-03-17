import csv
import io
from typing import List, Dict, Tuple


def parse_csv(text: str, delimiter: str = ",") -> Tuple[List[str], List[Dict[str, str]]]:
    """
    Parse CSV text into headers and rows.
    """

    if not text.strip():
        return [], []

    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)

    headers = [h.strip() for h in (reader.fieldnames or [])]

    rows = []
    for row in reader:
        rows.append({
            k.strip(): (str(v).strip() if v is not None else "")
            for k, v in row.items()
        })

    return headers, rows