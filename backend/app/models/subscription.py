from sqlalchemy import Column, String, DateTime, ForeignKey, UUID, Boolean
from app.models.base import Base, TimestampMixin, TenantMixin
import uuid

class Subscription(Base, TimestampMixin, TenantMixin):
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id"))
    provider = Column(String, default="polar")
    polar_customer_id = Column(String)
    polar_subscription_id = Column(String, unique=True, index=True)
    polar_price_id = Column(String)
    status = Column(String, nullable=False) # active, canceled, trialing, past_due, unpaid
    current_period_start = Column(DateTime(timezone=True))
    current_period_end = Column(DateTime(timezone=True))
    cancel_at_period_end = Column(Boolean, default=False)
    canceled_at = Column(DateTime(timezone=True))
    revoked_at = Column(DateTime(timezone=True))
