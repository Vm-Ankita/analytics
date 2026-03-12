import io


def parse_pdf(raw_bytes: bytes) -> str:
    try:
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(raw_bytes))
        return "\n\n".join(p.extract_text() or "" for p in reader.pages).strip()
    except Exception:
        return ""
