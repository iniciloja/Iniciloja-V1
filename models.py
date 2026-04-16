from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# ==================== USER MODELS ====================
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class User(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: str
    shop_id: Optional[str] = None
    created_at: datetime


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ==================== SHOP MODELS ====================
class ShopCreate(BaseModel):
    name: str
    description: Optional[str] = None


class Shop(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    owner_id: str
    total_sales: float = 0
    violations: int = 0
    created_at: datetime
    days_active: int = 0


class ShopSettings(BaseModel):
    pickup_enabled: Optional[bool] = False
    pickup_address: Optional[str] = None
    pickup_city: Optional[str] = None
    pickup_state: Optional[str] = None
    pickup_zip: Optional[str] = None
    pix_key: Optional[str] = None


# ==================== PRODUCT MODELS ====================
class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    category: str
    image: Optional[str] = None
    product_type: Optional[str] = "physical"
    delivery_type: Optional[str] = "shipping"
    delivery_time: Optional[str] = None


class Product(BaseModel):
    id: str
    shop_id: str
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    category: str
    image: Optional[str] = None
    product_type: str = "physical"
    delivery_type: str = "shipping"
    delivery_time: Optional[str] = None
    is_used: bool = False
    created_at: datetime


# ==================== ORDER MODELS ====================
class OrderItem(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    price: float


class OrderCreate(BaseModel):
    shop_id: str
    buyer_name: str
    buyer_email: EmailStr
    buyer_phone: str
    shipping_zip: str
    shipping_address: str
    items: List[OrderItem]
    total_amount: float


class Order(BaseModel):
    id: str
    shop_id: str
    buyer_name: str
    buyer_email: EmailStr
    buyer_phone: str
    shipping_zip: str
    shipping_address: str
    items: List[OrderItem]
    total_amount: float
    status: str = "pending"
    fraud_score: int = 0
    created_at: datetime


# ==================== AUTH MODELS ====================
class Token(BaseModel):
    access_token: str
    token_type: str


# ==================== AI MODELS ====================
class AIRequest(BaseModel):
    prompt: str
    context: Optional[str] = None
