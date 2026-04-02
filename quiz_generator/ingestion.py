from __future__ import annotations

from io import BytesIO

from pypdf import PdfReader


def extract_text_from_file(uploaded_file, suffix: str) -> str:
    raw_bytes = uploaded_file.read()

    if suffix == ".txt":
        return raw_bytes.decode("utf-8", errors="ignore")

    if suffix == ".pdf":
        pdf_reader = PdfReader(BytesIO(raw_bytes))
        pages = [page.extract_text() or "" for page in pdf_reader.pages]
        return "\n".join(pages)

    raise ValueError(f"Unsupported file type: {suffix}")
