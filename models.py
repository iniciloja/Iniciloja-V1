Vou te dar TODOS os arquivos corretos agora. Você vai DELETAR os antigos e CRIAR NOVOS.

📝 PASSO 1: DELETAR TODOS OS .py DO GITHUB
Vá em: https://github.com/iniciloja/Iniciloja-V1
Delete CADA arquivo .py (clique no arquivo → ícone lixeira 🗑️)
Delete: auth.py, models.py, server.py, etc.
MANTENHA: requirements.txt, Procfile, railway.json, etc.
📄 PASSO 2: CRIAR ARQUIVOS NOVOS - SEM ERROS!
Vou postar os arquivos SEM MINHAS INSTRUÇÕES. Copie APENAS entre as linhas de código!

1. Criar models.py
No GitHub: "Add file" → "Create new file" → Nome: models.py

Copie APENAS o código abaixo (entre python e ):

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

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

class Token(BaseModel):
    access_token: str
    token_type: str

class AIRequest(BaseModel):
    prompt: str
    context: Optional[str] = None

# ==================== AI MODELS ====================
class AIRequest(BaseModel):
    prompt: str
    context: Optional[str] = None
