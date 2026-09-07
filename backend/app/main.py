import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, categories, claims, admin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(
    "AI_MODE=%s  anthropic_key=%s  google_key=%s  env=%s",
    settings.ai_mode,
    "set" if settings.anthropic_api_key else "MISSING",
    "set" if settings.google_ai_api_key else "missing",
    settings.environment,
)

app = FastAPI(title="ExpenseFlow API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(claims.router)
app.include_router(admin.router)


@app.get("/health")
def health():
    return {"status": "ok"}
