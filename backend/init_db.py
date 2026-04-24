import sys
import os
# SQLAlchemy 모델들을 로드하기 위해 현재 경로를 파이썬 경로에 추가
sys.path.append(os.getcwd())

from app.core.depends import engine
from app.models.base import Base
# 모든 모델을 명시적으로 임포트해야 create_all이 이를 인식합니다.
from app.models import user, subscription, license, device, plan, order, entitlement, webhook

def init_db():
    print("🚀 Initializing Database...")
    try:
        # Base.metadata.create_all 사용
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully.")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    init_db()
