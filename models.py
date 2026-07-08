 
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(100))
    contact = db.Column(db.String(20))
    is_blacklisted = db.Column(db.Boolean, default=False)
class Trek(db.Model):
	__tablename__ = "trek"
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(80), unique=True, nullable=False)
	location= db.Column(db.String(200), nullable=False)	
	difficulty= db.Column(db.String(20), nullable=False)
	duration=db.Column(db.Integer)
	available_slots=db.Column(db.Integer)
	status=db.Column(db.String(20), nullable=False)
	start_date=db.Column(db.String(20))
	end_date=db.Column(db.String(20))
	assigned_staff_id=db.Column(db.Integer, db.ForeignKey("user.id"))
class Booking(db.Model):
	__tablename__="booking"
	id = db.Column(db.Integer, primary_key=True)
	user_id=db.Column(db.Integer, db.ForeignKey("user.id"))
	trek_id=db.Column(db.Integer, db.ForeignKey("trek.id"))
	booking_date=db.Column(db.String(20))
	status=db.Column(db.String(20))







	
	