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
