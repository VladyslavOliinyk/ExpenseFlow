from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, categories, claims, admin

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
