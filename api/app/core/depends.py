from typing import Generator, Optional

from fastapi import Header, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import PyJWKClient, decode, InvalidTokenError

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings


engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_project_id(
    x_project_id: str = Header(..., alias="x-project-id", description="Multi-tenant Project Identifier")
) -> str:
    if not x_project_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="x-project-id header is required",
        )
    return x_project_id


security = HTTPBearer(auto_error=True)


jwks_client = PyJWKClient(
    f"{settings.SUPABASE_URL}/auth/v1/.well-known/jwks.json"
)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    project_id: str = Depends(get_project_id),
) -> dict:
    token = credentials.credentials

    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        payload = decode(
            token,
            signing_key.key,
            algorithms=["ES256", "RS256"],
            audience="authenticated",
            issuer=f"{settings.SUPABASE_URL}/auth/v1",
        )

        user_id: Optional[str] = payload.get("sub")
        email: Optional[str] = payload.get("email")
        role: Optional[str] = payload.get("role")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if role != "authenticated":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role",
            )

        return {
            "id": user_id,
            "email": email,
            "project_id": project_id,
        }

    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )