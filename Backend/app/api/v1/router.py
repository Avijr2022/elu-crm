from fastapi import APIRouter

from app.api.v1 import auth
from app.api.v1.crm import leads as crm_leads
from app.api.v1.crm import opportunities as crm_opportunities
from app.api.v1.pf import editions as pf_editions
from app.api.v1.pf import organizations as pf_organizations
from app.api.v1.pf import subscriptions as pf_subscriptions
from app.api.v1.pf import tenants as pf_tenants

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(pf_editions.router)
api_router.include_router(pf_tenants.router)
api_router.include_router(pf_subscriptions.router)
api_router.include_router(pf_organizations.router)
api_router.include_router(crm_leads.router)
api_router.include_router(crm_opportunities.router)
