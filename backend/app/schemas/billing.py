from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from uuid import UUID

class PlanSchema(BaseModel):
    id: UUID
    plan_code: str
    display_name: str
    billing_type: str
    price_amount: int
    currency: str
    interval: Optional[str]
    max_devices: int
    
    class Config:
        from_attributes = True

class CheckoutRequest(BaseModel):
    plan_code: str
    success_url: str

class CheckoutResponse(BaseModel):
    url: str
    checkout_id: str
