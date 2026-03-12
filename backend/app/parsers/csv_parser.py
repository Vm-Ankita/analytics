import csv
import io


def parse_csv(text: str, delimiter: str = ","):
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    rows   = list(reader)
    return list(reader.fieldnames or []), rows
