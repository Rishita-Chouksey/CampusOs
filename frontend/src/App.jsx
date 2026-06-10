import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import NotesVaultPage from "./modules/notevault/pages/NotesVaultPage";
import FolderPage from "./modules/notevault/pages/FolderPage";
import "./modules/notevault/styles/global.css";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/notevault" replace />} />
        <Route path="/notevault" element={<NotesVaultPage />} />
        <Route path="/notevault/folder/:folderId" element={<FolderPage />} />
      </Routes>
    </BrowserRouter>
  );
}