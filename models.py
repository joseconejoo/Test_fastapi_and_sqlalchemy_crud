from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    active = Column(Boolean, default=True)
    price = Column(Float)
    order_id = Column(Integer, ForeignKey('orders.id'))
    
    order = relationship("Order", back_populates="items")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship("User", back_populates="orders")
    items = relationship("Item", order_by=Item.id, back_populates="order")

User.orders = relationship("Order", order_by=Order.id, back_populates="user")