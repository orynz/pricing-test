from sqlalchemy import Column, String, ForeignKey, DateTime, func, UUID
from app.models.base import Base, TimestampMixin
import uuid

class Device(Base, TimestampMixin):
    __tablename__ = "devices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    license_id = Column(UUID(as_uuid=True), ForeignKey("licenses.id"), nullable=False)
    device_fingerprint = Column(String, nullable=False, index=True)
    platform = Column(String) # windows, macos, linux, etc.
    device_name = Column(String)
    last_seen_at = Column(DateTime(timezone=True), onupdate=func.now())
