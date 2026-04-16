import os
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY") or os.getenv("EMERGENT_LLM_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
        
    async def _generate_text(self, system_message: str, prompt: str) -> str:
        if not self.client:
            raise Exception("OpenAI client not configured")
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()

    async def generate_product_description(self, product_name: str, category: str = None) -> str:
        try:
            system_message = "Você é um especialista em e-commerce brasileiro. Crie descrições profissionais e atrativas de produtos."
            context = f"Categoria: {category}" if category else ""
            prompt = f"Crie uma descrição profissional para o produto '{product_name}'. {context}"
            
            return await self._generate_text(system_message, prompt)
        except Exception as e:
            logger.error(f"Error generating description: {e}")
            return f"{product_name} de alta qualidade."
    
    async def suggest_price(self, product_name: str, category: str) -> float:
        try:
            system_message = "Você é um especialista em precificação de produtos no mercado brasileiro."
            prompt = f"Sugira um preço em reais para '{product_name}' da categoria '{category}'. Responda APENAS com o número."
            
            response = await self._generate_text(system_message, prompt)
            price_str = response.strip().replace("R$", "").replace(",", ".").strip()
            price = float(price_str)
            return round(price, 2)
        except Exception as e:
            logger.error(f"Error suggesting price: {e}")
            defaults = {
                "Eletrônicos": 199.90,
                "Moda": 89.90,
                "Casa": 79.90,
                "Beleza": 49.90
            }
            return defaults.get(category, 99.90)

ai_service = AIService()
