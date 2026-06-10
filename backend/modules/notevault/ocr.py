"""
OCR module for NoteVault
Supports: PDF, JPG, PNG, DOCX
"""

import io
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def extract_text(file_bytes: bytes, file_type: str) -> str:
    """
    Extract raw text from file bytes.

    Args:
        file_bytes: Raw bytes of the uploaded file
        file_type:  One of "pdf", "jpg", "png", "docx"

    Returns:
        Extracted text string (may be empty if extraction fails)
    """
    try:
        if file_type == "pdf":
            return _extract_pdf(file_bytes)
        elif file_type in ("jpg", "jpeg", "png"):
            return _extract_image(file_bytes)
        elif file_type == "docx":
            return _extract_docx(file_bytes)
        else:
            logger.warning(f"Unsupported file type for OCR: {file_type}")
            return ""
    except Exception as e:
        logger.error(f"OCR extraction failed for {file_type}: {e}")
        return ""


# ── PDF ───────────────────────────────────────────────────────────────────────

def _extract_pdf(file_bytes: bytes) -> str:
    """
    Try embedded text first (fast). Fall back to image-based OCR
    if the PDF is scanned (no embedded text layer).
    """
    import pdfplumber

    text_parts = []

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)

    full_text = "\n".join(text_parts).strip()

    # If we got almost nothing, the PDF is likely a scanned image — run OCR
    if len(full_text) < 50:
        logger.info("PDF appears to be scanned; falling back to image OCR")
        full_text = _ocr_pdf_pages(file_bytes)

    return full_text


def _ocr_pdf_pages(file_bytes: bytes) -> str:
    """Convert each PDF page to an image and OCR it."""
    from pdf2image import convert_from_bytes
    import pytesseract

    images = convert_from_bytes(file_bytes, dpi=200)
    parts = [pytesseract.image_to_string(img, lang="eng") for img in images]
    return "\n".join(parts).strip()


# ── Images ────────────────────────────────────────────────────────────────────

def _extract_image(file_bytes: bytes) -> str:
    """Run Tesseract OCR on a JPEG or PNG image."""
    import pytesseract
    from PIL import Image

    image = Image.open(io.BytesIO(file_bytes))

    # Convert to RGB if needed (e.g. RGBA PNGs)
    if image.mode not in ("RGB", "L"):
        image = image.convert("RGB")

    return pytesseract.image_to_string(image, lang="eng").strip()


# ── DOCX ──────────────────────────────────────────────────────────────────────

def _extract_docx(file_bytes: bytes) -> str:
    """Extract text from a Word .docx file."""
    from docx import Document

    doc = Document(io.BytesIO(file_bytes))
    paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
    return "\n".join(paragraphs).strip()
