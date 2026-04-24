from sqlalchemy import Column, String, Integer, Boolean, UUID
from app.models.base import Base, TimestampMixin
import uuid

class Plan(Base, TimestampMixin):
    __tablename__ = "plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_code = Column(String, unique=True, nullable=False) # free, pro_monthly, pro_yearly, lifetime
    display_name = Column(String, nullable=False)
    billing_type = Column(String, nullable=False) # none, subscription, one_time
    polar_product_id = Column(String, unique=True)
    price_amount = Column(Integer) # in cents
    currency = Column(String, default="USD")
    interval = Column(String) # month, year, None
    entitlement_level = Column(String, nullable=False) # free, pro, lifetime
    max_devices = Column(Integer, default=1)
    max_daily_requests = Column(Integer, default=0)
    offline_access_days = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
