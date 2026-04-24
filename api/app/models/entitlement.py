from sqlalchemy import Column, String, ForeignKey, UUID, DateTime, JSON
from app.models.base import Base, TimestampMixin
import uuid

class EntitlementSnapshot(Base, TimestampMixin):
    __tablename__ = "entitlement_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    plan_code = Column(String, nullable=False)
    entitlement_level = Column(String, nullable=False)
    source = Column(String, nullable=False) # polar, admin, system
    status = Column(String, nullable=False) # active, expired, revoked
    features = Column(JSON, nullable=False)
    valid_until = Column(DateTime(timezone=True))
