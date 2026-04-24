from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class DashboardSummary(BaseModel):
    user_email: Optional[str]
    current_plan: Optional[str]
    subscription_status: Optional[str]
    active_licenses_count: int
    active_devices_count: int

class DeviceInfo(BaseModel):
    id: UUID
    device_name: Optional[str]
    platform: Optional[str]
    device_fingerprint: str
    last_seen_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

class LicenseInfo(BaseModel):
    id: UUID
    license_key_prefix: str
    status: str
    issued_at: Optional[datetime]
    expires_at: Optional[datetime]
    max_devices: int
    active_devices_count: int

    class Config:
        from_attributes = True
