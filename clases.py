from sqlalchemy.orm import backref
from enum import unique
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost:3306/pytiendaEquipo'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'MisterFantasy'

db=SQLAlchemy(app)

# Clase User
class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    roles = db.Column(db.String(50), nullable=False)

    purchases = db.relationship('Purchase', back_populates='user')

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.roles = 'user'

    # Getters
    def get_id(self):
        return self.id

    def get_username(self):
        return self.username

    def get_password(self):
        return self.password

    def get_roles(self):
        return self.roles

    # Setters
    def set_password(self, password):
        self.password = password

    def set_roles(self, roles):
        self.roles = roles


# Clase Product
class Product(db.Model):
    __tablename__ = 'product'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    img = db.Column(db.String(255), nullable=False)

    purchase_lines = db.relationship('PurchaseLine', back_populates='product')

    def __init__(self, name, price, stock, img):
        self.name = name
        self.price = price
        self.stock = stock
        self.img = img

    # Getters
    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_price(self):
        return self.price

    def get_stock(self):
        return self.stock

    def get_img(self):
        return self.img

    # Setters
    def set_name(self, name):
        self.name = name

    def set_price(self, price):
        self.price = price

    def set_stock(self, stock):
        self.stock = stock

    def set_img(self, img):
        self.img = img

    

# Clase Purchase
class Purchase(db.Model):
    __tablename__ = 'purchase'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='OPEN')
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship('User', back_populates='purchases')
    lines = db.relationship(
        'PurchaseLine',
        back_populates='purchase',
        cascade='all, delete-orphan'
    )

    def __init__(self, user_id, status='OPEN'):
        self.user_id = user_id
        self.status = status

    # Getters
    def get_id(self):
        return self.id

    def get_user_id(self):
        return self.user_id

    def get_status(self):
        return self.status

    def get_created_at(self):
        return self.created_at

    # Setters
    def set_user_id(self, user_id):
        self.user_id = user_id

    def set_status(self, status):
        self.status = status


# Clase PurchaseLine
class PurchaseLine(db.Model):
    __tablename__ = 'purchase_line'

    id = db.Column(db.Integer, primary_key=True)
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchase.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unidad = db.Column(db.Float, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('purchase_id', 'product_id', name='unique_product_per_purchase'),
    )

    purchase = db.relationship('Purchase', back_populates='lines')
    product = db.relationship('Product', back_populates='purchase_lines')

    def __init__(self, purchase_id, product_id, cantidad, precio_unidad):
        self.purchase_id = purchase_id
        self.product_id = product_id
        self.cantidad = cantidad
        self.precio_unidad = precio_unidad

    # Getters
    def get_id(self):
        return self.id

    def get_purchase_id(self):
        return self.purchase_id

    def get_product_id(self):
        return self.product_id

    def get_cantidad(self):
        return self.cantidad

    def get_precio_unidad(self):
        return self.precio_unidad

    # Setters
    def set_purchase_id(self, purchase_id):
        self.purchase_id = purchase_id

    def set_product_id(self, product_id):
        self.product_id = product_id

    def set_cantidad(self, cantidad):
        self.cantidad = cantidad

    def set_precio_unidad(self, precio_unidad):
        self.precio_unidad = precio_unidad
