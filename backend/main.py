from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from modules.notevault import folders, files

app = FastAPI(title="CampusOS API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Notes Vault routes
app.include_router(folders.router, prefix="/api", tags=["NoteVault - Folders"])
app.include_router(files.router, prefix="/api", tags=["NoteVault - Files"])

# Teammates: add your routers below
# from modules.calendar import routes as calendar_routes
# app.include_router(calendar_routes.router, prefix="/api/calendar", tags=["Calendar"])

@app.get("/")
def root():
    return {"status": "CampusOS API running"}
