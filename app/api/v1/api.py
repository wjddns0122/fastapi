from fastapi import APIRouter

from app.api.v1.activities import router as activities_router
from app.api.v1.auth import router as auth_router
from app.api.v1.compatibility import router as compatibility_router
from app.api.v1.relationships import router as relationships_router
from app.api.v1.users import router as users_router

api_router = APIRouter()
api_router.include_router(activities_router, tags=["activities"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(compatibility_router, prefix="/compatibility", tags=["compatibility"])
api_router.include_router(relationships_router, prefix="/relationships", tags=["relationships"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
