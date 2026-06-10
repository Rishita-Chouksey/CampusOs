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
