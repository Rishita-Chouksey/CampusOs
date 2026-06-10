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
