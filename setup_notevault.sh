#!/bin/bash
# Run this from the CAMPUSOS root folder
# bash setup_notevault.sh

echo "Setting up Notes Vault files..."

# ── backend/modules/notevault/__init__.py ─────────────────────────────────────
touch backend/modules/notevault/__init__.py

# ── frontend/src/modules/notvault/services/api.js ────────────────────────────
cat > frontend/src/modules/notvault/services/api.js << 'JSEOF'
import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000/api",
});

export const getFolders = () => api.get("/folders").then((r) => r.data);

export const createFolder = (name) =>
  api.post("/folders", { name }).then((r) => r.data);

export const getFilesInFolder = (folderId) =>
  api.get(`/folder/${folderId}/files`).then((r) => r.data);

export const uploadFile = (folderId, file, onProgress) => {
  const formData = new FormData();
  formData.append("folder_id", folderId);
  formData.append("file", file);
  return api
    .post("/upload-file", formData, {
      headers: { "Content-Type": "multipart/form-data" },
      onUploadProgress: (e) => {
        if (onProgress && e.total) {
          onProgress(Math.round((e.loaded * 100) / e.total));
        }
      },
    })
    .then((r) => r.data);
};

export const deleteFile = (fileId) =>
  api.delete(`/file/${fileId}`).then((r) => r.data);
JSEOF

# ── Components ────────────────────────────────────────────────────────────────
cat > frontend/src/modules/notvault/components/FolderCard.jsx << 'JSEOF'
import "../styles/FolderCard.css";

const FOLDER_COLORS = [
  "#4F7EF7","#E05FA0","#22C55E","#F59E0B",
  "#8B5CF6","#14B8A6","#EF4444","#F97316",
];

function colorFromName(name) {
  let hash = 0;
  for (const ch of name) hash = ch.charCodeAt(0) + ((hash << 5) - hash);
  return FOLDER_COLORS[Math.abs(hash) % FOLDER_COLORS.length];
}

function formatDate(iso) {
  return new Date(iso).toLocaleDateString("en-IN", {
    day: "numeric", month: "short", year: "numeric",
  });
}

export default function FolderCard({ folder, onClick }) {
  const color = colorFromName(folder.name);
  return (
    <button className="folder-card" onClick={onClick}>
      <div className="folder-card__icon" style={{ backgroundColor: color + "22", color }}>
        📁
      </div>
      <div className="folder-card__body">
        <h3 className="folder-card__name">{folder.name}</h3>
        <p className="folder-card__date">Created {formatDate(folder.createdAt)}</p>
      </div>
      <span className="folder-card__arrow">→</span>
    </button>
  );
}
JSEOF

cat > frontend/src/modules/notvault/components/FileRow.jsx << 'JSEOF'
import "../styles/FileRow.css";

const TYPE_ICONS = { pdf:"📕", jpg:"🖼️", jpeg:"🖼️", png:"🖼️", docx:"📘" };

function formatDate(iso) {
  return new Date(iso).toLocaleDateString("en-IN", {
    day: "numeric", month: "short", year: "numeric",
  });
}

export default function FileRow({ file, onDelete, isDeleting }) {
  const icon = TYPE_ICONS[file.fileType] || "📄";
  return (
    <div className={`file-row ${isDeleting ? "file-row--deleting" : ""}`}>
      <span className="file-row__name">
        <span className="file-row__icon">{icon}</span>
        {file.fileName}
      </span>
      <span className="file-row__type">{file.fileType.toUpperCase()}</span>
      <span className="file-row__date">{formatDate(file.uploadedAt)}</span>
      <div className="file-row__actions">
        <a href={file.fileUrl} target="_blank" rel="noopener noreferrer" className="btn btn--sm btn--outline">
          Open
        </a>
        <button className="btn btn--sm btn--danger" onClick={onDelete} disabled={isDeleting}>
          {isDeleting ? "…" : "Delete"}
        </button>
      </div>
    </div>
  );
}
JSEOF

cat > frontend/src/modules/notvault/components/CreateFolderModal.jsx << 'JSEOF'
import { useState } from "react";
import "../styles/Modal.css";

const QUICK_SUBJECTS = ["DBMS","CN","DAA","OS","TOC","SE","COA","DSA"];

export default function CreateFolderModal({ onClose, onCreate }) {
  const [name, setName] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    const trimmed = name.trim();
    if (!trimmed) { setError("Enter a subject name."); return; }
    setLoading(true);
    setError("");
    try {
      await onCreate(trimmed);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleKey = (e) => {
    if (e.key === "Enter") handleSubmit();
    if (e.key === "Escape") onClose();
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal__header">
          <h2>New Subject Folder</h2>
          <button className="modal__close" onClick={onClose}>✕</button>
        </div>
        <div className="modal__body">
          <label className="modal__label">Subject name</label>
          <input
            className="modal__input"
            type="text"
            placeholder="e.g. DBMS, Computer Networks…"
            value={name}
            onChange={(e) => { setName(e.target.value); setError(""); }}
            onKeyDown={handleKey}
            autoFocus
          />
          {error && <p className="modal__error">{error}</p>}
          <div className="modal__chips">
            {QUICK_SUBJECTS.map((s) => (
              <button key={s} className="chip" onClick={() => setName(s)}>{s}</button>
            ))}
          </div>
        </div>
        <div className="modal__footer">
          <button className="btn btn--ghost" onClick={onClose} disabled={loading}>Cancel</button>
          <button className="btn btn--primary" onClick={handleSubmit} disabled={loading}>
            {loading ? "Creating…" : "Create Folder"}
          </button>
        </div>
      </div>
    </div>
  );
}
JSEOF

cat > frontend/src/modules/notvault/components/EmptyState.jsx << 'JSEOF'
import "../styles/EmptyState.css";

export default function EmptyState({ icon, title, description, action }) {
  return (
    <div className="empty-state">
      <span className="empty-state__icon">{icon}</span>
      <h3 className="empty-state__title">{title}</h3>
      <p className="empty-state__desc">{description}</p>
      {action && (
        <button className="btn btn--primary" onClick={action.onClick}>{action.label}</button>
      )}
    </div>
  );
}
JSEOF

cat > frontend/src/modules/notvault/components/UploadProgress.jsx << 'JSEOF'
import "../styles/UploadProgress.css";

export default function UploadProgress({ name, pct }) {
  return (
    <div className="upload-progress">
      <span className="upload-progress__name">⬆ Uploading {name}</span>
      <div className="upload-progress__bar-wrap">
        <div className="upload-progress__bar" style={{ width: `${pct}%` }} />
      </div>
      <span className="upload-progress__pct">{pct}%</span>
    </div>
  );
}
JSEOF

# ── Styles ────────────────────────────────────────────────────────────────────
cat > frontend/src/modules/notvault/styles/global.css << 'CSSEOF'
:root {
  --bg: #0f1117;
  --surface: #181c25;
  --surface-2: #1e2433;
  --border: #2a3045;
  --text: #e8eaf2;
  --text-muted: #7a82a0;
  --accent: #4f7ef7;
  --accent-hover: #6b95ff;
  --danger: #ef4444;
  --danger-hover: #dc2626;
  --radius: 10px;
  --radius-sm: 6px;
  --font: "Inter", system-ui, sans-serif;
  --shadow: 0 2px 12px rgba(0,0,0,0.4);
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
body{font-family:var(--font);background:var(--bg);color:var(--text);min-height:100vh;-webkit-font-smoothing:antialiased;}
a{color:inherit;text-decoration:none;}
.btn{display:inline-flex;align-items:center;gap:6px;padding:9px 18px;border-radius:var(--radius-sm);font-size:14px;font-weight:500;cursor:pointer;border:none;transition:background 0.15s,opacity 0.15s;}
.btn:disabled{opacity:0.5;cursor:not-allowed;}
.btn--primary{background:var(--accent);color:#fff;}
.btn--primary:hover:not(:disabled){background:var(--accent-hover);}
.btn--ghost{background:transparent;color:var(--text-muted);border:1px solid var(--border);}
.btn--ghost:hover:not(:disabled){background:var(--surface-2);color:var(--text);}
.btn--outline{background:transparent;color:var(--accent);border:1px solid var(--accent);}
.btn--outline:hover:not(:disabled){background:var(--accent);color:#fff;}
.btn--danger{background:var(--danger);color:#fff;}
.btn--danger:hover:not(:disabled){background:var(--danger-hover);}
.btn--sm{padding:5px 12px;font-size:13px;}
.loader{text-align:center;color:var(--text-muted);padding:60px 0;font-size:15px;}
.error-banner{background:rgba(239,68,68,0.12);border:1px solid rgba(239,68,68,0.3);color:#fca5a5;border-radius:var(--radius-sm);padding:12px 16px;font-size:14px;display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:16px;}
.error-banner button{background:none;border:none;color:inherit;cursor:pointer;font-size:16px;}
CSSEOF

cat > frontend/src/modules/notvault/styles/NotesVaultPage.css << 'CSSEOF'
.vault-page{max-width:1100px;margin:0 auto;padding:32px 24px;}
.vault-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:36px;}
.vault-header__left{display:flex;align-items:center;gap:14px;}
.vault-logo{font-size:36px;}
.vault-title{font-size:26px;font-weight:700;letter-spacing:-0.5px;}
.vault-subtitle{font-size:13px;color:var(--text-muted);margin-top:2px;}
.folder-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:16px;}
CSSEOF

cat > frontend/src/modules/notvault/styles/FolderCard.css << 'CSSEOF'
.folder-card{display:flex;align-items:center;gap:14px;background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:18px 20px;cursor:pointer;text-align:left;width:100%;transition:border-color 0.15s,transform 0.15s,box-shadow 0.15s;}
.folder-card:hover{border-color:var(--accent);transform:translateY(-2px);box-shadow:var(--shadow);}
.folder-card__icon{font-size:26px;width:48px;height:48px;border-radius:10px;display:grid;place-items:center;flex-shrink:0;}
.folder-card__body{flex:1;overflow:hidden;}
.folder-card__name{font-size:16px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.folder-card__date{font-size:12px;color:var(--text-muted);margin-top:3px;}
.folder-card__arrow{color:var(--text-muted);font-size:18px;flex-shrink:0;}
CSSEOF

cat > frontend/src/modules/notvault/styles/FolderPage.css << 'CSSEOF'
.folder-page{max-width:960px;margin:0 auto;padding:28px 24px;}
.folder-header{display:flex;align-items:center;gap:16px;margin-bottom:28px;flex-wrap:wrap;}
.folder-header__info{display:flex;align-items:center;gap:10px;flex:1;}
.folder-icon{font-size:28px;}
.folder-name{font-size:22px;font-weight:700;}
.file-count{font-size:13px;color:var(--text-muted);background:var(--surface-2);border-radius:20px;padding:2px 10px;}
.file-list{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);overflow:hidden;}
.file-list__header{display:grid;grid-template-columns:1fr 80px 130px 160px;padding:10px 20px;font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:0.6px;color:var(--text-muted);border-bottom:1px solid var(--border);background:var(--surface-2);}
.upload-error{margin:0 0 16px;}
CSSEOF

cat > frontend/src/modules/notvault/styles/FileRow.css << 'CSSEOF'
.file-row{display:grid;grid-template-columns:1fr 80px 130px 160px;align-items:center;padding:14px 20px;border-bottom:1px solid var(--border);transition:background 0.1s,opacity 0.2s;}
.file-row:last-child{border-bottom:none;}
.file-row:hover{background:var(--surface-2);}
.file-row--deleting{opacity:0.4;pointer-events:none;}
.file-row__name{display:flex;align-items:center;gap:10px;font-size:14px;font-weight:500;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;}
.file-row__icon{font-size:20px;flex-shrink:0;}
.file-row__type{font-size:12px;font-weight:600;color:var(--text-muted);}
.file-row__date{font-size:13px;color:var(--text-muted);}
.file-row__actions{display:flex;gap:8px;justify-content:flex-end;}
CSSEOF

cat > frontend/src/modules/notvault/styles/Modal.css << 'CSSEOF'
.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,0.65);display:grid;place-items:center;z-index:100;padding:20px;backdrop-filter:blur(3px);}
.modal{background:var(--surface);border:1px solid var(--border);border-radius:14px;width:100%;max-width:440px;box-shadow:0 8px 40px rgba(0,0,0,0.6);}
.modal__header{display:flex;justify-content:space-between;align-items:center;padding:20px 24px 0;}
.modal__header h2{font-size:18px;font-weight:700;}
.modal__close{background:none;border:none;color:var(--text-muted);font-size:18px;cursor:pointer;line-height:1;}
.modal__close:hover{color:var(--text);}
.modal__body{padding:20px 24px;}
.modal__label{display:block;font-size:13px;font-weight:500;color:var(--text-muted);margin-bottom:8px;}
.modal__input{width:100%;padding:10px 14px;background:var(--surface-2);border:1px solid var(--border);border-radius:var(--radius-sm);color:var(--text);font-size:15px;outline:none;transition:border-color 0.15s;}
.modal__input:focus{border-color:var(--accent);}
.modal__input::placeholder{color:var(--text-muted);}
.modal__error{font-size:13px;color:#fca5a5;margin-top:6px;}
.modal__chips{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px;}
.chip{padding:5px 12px;background:var(--surface-2);border:1px solid var(--border);border-radius:20px;font-size:13px;color:var(--text);cursor:pointer;transition:border-color 0.15s,background 0.15s;}
.chip:hover{border-color:var(--accent);color:var(--accent);background:rgba(79,126,247,0.08);}
.modal__footer{display:flex;justify-content:flex-end;gap:10px;padding:16px 24px;border-top:1px solid var(--border);}
CSSEOF

cat > frontend/src/modules/notvault/styles/EmptyState.css << 'CSSEOF'
.empty-state{display:flex;flex-direction:column;align-items:center;gap:12px;padding:80px 20px;text-align:center;}
.empty-state__icon{font-size:52px;}
.empty-state__title{font-size:18px;font-weight:600;}
.empty-state__desc{font-size:14px;color:var(--text-muted);max-width:340px;line-height:1.6;}
CSSEOF

cat > frontend/src/modules/notvault/styles/UploadProgress.css << 'CSSEOF'
.upload-progress{display:flex;align-items:center;gap:12px;background:rgba(79,126,247,0.1);border:1px solid rgba(79,126,247,0.25);border-radius:var(--radius-sm);padding:10px 16px;margin-bottom:16px;font-size:14px;}
.upload-progress__name{flex-shrink:0;color:var(--accent);max-width:240px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
.upload-progress__bar-wrap{flex:1;height:6px;background:var(--surface-2);border-radius:3px;overflow:hidden;}
.upload-progress__bar{height:100%;background:var(--accent);border-radius:3px;transition:width 0.2s;}
.upload-progress__pct{font-size:13px;color:var(--text-muted);flex-shrink:0;}
CSSEOF

# ── Updated pages with correct import paths ───────────────────────────────────
cat > frontend/src/modules/notvault/pages/NotesVaultPage.jsx << 'JSEOF'
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getFolders, createFolder } from "../services/api";
import FolderCard from "../components/FolderCard";
import CreateFolderModal from "../components/CreateFolderModal";
import EmptyState from "../components/EmptyState";
import "../styles/NotesVaultPage.css";

export default function NotesVaultPage() {
  const [folders, setFolders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const navigate = useNavigate();

  const loadFolders = async () => {
    try {
      setLoading(true);
      const data = await getFolders();
      setFolders(data);
    } catch {
      setError("Couldn't load folders. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadFolders(); }, []);

  const handleCreateFolder = async (name) => {
    try {
      const newFolder = await createFolder(name);
      setFolders((prev) => [newFolder, ...prev]);
      setShowModal(false);
    } catch (err) {
      throw new Error(err.response?.data?.detail || "Failed to create folder");
    }
  };

  return (
    <div className="vault-page">
      <header className="vault-header">
        <div className="vault-header__left">
          <span className="vault-logo">📚</span>
          <div>
            <h1 className="vault-title">Notes Vault</h1>
            <p className="vault-subtitle">{folders.length} subject{folders.length !== 1 ? "s" : ""}</p>
          </div>
        </div>
        <button className="btn btn--primary" onClick={() => setShowModal(true)}>+ New Subject</button>
      </header>
      <main className="vault-content">
        {loading && <div className="loader">Loading folders…</div>}
        {error && <div className="error-banner">{error}</div>}
        {!loading && !error && folders.length === 0 && (
          <EmptyState
            icon="🗂️"
            title="No subjects yet"
            description="Create your first subject folder — DBMS, CN, OS, whatever you need."
            action={{ label: "+ New Subject", onClick: () => setShowModal(true) }}
          />
        )}
        {!loading && !error && folders.length > 0 && (
          <div className="folder-grid">
            {folders.map((folder) => (
              <FolderCard
                key={folder.id}
                folder={folder}
                onClick={() => navigate(`/notevault/folder/${folder.id}`, { state: { folder } })}
              />
            ))}
          </div>
        )}
      </main>
      {showModal && <CreateFolderModal onClose={() => setShowModal(false)} onCreate={handleCreateFolder} />}
    </div>
  );
}
JSEOF

cat > frontend/src/modules/notvault/pages/FolderPage.jsx << 'JSEOF'
import { useState, useEffect, useRef } from "react";
import { useParams, useLocation, useNavigate } from "react-router-dom";
import { getFilesInFolder, uploadFile, deleteFile } from "../services/api";
import FileRow from "../components/FileRow";
import EmptyState from "../components/EmptyState";
import UploadProgress from "../components/UploadProgress";
import "../styles/FolderPage.css";

const ACCEPTED = ".pdf,.jpg,.jpeg,.png,.docx";

export default function FolderPage() {
  const { folderId } = useParams();
  const { state } = useLocation();
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  const folderName = state?.folder?.name || "Folder";

  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(null);
  const [uploadError, setUploadError] = useState(null);
  const [deletingId, setDeletingId] = useState(null);

  const loadFiles = async () => {
    try {
      setLoading(true);
      const data = await getFilesInFolder(folderId);
      setFiles(data);
    } catch {
      setError("Couldn't load files.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadFiles(); }, [folderId]);

  const handleFileChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploadError(null);
    setUploadProgress({ name: file.name, pct: 0 });
    try {
      const newFile = await uploadFile(folderId, file, (pct) =>
        setUploadProgress({ name: file.name, pct })
      );
      setFiles((prev) => [newFile, ...prev]);
    } catch (err) {
      setUploadError(err.response?.data?.detail || "Upload failed. Check file type and size.");
    } finally {
      setUploadProgress(null);
      e.target.value = "";
    }
  };

  const handleDelete = async (fileId) => {
    if (!confirm("Delete this file? This cannot be undone.")) return;
    setDeletingId(fileId);
    try {
      await deleteFile(fileId);
      setFiles((prev) => prev.filter((f) => f.id !== fileId));
    } catch {
      alert("Delete failed. Try again.");
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="folder-page">
      <header className="folder-header">
        <button className="btn btn--ghost" onClick={() => navigate("/notevault")}>← Back</button>
        <div className="folder-header__info">
          <span className="folder-icon">📁</span>
          <h1 className="folder-name">{folderName}</h1>
          <span className="file-count">{files.length} file{files.length !== 1 ? "s" : ""}</span>
        </div>
        <button className="btn btn--primary" onClick={() => fileInputRef.current?.click()}>↑ Upload File</button>
        <input ref={fileInputRef} type="file" accept={ACCEPTED} style={{ display: "none" }} onChange={handleFileChange} />
      </header>
      {uploadProgress && <UploadProgress name={uploadProgress.name} pct={uploadProgress.pct} />}
      {uploadError && (
        <div className="error-banner upload-error">
          ⚠ {uploadError}
          <button onClick={() => setUploadError(null)}>✕</button>
        </div>
      )}
      <main className="folder-content">
        {loading && <div className="loader">Loading files…</div>}
        {error && <div className="error-banner">{error}</div>}
        {!loading && !error && files.length === 0 && (
          <EmptyState
            icon="📄"
            title="No files yet"
            description={`Upload PDFs, images, or DOCX files into ${folderName}.`}
            action={{ label: "↑ Upload File", onClick: () => fileInputRef.current?.click() }}
          />
        )}
        {!loading && !error && files.length > 0 && (
          <div className="file-list">
            <div className="file-list__header">
              <span>Name</span><span>Type</span><span>Uploaded</span><span>Actions</span>
            </div>
            {files.map((file) => (
              <FileRow key={file.id} file={file} isDeleting={deletingId === file.id} onDelete={() => handleDelete(file.id)} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
JSEOF

# ── Shared App.jsx with module routes ────────────────────────────────────────
cat > frontend/src/App.jsx << 'JSEOF'
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import NotesVaultPage from "./modules/notvault/pages/NotesVaultPage";
import FolderPage from "./modules/notvault/pages/FolderPage";
import "./modules/notvault/styles/global.css";

// Teammates: import your pages here and add a <Route> below

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/notevault" replace />} />

        {/* ── Notes Vault ── */}
        <Route path="/notevault" element={<NotesVaultPage />} />
        <Route path="/notevault/folder/:folderId" element={<FolderPage />} />

        {/* ── Add teammate routes below this line ── */}
        {/* <Route path="/calendar" element={<CalendarPage />} /> */}
        {/* <Route path="/examprep" element={<ExamPrepPage />} /> */}
      </Routes>
    </BrowserRouter>
  );
}
JSEOF

# ── Backend __init__ files ────────────────────────────────────────────────────
touch backend/modules/__init__.py
touch backend/modules/notevault/__init__.py

# ── Updated backend main.py ───────────────────────────────────────────────────
cat > backend/main.py << 'PYEOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from modules.notevault import folders, files

app = FastAPI(title="CampusOS API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Notes Vault routes
app.include_router(folders.router, prefix="/api", tags=["NoteVault - Folders"])
app.include_router(files.router, prefix="/api", tags=["NoteVault - Files"])

# Teammates: add your routers below
# from modules.calendar import routes as calendar_routes
# app.include_router(calendar_routes.router, prefix="/api/calendar", tags=["Calendar"])

@app.get("/")
def root():
    return {"status": "CampusOS API running"}
PYEOF

echo ""
echo "✅ Done! All files created."
echo ""
echo "Next steps:"
echo "  1. cd backend && pip install -r requirements.txt"
echo "  2. Add your .env file (copy from .env.example)"
echo "  3. uvicorn main:app --reload"
echo "  4. cd frontend && npm install && npm run dev"
EOF