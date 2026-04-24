from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.depends import get_db, get_current_user, get_project_id
from app.models.user import User
from app.models.subscription import Subscription
from app.models.license import License
from app.models.device import Device
from app.models.plan import Plan
from app.schemas.dashboard import DashboardSummary, DeviceInfo, LicenseInfo

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(
    db: Session = Depends(get_db),
    user_info: dict = Depends(get_current_user),
    project_id: str = Depends(get_project_id)
):
    user = db.query(User).filter(
        User.supabase_user_id == user_info["id"], 
        User.project_id == project_id
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    subscription = db.query(Subscription).filter(Subscription.user_id == user.id).first()
    
    plan_name = "Free"
    if subscription:
        plan = db.query(Plan).filter(Plan.id == subscription.plan_id).first()
        if plan:
            plan_name = plan.display_name

    licenses = db.query(License).filter(License.user_id == user.id).all()
    license_ids = [l.id for l in licenses]
    devices_count = db.query(Device).filter(Device.license_id.in_(license_ids)).count() if license_ids else 0

    return {
        "user_email": user.email,
        "current_plan": plan_name,
        "subscription_status": subscription.status if subscription else "None",
        "active_licenses_count": len(licenses),
        "active_devices_count": devices_count
    }

@router.get("/licenses", response_model=List[LicenseInfo])
async def get_user_licenses(
    db: Session = Depends(get_db),
    user_info: dict = Depends(get_current_user),
    project_id: str = Depends(get_project_id)
):
    user = db.query(User).filter(
        User.supabase_user_id == user_info["id"], 
        User.project_id == project_id
    ).first()
    
    if not user:
        return []
        
    licenses = db.query(License).filter(License.user_id == user.id).all()
    
    result = []
    for l in licenses:
        active_devices = db.query(Device).filter(Device.license_id == l.id, Device.status == "active").count()
        result.append({
            "id": l.id,
            "license_key_prefix": l.license_key_prefix,
            "status": l.status,
            "issued_at": l.issued_at,
            "expires_at": l.expires_at,
            "max_devices": l.max_devices,
            "active_devices_count": active_devices
        })
        
    return result

@router.get("/devices", response_model=List[DeviceInfo])
async def get_user_devices(
    db: Session = Depends(get_db),
    user_info: dict = Depends(get_current_user),
    project_id: str = Depends(get_project_id)
):
    user = db.query(User).filter(
        User.supabase_user_id == user_info["id"], 
        User.project_id == project_id
    ).first()
    
    if not user:
        return []
        
    licenses = db.query(License).filter(License.user_id == user.id).all()
    license_ids = [l.id for l in licenses]
    
    if not license_ids:
        return []
        
    devices = db.query(Device).filter(Device.license_id.in_(license_ids)).all()
    return devices

@router.post("/devices/{device_id}/remove")
async def remove_device(
    device_id: str,
    db: Session = Depends(get_db),
    user_info: dict = Depends(get_current_user),
    project_id: str = Depends(get_project_id)
):
    user = db.query(User).filter(
        User.supabase_user_id == user_info["id"], 
        User.project_id == project_id
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    device = db.query(Device).join(License).filter(
        Device.id == device_id,
        License.user_id == user.id
    ).first()
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found or unauthorized")
        
    db.delete(device)
    db.commit()
    return {"status": "success", "message": "Device removed"}
