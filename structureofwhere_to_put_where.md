# CampusOS – Notes Vault MVP

A file management system for engineering students to organise lecture notes, PDFs, and assignments by subject.

---

## Project Structure

```
campusos/
├── backend/
│   ├── main.py                  ← FastAPI app entry point
│   ├── models.py                ← Data models + in-memory DB
│   ├── firebase_storage.py      ← Firebase upload/delete helpers
│   ├── requirements.txt
│   ├── .env.example
│   └── routes/
│       ├── __init__.py
│       ├── folders.py           ← POST /folders, GET /folders
│       └── files.py             ← POST /upload-file, GET /folder/{id}/files, DELETE /file/{id}
│
└── frontend/
    ├── index.html
    ├── vite.config.js
    ├── package.json
    ├── .env.example
    └── src/
        ├── main.jsx             ← React entry
        ├── App.jsx              ← Router setup
        ├── services/
        │   └── api.js           ← All Axios calls
        ├── pages/
        │   ├── NotesVaultPage.jsx   ← Home: list + create folders
        │   └── FolderPage.jsx       ← Inside folder: list, upload, delete files
        ├── components/
        │   ├── FolderCard.jsx
        │   ├── FileRow.jsx
        │   ├── CreateFolderModal.jsx
        │   ├── EmptyState.jsx
        │   └── UploadProgress.jsx
        └── styles/
            ├── global.css
            ├── NotesVaultPage.css
            ├── FolderCard.css
            ├── FolderPage.css
            ├── FileRow.css
            ├── Modal.css
            ├── EmptyState.css
            └── UploadProgress.css
```

---

## Step 1 – Firebase Setup

1. Go to https://console.firebase.google.com → Create a project (e.g. `campusos`)
2. Enable **Storage** (Firebase Storage) from the left sidebar
3. Set Storage rules to allow reads/writes (for dev only):
   ```
   rules_version = '2';
   service firebase.storage {
     match /b/{bucket}/o {
       match /{allPaths=**} {
         allow read, write: if true;
       }
     }
   }
   ```
4. Go to **Project Settings → Service Accounts → Generate New Private Key**
5. Download the JSON file, rename it `serviceAccountKey.json`
6. Place it inside the `backend/` folder
7. Note your Storage bucket name (looks like `campusos-xxxx.appspot.com`)

---

## Step 2 – Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

Edit `.env`:
```
FIREBASE_CREDENTIALS_PATH=serviceAccountKey.json
FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
```

Start the server:
```bash
uvicorn main:app --reload --port 8000
```

Verify at: http://localhost:8000/docs (Swagger UI)

---

## Step 3 – Frontend Setup

```bash
cd frontend

npm install

cp .env.example .env
```

`.env` is already set correctly for local dev:
```
VITE_API_URL=http://localhost:8000/api
```

Start dev server:
```bash
npm run dev
```

Open: http://localhost:5173

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/folders` | Create a subject folder |
| GET | `/api/folders` | List all folders |
| POST | `/api/upload-file` | Upload a file (multipart/form-data) |
| GET | `/api/folder/{folder_id}/files` | List files in a folder |
| DELETE | `/api/file/{file_id}` | Delete a file |

### Upload file — form fields
- `folder_id` (string) — UUID of the target folder
- `file` (File) — PDF, JPG, JPEG, PNG, or DOCX (max 20 MB)

---

## Supported File Types

| Extension | MIME Type |
|-----------|-----------|
| PDF | application/pdf |
| JPG/JPEG | image/jpeg |
| PNG | image/png |
| DOCX | application/vnd.openxmlformats-officedocument.wordprocessingml.document |

---

## Moving to a Real Database (Production Upgrade)

The current backend uses a Python dict as an in-memory store. Data resets on every restart.

To persist data, swap `models.py` with **SQLite + SQLAlchemy** (easiest) or **PostgreSQL**.

Minimum change needed: replace the `folders_db` and `files_db` dicts with DB table operations. The route files don't need to change.


