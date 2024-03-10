from flask import Flask, render_template, redirect, request, session
from flask import current_app as app
from .models import *


# import datetime


@app.route('/')
def main():
    if session.get("name"):
        if (session["name"] == "Admin"):
            return redirect("/admin")
        else:
            return redirect("/user")

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
                session["name"] = this_user.user_name
                if (this_user.user_type == "admin"):
                    return redirect("/admin")
                else:
                    return redirect("/user")
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

# =======================Admin Dashboard Code Start========================


@app.route('/admin')
def Admin():
    if session.get("name") != "Admin":
        return redirect("/logout")
    return render_template("admin/admin_dashboard.html")


@app.route('/book_management')
def Book_Management():
    if session.get("name") != "Admin":
        return redirect("/logout")
    return render_template("admin/book_management.html")


@app.route('/add-book', methods=["POST"])
def Add_Book():
    if session.get("name") != "Admin":
        return redirect("/logout")

    return redirect("/book_management")


@app.route('/section_management')
def Section_Management():
    if session.get("name") != "Admin":
        return redirect("/logout")
    return render_template("admin/section_management.html")


@app.route('/add-section', methods=["POST"])
def Add_Section():
    if session.get("name") != "Admin":
        return redirect("/logout")

    return redirect("/book_section")


@app.route('/requests')
def Requests():
    if session.get("name") != "Admin":
        return redirect("/logout")
    return render_template("admin/requests.html")


@app.route('/statistics')
def Statistics():
    if session.get("name") != "Admin":
        return redirect("/logout")
    return render_template("admin/stats.html")

# =======================Admin Dashboard Code End========================


@app.route("/logout")
def Logout():
    session.clear()
    return redirect("/")


@app.route("/user")
def User_Dashboard():
    if not session.get("name"):
        return redirect("/logout")
    return render_template("user_dashboard.html")
