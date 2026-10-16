import hashlib

from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import User, Product, CartItem

Base.metadata.create_all(bind=engine)   # tables auto create avthayi

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="change-this-secret-key")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# ---------- helper functions ----------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def get_user(request, db):
    user_id = request.session.get("user_id")
    if user_id:
        return db.query(User).filter(User.id == user_id).first()
    return None


def render(request, db, page, **data):
    user = get_user(request, db)
    cart_count = 0
    if user:
        items = db.query(CartItem).filter(CartItem.user_id == user.id).all()
        cart_count = sum(i.quantity for i in items)
    data["user"] = user
    data["cart_count"] = cart_count
    data["message"] = request.session.pop("message", None)
    return templates.TemplateResponse(request, page, data)


def go(url):
    return RedirectResponse(url, status_code=303)


# ---------- pages ----------
@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    products = db.query(Product).order_by(Product.id.desc()).limit(4).all()
    return render(request, db, "home.html", products=products)


@app.get("/products", response_class=HTMLResponse)
def products_page(request: Request, db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return render(request, db, "products.html", products=products)


# ---------- register / login / logout ----------
@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request, db: Session = Depends(get_db)):
    return render(request, db, "register.html")


@app.post("/register", response_class=HTMLResponse)
def register(request: Request, name: str = Form(...), email: str = Form(...),
             password: str = Form(...), db: Session = Depends(get_db)):
    email = email.strip().lower()
    if db.query(User).filter(User.email == email).first():
        return render(request, db, "register.html", error="This email is already registered")

    user = User(name=name, email=email, password=hash_password(password))
    db.add(user)
    db.commit()
    request.session["user_id"] = user.id
    request.session["message"] = "Account created. Welcome!"
    return go("/")


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request, db: Session = Depends(get_db)):
    return render(request, db, "login.html")


@app.post("/login", response_class=HTMLResponse)
def login(request: Request, email: str = Form(...), password: str = Form(...),
          db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email.strip().lower()).first()
    if not user or user.password != hash_password(password):
        return render(request, db, "login.html", error="Wrong email or password")

    request.session["user_id"] = user.id
    request.session["message"] = "Logged in"
    return go("/")


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return go("/")


# ---------- cart ----------
@app.post("/cart/add/{product_id}")
def add_to_cart(request: Request, product_id: int, db: Session = Depends(get_db)):
    user = get_user(request, db)
    if not user:
        request.session["message"] = "Please login first"
        return go("/login")

    product = db.query(Product).filter(Product.id == product_id).first()
    item = db.query(CartItem).filter(CartItem.user_id == user.id,
                                     CartItem.product_id == product_id).first()
    back = request.headers.get("referer", "/products")

    if not product:
        return go("/products")

    in_cart = item.quantity if item else 0
    if in_cart + 1 > product.stock:
        request.session["message"] = "Not enough stock"
        return go(back)

    if item:
        item.quantity += 1
    else:
        db.add(CartItem(user_id=user.id, product_id=product_id, quantity=1))
    db.commit()
    request.session["message"] = product.name + " added to cart"
    return go(back)


@app.get("/cart", response_class=HTMLResponse)
def cart(request: Request, db: Session = Depends(get_db)):
    user = get_user(request, db)
    if not user:
        return go("/login")

    rows = (db.query(CartItem, Product)
              .join(Product, CartItem.product_id == Product.id)
              .filter(CartItem.user_id == user.id)
              .all())
    total = sum(product.price * item.quantity for item, product in rows)
    return render(request, db, "cart.html", rows=rows, total=total)


@app.post("/cart/remove/{item_id}")
def remove_from_cart(request: Request, item_id: int, db: Session = Depends(get_db)):
    user = get_user(request, db)
    if not user:
        return go("/login")

    item = db.query(CartItem).filter(CartItem.id == item_id,
                                     CartItem.user_id == user.id).first()
    if item:
        db.delete(item)
        db.commit()
    return go("/cart")
