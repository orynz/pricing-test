import pytest
from app.core.security import cipher, verify_hmac_signature, get_password_hash, verify_password

def test_aes_encryption_decryption():
    """AES-256-GCM 암복호화 테스트"""
    original_data = {"license_key": "SECURE-KEY-123", "user_id": "user_abc"}
    
    # 1. 암호화
    encrypted = cipher.encrypt(original_data)
    assert isinstance(encrypted, str)
    assert encrypted != str(original_data)
    
    # 2. 복호화
    decrypted = cipher.decrypt_to_dict(encrypted)
    assert decrypted == original_data

def test_hmac_signature_verification():
    """HMAC 서명 검증 테스트 (웹훅용)"""
    secret = "webhook-secret-key"
    payload = b'{"event": "payment_success"}'
    
    # 올바른 서명 생성 (외부 서비스 시뮬레이션)
    import hmac
    import hashlib
    signature = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    
    # 검증 성공
    assert verify_hmac_signature(payload, signature, secret) is True
    # 잘못된 서명 검증 실패
    assert verify_hmac_signature(payload, "wrong-signature", secret) is False

def test_password_hashing():
    """패스워드 해싱 및 검증 테스트"""
    password = "secure_password_123"
    hashed = get_password_hash(password)
    
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False
