from io import BytesIO
from pathlib import Path
from uuid import uuid4

from docx import Document
from fastapi import HTTPException, UploadFile, status
from pypdf import PdfReader

from app.config import Settings

ALLOWED_EXTENSIONS = {".pdf", ".docx"}


def _extension_from_filename(filename: str) -> str:
    return Path(filename).suffix.lower()


def _validate_signature(extension: str, file_bytes: bytes) -> bool:
    if extension == ".pdf":
        return file_bytes.startswith(b"%PDF")
    if extension == ".docx":
        return file_bytes.startswith(b"PK")
    return False


def _extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(file_bytes))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages).strip()


def _extract_text_from_docx(file_bytes: bytes) -> str:
    document = Document(BytesIO(file_bytes))
    paragraphs = [paragraph.text for paragraph in document.paragraphs]
    return "\n".join(paragraphs).strip()


def parse_and_store_resume(
    upload_file: UploadFile,
    settings: Settings,
) -> tuple[str, str, str, int]:
    extension = _extension_from_filename(upload_file.filename or "")
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file extension. Allowed: .pdf, .docx",
        )

    file_bytes = upload_file.file.read()
    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty",
        )

    max_upload_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(file_bytes) > max_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds {settings.max_upload_size_mb} MB limit",
        )

    if not _validate_signature(extension, file_bytes):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File signature does not match extension",
        )

    if extension == ".pdf":
        extracted_text = _extract_text_from_pdf(file_bytes)
        mime_type = "application/pdf"
    else:
        extracted_text = _extract_text_from_docx(file_bytes)
        mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    if not extracted_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to extract text from uploaded document",
        )

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    stored_filename = f"{uuid4().hex}{extension}"
    output_path = upload_dir / stored_filename
    output_path.write_bytes(file_bytes)

    return str(output_path), extracted_text, mime_type, len(file_bytes)
