import sys
import os

# 현재 파일의 부모의 부모가 프로젝트 루트
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend_path = os.path.join(project_root, "backend")

if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# FastAPI 앱 임포트
try:
    from app.main import app
except ImportError as e:
    # 에러 발생 시 로그에 남기기 위해 출력
    print(f"CRITICAL: Module app.main not found. backend_path: {backend_path}")
    print(f"sys.path: {sys.path}")
    raise e
