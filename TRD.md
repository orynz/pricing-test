# Technical Requirements Document (TRD)
# Reusable Secure Core Platform

## 1. 시스템 개요

모바일 앱, 데스크톱 앱, 신규 SaaS 프로젝트에서 공통으로 사용할 수 있는 인증 / 결제 / 라이선스 / 대시보드 / 관리자 기능을 제공하는 재사용형 백엔드 플랫폼이다.

**핵심 목적:**
- 중복 개발 제거 및 빠른 신규 서비스 출시
- 공통 보안 정책 적용 (특히 데스크톱 앱 패킷 스니핑 방지)
- 모바일/데스크톱 동시 지원
- 단일 백엔드로 여러 앱을 서비스할 수 있는 **Multi-tenant(다중 프로젝트) 구조 지원**
- 확장 가능한 모듈 구조

---

## 2. 전체 아키텍처

~~~text
Mobile App (Flutter)
Desktop App (PySide6/Tauri)
Web Dashboard (Next.js)

        ↓ HTTPS / TLS 1.3 ( + App-Level Payload Encryption )

Reverse Proxy
(Nginx / Caddy / Cloudflare)

        ↓ 

FastAPI Core Backend (Managed by `uv`)
 ├── Auth Module (Supabase JWT Sync)
 ├── Billing Module (Polar Checkout)
 ├── License Module (Node-locked & Offline)
 ├── Dashboard Module
 ├── Admin Module
 ├── Security Module (AES-GCM & Signature Validate)
 └── Webhook Module (Polar Event Receiver)

        ↓

PostgreSQL (Supabase)
Redis (Rate Limit & Caching)
~~~

---

## 3. 기술 스택

### Backend
- **Python Package Manager:** `uv` (빠른 의존성 관리 및 가상환경 구축)
- **Framework:** FastAPI
- **ORM / DB Toolkit:** SQLAlchemy, Alembic
- **Validation:** Pydantic v2
- **HTTP Client:** httpx
- **Caching/Queue:** Redis, Celery / RQ (또는 FastAPI BackgroundTasks 활용)

### Authentication & Database
- Supabase Auth (JWT Provider)
- PostgreSQL (Supabase 연동)

### Billing & MoR
- Polar.sh (결제, 글로벌 세금, 라이선스 키 생성)

### Client
- Flutter (Mobile)
- PySide6 / Tauri / Electron (Desktop)
- Next.js (Dashboard)

---

## 4. 프로젝트 구조

~~~text
backend/
 ├── pyproject.toml       # uv 설정 파일
 ├── .env                 # 환경변수 (Supabase, Polar Keys)
 ├── app/
 │   ├── main.py
 │   ├── core/
 │   │   ├── config.py
 │   │   ├── security.py  # AES-256-GCM 페이로드 암복호화, Webhook 서명 검증
 │   │   └── depends.py   # JWT 토큰 검증 및 Tenant(Project ID) 주입
 │   │
 │   ├── modules/
 │   │   ├── auth/
 │   │   ├── billing/     # Polar API 연동 (Checkout)
 │   │   ├── license/
 │   │   ├── dashboard/
 │   │   ├── admin/
 │   │   └── webhooks/    # Polar Webhook 수신 엔드포인트
 │   │
 │   ├── middleware/      # Payload 암호화/복호화 미들웨어
 │   ├── schemas/         # Pydantic Models
 │   ├── models/          # SQLAlchemy Models
 │   └── services/
 │
 ├── tests/
 ├── alembic/
 └── docker-compose.yml
~~~

---

## 5. 모듈 설계

**[중요] 모든 API 호출 시 Header에 `x-project-id`를 포함하여 Multi-tenant(다중 프로젝트)를 식별한다.**

### A. Auth Module
**기능:** 회원가입, 로그인, 로그아웃, 토큰 검증, 세션 갱신
**API:**
~~~text
POST /auth/login (Supabase Proxy or Direct)
POST /auth/logout
GET  /auth/me
~~~

### B. Billing Module (Polar 연동)
**기능:** 상품 플랜 조회, Polar Checkout URL 생성, 구독 취소
**API:**
~~~text
GET  /billing/plans
POST /billing/checkout
GET  /billing/subscription
POST /billing/cancel
~~~

### C. License Module
**기능:** 라이선스 활성화, 기기 인증(Node-locked), 오프라인 암호화 토큰 발급
**API:**
~~~text
POST /license/activate   (Client HWID 전송 -> Polar 검증 -> DB 저장)
POST /license/validate   (앱 실행 시 검증 - E2E 암호화 필수 적용 API)
POST /license/deactivate
GET  /license/list
~~~

### D. Webhook Module (Polar -> FastAPI)
**기능:** Polar 결제 및 구독 상태 변경 이벤트를 수신하여 DB 동기화
**API:**
~~~text
POST /webhooks/polar  (Signature Header 검증 필수)
~~~

---

## 6. 데이터베이스 설계 (Multi-tenant 반영)

모든 주요 테이블에 `project_id`를 추가하여 하나의 백엔드에서 여러 서비스를 분리 관리한다.

~~~sql
-- users
id uuid primary key
project_id text not null
supabase_user_id uuid unique
email text
name text
status text
created_at timestamp

-- subscriptions
id uuid primary key
project_id text not null
user_id uuid references users(id)
polar_subscription_id text unique
polar_price_id text
status text
current_period_end timestamp
created_at timestamp

-- licenses
id uuid primary key
project_id text not null
user_id uuid references users(id)
polar_license_key_id text unique
key_hash text -- DB 유출 시 방어를 위한 해시 저장
device_limit integer
status text
created_at timestamp

-- devices
id uuid primary key
license_id uuid references licenses(id)
device_fingerprint text -- 하드웨어 고유 ID
platform text
device_name text
last_seen_at timestamp
created_at timestamp
~~~

---

## 7. 인증 및 인가 설계

클라이언트는 Supabase Auth에서 발급받은 JWT를 Bearer Token으로 전송한다.

FastAPI의 `Depends`에서 매 요청마다 다음을 수행한다:
1. `x-project-id` 헤더 존재 확인
2. Supabase Public Key로 JWT 서명 검증 (비대칭 키 검증)
3. 만료시간(exp) 및 발급자(iss) 검증
4. 토큰의 `sub` (User ID)를 기반으로 DB 사용자 동기화 및 인가(Role/Project 권한) 체크

---

## 8. 암호화 설계 (Security Deep Dive)

### 1. API 페이로드 암호화 (Application-Level E2E)
**목적:** Charles Proxy, Wireshark 등을 이용한 데스크톱 앱 라이선스 검증 우회 방지
**적용 대상:** `/license/validate`, `/license/activate` 등 민감한 API
**방식:**
- 클라이언트(데스크톱 앱)와 서버는 사전에 공유된 Secret 혹은 동적 Key Exchange를 통해 암호화 키를 보유.
- 클라이언트가 `{"hwid": "...", "key": "..."}` 데이터를 **AES-256-GCM**으로 암호화하여 전송.
- FastAPI `PayloadEncryptionMiddleware`가 이를 복호화하여 처리하고, 응답 데이터(프리미엄 권한 여부)도 암호화하여 반환.

### 2. Webhook 서명 검증
- Polar에서 들어오는 POST 요청은 헤더에 포함된 `StandardWebhooks` 서명과 서버에 저장된 `POLAR_WEBHOOK_SECRET`을 대조하여 위변조 여부를 100% 검증한다.

### 3. 저장 구간 (DB)
- API Keys, License Search Token 등은 평문으로 저장하지 않고 `bcrypt` 또는 `Argon2id`로 단방향 해시 처리하여 저장 (`key_hash`).

---

## 9. 미들웨어 및 의존성 설계

~~~text
1. Request ID Middleware (추적 용이)
2. Rate Limit Middleware (Redis 활용, Brute-force 방지)
3. Tenant Middleware (Header에서 x-project-id 파싱 및 검증)
4. Payload Encryption Middleware (특정 엔드포인트 바디 암/복호화 처리)
5. Error Handler Middleware (내부 에러 스택 트레이스 노출 방지)
~~~

---

## 10. Background Worker

비동기 작업 (Celery 또는 FastAPI BackgroundTasks 활용):
~~~text
- Email 전송 큐
- Expired Subscription 주기적 DB 정리 배치
- Polar Webhook 처리 실패 시 Retry 로직
- Nightly Reports (관리자용 일일 요약 생성)
~~~

---

## 11. 클라이언트 연동 방식

### Flutter (Mobile)
- `flutter_secure_storage`에 Supabase JWT 및 기기 인증 정보 저장
- 결제 시 `url_launcher` 또는 WebView를 통해 Polar Checkout 연결

### PySide6 / Desktop 앱
- OS Native Secure Storage (Windows Credential Manager / macOS Keychain)에 토큰 저장
- `uuid` 및 `wmi`(Windows) 등을 활용한 강력한 Machine Fingerprint(HWID) 추출
- 인터넷이 끊긴 환경을 고려한 Offline RSA Signed Token 로컬 캐싱 기능

---

## 12. 운영 환경 및 배포

- **개발 환경:** `uv` 기반 로컬 가상환경 및 Docker Compose (FastAPI, Redis)
- **운영 환경:** GitHub Actions 빌드 -> Docker 이미지 배포 -> Managed 플랫폼(Render, Railway, AWS ECS 등) + Supabase Managed DB
- **모니터링:** Sentry (에러 로깅), UptimeRobot (헬스체크)

---

## 13. 성능 및 성공 지표

- API 평균 응답 300ms 이하
- 무상태(Stateless) 구조를 통해 단일 컨테이너에서 초당 500+ Req 처리
- 결제 웹훅 처리 성공률 99.9%+
- 라이선스 페이로드 복호화 및 검증 응답 500ms 이하