# POLAR_PLAN_LIFECYCLE.md

# Polar 구독 플랜 구성 및 라이프사이클 설계서
## 무료 / Pro / 평생 플랜
## Stack
- Supabase Auth
- Polar
- FastAPI
- PostgreSQL
- PySide6 Desktop
- Flutter Mobile

---

## 1. 목적

본 문서는 `무료`, `Pro 구독`, `평생 라이선스` 플랜을 Polar 기반으로 구성하고, FastAPI 서버와 연동하여 다음 기능을 안정적으로 제공하기 위한 상세 작업 계획서다.

- 회원가입 후 무료 플랜 자동 부여
- Pro 월간/연간 구독 결제
- 평생 플랜 1회 결제
- 결제 성공 후 권한 활성화
- 라이선스 키 발급
- 구독 갱신 / 취소 / 만료 / 환불 처리
- 모바일 / 데스크톱 앱에서 권한 검증
- 네트워크 장애 / 웹훅 중복 / 지연 대응
- 다른 프로젝트에서 재사용 가능한 구조화

---

## 2. 핵심 설계 원칙

### 2.1 결제 상태의 진실은 Polar

앱이나 프론트엔드가 결제 성공을 직접 판단하지 않는다.

```text
잘못된 방식:
클라이언트에서 "결제 성공 페이지에 도착했다" → Pro 권한 부여

올바른 방식:
Polar Webhook 수신 → FastAPI 서버 검증 → DB 반영 → 권한 활성화
```

---

### 2.2 서비스 권한의 진실은 내부 DB

Polar는 결제/구독의 원천이고, 실제 앱 접근 권한은 내부 DB에서 빠르게 판단한다.

```text
Polar:
결제, 구독, 주문, 환불, 고객 포털

FastAPI DB:
사용자 플랜, 라이선스, 기기 활성화, 기능 권한, 사용량 제한
```

---

### 2.3 플랜은 “상품”과 “권한”을 분리한다

Polar 상품명과 내부 권한명을 1:1로 강하게 묶지 않는다.

```text
Polar Product:
pro_monthly_product_id
pro_yearly_product_id
lifetime_product_id

Internal Entitlement:
plan = free | pro | lifetime
features = [...]
license_policy = [...]
```

이렇게 해야 나중에 가격 변경, 할인 상품, 이벤트 상품을 추가해도 내부 권한 구조가 깨지지 않는다.

---

## 3. Polar 플랜 구성 전략

Polar는 일반적인 “상품 하나 + 여러 가격 variant” 방식보다, 각 pricing model을 별도 product로 만드는 접근이 적합하다.

따라서 아래처럼 구성한다.

```text
Free Plan:
내부 DB에서만 관리
Polar 상품 생성 불필요

Pro Monthly:
Polar Product 1개
Recurring monthly

Pro Yearly:
Polar Product 1개
Recurring yearly

Lifetime:
Polar Product 1개
One-time payment
```

---

## 4. 플랜 정의

## 4.1 Free Plan

### 목적

가입 즉시 사용할 수 있는 기본 무료 플랜.

### Polar 구성

```text
Polar Product 생성하지 않음
```

### 내부 DB 구성

```text
plan_code = "free"
billing_type = "none"
subscription_status = "free"
license_policy = "none" 또는 "limited"
```

### 제공 기능 예시

```text
- 기본 기능 사용
- 하루 분석 3회
- 저장 프로젝트 1개
- 라이선스 키 발급 없음
- 데스크톱 앱 로그인은 가능
- 고급 기능 잠금
```

### 제한 정책 예시

```yaml
plan_code: free
max_projects: 1
max_daily_requests: 3
max_devices: 0
license_enabled: false
offline_access_days: 0
priority_support: false
```

---

## 4.2 Pro Monthly Plan

### 목적

월간 구독형 유료 플랜.

### Polar 구성

```text
Product Name: Secure Core Pro Monthly
Pricing Type: Recurring
Billing Interval: Monthly
Trial: optional
Benefits:
  - License Key
  - Feature Flag: pro
  - Custom Benefit: app_access
```

### 내부 플랜 코드

```text
plan_code = "pro_monthly"
entitlement_level = "pro"
billing_type = "subscription"
```

### 제공 기능 예시

```text
- 모든 Pro 기능 사용
- 데스크톱 라이선스 키 발급
- 최대 2대 기기 활성화
- 월간 구독 유지 중 사용 가능
- 구독 취소 시 현재 결제 기간 종료일까지 사용 가능
```

### 제한 정책 예시

```yaml
plan_code: pro_monthly
max_projects: 20
max_daily_requests: 500
max_devices: 2
license_enabled: true
offline_access_days: 7
priority_support: false
```

---

## 4.3 Pro Yearly Plan

### 목적

연간 구독형 유료 플랜.

### Polar 구성

```text
Product Name: Secure Core Pro Yearly
Pricing Type: Recurring
Billing Interval: Yearly
Trial: optional
Benefits:
  - License Key
  - Feature Flag: pro
  - Custom Benefit: app_access
```

### 내부 플랜 코드

```text
plan_code = "pro_yearly"
entitlement_level = "pro"
billing_type = "subscription"
```

### 제공 기능 예시

```text
- Pro Monthly와 동일한 기능
- 연간 할인 적용
- 최대 2대 또는 3대 기기 활성화
- 구독 기간 동안 사용 가능
```

### 제한 정책 예시

```yaml
plan_code: pro_yearly
max_projects: 20
max_daily_requests: 500
max_devices: 3
license_enabled: true
offline_access_days: 14
priority_support: true
```

---

## 4.4 Lifetime Plan

### 목적

1회 결제로 영구 사용 권한을 제공하는 플랜.

### Polar 구성

```text
Product Name: Secure Core Lifetime
Pricing Type: One-time
Benefits:
  - License Key
  - Feature Flag: lifetime
  - Custom Benefit: app_access
```

### 내부 플랜 코드

```text
plan_code = "lifetime"
entitlement_level = "lifetime"
billing_type = "one_time"
```

### 제공 기능 예시

```text
- 구매한 버전의 영구 사용
- 최대 3대 기기 활성화
- 구독 갱신 없음
- 환불 시 즉시 권한 회수
```

### 제한 정책 예시

```yaml
plan_code: lifetime
max_projects: 999
max_daily_requests: 1000
max_devices: 3
license_enabled: true
offline_access_days: 30
priority_support: true
upgrade_policy: "major_version_paid_upgrade_possible"
```

---

## 5. 상품 ID 매핑 전략

Polar Product ID를 코드에 직접 박지 않는다.

`.env` 또는 DB `plans` 테이블에 저장한다.

### .env 예시

```env
POLAR_PRODUCT_PRO_MONTHLY="product_xxx_monthly"
POLAR_PRODUCT_PRO_YEARLY="product_xxx_yearly"
POLAR_PRODUCT_LIFETIME="product_xxx_lifetime"
```

### plans 테이블 예시

```sql
create table plans (
    id uuid primary key,
    plan_code text unique not null,
    display_name text not null,
    billing_type text not null,
    polar_product_id text unique,
    price_amount integer,
    currency text default 'USD',
    interval text,
    entitlement_level text not null,
    max_devices integer default 1,
    max_daily_requests integer default 0,
    offline_access_days integer default 0,
    is_active boolean default true,
    created_at timestamp default now(),
    updated_at timestamp default now()
);
```

### seed 예시

```sql
insert into plans (
    id,
    plan_code,
    display_name,
    billing_type,
    polar_product_id,
    price_amount,
    currency,
    interval,
    entitlement_level,
    max_devices,
    max_daily_requests,
    offline_access_days,
    is_active
) values
(gen_random_uuid(), 'free', 'Free', 'none', null, 0, 'USD', null, 'free', 0, 3, 0, true),
(gen_random_uuid(), 'pro_monthly', 'Pro Monthly', 'subscription', 'polar_product_monthly', 1900, 'USD', 'month', 'pro', 2, 500, 7, true),
(gen_random_uuid(), 'pro_yearly', 'Pro Yearly', 'subscription', 'polar_product_yearly', 19000, 'USD', 'year', 'pro', 3, 500, 14, true),
(gen_random_uuid(), 'lifetime', 'Lifetime', 'one_time', 'polar_product_lifetime', 19900, 'USD', null, 'lifetime', 3, 1000, 30, true);
```

---

## 6. 내부 상태 모델

## 6.1 사용자 플랜 상태

```text
free
trialing
active
past_due
canceled
expired
revoked
refunded
lifetime_active
```

---

## 6.2 구독 상태

```text
none
trialing
active
past_due
canceled
revoked
expired
```

---

## 6.3 라이선스 상태

```text
not_issued
active
expired
revoked
refunded
device_limit_exceeded
```

---

## 6.4 권한 상태

권한은 `plan_status`, `subscription_status`, `license_status`를 종합해서 계산한다.

```text
free:
무료 기능만 허용

active:
Pro 기능 허용

lifetime_active:
평생 기능 허용

past_due:
유예 기간 동안 제한적 허용

canceled:
현재 기간 종료일까지 허용

expired:
무료 기능으로 강등

revoked:
즉시 차단

refunded:
즉시 차단
```

---

## 7. 데이터베이스 설계

## 7.1 users

```sql
create table users (
    id uuid primary key,
    supabase_user_id uuid unique not null,
    email text unique not null,
    display_name text,
    status text default 'active',
    created_at timestamp default now(),
    updated_at timestamp default now()
);
```

---

## 7.2 plans

```sql
create table plans (
    id uuid primary key,
    plan_code text unique not null,
    display_name text not null,
    billing_type text not null,
    polar_product_id text unique,
    price_amount integer,
    currency text default 'USD',
    interval text,
    entitlement_level text not null,
    max_devices integer default 1,
    max_daily_requests integer default 0,
    offline_access_days integer default 0,
    is_active boolean default true,
    created_at timestamp default now(),
    updated_at timestamp default now()
);
```

---

## 7.3 subscriptions

```sql
create table subscriptions (
    id uuid primary key,
    user_id uuid references users(id),
    plan_id uuid references plans(id),
    provider text default 'polar',
    polar_customer_id text,
    polar_subscription_id text unique,
    status text not null,
    current_period_start timestamp,
    current_period_end timestamp,
    cancel_at_period_end boolean default false,
    canceled_at timestamp,
    revoked_at timestamp,
    created_at timestamp default now(),
    updated_at timestamp default now()
);
```

---

## 7.4 orders

```sql
create table orders (
    id uuid primary key,
    user_id uuid references users(id),
    plan_id uuid references plans(id),
    provider text default 'polar',
    polar_order_id text unique,
    polar_checkout_id text,
    amount integer,
    currency text,
    status text not null,
    paid_at timestamp,
    refunded_at timestamp,
    created_at timestamp default now(),
    updated_at timestamp default now()
);
```

---

## 7.5 licenses

```sql
create table licenses (
    id uuid primary key,
    user_id uuid references users(id),
    plan_id uuid references plans(id),
    license_key_hash text unique not null,
    license_key_prefix text not null,
    status text not null,
    max_devices integer default 1,
    expires_at timestamp,
    issued_at timestamp default now(),
    revoked_at timestamp,
    created_at timestamp default now(),
    updated_at timestamp default now()
);
```

---

## 7.6 license_activations

```sql
create table license_activations (
    id uuid primary key,
    license_id uuid references licenses(id),
    user_id uuid references users(id),
    device_fingerprint_hash text not null,
    device_name text,
    platform text,
    app_version text,
    activated_at timestamp default now(),
    last_seen_at timestamp,
    deactivated_at timestamp,
    status text default 'active'
);
```

---

## 7.7 entitlement_snapshots

```sql
create table entitlement_snapshots (
    id uuid primary key,
    user_id uuid references users(id),
    plan_code text not null,
    entitlement_level text not null,
    source text not null,
    status text not null,
    features jsonb not null,
    valid_until timestamp,
    created_at timestamp default now(),
    updated_at timestamp default now()
);
```

---

## 7.8 webhook_events

```sql
create table webhook_events (
    id uuid primary key,
    provider text default 'polar',
    event_id text unique not null,
    event_type text not null,
    payload jsonb not null,
    processed boolean default false,
    processed_at timestamp,
    error_message text,
    created_at timestamp default now()
);
```

---

## 8. 플랜별 라이프사이클

## 8.1 Free 라이프사이클

```text
회원가입
→ Supabase Auth user 생성
→ FastAPI /me 최초 호출
→ users 테이블 upsert
→ entitlement_snapshots에 free 생성
→ 무료 기능 사용
```

### 상태 전이

```text
none → free
free → pro_active
free → lifetime_active
free → suspended
```

### 처리 규칙

```text
- 무료 플랜은 Polar와 무관하다.
- 결제 정보가 없어도 항상 기본 entitlement를 가진다.
- 유료 권한이 만료되면 free로 강등된다.
```

---

## 8.2 Pro 구독 라이프사이클

### 신규 구독

```text
사용자 로그인
→ Pro Monthly 또는 Pro Yearly 선택
→ FastAPI /billing/checkout 호출
→ Polar Checkout 생성
→ 사용자가 결제
→ Polar Webhook 수신
→ subscription.created / subscription.active / order.created / order.paid 처리
→ subscriptions upsert
→ orders upsert
→ licenses 발급 또는 갱신
→ entitlement_snapshots 갱신
→ 앱에서 /me 또는 /license/check로 Pro 권한 확인
```

### 정상 갱신

```text
현재 구독 active
→ 갱신일 도래
→ Polar renewal event 발생
→ order.created
→ order.paid
→ current_period_end 연장
→ entitlement valid_until 갱신
→ 라이선스 expires_at 갱신
```

### 결제 실패

```text
갱신 결제 실패
→ subscription.updated 또는 payment/order 관련 이벤트 수신
→ status = past_due
→ grace period 시작
→ 앱에서는 제한적 Pro 유지
→ grace period 종료 후 free 강등
```

### 구독 취소

```text
사용자가 Customer Portal에서 취소
→ subscription.canceled 수신
→ cancel_at_period_end = true
→ current_period_end까지 Pro 유지
→ 기간 종료 후 expired 처리
→ free 강등
```

### 즉시 회수

```text
운영자 강제 취소 또는 환불
→ subscription.revoked 또는 refund 관련 이벤트 수신
→ license.status = revoked
→ entitlement.status = revoked
→ 앱 접근 즉시 제한
```

---

## 8.3 Lifetime 라이프사이클

### 신규 구매

```text
사용자 로그인
→ Lifetime 선택
→ FastAPI /billing/checkout 호출
→ Polar Checkout 생성
→ 사용자가 1회 결제
→ Polar Webhook 수신
→ order.paid 처리
→ orders 저장
→ lifetime license 발급
→ entitlement_snapshots = lifetime_active
→ 앱에서 평생 권한 확인
```

### 환불

```text
환불 발생
→ refund 또는 order updated 이벤트 수신
→ order.status = refunded
→ license.status = refunded 또는 revoked
→ entitlement.status = revoked
→ 앱 기능 제한
```

### 버전 정책

평생 플랜은 반드시 범위를 명확히 해야 한다.

```text
옵션 A:
모든 미래 업데이트 포함

옵션 B:
현재 major version 영구 사용
예: v1.x 영구, v2는 유료 업그레이드

옵션 C:
기능은 영구, 클라우드 사용량은 별도 제한
```

추천:

```text
Lifetime = 앱 핵심 기능 영구 사용
클라우드 API 사용량은 월 제한 적용
대규모 AI 사용량은 별도 크레딧 과금
```

---

## 9. Polar Webhook 이벤트 처리 전략

## 9.1 필수 이벤트

```text
checkout.created
checkout.updated

order.created
order.paid
order.updated

subscription.created
subscription.active
subscription.updated
subscription.canceled
subscription.uncanceled
subscription.revoked

refund.created
refund.updated

benefit_grant.created
benefit_grant.updated
benefit_grant.revoked
```

---

## 9.2 Webhook 처리 원칙

```text
1. 서명 검증
2. event_id 중복 확인
3. webhook_events에 원본 저장
4. 즉시 2xx 응답 가능하도록 가볍게 처리
5. 실제 처리는 background worker로 위임 가능
6. idempotent 처리
7. 실패 시 retry 가능
```

---

## 9.3 Webhook 처리 순서

```text
POST /api/v1/billing/webhook/polar
→ verify_signature()
→ save_webhook_event()
→ enqueue_processing()
→ return 200
```

worker:

```text
process_webhook_event(event_id)
→ event_type 분기
→ user 매핑
→ plan 매핑
→ order/subscription/license/entitlement 갱신
→ processed = true
```

---

## 10. Checkout 생성 전략

## 10.1 API

```text
POST /api/v1/billing/checkout
```

### Request

```json
{
  "plan_code": "pro_monthly",
  "success_url": "myapp://billing/success",
  "cancel_url": "myapp://billing/cancel"
}
```

### Response

```json
{
  "checkout_url": "https://polar.sh/checkout/...",
  "checkout_id": "checkout_xxx"
}
```

---

## 10.2 처리 흐름

```text
1. JWT 인증
2. user 조회
3. plan_code 검증
4. free plan이면 결제 생성 차단
5. 이미 lifetime이면 pro 결제 차단 또는 경고
6. 이미 active pro이면 중복 구독 차단
7. Polar checkout 생성
8. checkout_url 반환
```

---

## 10.3 중복 결제 방지

```text
상황:
사용자가 Pro 구독 중인데 또 Pro 결제 시도

처리:
- active subscription 존재하면 checkout 생성하지 않음
- "이미 활성 구독이 있습니다" 반환
- Customer Portal 링크 제공
```

---

## 11. 권한 계산 로직

## 11.1 우선순위

```text
revoked/refunded/suspended
> lifetime_active
> pro_active
> pro_past_due_grace
> free
```

---

## 11.2 Entitlement Resolver

```python
def resolve_entitlement(user):
    if user.status in ["banned", "suspended"]:
        return "blocked"

    lifetime = find_active_lifetime_license(user.id)
    if lifetime:
        return "lifetime"

    subscription = find_latest_subscription(user.id)
    if subscription and subscription.status == "active":
        return "pro"

    if subscription and subscription.status == "past_due":
        if within_grace_period(subscription):
            return "pro_limited"
        return "free"

    return "free"
```

---

## 11.3 기능 매핑

```yaml
free:
  can_use_desktop: true
  can_use_mobile: true
  can_export: false
  can_batch_process: false
  can_use_cloud_sync: false
  daily_requests: 3
  max_devices: 0

pro:
  can_use_desktop: true
  can_use_mobile: true
  can_export: true
  can_batch_process: true
  can_use_cloud_sync: true
  daily_requests: 500
  max_devices: 2

lifetime:
  can_use_desktop: true
  can_use_mobile: true
  can_export: true
  can_batch_process: true
  can_use_cloud_sync: true
  daily_requests: 1000
  max_devices: 3
```

---

## 12. 라이선스 키 발급 정책

## 12.1 발급 대상

```text
Free:
발급 안 함

Pro:
구독 active 상태에서 발급

Lifetime:
결제 완료 후 영구 라이선스 발급
```

---

## 12.2 키 형식

```text
SCP-PRO-XXXX-XXXX-XXXX
SCP-LIFE-XXXX-XXXX-XXXX
```

---

## 12.3 저장 방식

원문 키는 DB에 저장하지 않는다.

```text
사용자에게 최초 1회 표시
DB에는 hash 저장
검색용 prefix만 저장
```

### 예시

```text
license_key = SCP-PRO-A7F2-K9QX-LM31
license_key_prefix = SCP-PRO-A7F2
license_key_hash = sha256(server_pepper + license_key)
```

---

## 12.4 기기 활성화 정책

```text
POST /api/v1/license/activate
```

### Request

```json
{
  "license_key": "SCP-PRO-A7F2-K9QX-LM31",
  "device_fingerprint": "hashed-device-id",
  "device_name": "Hyunseok-Windows-Laptop",
  "platform": "windows",
  "app_version": "0.1.0"
}
```

### Response

```json
{
  "status": "active",
  "plan": "pro",
  "max_devices": 2,
  "activated_devices": 1,
  "offline_token": "signed-offline-token"
}
```

---

## 13. 오프라인 토큰 정책

## 13.1 목적

데스크톱 앱에서 네트워크가 잠시 없어도 사용 가능하게 한다.

---

## 13.2 플랜별 오프라인 허용

```text
free:
0일

pro_monthly:
7일

pro_yearly:
14일

lifetime:
30일
```

---

## 13.3 Offline Token Payload

```json
{
  "user_id": "uuid",
  "license_id": "uuid",
  "plan": "pro",
  "device_hash": "hash",
  "features": ["export", "batch_process"],
  "issued_at": "2026-04-24T00:00:00Z",
  "expires_at": "2026-05-01T00:00:00Z"
}
```

---

## 13.4 주의사항

```text
- 오프라인 토큰은 서버 개인키로 서명한다.
- 앱 내부에서 premium=true 같은 값을 신뢰하지 않는다.
- 네트워크 복구 시 반드시 서버 검증을 다시 수행한다.
```

---

## 14. 고객 대시보드 구성

## 14.1 Dashboard 메뉴

```text
계정
구독 관리
라이선스 키
활성화 기기
결제 내역
인보이스
보안 설정
지원 요청
```

---

## 14.2 구독 관리

표시 항목:

```text
현재 플랜
상태
다음 결제일
구독 취소 버튼
Customer Portal 이동 버튼
플랜 변경 버튼
```

---

## 14.3 라이선스 키 관리

표시 항목:

```text
라이선스 prefix
상태
발급일
만료일
활성화 기기 수
기기 해제 버튼
재발급 요청 버튼
```

---

## 14.4 Customer Portal 연동

Polar Customer Portal은 사용자가 구독, 결제 내역, 인보이스, 결제수단 업데이트, 구독 취소 등을 직접 처리하는 용도로 사용한다.

내 대시보드에서는 다음만 제공한다.

```text
- 현재 상태 요약
- Customer Portal로 이동
- 라이선스/기기 관리
- 앱 권한 상태 표시
```

---

## 15. API 설계

## 15.1 Billing API

```text
GET    /api/v1/billing/plans
POST   /api/v1/billing/checkout
GET    /api/v1/billing/subscription
GET    /api/v1/billing/orders
POST   /api/v1/billing/customer-portal
POST   /api/v1/billing/webhook/polar
```

---

## 15.2 License API

```text
GET    /api/v1/licenses/me
POST   /api/v1/licenses/activate
POST   /api/v1/licenses/check
POST   /api/v1/licenses/deactivate
POST   /api/v1/licenses/reissue
```

---

## 15.3 Entitlement API

```text
GET    /api/v1/entitlements/me
POST   /api/v1/entitlements/sync
```

---

## 15.4 Admin API

```text
GET    /api/v1/admin/subscriptions
GET    /api/v1/admin/orders
GET    /api/v1/admin/licenses
POST   /api/v1/admin/licenses/revoke
POST   /api/v1/admin/subscriptions/sync
```

---

## 16. 플랜 전환 시나리오

## 16.1 Free → Pro Monthly

```text
free
→ checkout_created
→ payment_success
→ subscription_active
→ license_issued
→ entitlement_pro
```

---

## 16.2 Free → Lifetime

```text
free
→ checkout_created
→ order_paid
→ lifetime_license_issued
→ entitlement_lifetime
```

---

## 16.3 Pro Monthly → Pro Yearly

선택지:

```text
A. 즉시 변경
B. 다음 결제 주기부터 변경
```

추천:

```text
초기 MVP에서는 Customer Portal에 위임한다.
내부에서는 webhook 결과만 동기화한다.
```

---

## 16.4 Pro → Lifetime

처리 정책을 반드시 정해야 한다.

추천 정책:

```text
- Lifetime 구매 가능
- 기존 Pro 구독은 사용자에게 Customer Portal에서 취소 안내
- Lifetime 활성화 후 entitlement는 lifetime 우선 적용
- Pro 갱신 방지를 위해 대시보드에서 구독 취소 안내 표시
```

자동 취소를 API로 처리할 수도 있지만, 초기에는 사용자 명시 동작을 권장한다. 자동으로 돈 관련 작업을 건드리는 건 대체로 인간 분쟁 제조기다.

---

## 16.5 Lifetime → Pro

```text
허용하지 않음
```

Lifetime이 이미 최상위 권한이므로 Pro checkout 차단.

---

## 17. 환불 / 취소 / 만료 정책

## 17.1 Pro 구독 취소

```text
취소 즉시:
subscription.status = canceled
cancel_at_period_end = true

권한:
current_period_end까지 유지

기간 종료:
entitlement = free
license = expired
```

---

## 17.2 Pro 즉시 취소 / 강제 회수

```text
subscription.revoked
→ entitlement = revoked
→ license = revoked
→ 앱 접근 제한
```

---

## 17.3 Lifetime 환불

```text
refund event
→ order.status = refunded
→ license.status = refunded
→ entitlement = revoked
→ 앱 접근 제한
```

---

## 17.4 결제 실패

```text
subscription = past_due
→ grace_period 시작
→ 앱에 결제수단 업데이트 안내
→ grace_period 종료 후 free 강등
```

---

## 18. 장애 대응 시나리오

## 18.1 Webhook 중복 수신

문제:

```text
Polar webhook이 같은 event를 여러 번 보낼 수 있음
```

해결:

```text
webhook_events.event_id unique
이미 처리된 event는 skip
```

---

## 18.2 Webhook 지연

문제:

```text
결제는 성공했지만 앱에 Pro 권한이 바로 안 보임
```

해결:

```text
대시보드에 "결제 동기화" 버튼 제공
POST /api/v1/entitlements/sync
Polar API에서 현재 customer 상태 조회 후 내부 DB 보정
```

---

## 18.3 앱 복귀 실패

문제:

```text
데스크톱 앱에서 브라우저 결제 후 앱으로 돌아오지 못함
```

해결:

```text
success_url은 보조 수단
실제 권한 반영은 webhook 기준
앱에는 "결제 완료 확인" 버튼 제공
```

---

## 18.4 네트워크 장애

```text
로그인 중 실패:
명확한 재시도 메시지

라이선스 검증 실패:
오프라인 토큰 유효기간 내 제한 허용

결제 중 실패:
Polar Checkout 상태는 서버에서 재확인
```

---

## 19. 테스트 계획

## 19.1 단위 테스트

```text
plan resolver
entitlement resolver
license generator
license hash verify
webhook parser
status transition
device limit checker
```

---

## 19.2 통합 테스트

```text
Free signup → free entitlement
Pro checkout → subscription active → license issued
Lifetime order paid → lifetime active
Cancel subscription → free downgrade
Refund lifetime → revoked
Duplicate webhook → only once processed
```

---

## 19.3 E2E 테스트

```text
회원가입
→ 로그인
→ Pro 결제
→ 데스크톱 앱 활성화
→ 앱 재시작
→ 라이선스 유지 확인
```

```text
회원가입
→ Lifetime 결제
→ 라이선스 발급
→ 3대 기기 활성화
→ 4대 차단 확인
```

---

## 19.4 수동 QA

```text
결제창 닫기
잘못된 카드
구독 취소
환불
앱 삭제 후 재설치
오프라인 실행
기기 이름 변경
VPN 환경
```

---

## 20. 개발 작업 순서

## Phase 1. Polar 상품 구성

```text
1. Polar Organization 생성
2. Pro Monthly Product 생성
3. Pro Yearly Product 생성
4. Lifetime Product 생성
5. 각 상품에 Benefit 연결
6. Webhook Endpoint 등록
7. Sandbox 결제 테스트
```

---

## Phase 2. DB 및 Plan Seed

```text
1. plans 테이블 생성
2. subscriptions 테이블 생성
3. orders 테이블 생성
4. licenses 테이블 생성
5. license_activations 테이블 생성
6. entitlement_snapshots 테이블 생성
7. webhook_events 테이블 생성
8. plan seed 작성
```

---

## Phase 3. Checkout API

```text
1. GET /billing/plans
2. POST /billing/checkout
3. 중복 구독 차단
4. Lifetime 보유자 checkout 차단
5. Checkout URL 반환
```

---

## Phase 4. Webhook API

```text
1. Webhook signature 검증
2. event_id 저장
3. 중복 이벤트 skip
4. order.paid 처리
5. subscription.created 처리
6. subscription.updated 처리
7. subscription.canceled 처리
8. subscription.revoked 처리
9. refund 처리
```

---

## Phase 5. Entitlement Resolver

```text
1. user 현재 플랜 계산
2. lifetime 우선순위 적용
3. pro active 처리
4. past_due grace 처리
5. free fallback
6. /entitlements/me API 작성
```

---

## Phase 6. License Module

```text
1. license key generator
2. hash 저장
3. activate API
4. check API
5. deactivate API
6. device limit 검사
7. offline token 발급
```

---

## Phase 7. Dashboard

```text
1. 현재 플랜 표시
2. 구독 상태 표시
3. Customer Portal 이동 버튼
4. 라이선스 목록 표시
5. 기기 목록 표시
6. 기기 해제 버튼
7. 결제 내역 표시
```

---

## Phase 8. Client Integration

### PySide6

```text
1. 로그인
2. /entitlements/me 호출
3. /licenses/check 호출
4. offline token 저장
5. Pro 기능 unlock
6. 만료 시 제한 모드
```

### Flutter

```text
1. 로그인
2. 권한 조회
3. 결제 checkout 브라우저 열기
4. 앱 복귀 후 권한 재조회
5. Customer Portal 이동
```

---

## 21. 운영 체크리스트

```text
- Polar live mode product id 등록
- sandbox key와 live key 분리
- webhook secret 환경별 분리
- .env에 product id 등록
- webhook endpoint HTTPS 적용
- event_id idempotency 적용
- 실패 이벤트 재처리 기능
- admin sync 기능
- 환불 처리 테스트
- 구독 취소 테스트
- 라이선스 revoke 테스트
```

---

## 22. 권장 정책 결정표

| 항목 | 추천 정책 |
|---|---|
| Free 라이선스 | 발급 안 함 |
| Pro 라이선스 | 구독 active 동안 발급 |
| Lifetime 라이선스 | 1회 결제 후 발급 |
| Pro 취소 | 기간 종료일까지 유지 |
| Pro 환불 | 즉시 회수 |
| Lifetime 환불 | 즉시 회수 |
| Pro → Lifetime | 허용 |
| Lifetime → Pro | 차단 |
| Lifetime 업데이트 | major version 정책 명시 |
| 오프라인 허용 | Pro 7~14일, Lifetime 30일 |
| 기기 제한 | Pro 2~3대, Lifetime 3대 |

---

## 23. 최종 추천 구성

```text
Free:
내부 DB 기본 플랜
Polar 상품 없음
라이선스 없음

Pro Monthly:
Polar recurring monthly product
구독형 라이선스
2대 기기
7일 오프라인

Pro Yearly:
Polar recurring yearly product
구독형 라이선스
3대 기기
14일 오프라인

Lifetime:
Polar one-time product
평생 라이선스
3대 기기
30일 오프라인
환불 시 revoke
```

---

## 24. 가장 중요한 결론

이 시스템의 핵심은 플랜을 이렇게 분리하는 것이다.

```text
Polar = 결제와 구독 이벤트의 원천
FastAPI = 권한과 라이선스의 원천
Client = 서버가 허용한 기능만 표시
```

절대로 클라이언트에서 결제 성공이나 유료 상태를 판단하지 않는다.

```text
클라이언트 premium=true 저장
```