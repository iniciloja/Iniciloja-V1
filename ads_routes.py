from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import uuid
import logging

from auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ads")
db = None

def init_ads_routes(database):
    global db
    db = database
    return router

class AdCreate(BaseModel):
    product_id: str
    title: str
    description: str
    duration_days: int = 7
    budget: float

@router.post("/create")
async def create_ad(ad_data: AdCreate, email: str = Depends(get_current_user)):
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    subscription = user.get("subscription", {})
    plan_id = subscription.get("plan_id")
    if plan_id not in ["premium", "ai_pro"]:
        raise HTTPException(status_code=403, detail="Premium plan required")
    
    product = await db.products.find_one({"id": ad_data.product_id})
    if not product or product.get("shop_id") != user.get("shop_id"):
        raise HTTPException(status_code=404, detail="Product not found")
    
    ad_dict = {
        "id": str(uuid.uuid4()),
        "shop_id": user.get("shop_id"),
        "product_id": ad_data.product_id,
        "title": ad_data.title,
        "description": ad_data.description,
        "budget": float(ad_data.budget),
        "duration_days": ad_data.duration_days,
        "active": True,
        "impressions": 0,
        "clicks": 0,
        "spent": 0.0,
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(days=ad_data.duration_days)
    }
    
    await db.ads.insert_one(ad_dict)
    ad_dict.pop("_id", None)
    return ad_dict

@router.get("/my")
async def get_my_ads(email: str = Depends(get_current_user)):
    user = await db.users.find_one({"email": email})
    if not user or not user.get("shop_id"):
        return []
    
    ads = await db.ads.find({"shop_id": user.get("shop_id")}).to_list(100)
    for ad in ads:
        ad.pop("_id", None)
    
    return ads

@router.get("/marketplace")
async def get_marketplace_ads(limit: int = 20):
    ads = await db.ads.find({
        "active": True,
        "expires_at": {"$gt": datetime.utcnow()}
    }).sort("budget", -1).limit(limit).to_list(limit)
    
    for ad in ads:
        ad.pop("_id", None)
        await db.ads.update_one({"id": ad["id"]}, {"$inc": {"impressions": 1}})
    
    return ads
