from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    # Relacionamento para múltiplos endereços
    addresses = db.relationship('Address', backref='user', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    promo_price = db.Column(db.Float, nullable=True) # Preço promocional
    description = db.Column(db.Text)
    image = db.Column(db.String(200))
    category = db.Column(db.String(50))
    # Grade de Estoque
    stock_p = db.Column(db.Integer, default=0)
    stock_m = db.Column(db.Integer, default=0)
    stock_g = db.Column(db.Integer, default=0)
    stock_gg = db.Column(db.Integer, default=0)

class Coupon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    discount_percent = db.Column(db.Integer, nullable=False)
    min_purchase = db.Column(db.Float, default=0.0) # NOVO: Valor mínimo para ativar
    active = db.Column(db.Boolean, default=True)

class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cep = db.Column(db.String(9), nullable=False)
    rua = db.Column(db.String(200), nullable=False)
    numero = db.Column(db.String(20), nullable=False)
    bairro = db.Column(db.String(100), nullable=False)
    cidade = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(2), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)    

