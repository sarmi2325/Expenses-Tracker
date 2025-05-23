from app import db
from flask_login import UserMixin

class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(100),unique=True,nullable=False)
    email=db.Column(db.String(100),unique=True,nullable=False)
    password=db.Column(db.String(100),nullable=False)
    expenses=db.relationship('Expense',backref='user',lazy=True)
    
class Expense(db.Model):
    id =db.Column(db.Integer,primary_key=True)
    date=db.Column(db.Date,nullable=False)
    amount=db.Column(db.Float,nullable=False)
    category=db.Column(db.String(100),nullable=False)
    description=db.Column(db.String(300),nullable=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
