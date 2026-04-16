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
Commit!

2. Criar auth.py
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.environ.get("JWT_SECRET", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60

security = HTTPBearer()

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    token = credentials.credentials
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        return email
    except JWTError:
        raise credentials_exception
