from fastapi import APIRouter

from app.api.routes.auth_routes import router as auth_router
from app.api.routes.job_routes import router as job_router
from app.api.routes.note_routes import router as note_router


api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(note_router)
api_router.include_router(job_router)
