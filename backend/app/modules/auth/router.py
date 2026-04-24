from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.depends import get_db, get_current_user, get_project_id
from app.services import user_service
from app.schemas.user import UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/me", response_model=UserResponse)
async def get_me(
    db: Session = Depends(get_db),
    user_info: dict = Depends(get_current_user),
    project_id: str = Depends(get_project_id)
):
    """
    현재 로그인한 사용자의 정보를 반환합니다. 
    최초 로그인 시 DB 동기화를 수행합니다.
    """
    user = user_service.sync_supabase_user(
        db, 
        supabase_user_id=user_info["id"], 
        project_id=project_id,
        email=user_info.get("email")
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
        
    return user
