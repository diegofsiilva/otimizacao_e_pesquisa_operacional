"""
app/backend/main.py
Ponto de entrada da aplicação FastAPI.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response

from api.routes import router
from api.upload_routes import router as upload_router
from config import FRONTEND_ORIGINS
from db.storage import close_pool, init_pool

BACKEND_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BACKEND_DIR.parent / "frontend"
FRONTEND_INDEX = FRONTEND_DIR / "index.html"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa e encerra recursos da aplicação."""
    await init_pool()
    yield
    await close_pool()


app = FastAPI(
    title="Sistema de Credito API",
    description="Backend para cockpit, upload de bases, geracao de limites e resultados.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)

app.include_router(router, prefix="/api")
app.include_router(upload_router, prefix="/api")


def _safe_frontend_path(path: str) -> Path | None:
    candidate = (FRONTEND_DIR / path).resolve()
    frontend_root = FRONTEND_DIR.resolve()
    if frontend_root not in candidate.parents and candidate != frontend_root:
        return None
    return candidate if candidate.is_file() else None


@app.get("/", include_in_schema=False)
def frontend_root():
    if FRONTEND_INDEX.exists():
        return FileResponse(FRONTEND_INDEX)
    return {"message": "Sistema de Credito API", "docs": "/docs"}


@app.get("/runtime-config.js", include_in_schema=False)
def runtime_config() -> Response:
    return Response(
        'window.API_BASE_URL = "/api";\n',
        media_type="application/javascript",
    )


@app.get("/{path:path}", include_in_schema=False)
def frontend_static(path: str):
    if path.startswith("api/") or path in {"docs", "openapi.json", "redoc"}:
        raise HTTPException(status_code=404, detail="Not found")

    static_file = _safe_frontend_path(path)
    if static_file is not None:
        return FileResponse(static_file)

    if FRONTEND_INDEX.exists():
        return FileResponse(FRONTEND_INDEX)

    raise HTTPException(status_code=404, detail="Frontend nao encontrado.")
