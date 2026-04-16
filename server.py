🚨 ACHEI O ERRO! VOCÊ COPIOU MINHAS INSTRUÇÕES NO CÓDIGO!
O erro diz:

File "/app/server.py", line 3
  "Add file" → "Create new file"
SyntaxError: invalid character '→'
O PROBLEMA: Você copiou o texto "Add file" → "Create new file" (minhas instruções) dentro do arquivo server.py!

✅ SOLUÇÃO RÁPIDA:
1. DELETAR o server.py do GitHub
Vá em: https://github.com/iniciloja/Iniciloja-V1
Clique no arquivo server.py
Clique no ícone da lixeira (🗑️) no canto direito
Commit delete
2. CRIAR server.py CORRETO
Agora vou te dar o código LIMPO SEM INSTRUÇÕES:

No GitHub, clique "Add file" → "Create new file"
Nome: server.py
Cole EXATAMENTE isto (SEM copiar nada a mais):
from fastapi import FastAPI, APIRouter, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
import os
import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional, List
import stripe

from models import (
    UserCreate, User, ShopCreate, Shop, ProductCreate, Product,
    OrderCreate, Order, Token, AIRequest, ShopSettings, LoginRequest
)
from auth import (
    get_password_hash, verify_password, create_access_token, get_current_user
)
from ai_service import ai_service
from shipping_service import shipping_service
from payment_service import payment_service
from email_service import email_service
from admin_routes import init_admin_routes, seed_admin
from subscription_routes import init_subscription_routes
from chatbot_routes import init_chatbot_routes
from ads_routes import init_ads_routes
from pix_qrcode import generate_pix_qrcode
from antifraud import AntiFraudMiddleware, validate_order_data
from commission_routes import init_commission_routes, get_seller_level, calculate_dynamic_commission

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI()
api_router = APIRouter(prefix="/api")

admin_router = init_admin_routes(db)
subscription_router = init_subscription_routes(db)
chatbot_router = init_chatbot_routes(db)
ads_router = init_ads_routes(db)
commission_router = init_commission_routes(db)
app.include_router(admin_router)
app.include_router(subscription_router)
app.include_router(chatbot_router)
app.include_router(ads_router)
app.include_router(commission_router)

app.add_middleware(AntiFraudMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@api_router.post("/auth/register", response_model=dict)
async def register(user_data: UserCreate):
    existing = await db.users.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_dict = {
        "id": str(uuid.uuid4()),
        "name": user_data.name,
        "email": user_data.email,
        "password": get_password_hash(user_data.password),
        "role": "seller",
        "shop_id": None,
        "created_at": datetime.utcnow()
    }
    
    await db.users.insert_one(user_dict)
    access_token = create_access_token(data={"sub": user_data.email})
    
    user_dict.pop("password")
    user_dict.pop("_id", None)
    return {"user": user_dict, "access_token": access_token, "token_type": "bearer"}

@api_router.post("/auth/login", response_model=dict)
async def login(login_data: LoginRequest):
    user = await db.users.find_one({"email": login_data.email})
    if not user or not verify_password(login_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if user.get("banned"):
        raise HTTPException(status_code=403, detail="Conta banida")
    
    access_token = create_access_token(data={"sub": login_data.email})
    
    shop = None
    if user.get("shop_id"):
        shop = await db.shops.find_one({"id": user["shop_id"]})
        if shop:
            shop.pop("_id", None)
    
    user.pop("password")
    user.pop("_id", None)
    user["shop"] = shop
    user["role"] = user.get("role", "seller")
    
    return {"user": user, "access_token": access_token, "token_type": "bearer"}

@api_router.get("/auth/me")
async def get_me(email: str = Depends(get_current_user)):
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    shop = None
    if user.get("shop_id"):
        shop = await db.shops.find_one({"id": user["shop_id"]})
        if shop:
            shop.pop("_id", None)
    
    user.pop("password")
    user.pop("_id", None)
    user["shop"] = shop
    return {"user": user}

@api_router.post("/shops", response_model=Shop)
async def create_shop(shop_data: ShopCreate, email: str = Depends(get_current_user)):
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.get("shop_id"):
        raise HTTPException(status_code=400, detail="User already has a shop")
    
    shop_dict = {
        "id": str(uuid.uuid4()),
        "name": shop_data.name,
        "description": shop_data.description,
        "owner_id": user["id"],
        "total_sales": 0,
        "violations": 0,
        "created_at": datetime.utcnow(),
        "days_active": 0
    }
    
    await db.shops.insert_one(shop_dict)
    await db.users.update_one({"id": user["id"]}, {"$set": {"shop_id": shop_dict["id"]}})
    return shop_dict

@api_router.get("/shops/{shop_id}", response_model=Shop)
async def get_shop(shop_id: str):
    shop = await db.shops.find_one({"id": shop_id})
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    shop.pop("_id", None)
    return shop

@api_router.put("/shops/{shop_id}/settings")
async def update_shop_settings(shop_id: str, settings: ShopSettings, email: str = Depends(get_current_user)):
    user = await db.users.find_one({"email": email})
    shop = await db.shops.find_one({"id": shop_id})
    
    if not shop or shop["owner_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    await db.shops.update_one({"id": shop_id}, {"$set": {"settings": settings.dict()}})
    return {"message": "Settings updated successfully"}

@api_router.post("/products", response_model=Product)
async def create_product(product_data: ProductCreate, email: str = Depends(get_current_user)):
    user = await db.users.find_one({"email": email})
    if not user or not user.get("shop_id"):
        raise HTTPException(status_code=400, detail="User has no shop")
    
    image_url = product_data.image or "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400"
    
    product_dict = {
        "id": str(uuid.uuid4()),
        "shop_id": user["shop_id"],
        "name": product_data.name,
        "description": product_data.description or "",
        "price": float(product_data.price),
        "stock": int(product_data.stock),
        "category": product_data.category,
        "image": image_url,
        "product_type": product_data.product_type or "physical",
        "delivery_type": product_data.delivery_type,
        "delivery_time": product_data.delivery_time,
        "is_used": False,
        "created_at": datetime.utcnow()
    }
    
    await db.products.insert_one(product_dict)
    product_dict.pop("_id", None)
    return product_dict

@api_router.get("/products")
async def get_products(shop_id: str = None, email: str = Depends(get_current_user)):
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    query = {"shop_id": shop_id or user.get("shop_id")}
    products = await db.products.find(query).to_list(1000)
    
    for product in products:
        product.pop("_id", None)
    
    return products

@api_router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    product = await db.products.find_one({"id": product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@api_router.put("/products/{product_id}", response_model=Product)
async def update_product(product_id: str, product_data: ProductCreate, email: str = Depends(get_current_user)):
    user = await db.users.find_one({"email": email})
    product = await db.products.find_one({"id": product_id})
    
    if not product or product["shop_id"] != user.get("shop_id"):
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = {
        "name": product_data.name,
        "description": product_data.description,
        "price": product_data.price,
        "stock": product_data.stock,
        "category": product_data.category,
        "image": product_data.image,
        "product_type": product_data.product_type or "physical",
        "delivery_type": product_data.delivery_type,
        "delivery_time": product_data.delivery_time
    }
    
    await db.products.update_one({"id": product_id}, {"$set": update_data})
    updated = await db.products.find_one({"id": product_id})
    return updated

@api_router.delete("/products/{product_id}")
async def delete_product(product_id: str, email: str = Depends(get_current_user)):
    user = await db.users.find_one({"email": email})
    product = await db.products.find_one({"id": product_id})
    
    if not product or product["shop_id"] != user.get("shop_id"):
        raise HTTPException(status_code=404, detail="Product not found")
    
    await db.products.delete_one({"id": product_id})
    return {"message": "Product deleted"}

@api_router.post("/orders", response_model=Order)
async def create_order(order_data: OrderCreate):
    warnings = validate_order_data({
        "buyer_email": order_data.buyer_email,
        "buyer_name": order_data.buyer_name,
        "buyer_phone": order_data.buyer_phone,
        "shipping_zip": order_data.shipping_zip
    })
    
    order_dict = {
        "id": str(uuid.uuid4()),
        "shop_id": order_data.shop_id,
        "buyer_name": order_data.buyer_name,
        "buyer_email": order_data.buyer_email,
        "buyer_phone": order_data.buyer_phone,
        "shipping_zip": order_data.shipping_zip,
        "shipping_address": order_data.shipping_address,
        "items": order_data.items,
        "total_amount": float(order_data.total_amount),
        "status": "pending",
        "fraud_score": len(warnings),
        "created_at": datetime.utcnow()
    }
    
    await db.orders.insert_one(order_dict)
    order_dict.pop("_id", None)
    return order_dict

@api_router.get("/orders")
async def get_orders(shop_id: str = None, email: str = Depends(get_current_user)):
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    query = {"shop_id": shop_id or user.get("shop_id")}
    orders = await db.orders.find(query).to_list(1000)
    
    for order in orders:
        order.pop("_id", None)
    
    return orders

@api_router.get("/")
async def root():
    return {"message": "Iniciloja API is running"}

app.include_router(api_router)

@app.on_event("startup")
async def startup_event():
    await seed_admin()
    logger.info("Application started successfully")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
