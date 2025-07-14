#!/usr/bin/python3
"""
Flask app with:
- Sign up / Sign in (with Google OAuth and password)
- Order form with image upload
- Dynamic product & order display
- Contact info
- MariaDB backend
"""

import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_dance.contrib.google import make_google_blueprint, google
from werkzeug.utils import secure_filename
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URI")
app.config['UPLOAD_FOLDER'] = os.environ.get("UPLOAD_FOLDER", 'static/images')
db = SQLAlchemy(app)

# Google OAuth config
google_bp = make_google_blueprint(
    client_id=os.environ.get("GOOGLE_CLIENT_ID"),
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
    redirect_to='dashboard',
    scope=["profile", "email"]
)
app.register_blueprint(google_bp, url_prefix="/login")

# Models
class Customer(db.Model):
    """
    Customer table model
    """
    __tablename__ = 'customers'

    customer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email_address = db.Column(db.String(100), nullable=False, unique=True)

    orders = db.relationship('Order', backref='customer', cascade='all, delete', lazy=True)
    transactions = db.relationship('Transaction', backref='customer', cascade='all, delete', lazy=True)


class Product(db.Model):
    """
    Product table model
    """
    __tablename__ = 'products'

    product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    orders = db.relationship('Order', backref='product', cascade='all, delete', lazy=True)


class Order(db.Model):
    """
    Order table model
    """
    __tablename__ = 'orders'

    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id', ondelete='CASCADE'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Pending')

    transaction = db.relationship('Transaction', backref='order', cascade='all, delete', uselist=False)


class Transaction(db.Model):
    """
    Safaricom C2B Transaction table model
    """
    __tablename__ = 'transactions'

    transaction_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id', ondelete='CASCADE'), nullable=False)
    mpesa_code = db.Column(db.String(50), nullable=False, unique=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    order = db.relationship('Order', backref='transactions')

# Routes
@app.route('/')
def index():

    products = Product.query.all()
    return render_template('customer.html', orders=orders, products=products)

@app.route('/auth', methods=['GET', 'POST'])
def auth():
    return render_template('auth.html')

@app.route('/signup', methods=['POST'])
def signup():
    name = request.form['name']
    email = request.form['email_address']
    password = request.form['password']
    if User.query.filter_by(email=email).first():
        return "User already exists"
    user = User(name=name, email=email, password=password)
    db.session.add(user)
    db.session.commit()
    return redirect('/auth')

@app.route('/signin', methods=['POST'])
def signin():
    email = request.form['email_address']
    password = request.form['password']
    user = User.query.filter_by(email=email, password=password).first()
    if user:
        session['user_id'] = user.id
        return redirect('/dashboard')
    return "Invalid login"
@login required 
@app.route('/add_order', methods=['POST'])
def add_order():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/auth')

    product_id = request.form['product_id']
    status = request.form['status']
    image = request.files.get('image')

    filename = None
    if image:
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    new_order = Order(product_id=product_id, user_id=user_id, status=status, image_filename=filename)
    db.session.add(new_order)
    db.session.commit()
    return redirect('/dashboard')
@login required 
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

