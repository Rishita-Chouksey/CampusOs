from fastapi import APIRouter, HTTPException
from backend.modules.notevault.models import FolderCreate, FolderOut, create_folder, get_all_folders, get_folder

router = APIRouter()

@router.post("/folders", response_model=FolderOut, status_code=201)
def create_folder_endpoint(body: FolderCreate):
    if not body.name.strip():
        raise HTTPException(status_code=400, detail="Folder name cannot be empty")
    folder = create_folder(body.name.strip())
    return folder

@router.get("/folders", response_model=list[FolderOut])
def list_folders():
    return get_all_folders()
