from flask import Flask, render_template, redirect, request, session
from flask import current_app as app
from .models import *
import datetime


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


@app.route('/book-management')
def Book_Management():
    if session.get("name") != "Admin":
        return redirect("/logout")
    sections = Section.query.all()
    return render_template("admin/book_management.html", sections=sections)


@app.route('/add-book', methods=["POST"])
def Add_Book():
    if session.get("name") != "Admin":
        return redirect("/logout")
    if request.method == "POST":
        b_name = request.form.get("b_name")
        author = request.form.get("author")
        issue_time = request.form.get("issue_period")
        genre = request.form.get("genre")
        section = request.form.get("section")
        content = request.form.get("content")
        file = request.files['pdf']

        if file:
            filename = file.filename
            file.save("uploads/"+filename)
        this_book = Books.query.filter_by(name=b_name).first()
        if this_book:
            return "Book Already Exists!"
        else:
            new_book = Books(name=b_name, author=author, issue_time=issue_time,
                             genre=genre, section_id=section, content=content, pdf=filename)
            db.session.add(new_book)
            db.session.commit()

    return redirect("/book-management")


@app.route('/section-management')
def Section_Management():
    if session.get("name") != "Admin":
        return redirect("/logout")

    today_date = datetime.date.today()
    return render_template("admin/section_management.html", today_date=today_date)


@app.route('/add-section', methods=["POST"])
def Add_Section():
    if session.get("name") != "Admin":
        return redirect("/logout")
    if request.method == "POST":
        s_name = request.form.get("s_name")
        s_desc = request.form.get("s_desc")
        created_date = datetime.date.today()
        this_section = Section.query.filter_by(name=s_name).first()
        if this_section:
            return "Section Already Exists!"
        else:
            new_section = Section(
                name=s_name, description=s_desc, created_date=created_date)
            db.session.add(new_section)
            db.session.commit()
        print(s_name, s_desc, created_date)

        return redirect("/section-management")


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
