from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, List
import re
import logging

logger = logging.getLogger(__name__)

class AntiFraudMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        user_agent = request.headers.get("user-agent", "")
        suspicious_agents = ["bot", "crawler", "spider", "scraper"]
        if any(agent in user_agent.lower() for agent in suspicious_agents):
            logger.warning(f"Suspicious user agent: {user_agent}")
        
        response = await call_next(request)
        return response

def validate_order_data(data: Dict) -> List[str]:
    warnings = []
    
    email = data.get("buyer_email", "")
    if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        warnings.append("Email inválido")
    
    name = data.get("buyer_name", "")
    if not name or len(name) < 3:
        warnings.append("Nome muito curto")
    
    phone = data.get("buyer_phone", "")
    if not phone or len(re.sub(r'\D', '', phone)) < 10:
        warnings.append("Telefone inválido")
    
    zip_code = data.get("shipping_zip", "")
    if not zip_code or len(re.sub(r'\D', '', zip_code)) != 8:
        warnings.append("CEP inválido")
    
    return warnings
"Commit new file"
ARQUIVO 16: admin_routes.py
"Add file" → "Create new file"
Nome: admin_routes.py
Cole:
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid
import logging

from auth import get_current_user, get_password_hash

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin")
db = None

def init_admin_routes(database):
    global db
    db = database
    return router

async def seed_admin():
    try:
        existing_admin = await db.users.find_one({"email": "admin@iniciloja.com"})
        if not existing_admin:
            admin_user = {
                "id": str(uuid.uuid4()),
                "name": "Admin",
                "email": "admin@iniciloja.com",
                "password": get_password_hash("Admin123!"),
                "role": "admin",
                "shop_id": None,
                "created_at": datetime.utcnow()
            }
            await db.users.insert_one(admin_user)
            logger.info("Admin user created")
    except Exception as e:
        logger.error(f"Error seeding admin: {e}")

class BanUserRequest(BaseModel):
    user_id: str
    reason: Optional[str] = None

@router.post("/users/ban")
async def ban_user(req: BanUserRequest, email: str = Depends(get_current_user)):
    admin = await db.users.find_one({"email": email})
    if not admin or admin.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    await db.users.update_one(
        {"id": req.user_id},
        {"$set": {"banned": True, "ban_reason": req.reason}}
    )
    return {"message": "User banned"}

@router.get("/users")
async def list_users(email: str = Depends(get_current_user)):
    admin = await db.users.find_one({"email": email})
    if not admin or admin.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    users = await db.users.find({}).to_list(1000)
    for user in users:
        user.pop("password", None)
        user.pop("_id", None)
    
    return users

@router.get("/stats")
async def get_platform_stats(email: str = Depends(get_current_user)):
    admin = await db.users.find_one({"email": email})
    if not admin or admin.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    total_users = await db.users.count_documents({})
    total_shops = await db.shops.count_documents({})
    total_products = await db.products.count_documents({})
    total_orders = await db.orders.count_documents({})
    
    return {
        "total_users": total_users,
        "total_shops": total_shops,
        "total_products": total_products,
        "total_orders": total_orders
    }
