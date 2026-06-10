import firebase_admin
from firebase_admin import credentials, storage
import os
from pathlib import Path

_initialized = False

def _init_firebase():
    global _initialized
    if _initialized:
        return
    cred_path = os.environ.get("FIREBASE_CREDENTIALS_PATH", "serviceAccountKey.json")
    bucket_name = os.environ.get("FIREBASE_STORAGE_BUCKET")  # e.g. "your-project.appspot.com"
    if not bucket_name:
        raise RuntimeError("FIREBASE_STORAGE_BUCKET env var is not set")
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred, {"storageBucket": bucket_name})
    _initialized = True


def upload_to_firebase(file_bytes: bytes, destination_path: str, content_type: str) -> str:
    """
    Uploads bytes to Firebase Storage and returns a public download URL.
    destination_path example: "notes/DBMS/unit1.pdf"
    """
    _init_firebase()
    bucket = storage.bucket()
    blob = bucket.blob(destination_path)
    blob.upload_from_string(file_bytes, content_type=content_type)
    blob.make_public()
    return blob.public_url


def delete_from_firebase(destination_path: str) -> bool:
    """
    Deletes a file from Firebase Storage.
    Returns True if deleted, False if not found.
    """
    _init_firebase()
    bucket = storage.bucket()
    blob = bucket.blob(destination_path)
    if blob.exists():
        blob.delete()
        return True
    return False
