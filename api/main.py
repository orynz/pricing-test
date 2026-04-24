import sys
import os

# api 폴더를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# app 패키지 내부에서 FastAPI 인스턴스 가져오기
from app.main import app as fastapi_app

# Vercel이 찾을 수 있도록 최상단 레벨에 app 변수 할당
app = fastapi_app
