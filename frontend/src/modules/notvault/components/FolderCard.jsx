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
