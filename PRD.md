# Product Requirements Document (PRD)
# Reusable Secure Core Platform (Universal SaaS/Desktop Boilerplate)

## 1. 개요

1인 개발자가 모바일 앱, 데스크톱 앱, 신규 SaaS 프로젝트 등 다양한 환경에서 반복적으로 필요한 핵심 인프라(인증, 결제, 라이선스, 보안)를 즉시 재사용할 수 있도록 모듈화된 공통 플랫폼을 구축한다.

**핵심 목표:**
- 회원가입, 인증, 로그인
- 결제 및 글로벌 세금 처리 (MoR)
- 구독 관리 및 라이선스 발급
- 사용자 대시보드 및 통합 관리자(Admin) 기능
- 데스크톱/모바일 앱을 위한 엔드투엔드(E2E) 수준의 데이터 보안
- **단일 백엔드로 여러 앱(App/Project)을 지원하는 멀티 테넌트(Multi-tenant) 구조**

**기술 스택 및 역할:**
- **Supabase Auth & DB:** JWT 기반 인증, 세션 관리 및 사용자/구독 데이터 저장
- **Polar.sh:** 결제 처리, 글로벌 부가세(VAT) 대행(MoR), 네이티브 라이선스 키 생성
- **FastAPI (Python):** 무상태(Stateless) API 게이트웨이, 커스텀 비즈니스 로직, 웹훅 처리 및 데이터 암/복호화
- **PostgreSQL:** 메인 데이터베이스 (Supabase 내장)
- **Redis (Optional):** Rate Limiting 및 단기 세션 캐싱

---

## 2. 제품 비전

새 프로젝트를 기획할 때마다 로그인과 결제, 보안 로직을 다시 만드는 낭비를 완벽히 제거한다.

* **새 프로젝트 런칭 흐름:**
  1. 새 프로젝트 시작 (앱 A, 앱 B ...)
  2. 클라이언트(UI) 개발
  3. 공통 Core API (Project ID 기반) 연결
  4. 글로벌 결제 및 라이선스 보안이 완비된 상태로 즉시 운영 가능

---

## 3. 대상 사용자

**외부 사용자 (End-User)**
- 모바일 앱 사용자 / 데스크톱 앱 사용자
- 유료 구독 및 평생 이용권 구매자

**내부 사용자 (Operator)**
- 1인 개발자 (최소한의 공수로 다중 프로젝트 관리)
- 운영자/CS 담당자 (통합 대시보드에서 모든 앱의 고객 대응)

---

## 4. 핵심 기능

### A. 인증 (Auth)
- 이메일 회원가입 및 Magic Link / OTP 인증
- 소셜 로그인 (Google, GitHub, Apple 등 확장 가능 구조)
- JWT 기반 세션 관리 및 Refresh Token 로직
- MFA (2차 인증) 지원
- 기기별 로그인 기록 및 원격 로그아웃 기능

### B. 결제 (Billing - Powered by Polar)
- 글로벌 세금(VAT) 자동 처리 및 영수증 발급
- 월/연간 구독, 평생 이용권(One-time), 무료 체험(Trial) 지원
- 앱 내 Polar Checkout 세션 생성 및 리다이렉트
- 결제 성공/실패/환불 웹훅(Webhook) 처리 및 DB 동기화
- 사용자 대시보드 내 구독 해지 및 업그레이드/다운그레이드

### C. 라이선스 (License)
- 결제 완료 시 Polar API를 통한 라이선스 키 자동 발급
- 기기 종속(Node-locked) 활성화 (Hardware ID / Machine Fingerprint 연동)
- 대시보드에서 활성화된 기기 해제 및 관리
- **오프라인 토큰:** 인터넷이 없는 데스크톱 환경을 위해, 서버에서 RSA 비대칭키로 서명한 오프라인 라이선스 파일 발급 및 클라이언트 로컬 검증

### D. 대시보드 (User Dashboard)
- 현재 이용 중인 플랜 및 잔여 기간 조회
- 결제 내역 및 인보이스 다운로드
- 라이선스 키 목록 및 활성화된 기기 현황 관리
- 프로젝트별 API Key 발급 (Usage Billing 사용 시)
- 계정 보안 설정 (비밀번호 변경, MFA 관리)

### E. 관리자 (Admin)
- 통합 사용자 검색 (이메일, 프로젝트, 라이선스 키 기준)
- 계정 정지 및 강제 로그아웃
- 수동 구독 연장 및 라이선스 강제 회수/종료
- 결제 실패 내역 및 Webhook 처리 상태 확인
- 시스템 및 관리자 활동 감사 로그(Audit Logs) 조회

### F. 보안 (Security) - [강조 사항]
- **API 페이로드 암호화:** 데스크톱 앱 메모리 및 패킷 스니핑 방지를 위해, 중요 API(라이선스 검증 등) 통신 시 클라이언트-서버 간 AES-256-GCM 알고리즘으로 본문(Body) 데이터 암호화 전송
- **Webhook 서명 검증:** Polar 등 외부 서비스에서 들어오는 Webhook의 HMAC 서명을 필수 검증하여 위변조 방지
- JWT 기반 API 라우터 보호 (Depends 주입)
- Rate Limit 및 무차별 대입(Brute-force) 로그인 시도 제한
- DB 레벨의 RLS(Row Level Security) 적용 (Supabase)

### G. 다중 프로젝트 지원 (Multi-tenant) - [신규 추가]
- 모든 핵심 데이터(Users, Subscriptions, Licenses)에 project_id 컬럼 추가
- 클라이언트 API 요청 시 Header에 x-project-id를 포함하여, 단일 백엔드로 여러 프로덕트 서비스 가능

---

## 5. 추가 기능 (고도화 권장)

- **Referral (추천인):** 추천인 코드 발급 및 가입 시 크레딧/할인 보상
- **Team Billing (B2B):** 조직(Organization) 단위 결제 및 시트(Seat/좌석) 수 기반 과금 및 구성원 초대
- **Usage Billing (종량제):** API 호출량이나 특정 기능 사용량(Token 등)을 측정하여 Polar 단위 과금(Metered Billing) 연동
- **Feature Flags:** 서버 대시보드에서 프로젝트별, 유저별 특정 기능을 실시간으로 ON/OFF 할 수 있는 원격 구성(Remote Config)

---

## 6. 사용자 흐름 (User Flow)

**1. 일반적인 구독 및 라이선스 발급 흐름**
- 앱 내 로그인 완료 상태
- → 프리미엄 기능 클릭 시 [요금제 화면] 노출
- → 결제 버튼 클릭 → API: Polar Checkout URL 생성 및 브라우저 오픈
- → 사용자 결제 완료
- → Polar Webhook 전송 → FastAPI Webhook 엔드포인트 수신 및 서명 검증
- → DB 내 유저 구독 상태 'Active' 업데이트 및 라이선스 키 저장
- → 클라이언트(앱) 폴링 또는 웹소켓으로 결제 완료 감지 → 라이선스 자동 활성화

**2. 데스크톱 앱 보안 로그인 흐름 (페이로드 암호화 포함)**
- 데스크톱 앱 실행 (Hardware ID 추출)
- → Supabase Auth 로그인 (JWT 획득)
- → 암호화된 라이선스 검증 요청 (AES Encrypted: JWT + Hardware ID + License Key) 전송
- → FastAPI 복호화 및 유효성 검증
- → 암호화된 응답 (프리미엄 기능 해제 권한 및 오프라인 토큰) 반환
- → 앱 내 복호화 후 사용 시작

---

## 7. 성공 지표 (KPI)

- **생산성:** 신규 앱/프로젝트 백엔드 연동 시간 **1일(24시간) 이하**
- **안정성:** 결제 Webhook 처리 성공률 99.9%+
- **보안성:** 데스크톱 앱 비정상(우회) 라이선스 활성화 비율 0%
- 로그인 성공률 및 라이선스 초기 활성화 성공률 98%+

---

## 8. MVP 범위 (Phases)

### v1 (Core Infrastructure)
- Supabase Auth 기반 기본 인증 체계 마련
- Polar 연동: 구독 결제, 단건 결제, Webhook 처리, 세금 자동화
- 라이선스 API 구축 (기기 귀속 검증 및 AES 페이로드 암호화 적용)
- 단일/다중 프로젝트 구분을 위한 DB 스키마 (project_id) 설계
- 기초적인 사용자 대시보드 API (상태 조회)

### v2 (Expansion & Admin)
- 통합 관리자(Admin) 웹 대시보드 구축
- Team Billing (조직 단위 결제 및 권한 관리)
- 오프라인 라이선스 토큰 (RSA 서명 검증) 도입
- Audit Logs 및 관리자 모니터링 기능 강화

### v3 (Growth)
- Referral 시스템 및 Usage Billing (사용량 과금) 추가
- Feature Flags 시스템 도입