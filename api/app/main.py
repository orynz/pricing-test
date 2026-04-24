from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from app.core.config import settings
from app.models.base import Base
from app.core.depends import engine
# 모든 모델을 명시적으로 임포트해야 create_all이 이를 인식합니다.
from app.models import user, subscription, license, device, plan, order, entitlement, webhook
import os

# Create tables on startup
# Base.metadata.create_all(bind=engine) # 서버리스 환경에서는 주석 처리 (마이그레이션 도구 권장)

def get_application() -> FastAPI:
    _app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )

    # Templates setup
    templates = Jinja2Templates(directory="app/templates")

    # CORS Middleware
    _app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], # In production, replace with specific origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @_app.get(f"{settings.API_V1_STR}/")
    async def root():
        return {"message": "Welcome to Secure Core Platform API"}

    @_app.get(f"{settings.API_V1_STR}/health")
    async def health_check():
        return {"status": "healthy"}

    @_app.get(f"{settings.API_V1_STR}/test")
    async def test_page(request: Request):
        return templates.TemplateResponse("test_client.html", {
            "request": request,
            "supabase_url": settings.SUPABASE_URL,
            "supabase_anon_key": settings.SUPABASE_ANON_KEY
        })

    from app.api import api_router
    _app.include_router(api_router, prefix=settings.API_V1_STR)

    return _app

app = get_application()
