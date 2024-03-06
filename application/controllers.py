from flask import Flask, render_template, redirect, request
from flask import current_app as app
from .models import *
# import datetime


@app.route('/')
def main():
    return render_template("index.html")


@app.route('/signIn', methods=["GET", "POST"])
def signIn():
    if request.method == "GET":
        return render_template("signin.html")
    elif request.method == "POST":
        u_email = request.form.get("u_email")
        pwd = request.form.get("pwd")
        this_user = User.query.filter_by(user_email=u_email).first()
        if this_user:
            if this_user.password == pwd:
                if(this_user.user_type=="admin"):
                    return render_template("admin/admin_dashboard.html")
                else:
                    return render_template("user_dashboard.html")
            else:
                return "Wrong Password"


@app.route('/signUp', methods=["GET", "POST"])
def signUp():
    if request.method == "GET":
        return render_template("signup.html")
    elif request.method == "POST":
        # return "You just signed Up"
        u_name = request.form.get("u_name")
        u_email = request.form.get("u_email")
        pwd = request.form.get("pwd")
        this_user = User.query.filter_by(user_email=u_email).first()
        if this_user:
            return "User already exists!"
        else:
            new_user = User(user_name=u_name, user_email=u_email, password=pwd)
            db.session.add(new_user)
            db.session.commit()
            return render_template("signin.html")
