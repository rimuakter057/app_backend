from fastapi import APIRouter

from app.api.v1 import admin, auth, categories, chats, favorites, leads, notifications, owner, properties, reports, users, visits

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(properties.router)
api_router.include_router(categories.router)
api_router.include_router(favorites.router)
api_router.include_router(visits.router)
api_router.include_router(leads.router)
api_router.include_router(chats.router)
api_router.include_router(notifications.router)
api_router.include_router(reports.router)
api_router.include_router(admin.router)
api_router.include_router(owner.router)
