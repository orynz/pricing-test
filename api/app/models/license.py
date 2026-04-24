from sqlalchemy import Column, String, ForeignKey, Integer, UUID, DateTime
from app.models.base import Base, TimestampMixin, TenantMixin
import uuid

class License(Base, TimestampMixin, TenantMixin):
    __tablename__ = "licenses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id"))
    license_key = Column(String) # Plain key to show to user once
    license_key_prefix = Column(String, nullable=False) # e.g. SCP-PRO-A7F2
    key_hash = Column(String, unique=True, nullable=False, index=True) # sha256
    status = Column(String, default="active") # active, revoked, expired, refunded
    max_devices = Column(Integer, default=1)
    expires_at = Column(DateTime(timezone=True))
    issued_at = Column(DateTime(timezone=True))
    revoked_at = Column(DateTime(timezone=True))
    polar_license_key_id = Column(String, unique=True, index=True) # If using Polar's license feature
