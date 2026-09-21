from io import BytesIO
from pathlib import Path

from PyPDF2 import PdfReader
from docx import Document


ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def extract_text(filename: str, file_bytes: bytes) -> str:
    """
    Extract text from PDF, DOCX, or TXT.
    """

    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError(
            "Unsupported file type. Please upload PDF, DOCX, or TXT."
        )

    if not file_bytes:
        raise ValueError("The uploaded file is empty.")

    if extension == ".pdf":
        reader = PdfReader(BytesIO(file_bytes))

        pages = []

        for page in reader.pages:
            page_text = page.extract_text() or ""

            if page_text.strip():
                pages.append(page_text)

        text = "\n".join(pages)

    elif extension == ".docx":
        document = Document(BytesIO(file_bytes))

        paragraphs = [
            paragraph.text
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        ]

        text = "\n".join(paragraphs)

    else:
        text = file_bytes.decode("utf-8", errors="ignore")

    text = " ".join(text.split())

    if not text:
        raise ValueError(
            "No readable text could be extracted from this document."
        )

    return text