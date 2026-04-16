import os
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class ShippingService:
    def __init__(self):
        self.melhor_envio_token = os.environ.get("MELHOR_ENVIO_TOKEN")
        self.correios_user = os.environ.get("CORREIOS_USER")
    
    def calculate_all_shipping_options(
        self,
        cep_origem: str,
        cep_destino: str,
        peso: float,
        altura: float,
        largura: float,
        comprimento: float,
        pickup_enabled: bool = False,
        pickup_address: Optional[str] = None
    ) -> List[Dict]:
        options = []
        
        if pickup_enabled:
            options.append({
                "provider": "pickup",
                "name": "Retirar na Loja",
                "price": 0.0,
                "delivery_time": "Imediato",
                "address": pickup_address or "Loja física"
            })
        
        try:
            pac_price = self._calculate_correios_free(peso, cep_origem, cep_destino, "PAC")
            options.append({
                "provider": "correios",
                "name": "PAC - Correios",
                "price": pac_price,
                "delivery_time": "10-15 dias úteis"
            })
        except Exception as e:
            logger.error(f"Error calculating PAC: {e}")
        
        try:
            sedex_price = self._calculate_correios_free(peso, cep_origem, cep_destino, "SEDEX")
            options.append({
                "provider": "correios",
                "name": "SEDEX - Correios",
                "price": sedex_price,
                "delivery_time": "3-5 dias úteis"
            })
        except Exception as e:
            logger.error(f"Error calculating SEDEX: {e}")
        
        return options
    
    def _calculate_correios_free(self, peso: float, cep_origem: str, cep_destino: str, tipo: str) -> float:
        base_price = 15.0 if tipo == "PAC" else 25.0
        weight_factor = peso * 2.5
        
        try:
            origem_prefix = int(cep_origem[:2])
            destino_prefix = int(cep_destino[:2])
            distance_factor = abs(origem_prefix - destino_prefix) * 0.5
        except:
            distance_factor = 5.0
        
        total = base_price + weight_factor + distance_factor
        return round(total, 2)
    
    def track_package(self, tracking_code: str, provider: str = "correios") -> Dict:
        return {
            "tracking_code": tracking_code,
            "provider": provider,
            "status": "em_transito",
            "events": [
                {"date": "2025-04-15", "status": "Postado", "location": "São Paulo - SP"},
                {"date": "2025-04-16", "status": "Em trânsito", "location": "Centro de Distribuição"}
            ]
        }

shipping_service = ShippingService()
