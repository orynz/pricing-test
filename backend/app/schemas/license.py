from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class LicenseBase(BaseModel):
    license_key: str
    project_id: str

class LicenseActivateRequest(BaseModel):
    license_key: str
    fingerprint: str
    device_name: Optional[str] = None
    platform: Optional[str] = None

class LicenseValidateRequest(BaseModel):
    license_key: str
    fingerprint: str

class EncryptedPayload(BaseModel):
    payload: str # AES-256-GCM encrypted base64 string

class LicenseResponse(BaseModel):
    id: UUID
    status: str
    device_limit: int
    created_at: datetime

    class Config:
        from_attributes = True
