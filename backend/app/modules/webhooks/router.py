from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.depends import get_db
from app.services.polar_service import polar_service
from app.services import license_service
from app.models.subscription import Subscription
from app.models.order import Order
from app.models.plan import Plan
from app.models.webhook import WebhookEvent
from datetime import datetime, timezone
import json

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

@router.post("/polar")
async def polar_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    # StandardWebhooks 검증을 위해 필수 헤더들 추출
    headers = {
        "webhook-id": request.headers.get("webhook-id"),
        "webhook-timestamp": request.headers.get("webhook-timestamp"),
        "webhook-signature": request.headers.get("webhook-signature"),
    }
    
    if not headers["webhook-signature"]:
        raise HTTPException(status_code=401, detail="Missing signature")
    
    payload = await request.body()
    
    try:
        # 1. 서명 검증 및 이벤트 파싱
        event_data = polar_service.validate_webhook(payload, headers)
        event_id = event_data.get("id")
        event_type = event_data.get("type")
        data = event_data.get("data", {})

        # 2. 중복 이벤트 확인 (Idempotency)
        existing_event = db.query(WebhookEvent).filter(WebhookEvent.id == event_id).first()
        if existing_event and existing_event.processed:
            return {"status": "already_processed"}

        # 3. 이벤트 원본 저장
        if not existing_event:
            new_event = WebhookEvent(
                id=event_id,
                event_type=event_type,
                payload=event_data
            )
            db.add(new_event)
            db.commit()
            db.refresh(new_event)
        else:
            new_event = existing_event

        # 4. 이벤트 유형별 처리
        print(f"🔔 Processing Polar Event: {event_type}")
        
        metadata = data.get("metadata", {})
        user_id = metadata.get("user_id")
        project_id = metadata.get("project_id")
        plan_code = metadata.get("plan_code")

        # 구독 관련 이벤트 처리
        if event_type.startswith("subscription."):
            plan = db.query(Plan).filter(Plan.plan_code == plan_code).first()
            
            sub = db.query(Subscription).filter(Subscription.polar_subscription_id == data.get("id")).first()
            if not sub:
                sub = Subscription(
                    polar_subscription_id=data.get("id"),
                    user_id=user_id,
                    project_id=project_id,
                    plan_id=plan.id if plan else None
                )
                db.add(sub)
            
            sub.status = data.get("status")
            sub.polar_price_id = data.get("price_id")
            sub.current_period_start = data.get("current_period_start")
            sub.current_period_end = data.get("current_period_end")
            sub.cancel_at_period_end = data.get("cancel_at_period_end", False)
            
            if event_type == "subscription.revoked":
                sub.revoked_at = datetime.now(timezone.utc)
            
            # 라이선스 발급 (활성화 시)
            if event_type == "subscription.created" or (event_type == "subscription.updated" and data.get("status") == "active"):
                license_service.create_license(
                    db, 
                    user_id=user_id, 
                    project_id=project_id,
                    plan_name=plan.display_name if plan else "Pro"
                )

        # 주문 관련 이벤트 처리
        elif event_type == "order.paid":
            plan = db.query(Plan).filter(Plan.plan_code == plan_code).first()
            
            existing_order = db.query(Order).filter(Order.polar_order_id == data.get("id")).first()
            if not existing_order:
                order = Order(
                    user_id=user_id,
                    project_id=project_id,
                    plan_id=plan.id if plan else None,
                    polar_order_id=data.get("id"),
                    amount=data.get("amount"),
                    currency=data.get("currency"),
                    status="paid",
                    paid_at=datetime.now(timezone.utc)
                )
                db.add(order)
            
            # 평생 라이선스 발급
            if plan_code == "lifetime":
                license_service.create_license(
                    db, 
                    user_id=user_id, 
                    project_id=project_id,
                    plan_name="Lifetime"
                )

        # 5. 처리 완료 마킹
        new_event.processed = True
        new_event.processed_at = datetime.now(timezone.utc)
        db.commit()

        return {"status": "success"}

    except Exception as e:
        db.rollback()
        print(f"❌ Webhook Error: {e}")
        if 'event_id' in locals():
            ev = db.query(WebhookEvent).filter(WebhookEvent.id == event_id).first()
            if ev:
                ev.error_message = str(e)
                db.commit()
        raise HTTPException(status_code=400, detail=f"Webhook processing failed: {str(e)}")
