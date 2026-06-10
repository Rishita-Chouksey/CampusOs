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
