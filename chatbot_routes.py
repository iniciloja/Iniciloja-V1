from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import os
import uuid
from openai import OpenAI

from auth import get_current_user

router = APIRouter(prefix="/api/ai")
db = None

def init_chatbot_routes(database):
    global db
    db = database
    return router

class ChatbotRequest(BaseModel):
    message: str
    shop_id: str
    session_id: Optional[str] = None

@router.post("/chatbot")
async def chatbot_response(req: ChatbotRequest):
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("EMERGENT_LLM_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="AI key not configured")
    
    client = OpenAI(api_key=api_key)
    
    shop = await db.shops.find_one({"id": req.shop_id})
    shop_name = shop.get("name", "Loja") if shop else "Loja"
    
    products = await db.products.find({"shop_id": req.shop_id}).to_list(50)
    products_text = ""
    for p in products:
        products_text += f"- {p['name']}: R$ {p['price']:.2f}\n"
    
    session_id = req.session_id or str(uuid.uuid4())
    
    system_msg = f"""Você é o assistente da loja "{shop_name}".
Responda perguntas sobre os produtos de forma amigável.

Produtos disponíveis:
{products_text if products_text else 'Nenhum produto cadastrado.'}"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": req.message}
            ]
        )
        bot_response = response.choices[0].message.content.strip()
        
        msg_data = {
            "id": str(uuid.uuid4()),
            "shop_id": req.shop_id,
            "session_id": session_id,
            "user_message": req.message,
            "bot_response": bot_response,
            "created_at": datetime.utcnow()
        }
        await db.chatbot_messages.insert_one(msg_data)
        
        return {"response": bot_response, "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
