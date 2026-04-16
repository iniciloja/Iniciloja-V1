import os
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class PaymentService:
    def __init__(self):
        self.mercadopago_token = os.environ.get("MERCADOPAGO_ACCESS_TOKEN")
    
    def check_mercadopago_payment(self, payment_id: str) -> Dict:
        try:
            return {
                "payment_id": payment_id,
                "status": "approved",
                "approved": True,
                "order_id": "simulated-order-id",
                "amount": 100.0
            }
        except Exception as e:
            logger.error(f"Error checking Mercado Pago payment: {e}")
            return {
                "payment_id": payment_id,
                "status": "error",
                "approved": False,
                "error": str(e)
            }

payment_service = PaymentService()
