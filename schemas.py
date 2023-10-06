from pydantic import BaseModel
from typing import List, Optional


class TokenData(BaseModel):
    username: Optional[str] = None

class ItemBase(BaseModel):
    title: str
    description: str
    price: float
    order_id: int
class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    active: bool

    class Config:
        from_attributes = True

class ItemList(BaseModel):
    items: List[Item]

class ItemResponse(BaseModel):
    item: Item
    message: str

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int

    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    user_id: int

class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    id: int
    items: List[Item] = []