import json
import base64
import httpx
import platform
import subprocess
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class SecureClient:
    def __init__(self, api_url: str, project_id: str, aes_key: str):
        self.api_url = api_url
        self.project_id = project_id
        # 서버와 동일한 32바이트 키 생성
        self.aes_key = aes_key.encode().ljust(32, b'\0')[:32]
        self.aesgcm = AESGCM(self.aes_key)
        self.headers = {
            "x-project-id": self.project_id,
            "Content-Type": "application/json"
        }

    def _get_hwid(self) -> str:
        """
        간이 하드웨어 지문(HWID) 추출 예시. 
        실제 운영 환경에서는 더욱 복잡한 로직(WMI, CPUID 등) 사용 권장.
        """
        system_info = f"{platform.node()}-{platform.processor()}-{platform.system()}"
        return hashlib.sha256(system_info.encode()).hexdigest()

    def _encrypt_payload(self, data: dict) -> str:
        """데이터를 AES-256-GCM으로 암호화하여 Base64로 반환"""
        nonce = AESGCM.generate_nonce(12)
        data_bytes = json.dumps(data).encode()
        ciphertext = self.aesgcm.encrypt(nonce, data_bytes, None)
        return base64.b64encode(nonce + ciphertext).decode('utf-8')

    def _decrypt_payload(self, encrypted_base64: str) -> dict:
        """Base64 암호화 데이터를 복호화하여 딕셔너리로 반환"""
        encrypted_bytes = base64.b64decode(encrypted_base64)
        nonce = encrypted_bytes[:12]
        ciphertext = encrypted_bytes[12:]
        decrypted_bytes = self.aesgcm.decrypt(nonce, ciphertext, None)
        return json.loads(decrypted_bytes.decode('utf-8'))

    async def validate_license(self, license_key: str):
        """보안 엔드포인트를 통해 라이선스 유효성을 검증합니다."""
        hwid = self._get_hwid()
        
        # 1. 요청 데이터 준비 및 암호화
        request_data = {
            "license_key": license_key,
            "fingerprint": hwid
        }
        encrypted_payload = self._encrypt_payload(request_data)
        
        # 2. 서버로 암호화된 데이터 전송
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/license/validate-secure",
                json={"payload": encrypted_payload},
                headers=self.headers
            )
            
            if response.status_code != 200:
                print(f"Error: {response.status_code}")
                return None
            
            # 3. 응답 데이터 복호화
            encrypted_response = response.json().get("payload")
            decrypted_response = self._decrypt_payload(encrypted_response)
            return decrypted_response

# 사용 예시 (테스트용)
if __name__ == "__main__":
    import asyncio
    
    # 설정값 (서버의 config.py와 일치해야 함)
    CLIENT = SecureClient(
        api_url="http://localhost:8000/api/v1",
        project_id="test-project-001",
        aes_key="32-char-long-secret-key-for-aes-256"
    )
    
    async def main():
        print("라이선스 검증 시도 중...")
        result = await CLIENT.validate_license("YOUR-LICENSE-KEY-HERE")
        print(f"검증 결과: {result}")

    # asyncio.run(main()) # 서버가 실행 중일 때만 작동
