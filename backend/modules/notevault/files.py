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
import re

router = APIRouter()

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
    # Validate folder exists
    folder = get_folder(folder_id)
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    # Validate file type
    content_type = file.content_type or ""
    if content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{content_type}'. Allowed: PDF, JPG, PNG, DOCX",
        )

    file_ext = ALLOWED_TYPES[content_type]
    safe_name = _sanitize(file.filename or f"file.{file_ext}")
    destination = f"notes/{folder_id}/{safe_name}"

    file_bytes = await file.read()
    if len(file_bytes) > 20 * 1024 * 1024:  # 20 MB limit
        raise HTTPException(status_code=413, detail="File too large (max 20 MB)")

    public_url = upload_to_firebase(file_bytes, destination, content_type)

    record = create_file_record(
        folder_id=folder_id,
        file_name=safe_name,
        file_type=file_ext,
        file_url=public_url,
    )
    # Store destination path for future deletion
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
