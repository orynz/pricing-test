import sys
import os

# backend 디렉토리를 Python 경로에 추가하여 임포트가 가능하게 합니다.
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

# 실제 FastAPI 앱 인스턴스를 가져옵니다.
from app.main import app
