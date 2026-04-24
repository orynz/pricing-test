from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.depends import get_db, get_project_id
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter(prefix="/admin", tags=["admin"])

# Note: In a real app, you would add an admin role check here
def verify_admin_role():
    # Placeholder for actual admin role verification
    pass

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    project_id: str = Depends(get_project_id),
    email: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """관리자용 사용자 통합 검색 API"""
    query = db.query(User).filter(User.project_id == project_id)
    
    if email:
        query = query.filter(User.email.ilike(f"%{email}%"))
    if status:
        query = query.filter(User.status == status)
        
    return query.all()

@router.post("/users/{user_id}/suspend")
async def suspend_user(
    user_id: str,
    db: Session = Depends(get_db)
):
    """사용자 계정 정지"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.status = "suspended"
    db.commit()
    return {"status": "success", "message": "User suspended"}

@router.post("/users/{user_id}/activate")
async def activate_user(
    user_id: str,
    db: Session = Depends(get_db)
):
    """사용자 계정 활성화"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.status = "active"
    db.commit()
    return {"status": "success", "message": "User activated"}
