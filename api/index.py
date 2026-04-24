import sys
import os

# 현재 파일(api/index.py)의 부모 디렉토리를 기준으로 backend 경로 설정
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend_path = os.path.join(base_path, "backend")

if backend_path not in sys.path:
    sys.path.append(backend_path)

# FastAPI 앱 임포트
try:
    from app.main import app
except ImportError as e:
    print(f"Import Error: {e}")
    print(f"Current sys.path: {sys.path}")
    raise e
