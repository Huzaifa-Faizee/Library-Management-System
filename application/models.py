from .database import *


class User(db.Model):
    user_id = db.Column(db.Integer(), primary_key=True)
    user_name = db.Column(db.String(), nullable=False)
    user_email = db.Column(db.String(), nullable=False, unique=True)
    password = db.Column(db.String(), nullable=False, unique=True)
    user_type = db.Column(db.String(), nullable=False, default="user")
    book_issues = relationship("Book_Issues", backref="issued_by_user")


class Books(db.Model):
    book_id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), nullable=False, unique=True)
    author = db.Column(db.String(), nullable=False)
    issue_time = db.Column(db.Integer(), nullable=False)
    genre = db.Column(db.String())
    pdf = db.Column(db.String())
    content = db.Column(db.String())
    section_id = db.Column(db.Integer(), ForeignKey('section.section_id'))
    status = db.Column(db.Integer(), nullable=False, default=1)
    section = relationship("Section", backref="books")


class Book_Issues(db.Model):
    issue_id = db.Column(db.Integer(), primary_key=True)
    issue_date = db.Column(db.Date(), nullable=False)
    end_date = db.Column(db.Date(), nullable=False)
    status = db.Column(db.String(), nullable=False, default="pending")
    user_id = db.Column(db.Integer(), ForeignKey('user.user_id'))
    book_id = db.Column(db.Integer(), ForeignKey('books.book_id'))
    user = relationship("User", backref="user_book_issues")
    book = relationship("Books", backref="book_book_issues")


class Section(db.Model):
    section_id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), nullable=False, unique=True)
    created_date = db.Column(db.Date())
    description = db.Column(db.String())
