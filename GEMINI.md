# GEMINI.md - Project Instructional Context

## 1. Project Overview
이 프로젝트는 **멀티테넌트(Multi-tenant) 기반의 소프트웨어 라이선스 관리 플랫폼**입니다. 사용자가 Google 로그인을 통해 접속하고, Polar.sh를 통해 요금제를 구독하거나 평생 라이선스를 구매하며, 발급된 라이선스 키를 통해 데스크톱/모바일 앱의 권한을 제어하는 전체 생태계를 포함합니다.

### 핵심 스택
- **Frontend**: React (Vite), TypeScript, Axios, Supabase Auth SDK
- **Backend**: FastAPI, SQLAlchemy (PostgreSQL), PyJWT (ES256 Verification), Polar SDK
- **Authentication**: Supabase Auth (Google OAuth) + JWT 검증
- **Payment**: Polar.sh (Sandbox & Webhooks)
- **Deployment & Env**: uv (Python Package Manager), IPv4 Transaction Pooler (Supabase)

---

## 2. Architecture & Design Principles

### 2.1 결제 및 권한 분리 (POLAR_PLAN_LIFECYCLE.md 준수)
- **결제의 진실은 Polar**: 실제 구독 상태 및 결제 성공 여부는 Polar.sh의 데이터를 원천으로 합니다.
- **권한의 진실은 내부 DB**: 앱 기능 접근 권한은 백엔드 DB(`public.users`, `subscriptions`, `licenses`)에서 최종 결정합니다.
- **Webhook 중심**: 결제 완료 시 백엔드 Webhook 엔드포인트에서 라이선스를 자동 생성하고 DB를 동기화합니다.

### 2.2 인증 흐름
- 클라이언트는 Supabase에서 발급받은 JWT를 `Authorization: Bearer` 헤더에 담아 전송합니다.
- 모든 요청에는 `x-project-id` 헤더가 필수이며, 이는 테넌트 구분에 사용됩니다.
- 백엔드는 Supabase의 JWKS 엔드포인트를 통해 실시간으로 `ES256` 토큰을 검증합니다.

---

## 3. Building and Running

### Backend
```bash
cd backend
# 의존성 설치
uv pip install -r pyproject.toml
# DB 초기화 (테이블 생성)
uv run init_db.py
# 요금제 데이터 삽입
uv run seed_plans.py
# 서버 실행
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 4. Development Conventions

### 4.1 데이터베이스 (SQLAlchemy)
- **자동 초기화**: `app/main.py` 구동 시 `Base.metadata.create_all`이 실행되어 최신 모델 구조를 반영합니다.
- **UUID 사용**: 모든 기본 키(`id`)와 외부 키는 `UUID` 타입을 사용합니다. (Supabase ID와 호환성 유지)
- **Tenant Isolation**: 모든 비즈니스 모델은 `TenantMixin`을 상속받아 `project_id` 필드를 포함해야 합니다.

### 4.2 API 및 보안
- **JWT 검증**: `app.core.depends.get_current_user` 의존성을 사용하여 인증을 수행합니다.
- **암호화**: 라이선스 검증 등 보안이 필요한 데이터는 `app.core.security.cipher` (AES-256-GCM)를 사용하여 암호화 통신합니다.

### 4.3 Webhooks
- Polar 웹훅 처리 시 `WebhookEvent` 테이블에 원본 페이로드를 저장하여 Idempotency(중복 처리 방지)를 보장합니다.

---

## 5. Key Documentation References
- **AUTH_GUIDE.md**: 로그인 흐름 및 JWT 검증 이슈 해결 내역
- **POLAR_PLAN_LIFECYCLE.md**: 요금제 정의 및 라이프사이클 상세 설계
- **PRD.md / TRD.md**: 비즈니스 요구사항 및 기술 설계서
- **TASKS.md**: 현재 진행 중인 작업 목록 및 로드맵
