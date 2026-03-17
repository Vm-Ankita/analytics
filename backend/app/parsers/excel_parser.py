import io
from typing import List, Dict, Tuple, Optional


def parse_excel(raw_bytes: bytes) -> Tuple[Optional[List[str]], Optional[List[Dict[str, str]]]]:
    """
    Parse Excel file into headers and rows.
    """

    try:
        import openpyxl

        wb = openpyxl.load_workbook(
            io.BytesIO(raw_bytes),
            read_only=True,
            data_only=True
        )

        ws = wb.active
        data = list(ws.iter_rows(values_only=True))

        if not data:
            return None, None

        headers = [
            str(cell).strip() if cell is not None else ""
            for cell in data[0]
        ]

        rows = []

        for row in data[1:]:
            row_dict = {}

            for i, cell in enumerate(row):
                key = headers[i] if i < len(headers) else f"col_{i}"

                row_dict[key] = str(cell).strip() if cell is not None else ""

            rows.append(row_dict)

        return headers, rows

    except Exception:
        return None, None