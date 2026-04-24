import sys
import os

# 현재 파일(api/main.py)이 있는 디렉토리를 sys.path의 최상단에 추가
# 이 폴더 안에 app/ 폴더가 있으므로 'from app.main import app'이 가능해짐
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from app.main import app
except ImportError as e:
    # 디버깅을 위한 출력
    print(f"❌ Import failed. Path: {current_dir}")
    print(f"Files in path: {os.listdir(current_dir)}")
    raise e
