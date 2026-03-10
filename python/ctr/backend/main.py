from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.api.routers import data, jobs

import os

app = FastAPI(title="CTR Data Pipeline API")

# Mount Vite static assets
app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")

app.include_router(data.router)
app.include_router(jobs.router)

@app.get("/{full_path:path}")
def serve_frontend(full_path: str):
    # Support React Router SPA
    return FileResponse("frontend/dist/index.html")
