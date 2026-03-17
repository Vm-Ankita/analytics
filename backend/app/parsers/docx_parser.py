import io


def parse_docx(raw_bytes: bytes) -> str:
    """
    Extract text from a DOCX file.
    """

    try:
        import docx

        doc = docx.Document(io.BytesIO(raw_bytes))

        paragraphs = [
            p.text.strip()
            for p in doc.paragraphs
            if p.text and p.text.strip()
        ]

        return "\n".join(paragraphs)

    except Exception:
        return ""