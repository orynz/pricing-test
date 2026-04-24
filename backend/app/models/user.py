from sqlalchemy import Column, String, Enum, UUID
from app.models.base import Base, TimestampMixin, TenantMixin
import uuid

class User(Base, TimestampMixin, TenantMixin):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    supabase_user_id = Column(UUID(as_uuid=True), unique=True, index=True, nullable=False)
    email = Column(String, index=True)
    name = Column(String)
    status = Column(String, default="active") # active, suspended, deleted
