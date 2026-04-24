from sqlalchemy.orm import Session
from app.models.user import User
from uuid import UUID
from typing import Optional
import uuid

def get_user_by_supabase_id(db: Session, supabase_user_id: str, project_id: str = None) -> Optional[User]:
    # supabase_user_id가 문자열인 경우 UUID로 변환 시도
    try:
        if isinstance(supabase_user_id, str):
            target_uuid = uuid.UUID(supabase_user_id)
        else:
            target_uuid = supabase_user_id
    except ValueError:
        return None

    query = db.query(User).filter(User.supabase_user_id == target_uuid)
    if project_id:
        user = query.filter(User.project_id == project_id).first()
        if user:
            return user
    return query.first()

def create_user_from_supabase(db: Session, supabase_user_id: str, project_id: str, email: str = None, name: str = None) -> User:
    # 문자열 ID를 UUID 객체로 명시적 변환
    if isinstance(supabase_user_id, str):
        supabase_user_id = uuid.UUID(supabase_user_id)
        
    user = User(
        supabase_user_id=supabase_user_id,
        project_id=project_id,
        email=email,
        name=name,
        status="active"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def sync_supabase_user(db: Session, supabase_user_id: str, project_id: str, email: str = None) -> User:
    """
    Supabase 인증 정보를 바탕으로 로컬 DB와 동기화합니다.
    """
    user = get_user_by_supabase_id(db, supabase_user_id)
    
    if not user:
        user = create_user_from_supabase(db, supabase_user_id, project_id, email=email)
    else:
        # 기존 사용자가 있다면 정보 업데이트
        updated = False
        if user.project_id != project_id:
            user.project_id = project_id
            updated = True
        if email and user.email != email:
            user.email = email
            updated = True
            
        if updated:
            db.commit()
            db.refresh(user)
            
    return user
