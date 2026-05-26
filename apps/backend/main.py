from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from config import FRONTEND_ORIGINS


app = FastAPI(
    title="Sistema de Credito API",
    description="Backend para dashboard, upload de bases, geracao de limites e resultados.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Sistema de Credito API", "docs": "/docs"}
