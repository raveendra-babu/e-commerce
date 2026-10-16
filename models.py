from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(255), unique=True)
    password = Column(String(255))


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(150))
    description = Column(Text)
    price = Column(Numeric(10, 2))
    image_url = Column(String(500))
    stock = Column(Integer, default=0)


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)
