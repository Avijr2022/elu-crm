from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class WorkOrderResponse(BaseModel):
    work_order_id: UUID
    wo_number: str
    opportunity_id: Optional[UUID]
    customer_id: Optional[UUID]
    sales_order_id: Optional[UUID] = None
    so_number: Optional[str] = None
    status: str
    created_on: datetime

    model_config = {"from_attributes": True}


class WorkOrderListResponse(BaseModel):
    items: list[WorkOrderResponse]
    total: int
    page: int
    page_size: int
