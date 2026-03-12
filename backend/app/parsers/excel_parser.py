import io


def parse_excel(raw_bytes: bytes):
    try:
        import openpyxl
        wb = openpyxl.load_workbook(io.BytesIO(raw_bytes), read_only=True, data_only=True)
        ws = wb.active
        data = list(ws.iter_rows(values_only=True))
        if not data:
            return None, None
        headers = [str(c) if c is not None else "" for c in data[0]]
        rows = [
            {headers[i]: str(cell) if cell is not None else ""
             for i, cell in enumerate(row)}
            for row in data[1:]
        ]
        return headers, rows
    except Exception:
        return None, None
