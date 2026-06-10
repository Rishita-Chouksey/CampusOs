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
