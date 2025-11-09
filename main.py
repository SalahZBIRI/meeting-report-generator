

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import report_router
from app.core.config import settings
from fastapi import APIRouter

health_router = APIRouter()

@health_router.get("/health", tags=["system"])
async def health():
    return {"status": "ok"}

app = FastAPI(
    title="Meeting Report Generator",
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure ton router
app.include_router(report_router.router)
app.include_router(health_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
