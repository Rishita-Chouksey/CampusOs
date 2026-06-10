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
