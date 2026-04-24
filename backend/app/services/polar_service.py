from typing import List, Dict, Any, Optional

from polar_sdk import Polar
from standardwebhooks import Webhook, WebhookVerificationError

from app.core.config import settings


class PolarService:
    def __init__(self):
        self.client = Polar(
            access_token=settings.POLAR_API_KEY,
            server="sandbox",
        )
        self.org_id = settings.POLAR_ORGANIZATION_ID

    async def get_products(self) -> List[Any]:
        """
        조직의 상품 목록을 가져옵니다.
        """
        # 동기 호출로 변경 (await 제거)
        result = self.client.products.list(
            organization_id=self.org_id
        )
        return result.items

    async def create_checkout(
        self,
        product_id: str,
        success_url: str,
        customer_email: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        return_url: Optional[str] = None,
    ) -> Any:
        """
        Polar Checkout Session을 생성합니다.
        """
        request: Dict[str, Any] = {
            "products": [product_id],
            "success_url": success_url,
            "metadata": metadata or {},
        }

        if customer_email:
            request["customer_email"] = customer_email

        if return_url:
            request["return_url"] = return_url

        # 동기 호출로 변경 (await 제거)
        return self.client.checkouts.create(request=request)

    def validate_webhook(
        self,
        payload: bytes,
        headers: Dict[str, str],
    ) -> Dict[str, Any]:
        """
        Polar Webhook 서명을 검증합니다.
        """
        try:
            wh = Webhook(settings.POLAR_WEBHOOK_SECRET)
            return wh.verify(payload, headers)
        except WebhookVerificationError:
            raise ValueError("Invalid Polar webhook signature")


polar_service = PolarService()