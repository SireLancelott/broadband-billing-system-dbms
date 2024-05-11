# models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class UserLogin(db.Model):
    __tablename__ = 'user_login'
    user_id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(255), nullable=False)

class CustDetails(db.Model):
    __tablename__ = 'cust_details'
    customer_id = db.Column(db.Integer, primary_key=True)
    mobile_number = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    customer_type = db.Column(db.String(50))
    customer_id_proof = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user_login.user_id'))

class Subscription(db.Model):
    __tablename__ = 'subscription'
    subscription_id = db.Column(db.Integer, primary_key=True)
    subscription_cost = db.Column(db.Float, nullable=False)
    subscription_details = db.Column(db.String(255))
    subscription_speed = db.Column(db.String(50))

class Bills(db.Model):
    __tablename__ = 'bills'
    bill_number = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('cust_details.customer_id'))
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscription.subscription_id'))
    month = db.Column(db.String(10), nullable=False)
    cost = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False)

class TransactionDetails(db.Model):
    __tablename__ = 'transaction_details'
    transaction_id = db.Column(db.Integer, primary_key=True)
    bill_number = db.Column(db.Integer, db.ForeignKey('bills.bill_number'))
    date_of_issue = db.Column(db.DateTime, nullable=False)
    paid_amount = db.Column(db.Float, nullable=False)
    pay_method = db.Column(db.String(50), nullable=False)
