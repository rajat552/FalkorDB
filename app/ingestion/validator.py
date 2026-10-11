from __future__ import annotations
import hashlib
import io
import os
from pathlib import Path
from typing import Tuple, Dict, Any
from app.config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE_MB

try:
    import pypdf
except ImportError:
    pypdf = None


class DocumentValidationError(Exception):
    """Raised when an uploaded document fails validation."""
    pass


def compute_content_hash(content: bytes) -> str:
    """Compute SHA-256 hash for document content to detect duplicates."""
    return hashlib.sha256(content).hexdigest()


def validate_file(filename: str, content: bytes) -> Tuple[str, str]:
    """
    Validate file extension, size, and extract text.
    Returns (cleaned_filename, extracted_text).
    """
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise DocumentValidationError(
            f"Unsupported file extension '{ext}'. Allowed extensions: {sorted(ALLOWED_EXTENSIONS)}"
        )

    size_mb = len(content) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise DocumentValidationError(
            f"File size {size_mb:.2f}MB exceeds limit of {MAX_FILE_SIZE_MB}MB."
        )

    text = ""
    if ext in {".md", ".txt", ".json"}:
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            text = content.decode("latin-1", errors="replace")
    elif ext == ".pdf":
        if pypdf is None:
            raise DocumentValidationError("pypdf is required to parse PDF documents.")
        try:
            reader = pypdf.PdfReader(io.BytesIO(content))
            pages = []
            for idx, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    pages.append(page_text)
            text = "\n\n".join(pages)
        except Exception as e:
            raise DocumentValidationError(f"Failed to parse PDF document: {e}")

    if not text.strip():
        raise DocumentValidationError("Document content is empty or unreadable.")

    return os.path.basename(filename), text
