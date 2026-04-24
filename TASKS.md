# TASKS.md
# Build Tasks Roadmap (Reusable Secure Core Platform)

## Phase 1. Foundation (기반 인프라 구축)
- [ ] FastAPI 프로젝트 초기화 (`uv init backend`)
- [ ] `pyproject.toml` 및 필수 의존성 추가 (`uv add fastapi sqlalchemy alembic pydantic httpx ...`)
- [ ] PostgreSQL (Supabase) 및 Redis 연결 설정
- [ ] 다중 프로젝트(Multi-tenant) 지원을 위한 DB 스키마 설계 (`users`, `subscriptions`, `licenses` 테이블에 `project_id` 추가)
- [ ] Alembic 초기화 및 최초 마이그레이션 스크립트 작성
- [ ] 로컬 개발용 Docker Compose 구성 (FastAPI, Redis)
- [ ] `core/config.py` 작성 (환경변수 관리)

---

## Phase 2. Security Base (보안 코어 로직)
- [ ] HTTPS 강제 및 TLS/HSTS 미들웨어 설정
- [ ] JWT 서명 검증 및 파싱 유틸리티 작성 (Supabase Public Key 연동)
- [ ] API 라우터 보호용 Dependency Injection (`Depends`) 작성 (`x-project-id` 헤더 검증 포함)
- [ ] **[핵심]** AES-256-GCM 애플리케이션 레벨(Payload) 암/복호화 미들웨어/유틸리티 작성
- [ ] Polar 등 외부 서비스 연동을 위한 Webhook HMAC 서명 검증 로직 구현
- [ ] Redis 기반 Rate Limit 및 IP 차단 미들웨어 적용
- [ ] 시스템 감사 로그(Audit Log) 로깅 구조 및 포맷팅 작성
- [ ] Secret Key Rotation 정책 수립 및 스크립트 작성

---

## Phase 3. Supabase Auth (인증 체계)
- [ ] Supabase 프로젝트 생성 및 초기 세팅
- [ ] Email Auth 및 소셜 로그인 (Google, GitHub) 활성화
- [ ] `GET /auth/me` 엔드포인트 구현 (JWT를 바탕으로 DB에서 유저 정보 반환)
- [ ] 최초 로그인 시 Supabase User ID를 자체 DB(`users` 테이블)로 동기화하는 로직 구현 (`project_id` 매핑)
- [ ] 클라이언트 세션 갱신(Refresh Token) 가이드라인 문서화
- [ ] MFA(2차 인증) 정책 설계 및 도입 준비

---

## Phase 4. Polar Billing (결제 및 구독)
- [ ] Polar.sh Sandbox 환경 구성 및 상품(월간/연간/평생) 플랜 생성
- [ ] `GET /billing/plans` 엔드포인트 구현 (Project별 플랜 조회)
- [ ] `POST /billing/checkout` 엔드포인트 구현 (Polar Checkout URL 생성 및 반환)
- [ ] `POST /webhooks/polar` 웹훅 수신 엔드포인트 구현 (서명 검증 필수)
- [ ] 웹훅 이벤트(`subscription.created`, `updated`, `canceled` 등) 수신 시 DB 동기화 로직 구현
- [ ] 결제 해지 및 환불 상태 처리 로직 작성
- [ ] 웹훅 처리 실패 시 복구를 위한 Redis 기반 Retry Queue (또는 BackgroundTasks) 작성

---

## Phase 5. License Module (라이선스 관리)
- [ ] Polar API와 연동된 라이선스 키 생성 및 동기화 처리
- [ ] DB 유출에 대비한 키 해시(Hash) 저장 로직 작성
- [ ] `POST /license/activate` 구현 (Client의 Hardware Fingerprint 수집 및 기기 등록)
- [ ] **[핵심]** `POST /license/validate` 구현 (데스크톱 앱 E2E 보안을 위해 암호화된 Payload만 수신 및 응답)
- [ ] `POST /license/deactivate` 및 라이선스 강제 회수(Revoke) 기능 구현
- [ ] **[핵심]** 인터넷 단절 환경을 위한 서버 측 RSA 비대칭키 서명 오프라인 토큰 생성기 작성

---

## Phase 6. Dashboard (사용자 웹/API 대시보드)
- [ ] `GET /dashboard/summary` (현재 플랜 및 라이선스 요약)
- [ ] `GET /dashboard/invoices` (결제 내역 및 영수증 다운로드 링크 제공)
- [ ] `GET /dashboard/devices` (등록된 기기 목록 조회)
- [ ] `POST /dashboard/devices/remove` (특정 기기 연결 해제)
- [ ] API Key 발급 및 스코프(Scope) 관리 기능
- [ ] 사용자 계정 보안 설정 (비밀번호 변경 연동) API 구현

---

## Phase 7. Admin (통합 관리자 기능)
- [ ] 다중 프로젝트 통합 조회를 위한 Admin Dashboard 구조 설계
- [ ] 사용자 통합 검색 기능 구현 (이메일, 프로젝트, 결제 상태 기준)
- [ ] 불량 사용자 계정 정지(Ban) API 구현
- [ ] 특정 사용자의 구독 수동 연장 및 라이선스 강제 만료 처리 API
- [ ] 관리자 행동에 대한 감사 로그(Audit Log) 조회 페이지 연결

---

## Phase 8. Client SDK (프론트엔드/클라이언트 연동)

### 8.1. PySide6 / Tauri (Desktop App - High Security)
- [ ] OS Native Secure Storage를 활용한 토큰 저장소 구현
- [ ] 강력한 Machine Fingerprint (HWID) 추출 모듈 작성
- [ ] **[핵심]** 서버와 통신하기 위한 AES-256-GCM 페이로드 암호화/복호화 네트워크 인터셉터 작성
- [ ] 데스크톱 환경용 로그인 팝업 또는 딥링크 연동
- [ ] 서버에서 발급한 RSA 오프라인 토큰 파싱 및 로컬 캐싱 기능

### 8.2. Flutter (Mobile App)
- [ ] `flutter_secure_storage` 연동
- [ ] 모든 API 요청 시 Header (`x-project-id`, `Authorization`) 자동 첨부 인터셉터 작성
- [ ] 앱 내 브라우저(WebView)를 활용한 Polar Checkout 결제 흐름 구현
- [ ] JWT Refresh Token 갱신 자동화 로직 추가

---

## Phase 9. Multi Project Reuse (보일러플레이트 패키징)
- [ ] GitHub Template Repository 생성 (`core-backend-template`)
- [ ] 신규 프로젝트 세팅을 위한 환경변수(`.env.example`) 및 `README.md` 가이드 문서화
- [ ] `project.yaml` 또는 DB 설정을 통한 브랜드(테마, 이름) 및 Feature Flag 동적 로드 구조화
- [ ] 단일 서버에서 트래픽을 분산하기 위한 White Label 아키텍처 점검

---

## Phase 10. Launch Ready (배포 준비)
- [ ] GitHub Actions CI/CD 파이프라인(Lint, Test, Build, Deploy) 구축
- [ ] Staging 환경 배포 및 결제(Sandbox)/라이선스 E2E 테스트 진행
- [ ] Production 환경 배포 (클라우드 서비스, Managed DB 등)
- [ ] PostgreSQL 일일/주간 백업 자동화 정책 적용
- [ ] Sentry 연동(에러 로깅) 및 Uptime 모니터링 적용
- [ ] 공통 서비스 약관(ToS) 및 개인정보 처리방침 템플릿 준비

---

## Recommended Build Order (권장 작업 순서)
~~~text
1. Foundation & Multi-tenant DB (Phase 1)
2. Security & E2E Encryption Base (Phase 2)
3. Auth & Supabase Sync (Phase 3)
4. Billing & Polar MoR Webhooks (Phase 4)
5. License Activation & Offline Tokens (Phase 5)
6. Dashboard & Admin API (Phase 6, 7)
7. Client SDK (Desktop Encryption / Mobile WebView) (Phase 8)
8. Template Packaging & Deploy (Phase 9, 10)
~~~