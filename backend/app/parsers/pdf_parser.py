import io


def parse_pdf(raw_bytes: bytes) -> str:
    """
    Extract text from PDF pages.
    """

    try:
        import pypdf

        reader = pypdf.PdfReader(io.BytesIO(raw_bytes))

        text_parts = []

        for page in reader.pages:
            page_text = page.extract_text() or ""
            if page_text.strip():
                text_parts.append(page_text.strip())

        return "\n\n".join(text_parts)

    except Exception:
        return ""