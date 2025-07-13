#!/usr/bin/python3
"""
Flask-SQLAlchemy models for Customer, Product, Order, and C2B Transaction tables
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

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

