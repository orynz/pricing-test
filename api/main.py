import sys
import os

# 현재 파일의 위치를 기준으로 프로젝트 루트 경로 확보
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
backend_path = os.path.join(project_root, "backend")

# backend 폴더를 sys.path에 추가하여 app.main 임포트 가능하게 설정
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# FastAPI 앱 인스턴스 임포트
try:
    from app.main import app
except ImportError as e:
    print(f"❌ Backend Import Error: {e}")
    print(f"Current sys.path: {sys.path}")
    raise e
