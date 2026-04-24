import pytest
from app.core.security import cipher
import json

def test_health_check(client):
    """헬스체크 API 테스트"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_license_validate_secure_unauthorized(client):
    """인증 헤더(x-project-id) 누락 시 차단 테스트"""
    payload = cipher.encrypt({"license_key": "test", "fingerprint": "test"})
    response = client.post(
        "/api/v1/license/validate-secure",
        json={"payload": payload}
    )
    # Header가 없으므로 422 (Unprocessable Entity) 발생 확인
    assert response.status_code == 422

def test_license_validate_secure_flow(client):
    """암호화된 라이선스 검증 전체 흐름 테스트"""
    project_id = "test-project"
    request_data = {
        "license_key": "INVALID-KEY",
        "fingerprint": "test-device-id"
    }
    encrypted_request = cipher.encrypt(request_data)
    
    headers = {"x-project-id": project_id}
    response = client.post(
        "/api/v1/license/validate-secure",
        json={"payload": encrypted_request},
        headers=headers
    )
    
    assert response.status_code == 200
    
    # 응답 복호화
    encrypted_response = response.json().get("payload")
    decrypted_response = cipher.decrypt_to_dict(encrypted_response)
    
    # INVALID-KEY이므로 valid는 False여야 함
    assert decrypted_response["valid"] is False
    assert "timestamp" in decrypted_response
