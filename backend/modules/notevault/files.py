from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from backend.modules.notevault.models import (
    FileOut,
    get_folder,
    create_file_record,
    get_files_in_folder,
    delete_file_record,
    get_file,
)
from backend.modules.notevault.firebase_storage import upload_to_firebase, delete_from_firebase
from backend.modules.notevault.ocr import extract_text
from backend.modules.notevault.summarize import summarize
import logging
import re

router = APIRouter()
logger = logging.getLogger(__name__)

ALLOWED_TYPES = {
    "application/pdf": "pdf",
    "image/jpeg": "jpg",
    "image/png": "png",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
}

def _sanitize(name: str) -> str:
    """Remove characters unsafe for storage paths."""
    return re.sub(r"[^\w.\-]", "_", name)


@router.post("/upload-file", response_model=FileOut, status_code=201)
async def upload_file(
    folder_id: str = Form(...),
    file: UploadFile = File(...),
):
    # ── 1. Validate folder ────────────────────────────────────────────────────
    folder = get_folder(folder_id)
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    # ── 2. Validate file type ─────────────────────────────────────────────────
    content_type = file.content_type or ""
    if content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{content_type}'. Allowed: PDF, JPG, PNG, DOCX",
        )

    file_ext  = ALLOWED_TYPES[content_type]
    safe_name = _sanitize(file.filename or f"file.{file_ext}")
    destination = f"notes/{folder_id}/{safe_name}"

    # ── 3. Read + size-check ──────────────────────────────────────────────────
    file_bytes = await file.read()
    if len(file_bytes) > 20 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large (max 20 MB)")

    # ── 4. Upload to Firebase ─────────────────────────────────────────────────
    public_url = upload_to_firebase(file_bytes, destination, content_type)

    # ── 5. OCR ────────────────────────────────────────────────────────────────
    ocr_status = "pending"
    raw_text   = ""
    try:
        raw_text   = extract_text(file_bytes, file_ext)
        ocr_status = "done" if raw_text.strip() else "failed"
    except Exception as e:
        logger.error(f"OCR failed for {safe_name}: {e}")
        ocr_status = "failed"

    # ── 6. Summarize ──────────────────────────────────────────────────────────
    ai_title   = safe_name
    ai_summary = ""
    ai_tags    = []
    try:
        result     = summarize(raw_text, file_name=safe_name)
        ai_title   = result.get("title",   safe_name)
        ai_summary = result.get("summary", "")
        ai_tags    = result.get("tags",    [])
    except Exception as e:
        logger.error(f"Summarization failed for {safe_name}: {e}")

    # ── 7. Save record ────────────────────────────────────────────────────────
    record = create_file_record(
        folder_id=folder_id,
        file_name=safe_name,
        file_type=file_ext,
        file_url=public_url,
        ocr_text=raw_text,
        summary=ai_summary,
        title=ai_title,
        tags=ai_tags,
        ocr_status=ocr_status,
    )
    record["_storagePath"] = destination
    return record


@router.get("/folder/{folder_id}/files", response_model=list[FileOut])
def list_files(folder_id: str):
    folder = get_folder(folder_id)
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    return get_files_in_folder(folder_id)


@router.delete("/file/{file_id}", status_code=200)
def delete_file(file_id: str):
    record = get_file(file_id)
    if not record:
        raise HTTPException(status_code=404, detail="File not found")

    storage_path = record.get("_storagePath")
    if storage_path:
        delete_from_firebase(storage_path)

    delete_file_record(file_id)
    return {"message": "File deleted successfully", "id": file_id}
