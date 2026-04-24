from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session

from app.core.depends import get_db, get_current_user, get_project_id
from app.services.polar_service import polar_service
from app.schemas.billing import PlanSchema, CheckoutRequest, CheckoutResponse
from app.models.plan import Plan
from app.models.subscription import Subscription

router = APIRouter(prefix="/billing", tags=["billing"])


@router.get("/plans", response_model=List[PlanSchema])
async def get_billing_plans(db: Session = Depends(get_db)):
    """
    DB에서 활성화된 요금제 목록을 가져옵니다.
    """
    plans = db.query(Plan).filter(Plan.is_active.is_(True)).all()
    return plans


@router.post("/checkout", response_model=CheckoutResponse)
async def create_billing_checkout(
    request: CheckoutRequest,
    db: Session = Depends(get_db),
    user_info: dict = Depends(get_current_user),
    project_id: str = Depends(get_project_id),
):
    """
    결제 페이지 URL을 생성합니다.
    중복 활성 구독이 있으면 checkout 생성을 차단합니다.
    """

    # 1. 요금제 정보 확인
    plan = db.query(Plan).filter(Plan.plan_code == request.plan_code).first()

    if not plan:
        raise HTTPException(status_code=400, detail="Invalid plan selection")

    if plan.plan_code == "free":
        raise HTTPException(status_code=400, detail="Free plan does not require checkout")

    if not plan.polar_product_id:
        raise HTTPException(status_code=400, detail="Selected plan is not connected to Polar product")

    # 2. 중복 구독 확인
    existing_sub = (
        db.query(Subscription)
        .filter(
            Subscription.user_id == user_info["id"],
            Subscription.status.in_(["active", "trialing", "past_due"]),
        )
        .first()
    )

    if existing_sub:
        raise HTTPException(
            status_code=400,
            detail="이미 활성 구독이 있습니다. 관리 페이지에서 구독을 관리해 주세요.",
        )

    # 3. Polar 결제 생성
    try:
        checkout = await polar_service.create_checkout(
            product_id=plan.polar_product_id,
            success_url=request.success_url,
            customer_email=user_info.get("email"),
            metadata={
                "user_id": str(user_info["id"]),
                "project_id": project_id,
                "plan_code": plan.plan_code,
            },
        )

        return {
            "url": str(checkout.url),
            "checkout_id": str(checkout.id),
        }

    except Exception as e:
        print(f"Checkout Error: {e}")
        raise HTTPException(status_code=400, detail="Failed to create checkout session")