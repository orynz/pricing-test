from sqlalchemy import Column, String, Integer, ForeignKey, UUID, DateTime
from app.models.base import Base, TimestampMixin, TenantMixin
import uuid

class Order(Base, TimestampMixin, TenantMixin):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id"))
    provider = Column(String, default="polar")
    polar_order_id = Column(String, unique=True)
    polar_checkout_id = Column(String)
    amount = Column(Integer)
    currency = Column(String)
    status = Column(String, nullable=False) # created, paid, refunded
    paid_at = Column(DateTime(timezone=True))
    refunded_at = Column(DateTime(timezone=True))
