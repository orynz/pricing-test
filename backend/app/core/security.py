import json
import base64
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union

import jwt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from passlib.context import CryptContext

from app.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class SecurityError(Exception):
    """Base class for security-related errors."""
    pass

class AESCipher:
    """
    AES-256-GCM encryption and decryption utility for application-level payload security.
    """
    def __init__(self, key: str = settings.AES_SECRET_KEY):
        # Ensure key is 32 bytes for AES-256
        if isinstance(key, str):
            key_bytes = key.encode().ljust(32, b'\0')[:32]
        else:
            key_bytes = key
        self.aesgcm = AESGCM(key_bytes)

    def encrypt(self, data: Union[str, Dict[str, Any]]) -> str:
        """Encrypts data and returns a base64 encoded string containing nonce + ciphertext."""
        if isinstance(data, dict):
            data = json.dumps(data)
        
        data_bytes = data.encode()
        nonce = os.urandom(12) # 12 bytes nonce for GCM
        ciphertext = self.aesgcm.encrypt(nonce, data_bytes, None)
        
        # Combine nonce and ciphertext then encode to base64
        return base64.b64encode(nonce + ciphertext).decode('utf-8')

    def decrypt(self, encrypted_base64: str) -> str:
        """Decrypts a base64 encoded string and returns the original string."""
        try:
            encrypted_bytes = base64.b64decode(encrypted_base64)
            nonce = encrypted_bytes[:12]
            ciphertext = encrypted_bytes[12:]
            
            decrypted_bytes = self.aesgcm.decrypt(nonce, ciphertext, None)
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            raise SecurityError(f"Decryption failed: {str(e)}")

    def decrypt_to_dict(self, encrypted_base64: str) -> Dict[str, Any]:
        """Decrypts and parses JSON string to dictionary."""
        decrypted_str = self.decrypt(encrypted_base64)
        return json.loads(decrypted_str)

# Global cipher instance
cipher = AESCipher()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    # PyJWT.encode returns a string (already decoded in PyJWT 2.x)
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_hmac_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Verifies HMAC-SHA256 signature for webhooks.
    """
    import hmac
    import hashlib
    
    expected_signature = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_signature, signature)
