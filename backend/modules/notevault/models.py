from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

# ── Pydantic schemas ──────────────────────────────────────────────────────────

class FolderCreate(BaseModel):
    name: str

class FolderOut(BaseModel):
    id: str
    name: str
    createdAt: str

class FileOut(BaseModel):
    id: str
    folderId: str
    fileName: str
    fileType: str
    fileUrl: str
    uploadedAt: str
    # ── New OCR / summary fields ──────────────────────────────────────────────
    ocrText: Optional[str] = None      # Raw text extracted from file
    summary: Optional[str] = None      # AI-generated summary
    title: Optional[str] = None        # AI-suggested title
    tags: Optional[list[str]] = None   # AI-generated keyword tags
    ocrStatus: str = "pending"         # "pending" | "done" | "failed"

# ── In-memory store (replace with SQLite / Postgres in production) ────────────

folders_db: dict[str, dict] = {}
files_db: dict[str, dict] = {}

def create_folder(name: str) -> dict:
    folder_id = str(uuid.uuid4())
    folder = {
        "id": folder_id,
        "name": name,
        "createdAt": datetime.utcnow().isoformat(),
    }
    folders_db[folder_id] = folder
    return folder

def get_all_folders() -> list[dict]:
    return list(folders_db.values())

def get_folder(folder_id: str) -> Optional[dict]:
    return folders_db.get(folder_id)

def create_file_record(
    folder_id: str,
    file_name: str,
    file_type: str,
    file_url: str,
    ocr_text: str = "",
    summary: str = "",
    title: str = "",
    tags: list[str] = None,
    ocr_status: str = "pending",
) -> dict:
    file_id = str(uuid.uuid4())
    record = {
        "id":         file_id,
        "folderId":   folder_id,
        "fileName":   file_name,
        "fileType":   file_type,
        "fileUrl":    file_url,
        "uploadedAt": datetime.utcnow().isoformat(),
        # OCR / summary fields
        "ocrText":    ocr_text,
        "summary":    summary,
        "title":      title,
        "tags":       tags or [],
        "ocrStatus":  ocr_status,
    }
    files_db[file_id] = record
    return record

def get_files_in_folder(folder_id: str) -> list[dict]:
    return [f for f in files_db.values() if f["folderId"] == folder_id]

def delete_file_record(file_id: str) -> Optional[dict]:
    return files_db.pop(file_id, None)

def get_file(file_id: str) -> Optional[dict]:
    return files_db.get(file_id)
