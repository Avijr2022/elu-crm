from fastapi import APIRouter

from app.api.v1 import auth
from app.api.v1.crm import activities as crm_activities
from app.api.v1.crm import customers as crm_customers
from app.api.v1.crm import leads as crm_leads
from app.api.v1.crm import lookups as crm_lookups
from app.api.v1.crm import opportunities as crm_opportunities
from app.api.v1.pf import branding as pf_branding
from app.api.v1.pf import editions as pf_editions
from app.api.v1.pf import organizations as pf_organizations
from app.api.v1.pf import subscriptions as pf_subscriptions
from app.api.v1.pf import tenants as pf_tenants
from app.api.v1.fin import payment_receipts as fin_payment_receipts
from app.api.v1.prj import handoffs as prj_handoffs
from app.api.v1.prj import work_orders as prj_work_orders
from app.api.v1.sal import quotations as sal_quotations
from app.api.v1.sal import sales_orders as sal_sales_orders
from app.api.v1.integrations import deepseek as integrations_deepseek

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(pf_editions.router)
api_router.include_router(pf_branding.router)
api_router.include_router(pf_tenants.router)
api_router.include_router(pf_subscriptions.router)
api_router.include_router(pf_organizations.router)
api_router.include_router(crm_leads.router)
api_router.include_router(crm_opportunities.router)
api_router.include_router(crm_customers.router)
api_router.include_router(crm_activities.router)
api_router.include_router(crm_lookups.router)
api_router.include_router(sal_quotations.router)
api_router.include_router(sal_sales_orders.router)
api_router.include_router(fin_payment_receipts.router)
api_router.include_router(prj_handoffs.router)
api_router.include_router(prj_work_orders.router)
api_router.include_router(integrations_deepseek.router)
