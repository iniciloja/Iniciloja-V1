from fastapi import APIRouter, HTTPException, Depends
from typing import Dict
import logging

from auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/commission")
db = None

def init_commission_routes(database):
    global db
    db = database
    return router

def get_seller_level(total_sales: float, days_active: int, violations: int) -> str:
    if violations >= 3:
        return "bronze"
    
    if total_sales >= 50000 and days_active >= 180:
        return "diamond"
    elif total_sales >= 20000 and days_active >= 90:
        return "gold"
    elif total_sales >= 5000 and days_active >= 30:
        return "silver"
    else:
        return "bronze"

def calculate_dynamic_commission(sale_amount: float, seller_level: str) -> float:
    rates = {
        "diamond": 0.03,
        "gold": 0.05,
        "silver": 0.08,
        "bronze": 0.12
    }
    rate = rates.get(seller_level, 0.12)
    commission = sale_amount * rate
    return round(commission, 2)

@router.get("/my-level")
async def get_my_seller_level(email: str = Depends(get_current_user)):
    user = await db.users.find_one({"email": email})
    if not user or not user.get("shop_id"):
        raise HTTPException(status_code=400, detail="No shop found")
    
    shop = await db.shops.find_one({"id": user.get("shop_id")})
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    
    total_sales = shop.get("total_sales", 0)
    days_active = shop.get("days_active", 0)
    violations = shop.get("violations", 0)
    
    level = get_seller_level(total_sales, days_active, violations)
    
    return {
        "current_level": level,
        "total_sales": total_sales,
        "days_active": days_active,
        "violations": violations,
        "commission_rate": f"{calculate_dynamic_commission(100, level)}%"
    }

@router.get("/levels-info")
async def get_levels_info():
    return {
        "levels": [
            {"name": "Bronze", "commission_rate": "12%", "requirements": "Iniciante"},
            {"name": "Silver", "commission_rate": "8%", "requirements": "R$ 5.000 + 30 dias"},
            {"name": "Gold", "commission_rate": "5%", "requirements": "R$ 20.000 + 90 dias"},
            {"name": "Diamond", "commission_rate": "3%", "requirements": "R$ 50.000 + 180 dias"}
        ]
    }
