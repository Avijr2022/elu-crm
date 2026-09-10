from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class HandoffResponse(BaseModel):
    handoff_id: UUID
    work_order_id: UUID
    wo_number: str
    opportunity_id: UUID
    customer_id: Optional[UUID]
    status: str
    message: str
