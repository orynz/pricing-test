# TEST_PLAN.md
# Reusable Secure Core Platform 종합 테스트 계획서
(Supabase Auth + Polar + FastAPI + Mobile + Desktop)

---

## 1. 목적

현재 개발 완료 상태는 기능 구현 완료에 가깝고,  
실제 운영 가능한 품질 검증 완료 상태는 아닐 가능성이 높다.

즉:
```text
개발 완료 ≠ 운영 가능
코드 존재 ≠ 사용자 성공
API 존재 ≠ 장애 대응 가능
```

그래서 아래 항목 전체를 검증해야 한다.
- 기능 정상 작동 여부 및 모듈 간 연동 문제
- 다중 프로젝트(Multi-tenant) 간 완벽한 데이터 격리 여부
- 데스크톱/모바일 앱의 네트워크 장애 및 오프라인 대응
- 엔드투엔드(E2E) 페이로드 암호화 및 라이선스 보안성
- 결제 흐름 안정성 및 복구 가능성
- 실사용자 QA 및 동시 접속 부하

---

## 2. 테스트 전략 (Testing Pyramid)

Martin Fowler의 테스트 피라미드 방식처럼  
낮은 비용 테스트를 많이, 무거운 E2E 테스트는 핵심 흐름만 둔다.

```text
            [Manual QA / UAT]
           [E2E / System Test]
        [Integration / Contract]
          [Service / API Test]
             [Unit Test]
```

권장 비율:
```text
60% Unit
25% Integration
10% E2E
5% Manual Exploratory
```

---

## 3. 전체 테스트 범주

- **A. Unit Test:** 함수 / 클래스 / 암호화 모듈 단위 검증
- **B. Integration Test:** 모듈 간 연결 및 다중 프로젝트 격리 검증
- **C. API Test:** 실제 REST API 응답 검증 (Payload 암호화 포함)
- **D. E2E Test:** 회원가입부터 결제, 라이선스 오프라인 활성화까지 흐름 검증
- **E. Security Test:** 권한 우회 / JWT 위조 / 패킷 스니핑 방어 / Rate Limit 검증
- **F. Performance Test:** 동시 사용자 / 응답속도 / 부하 테스트
- **G. Chaos Test:** 네트워크 끊김 / DB 장애 / Webhook 지연
- **H. Manual QA / I. UAT:** 실제 사람이 직접 사용하는 테스트 및 베타 테스트

---

## 4. 테스트 환경 구성

### Local
```text
uv 기반 가상환경 (FastAPI)
Docker Compose (PostgreSQL, Redis)
Mock Polar API
Mock Email
```

### Staging
```text
실제 HTTPS 도메인
실제 Supabase Test Project
Polar Sandbox 환경
실제 모바일 APK / Desktop EXE (난독화 적용본)
```

### Production-like
```text
운영과 동일 인프라 및 설정
읽기전용 실험 DB
부하 테스트 환경
```

---

## 5. 기능별 테스트 계획

### A. 회원가입 / 인증 / 로그인
* **Unit Test:** 이메일 validator, 비밀번호 정책, JWT parser, refresh token logic
* **Integration Test:** Supabase 로그인 후 FastAPI 인증 성공, 만료 토큰 거절, **[추가] `x-project-id` 누락 시 접근 차단**
* **API Test:** `POST /signup`, `POST /login`, `GET /auth/me`, `POST /refresh`
* **장애/Manual 테스트:** Supabase 다운, 인터넷 끊김, 토큰 갱신 실패, 여러 기기 동시 로그인 시도

### B. 결제 시스템 (Polar 연동)
* **Unit Test:** Webhook parser, Plan mapping, Webhook 서명(Signature) 검증 로직
* **Integration Test:** Polar 결제 성공 → 구독 활성화, 중복 Webhook → 1회만 멱등성 처리
* **API Test:** `POST /billing/checkout`, `POST /webhooks/polar`, `GET /billing/subscription`
* **장애 테스트:** Webhook 10분 지연, Webhook 3회 중복, 수동 동기화(Manual Sync) 정상 작동 여부

### C. 라이선스 시스템 & 데스크톱 보안 (핵심)
* **Unit Test:** AES-256-GCM 암/복호화 모듈, RSA 오프라인 서명 생성기, Device Fingerprint 추출기
* **Integration Test:** 결제 성공 후 자동 발급, 기기 제한(Device Limit) 초과 차단, Revoke 즉시 반영
* **API Test:** `POST /license/activate`, `POST /license/validate` (반드시 암호화된 Payload만 허용)
* **Manual QA & 장애 테스트:** * 데스크톱 앱에서 다른 PC로 복사 후 실행 시도 (차단 검증)
  * 앱 실행 중 와이파이를 끄고 3일간 캐시된 RSA 오프라인 토큰으로 구동되는지 검증
  * 서버 만료 후 재실행 시 오프라인 토큰 무효화 확인

---

## 6. 연동 테스트 (Cross Module & Edge Cases)

### 시나리오 1: 정상 흐름 (Happy Path)
```text
회원가입 → 로그인 → 무료 플랜 → 결제 → Webhook 수신 → 유료 전환 → 라이선스 자동 발급 → 앱 실행 및 AES 활성화
```

### 시나리오 2: Multi-tenant (다중 프로젝트) 격리 테스트
```text
프로젝트 A 전용 데스크톱 앱 실행 → 프로젝트 B에만 가입된 이메일로 로그인 시도 → 403 Forbidden 및 차단 확인
```

### 시나리오 3: 구독 취소 및 권한 회수 흐름
```text
환불 또는 구독 종료 → Polar Webhook → 라이선스 비활성화 → 데스크톱 앱 Heartbeat 실패 → 프리미엄 기능 즉시 잠금
```

---

## 7. 네트워크 장애 테스트 (필수)

### 데스크톱 앱
* **인터넷 끊김:** 로그인 직후 랜선을 뽑았을 때, 오프라인 토큰 캐싱을 통해 며칠간 정상 작동하는지 확인
* **프록시 간섭:** 사내 VPN 등 중간자 인증서가 끼어들었을 때 TLS 검증 실패 또는 암호화 페이로드로 정상 보호되는지 확인

### 모바일 앱
* **망 전환:** 결제 WebView 진입 중 LTE ↔ WiFi 전환 시 세션 유지 여부
* **타임아웃:** API 응답 10초 이상 지연 시 스피너 무한 대기를 방지하고 Retry 팝업 노출

---

## 8. 보안 테스트 (Penetration Testing)

* **패킷 스니핑 방어 (Charles Proxy/Wireshark):** 데스크톱 앱 통신 패킷을 가로챘을 때, 라이선스 키와 하드웨어 ID가 AES-256-GCM으로 완벽히 암호화되어 읽을 수 없는지 눈으로 확인.
* **Replay Attack (재전송 공격) 방어:** 탈취한 암호화 페이로드를 Postman으로 다시 보냈을 때 서버가 Timestamp/Nonce를 통해 차단하는지 확인.
* **Webhook 위조:** Polar가 아닌 임의의 클라이언트가 Webhook 엔드포인트를 호출할 때 HMAC 서명 불일치로 100% 차단하는지 확인.
* **Multi-tenant 권한 상승 시도:** Header의 `x-project-id`를 변조하여 타 프로젝트의 유저 데이터를 조회하려는 시도 차단.

---

## 9. 성능 및 무결성 테스트

* **성능 목표:** `k6` 및 `Locust` 활용. 동시 접속 사용자 100명 로그인, 1000 license check/min. 평균 API 응답 300ms 이하 유지 (AES 복호화 연산 오버헤드 포함).
* **데이터 무결성:** 결제 1건 = 구독 1건. 유저 삭제 시 고아 데이터(Orphan data) 완벽 제거. 환불 후 상태 일관성.

---

## 10. 백업 / 복구 테스트

* **DR (Disaster Recovery):** 월 1회 이상 필수 진행.
* **절차:** DB 백업본 생성 → 별도 DB에 복구 리허설 → 특정 유저 상태 및 라이선스 복원 확인 → 누락된 시간 동안의 Polar Webhook 이벤트 수동 재처리(Replay) 테스트.

---

## 11. 사용자 직접 QA 체크리스트

* **모바일 사용자:** 버튼 터치 영역 확인, 결제 앱(토스/카카오페이 등) 딥링크 복귀 후 화면 갱신 여부.
* **데스크톱 사용자:** 설치(Installer) 경험, 재부팅 후 자동 로그인(OS Secure Storage) 유지 여부, 바이러스 백신(Windows Defender) 오탐지 여부.
* **관리자 (Admin):** 대시보드에서 1초 만에 유저를 찾아 수동으로 라이선스를 종료할 수 있는지 확인.

---

## 12. 출시 전 최종 Gate (배포 금지 조건)

```text
1. 회원가입 실패율 > 3%
2. 결제 Webhook 처리 성공률 < 99%
3. 라이선스 페이로드 암호화 해독 가능 (보안 치명타)
4. 멀티 테넌트 데이터 유출 가능성 존재
5. 오프라인 데스크톱 앱 구동 실패
6. P95 응답속도 > 1초
7. DB 백업/복구 리허설 미완료
```

---

## 13. 실제 실행 우선순위 (Action Items)

```text
1. 핵심 API E2E 테스트 (회원가입 → 결제 웹훅 수신 → DB 갱신)
2. 데스크톱 앱 AES 페이로드 암호화 및 찰스 프록시 방어 테스트
3. 데스크톱 오프라인 RSA 서명 토큰 캐싱 로직 테스트
4. 모바일 앱 환경 망 단절/전환 스트레스 테스트
5. Multi-tenant (A앱 vs B앱) 접근 격리 테스트
6. 베타 사용자 20명(모바일/데스크톱) 투입 및 피드백 수집
```