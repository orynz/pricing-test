from sqlalchemy.orm import Session
from app.core.depends import SessionLocal
from app.models.plan import Plan
import uuid

def seed_plans():
    db = SessionLocal()
    print("🌱 Seeding Plans with real Polar IDs...")
    
    plans = [
        {
            "plan_code": "free",
            "display_name": "Free",
            "billing_type": "none",
            "polar_product_id": "cc5e1df0-0c3c-4b0a-8a2f-d8e2a5aa9859",
            "price_amount": 0,
            "entitlement_level": "free",
            "max_devices": 0,
            "max_daily_requests": 3,
            "offline_access_days": 0
        },
        {
            "plan_code": "pro_monthly",
            "display_name": "Pro Monthly",
            "billing_type": "subscription",
            "polar_product_id": "d073ebd5-a3a9-4632-baeb-0f2de7512bb0",
            "price_amount": 1900,
            "interval": "month",
            "entitlement_level": "pro",
            "max_devices": 2,
            "max_daily_requests": 500,
            "offline_access_days": 7
        },
        {
            "plan_code": "pro_yearly",
            "display_name": "Pro Yearly",
            "billing_type": "subscription",
            "polar_product_id": "2ec40ef6-b652-463a-99ba-987dcc844a42",
            "price_amount": 19000,
            "interval": "year",
            "entitlement_level": "pro",
            "max_devices": 3,
            "max_daily_requests": 500,
            "offline_access_days": 14
        },
        {
            "plan_code": "lifetime",
            "display_name": "Lifetime",
            "billing_type": "one_time",
            "polar_product_id": "1b740621-65ef-4151-b74d-6b9a2c00429c",
            "price_amount": 19900,
            "entitlement_level": "lifetime",
            "max_devices": 3,
            "max_daily_requests": 1000,
            "offline_access_days": 30
        }
    ]

    for p_data in plans:
        existing = db.query(Plan).filter(Plan.plan_code == p_data["plan_code"]).first()
        if not existing:
            new_plan = Plan(**p_data)
            db.add(new_plan)
            print(f"✅ Added plan: {p_data['plan_code']}")
        else:
            # 업데이트
            for key, value in p_data.items():
                setattr(existing, key, value)
            print(f"🔄 Updated plan: {p_data['plan_code']}")
            
    db.commit()
    db.close()
    print("✨ Seeding completed.")

if __name__ == "__main__":
    seed_plans()
