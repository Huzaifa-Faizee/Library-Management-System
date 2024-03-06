from .database import db


class User(db.Model):
    user_id = db.Column(db.Integer(), primary_key=True)
    user_name = db.Column(db.String(), nullable=False)
    user_email = db.Column(db.String(), nullable=False, unique=True)
    password = db.Column(db.String(), nullable=False, unique=True)
    user_type = db.Column(db.String(), nullable=False, default="user")
