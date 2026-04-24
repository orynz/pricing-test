# Secure Core Platform (FastAPI Backend)

이 프로젝트는 1인 개발자를 위한 재사용 가능한 핵심 인프라(인증, 결제, 라이선스, 보안) 보일러플레이트입니다. 단일 백엔드로 여러 프로젝트를 지원하는 멀티 테넌트 구조를 가집니다.

## 🚀 주요 기능

- **멀티 테넌트:** Header의 `x-project-id`를 통해 다중 앱 서비스 지원
- **인증:** Supabase Auth JWT 연동 및 자동 유저 동기화
- **결제:** Polar.sh 기반 글로벌 결제 및 구독 관리 (MoR 지원)
- **라이선스:** 기기 귀속(Node-locked) 방식 및 AES-256-GCM 암호화 검증 API
- **보안:** 애플리케이션 레벨의 E2E 페이로드 암호화로 패킷 스니핑 방지

## 🛠 시작하기

### 1. 의존성 설치 (uv 사용)
```bash
uv sync
```

### 2. 환경 변수 설정
`.env.example` 파일을 복사하여 `.env` 파일을 생성하고 필요한 키들을 입력합니다.
```bash
cp .env.example .env
```

### 3. 데이터베이스 마이그레이션
```bash
uv run alembic upgrade head
```

### 4. 서버 실행
```bash
uv run uvicorn app.main:app --reload
```

## 🔐 보안 가이드 (데스크톱 앱)

데스크톱 앱에서 라이선스 검증 시 `/api/v1/license/validate-secure` 엔드포인트를 사용하세요. 모든 요청과 응답 데이터는 `.env`에 설정된 `AES_SECRET_KEY`를 이용해 암복호화되어야 합니다.

## 📁 프로젝트 구조

- `app/core`: 보안, 설정, 의존성 주입 등 핵심 로직
- `app/modules`: 기능별 라우터 (auth, billing, license, dashboard, admin, webhooks)
- `app/models`: SQLAlchemy DB 모델
- `app/schemas`: Pydantic 데이터 검증 모델
- `client_example`: 데스크톱 앱 연동을 위한 보안 SDK 예제
