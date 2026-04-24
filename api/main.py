import sys
import os

# 현재 api 폴더를 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 이제 바로 app.main 임포트 가능
try:
    from app.main import app
except ImportError as e:
    print(f"Import Error: {e}")
    raise e
