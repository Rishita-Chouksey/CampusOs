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
