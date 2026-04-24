# Authentication & Login Flow Guide

이 프로젝트는 Supabase Auth(Google OAuth)와 로컬 백엔드를 연동하여 멀티테넌트 라이선스 관리 시스템을 구현합니다.

## 1. 로그인 흐름
1. **Frontend**: 사용자가 Google 로그인을 완료하면 Supabase로부터 JWT(Access Token)를 받습니다.
2. **Backend Header**: 모든 백엔드 요청에는 다음 헤더가 포함됩니다.
   - `Authorization: Bearer <Supabase_JWT>`
   - `x-project-id: <Project_Reference_ID>`
3. **JWT Verification**: 백엔드는 Supabase의 JWKS 엔드포인트에서 공개 키를 실시간으로 가져와 `ES256` 토큰을 검증합니다 (`PyJWT` 사용).
4. **User Sync**: 검증된 사용자 정보를 바탕으로 로컬 DB(`public.users`)와 동기화합니다. 사용자가 처음 로그인하면 DB에 자동 등록됩니다.

## 2. 환경 설정 (.env)
- `DATABASE_URL`: Supabase Transaction Pooler 주소 (IPv4 지원, 6543 포트)를 사용합니다.
- `SUPABASE_URL`: JWT 검증 시 `issuer` 및 `JWKS` 엔드포인트 생성에 사용됩니다.
- `ALGORITHM`: Supabase 기본값인 `ES256`을 처리하도록 백엔드에 구현되어 있습니다.

## 3. 데이터베이스 초기화
최초 실행 시 테이블 생성이 필요합니다.
```bash
cd backend
uv run init_db.py
```
*참고: `app/main.py` 구동 시에도 `create_all`이 자동으로 실행되도록 설정되어 있습니다.*

## 4. 발생했던 주요 이슈 및 해결책
- **ES256 MalformedFraming**: `python-jose` 대신 `PyJWT`를 사용하고 공개 키를 PEM 형식으로 정규화하여 해결.
- **DB Connection Timeout**: 직접 연결 대신 Transaction Pooler를 사용하고 포트를 6543으로 지정하여 IPv4 환경 문제 해결.
- **Tenant Identifier Missing**: 연결 문자열의 사용자 이름에 `postgres.<project_id>` 형식을 적용하여 해결.
