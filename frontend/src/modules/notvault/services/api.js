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
