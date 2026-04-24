from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.depends import get_db, get_project_id
from app.core.security import cipher
from app.schemas.license import EncryptedPayload, LicenseActivateRequest
from app.services import license_service
import json
from datetime import datetime, timezone

router = APIRouter(prefix="/license", tags=["license"])

@router.post("/activate")
async def activate_license(
    request: LicenseActivateRequest,
    db: Session = Depends(get_db),
    project_id: str = Depends(get_project_id)
):
    """라이선스 키를 현재 기기에 활성화하고 오프라인 토큰을 발급합니다."""
    license = license_service.get_license_by_key(db, request.license_key, project_id)
    if not license:
        raise HTTPException(status_code=404, detail="License key not found")
    
    result = license_service.activate_device(
        db, 
        license.id, 
        request.fingerprint, 
        request.device_name, 
        request.platform
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
        
    return result

@router.post("/validate-secure")
async def validate_license_secure(
    encrypted_data: EncryptedPayload,
    db: Session = Depends(get_db),
    project_id: str = Depends(get_project_id)
):
    """
    데스크톱 앱 보안을 위한 암호화된 라이선스 검증 API.
    Payload: AES-256-GCM encrypted {"license_key": "...", "fingerprint": "..."}
    """
    try:
        # 1. 페이로드 복호화
        decrypted_data = cipher.decrypt_to_dict(encrypted_data.payload)
        license_key = decrypted_data.get("license_key")
        fingerprint = decrypted_data.get("fingerprint")
        
        if not license_key or not fingerprint:
            raise ValueError("Missing required fields in payload")
            
        # 2. 유효성 검증
        validation_result = license_service.validate_license_device(db, license_key, project_id, fingerprint)
        is_valid = validation_result["valid"]
        
        # 3. 결과 생성 및 암호화
        response_data = {
            "valid": is_valid,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "project_id": project_id
        }
        
        # 유효할 경우 추가 데이터 및 오프라인 토큰 갱신 정보 포함
        if is_valid:
            # 검증 성공 시 기기 활성화 정보를 다시 생성하여 최신 오프라인 토큰 제공
            act_result = license_service.activate_device(
                db, 
                validation_result["license_id"], 
                fingerprint
            )
            response_data.update({
                "features": ["premium_access", "cloud_sync"],
                "offline_token": act_result.get("offline_token"),
                "expires_at": act_result.get("expires_at")
            })
            
        return {"payload": cipher.encrypt(response_data)}
        
    except Exception as e:
        print(f"❌ Validation Error: {e}")
        error_response = {
            "valid": False, 
            "error": "Invalid request",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        return {"payload": cipher.encrypt(error_response)}
