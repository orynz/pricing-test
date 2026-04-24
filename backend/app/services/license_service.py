from sqlalchemy.orm import Session
from app.models.license import License
from app.models.device import Device
from app.models.plan import Plan
from app.core.security import create_access_token
from typing import Optional, Tuple, Dict, Any
import hashlib
from datetime import datetime, timezone, timedelta

import secrets
import string

def create_license(
    db: Session, 
    user_id: str, 
    project_id: str, 
    plan_name: str = "Pro",
    device_limit: int = 3,
    expires_at: Optional[datetime] = None
) -> License:
    """
    새로운 라이선스 키를 생성하고 DB에 저장합니다.
    형식: SCP-PRO-XXXX-XXXX-XXXX
    """
    # 1. 랜덤 라이선스 키 생성
    chars = string.ascii_uppercase + string.digits
    suffix = '-'.join(''.join(secrets.choice(chars) for _ in range(4)) for _ in range(2))
    
    # 접두사 결정
    prefix_main = "SCP-LIFE" if "Lifetime" in plan_name else "SCP-PRO"
    prefix_rand = ''.join(secrets.choice(chars) for _ in range(4))
    prefix = f"{prefix_main}-{prefix_rand}"
    
    full_key = f"{prefix}-{suffix}"
    key_hash = hash_license_key(full_key)
    
    new_license = License(
        user_id=user_id,
        project_id=project_id,
        license_key=full_key, # 사용자에게 1회 노출용
        license_key_prefix=prefix,
        key_hash=key_hash,
        status="active",
        max_devices=device_limit,
        issued_at=datetime.now(timezone.utc),
        expires_at=expires_at
    )
    db.add(new_license)
    db.commit()
    db.refresh(new_license)
    return new_license

def hash_license_key(key: str) -> str:
    """라이선스 키 해싱"""
    return hashlib.sha256(key.encode()).hexdigest()

def get_license_by_key(db: Session, license_key: str, project_id: str) -> Optional[License]:
    key_hash = hash_license_key(license_key)
    return db.query(License).filter(
        License.key_hash == key_hash,
        License.project_id == project_id
    ).first()

def activate_device(
    db: Session, 
    license_id: str, 
    fingerprint: str, 
    device_name: str = None, 
    platform: str = None,
    app_version: str = None
) -> Dict[str, Any]:
    """
    기기를 라이선스에 등록하고 오프라인 토큰을 발급합니다. (Section 12.4)
    """
    license = db.query(License).filter(License.id == license_id).first()
    if not license or license.status != "active":
        return {"success": False, "message": "License is not active"}

    # 이미 등록된 기기인지 확인
    existing_device = db.query(Device).filter(
        Device.license_id == license_id,
        Device.device_fingerprint == fingerprint
    ).first()
    
    if existing_device:
        existing_device.last_seen_at = datetime.now(timezone.utc)
        if app_version: existing_device.app_version = app_version
        db.commit()
    else:
        # 기기 제한 확인
        active_devices_count = db.query(Device).filter(
            Device.license_id == license_id,
            Device.status == "active"
        ).count()
        
        if active_devices_count >= license.max_devices:
            return {"success": False, "message": "Device limit exceeded"}

        # 신규 기기 등록
        new_device = Device(
            license_id=license_id,
            user_id=license.user_id,
            project_id=license.project_id,
            device_fingerprint=fingerprint,
            device_name=device_name,
            platform=platform,
            app_version=app_version,
            last_seen_at=datetime.now(timezone.utc),
            status="active"
        )
        db.add(new_device)
        db.commit()

    # 오프라인 토큰 발급 (Section 13.3)
    # 플랜별 오프라인 허용 기간 설정
    offline_days = 7
    plan = db.query(Plan).filter(Plan.id == license.plan_id).first()
    if plan:
        offline_days = plan.offline_access_days

    expires_at = datetime.now(timezone.utc) + timedelta(days=offline_days)
    
    token_payload = {
        "sub": str(license.user_id),
        "license_id": str(license.id),
        "device_hash": fingerprint,
        "entitlement": plan.entitlement_level if plan else "pro",
        "iat": datetime.now(timezone.utc),
        "exp": expires_at
    }
    
    offline_token = create_access_token(token_payload, expires_delta=timedelta(days=offline_days))
    
    return {
        "success": True,
        "message": "Activation successful",
        "offline_token": offline_token,
        "expires_at": expires_at.isoformat()
    }

def validate_license_device(db: Session, license_key: str, project_id: str, fingerprint: str) -> Dict[str, Any]:
    """라이선스와 기기 유효성 검증"""
    license = get_license_by_key(db, license_key, project_id)
    if not license or license.status != "active":
        return {"valid": False, "message": "Invalid or inactive license"}
        
    device = db.query(Device).filter(
        Device.license_id == license.id,
        Device.device_fingerprint == fingerprint,
        Device.status == "active"
    ).first()
    
    if not device:
        return {"valid": False, "message": "Device not registered for this license"}
        
    device.last_seen_at = datetime.now(timezone.utc)
    db.commit()
    
    return {"valid": True, "license_id": str(license.id), "user_id": str(license.user_id)}
