import sys
import os
sys.path.append(os.getcwd())

from app.core.depends import engine
from app.models.base import Base
from app.models import user, subscription, license, device, plan, order, entitlement, webhook

def force_reset_db():
    print("🗑️ Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("✨ Recreating tables with latest schema...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database reset successfully.")

if __name__ == "__main__":
    force_reset_db()
