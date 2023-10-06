
try:
    from fastapi import FastAPI, HTTPException, Depends, status
except:
    from fastapi import FastAPI, HTTPException, Depends, status
    print ('-- Recuerde instalar FastAPI --')
    pass
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from datetime import datetime, timedelta
import models, schemas
from database import SessionLocal, engine
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List

app = FastAPI()

# Iniciar la DB
models.Base.metadata.create_all(bind=engine)

# Obtener la DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    db_user = models.User(username=user.username)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User no encontrado")
    return user
@app.get("/users/", response_model=List[schemas.User]) 
def read_users(skip: int = 0, limit: int = 10000, db: Session = Depends(get_db)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    if users is None:
        raise HTTPException(status_code=404, detail="No hay usuarios disponibles")
    return users
@app.post("/items/", response_model=schemas.Item)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    db_item = models.Item(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/items/", response_model=List[schemas.Item])
def read_items(skip: int = 0, limit: int = 1000000, db: Session = Depends(get_db)):
    items = db.query(models.Item).offset(skip).limit(limit).all()
    return items

@app.get("/items/{id}", response_model=schemas.Item)
def read_item(id: int, db: Session = Depends(get_db)):
    item = db.query(models.Item).get(id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    return item
@app.put("/items/{item_id}", response_model=schemas.Item)
def update_item(item_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    print('testing', item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    for key, value in item.dict().items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

#@app.delete("/items/{item_id}", response_model=schemas.Item)
@app.delete("/items/{item_id}", response_model=schemas.ItemResponse)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    db.delete(db_item)
    db.commit()
    #return db_item
    return {"item": db_item, "message": "Item Borrado exitosamente"}
    
@app.post("/orders/", response_model=schemas.Order)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    db_order = models.Order(**order.dict())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

@app.get("/orders/{order_id}", response_model=schemas.Order)
def read_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.get("/orders", response_model=List[schemas.Order])
def read_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    orders = db.query(models.Order).offset(skip).limit(limit).all()
    return orders

@app.get("/users/{user_id}/items", response_model=List[schemas.Item])
def read_user_items(user_id: int, db: Session = Depends(get_db)):
    items = db.query(models.Item).join(models.Order).join(models.User).filter(models.User.id == user_id).all()
    return items

@app.get("/items/{item_id}/users", response_model=List[schemas.User])
@app.get("/items/{item_name}/users", response_model=List[schemas.User])
def read_item_users(item_name: str, db: Session = Depends(get_db)):
    users = db.query(models.User).\
        join(models.Order, models.User.id == models.Order.user_id).\
        join(models.Item, models.Order.id == models.Item.order_id).\
        filter(models.Item.title == item_name).\
        distinct().all()
    if not users:
        raise HTTPException(status_code=404, detail="No hay usuarios que hayan comprado este artículo.")
    return users    
    # query = text(f"""
    #     SELECT DISTINCT users.* 
    #     FROM users 
    #     INNER JOIN orders ON users.id = orders.user_id 
    #     INNER JOIN items ON orders.id = items.order_id 
    #     WHERE items.title = :item_name AND orders.id IN (
    #         SELECT order_id FROM items WHERE title = :item_name
    #     )
    # """)
    # result = db.execute(query, {"item_name": item_name})
    # users = result.fetchall()
    # if not users:
    #     raise HTTPException(status_code=404, detail="No hay usuarios que hayan comprado este artículo.")
    # return users

@app.get("/orders/{order_id}/items", response_model=List[schemas.Item])
def read_order_items(order_id: int, db: Session = Depends(get_db)):
    items = db.query(models.Item).filter(models.Item.order_id == order_id).all()
    return items