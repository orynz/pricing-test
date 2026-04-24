from sqlalchemy import Column, String, JSON, Boolean, DateTime
from app.models.base import Base, TimestampMixin
import uuid

class WebhookEvent(Base, TimestampMixin):
    __tablename__ = "webhook_events"

    id = Column(String, primary_key=True) # Polar Event ID (e.g. wh_...)
    provider = Column(String, default="polar")
    event_type = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    processed = Column(Boolean, default=False)
    processed_at = Column(DateTime(timezone=True))
    error_message = Column(String)
