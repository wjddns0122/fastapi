from fastapi import APIRouter

from app.api.v1.activities import router as activities_router
from app.api.v1.auth import router as auth_router
from app.api.v1.compatibility import router as compatibility_router
from app.api.v1.internal import router as internal_router
from app.api.v1.letters import router as letters_router
from app.api.v1.missions import router as missions_router
from app.api.v1.relationships import router as relationships_router
from app.api.v1.reports import router as reports_router
from app.api.v1.tarot import router as tarot_router
from app.api.v1.users import router as users_router

api_router = APIRouter()
api_router.include_router(activities_router, tags=["activities"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(compatibility_router, prefix="/compatibility", tags=["compatibility"])
api_router.include_router(internal_router, prefix="/internal", tags=["internal"])
api_router.include_router(letters_router, prefix="/letters", tags=["letters"])
api_router.include_router(missions_router, prefix="/missions", tags=["missions"])
api_router.include_router(relationships_router, prefix="/relationships", tags=["relationships"])
api_router.include_router(reports_router, prefix="/reports", tags=["reports"])
api_router.include_router(tarot_router, prefix="/tarot", tags=["tarot"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
