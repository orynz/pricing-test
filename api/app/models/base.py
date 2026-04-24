from sqlalchemy import Column, DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, declared_attr
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID

class Base(DeclarativeBase):
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class TenantMixin:
    project_id = Column(String, nullable=False, index=True)
