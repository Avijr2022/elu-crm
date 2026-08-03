from fastapi import APIRouter

from app.api.v1 import auth
from app.api.v1.crm import leads as crm_leads
from app.api.v1.crm import opportunities as crm_opportunities

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(crm_leads.router)
api_router.include_router(crm_opportunities.router)
