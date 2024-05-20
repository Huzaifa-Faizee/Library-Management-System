from flask import Flask, render_template, redirect, request, session
from flask import current_app as app
from .models import *
import datetime
from datetime import timedelta
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")  # tkAgg


@app.route('/')
def main():
    if session.get("name"):
        if (session["name"] == "Admin"):
            return redirect("/admin")
        else:
            return redirect("/user")
    top_books = Book_Issues.query.with_entities(Book_Issues.book_id, func.count(Book_Issues.book_id).label('issue_count')) \
        .group_by(Book_Issues.book_id) \
        .order_by(func.count(Book_Issues.book_id).desc()) \
        .limit(4) \
        .all()
    bestseller = []
    print(top_books)
    for book in top_books:
        book_data = Books.query.filter_by(book_id=book.book_id).first()
        bestseller.append(book_data)
    print(bestseller)

    new_added = Books.query.order_by(Books.book_id.desc()).limit(4).all()
    sections = Section.query.limit(2).all()
    return render_template("index.html", bestseller=bestseller, new_added=new_added, sections=sections)


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
                    session["user_id"] = this_user.user_id
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


@app.route("/logout")
def Logout():
    session.clear()
    return redirect("/")


# =======================Admin Dashboard Code Start========================


@app.route('/admin')
def Admin():
    if session.get("name") != "Admin":
        return redirect("/logout")
    users = User.query.count() - 1
    books = Books.query.count()
    sections = Section.query.count()
    pending_requests = Book_Issues.query.filter_by(status="pending").count()
    return render_template("admin/admin_dashboard.html", users=users, sections=sections, books=books, pending_requests=pending_requests)


@app.route('/book-management')
def Book_Management():
    if session.get("name") != "Admin":
        return redirect("/logout")
    sections = Section.query.all()
    books = Books.query.all()
    return render_template("admin/book_management.html", sections=sections, books=books)


@app.route("/edit-book/<int:book_id>", methods=["GET", "POST"])
def Edit_Book(book_id):
    if session.get("name") != "Admin":
        return redirect("/logout")
    book = Books.query.filter_by(book_id=book_id).first()
    if request.method == "GET":
        sections = Section.query.all()
        return render_template("/admin/edit_book.html", book=book, sections=sections)
    elif request.method == "POST":
        # return "POST METHOD"
        book.name = request.form.get("b_name")
        book.author = request.form.get("author")
        book.issue_time = request.form.get("issue_period")
        book.genre = request.form.get("genre")
        # book.section_id = request.form.get("section")
        book.content = request.form.get("content")
        db.session.add(book)
        db.session.commit()
        return redirect("/book-management")
    else:
        return "INCORRECT REQUEST!"


@app.route("/delete-book/<int:book_id>")
def Delete_Book(book_id):
    if session.get("name") != "Admin":
        return redirect("/logout")
    book = Books.query.filter_by(book_id=book_id).first()
    book_issues = Book_Issues.query.filter_by(book_id=book_id).first()
    db.session.delete(book)
    if book_issues:
        db.session.delete(book_issues)
    db.session.commit()
    return redirect("/book-management")


@app.route("/change-book-status/<int:book_id>/<int:status>")
def Change_Book_Status(book_id, status):
    if session.get("name") != "Admin":
        return redirect("/logout")

    book = Books.query.filter_by(book_id=book_id).first()
    book.status = status
    db.session.add(book)
    db.session.commit()
    return redirect("/book-management")


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
        fileName = None
        image = request.files['image']
        imageName = None
        if file:
            fileName = file.filename
            file.save("static/uploads/"+fileName)
        if image:
            imageName = image.filename
            image.save("static/uploads/"+imageName)
        this_book = Books.query.filter_by(name=b_name).first()
        if this_book:
            return "Book Already Exists!"
        else:
            new_book = Books(name=b_name, author=author, issue_time=issue_time,
                             genre=genre, section_id=section, content=content, pdf=fileName, image=imageName)
            db.session.add(new_book)
            db.session.commit()

    return redirect("/book-management")


@app.route('/section-management')
def Section_Management():
    if session.get("name") != "Admin":
        return redirect("/logout")
    sections = Section.query.all()
    today_date = datetime.date.today()
    return render_template("admin/section_management.html", sections=sections, today_date=today_date)


@app.route('/add-section', methods=["POST"])
def Add_Section():
    if session.get("name") != "Admin":
        return redirect("/logout")
    if request.method == "POST":
        s_name = request.form.get("s_name")
        s_desc = request.form.get("s_desc")
        created_date = datetime.date.today()
        image = request.files['image']
        imageName = None
        if image:
            imageName = image.filename
            image.save("static/uploads/"+imageName)
        this_section = Section.query.filter_by(name=s_name).first()
        if this_section:
            return "Section Already Exists!"
        else:
            new_section = Section(
                name=s_name, description=s_desc, created_date=created_date, image=imageName)
            db.session.add(new_section)
            db.session.commit()
        print(s_name, s_desc, created_date)

        return redirect("/section-management")


@app.route("/edit-section/<int:section_id>", methods=["GET", "POST"])
def Edit_Section(section_id):
    if session.get("name") != "Admin":
        return redirect("/logout")
    section = Section.query.filter_by(section_id=section_id).first()
    if request.method == "GET":
        return render_template("/admin/edit_section.html", section=section)
    elif request.method == "POST":
        section.name = request.form.get("s_name")
        section.description = request.form.get("desc")
        db.session.add(section)
        db.session.commit()
        return redirect("/section-management")
    else:
        return "INCORRECT REQUEST!"


@app.route("/delete-section/<int:section_id>")
def Delete_Section(section_id):
    if session.get("name") != "Admin":
        return redirect("/logout")
    section = Section.query.filter_by(section_id=section_id).first()
    db.session.delete(section)
    db.session.commit()
    return redirect("/section-management")


@app.route('/requests')
def Requests():
    if session.get("name") != "Admin":
        return redirect("/logout")
    today = datetime.date.today()
    completed_request_count = 0
    pending_requests = Book_Issues.query.filter_by(status="pending").all()

    all_accepted_requests = Book_Issues.query.filter_by(
        status="accepted").all()
    completed_requests = Book_Issues.query.filter_by(
        status="completed").all()
    revoked_requests = Book_Issues.query.filter_by(
        status="revoked").all()
    rejected_requests = Book_Issues.query.filter_by(
        status="rejected").all()
    accepted_requests = []
    for request in all_accepted_requests:
        if request.end_date < today:
            completed_request_count += 1
            request.status = "completed"
            db.session.add(request)
        else:
            accepted_requests.append(request)
    if completed_request_count > 0:
        db.session.commit()
    print(pending_requests, accepted_requests)
    return render_template("admin/requests.html", pending_requests=pending_requests, accepted_requests=accepted_requests, completed_requests=completed_requests, revoked_requests=revoked_requests, rejected_requests=rejected_requests)


@app.route('/edit-issue-status/<int:issue_id>/<status>')
def Edit_Issue_Status(issue_id, status):
    if session.get("name") != "Admin":
        return redirect("/logout")
    book_request = Book_Issues.query.filter_by(issue_id=issue_id).first()
    if (status == "accepted"):
        days = book_request.book.issue_time
        book_request.issue_date = datetime.date.today()
        book_request.end_date = datetime.date.today()+timedelta(days=days)
    book_request.status = status
    db.session.add(book_request)
    db.session.commit()
    return redirect("/requests")


@app.route('/statistics')
def Statistics():
    if session.get("name") != "Admin":
        return redirect("/logout")
    read_book_issues = Book_Issues.query.filter_by(status="completed").all()
    ongoing_book_issues = Book_Issues.query.filter_by(status="accepted").all()
    read_sections = []
    read_total_issues = []
    ongoing_books = []
    for issue in read_book_issues:
        read_total_issues.append(issue.book.name)
        read_sections.append(issue.book.section.name)
    for issue in ongoing_book_issues:
        ongoing_books.append(issue.book.name)
    print(read_sections)
    plt.clf()
    plt.hist(read_total_issues)
    plt.savefig("static/images/book_read_count.png")
    plt.clf()
    plt.hist(read_sections)
    plt.savefig("static/images/section_read_count.png")
    # plt.clf()
    # plt.figure(figsize=(2,6))
    # plt.hist(ongoing_books)
    # plt.savefig("static/images/ongoing_read_count.png")
    return render_template("admin/stats.html")


@app.route("/admin-search")
def admin_search():
    if session.get("name") != "Admin":
        return redirect("/logout")
    search_word = request.args.get("srch_val")
    search_val = "%"+search_word+"%"
    book_name = Books.query.filter(Books.name.like(search_val)).all()
    book_author = Books.query.filter(Books.author.like(search_val)).all()
    book_genre = Books.query.filter(Books.genre.like(search_val)).all()
    section_name = Section.query.filter(Section.name.like(search_val)).all()
    return render_template("admin/admin_search.html", book_name=book_name, book_author=book_author, book_genre=book_genre, section_name=section_name)
# =======================Admin Dashboard Code End========================

# =======================User Dashboard Code Start========================


@app.route("/user")
def User_Dashboard():
    if not session.get("name"):
        return redirect("/logout")
    top_books = Book_Issues.query.with_entities(Book_Issues.book_id, func.count(Book_Issues.book_id).label('issue_count')) \
        .group_by(Book_Issues.book_id) \
        .order_by(func.count(Book_Issues.book_id).desc()) \
        .limit(4) \
        .all()
    bestseller = []
    print(top_books)
    for book in top_books:
        book_data = Books.query.filter_by(book_id=book.book_id).first()
        bestseller.append(book_data)
    print(bestseller)

    new_added = Books.query.order_by(Books.book_id.desc()).limit(4).all()
    sections = Section.query.limit(2).all()
    return render_template("user/user_dashboard.html", trending=bestseller, new_added=new_added, sections=sections)


@app.route("/all-books")
def All_Books():
    if not session.get("name"):
        return redirect("/logout")

    books = Books.query.all()
    return render_template("user/all_books.html", books=books)


@app.route("/all-sections")
def All_Sections():
    if not session.get("name"):
        return redirect("/logout")
    sections = Section.query.all()
    return render_template("user/all_sections.html", sections=sections)


@app.route("/section-books/<int:section_id>")
def Section_Books(section_id):
    if not session.get("name"):
        return redirect("/logout")
    books = Books.query.filter_by(section_id=section_id).all()
    sect = Section.query.filter_by(section_id=section_id).first()
    return render_template("user/section_books.html", books=books, sect=sect)


@app.route("/my-books")
def My_Books():
    if not session.get("name"):
        return redirect("/logout")
    user_id = session.get("user_id")

    all_reading = Book_Issues.query.filter_by(
        user_id=user_id, status="accepted").all()
    reading = []
    today = datetime.date.today()
    count = 0
    for request in all_reading:
        if request.end_date < today:
            count += 1
            request.status = "completed"
            db.session.add(request)
        else:
            reading.append(request)
    if count > 0:
        db.session.commit()

    read = Book_Issues.query.filter_by(
        user_id=user_id, status="completed").all()
    requested = Book_Issues.query.filter_by(
        user_id=user_id, status="pending").all()

    return render_template("user/my_books.html", reading=reading, read=read, requested=requested)


@app.route("/view-book/<int:book_id>")
def View_Book(book_id):
    if not session.get("name"):
        return redirect("/logout")
    user_id = session.get("user_id")
    book = Books.query.filter_by(book_id=book_id).first()
    book_issue = Book_Issues.query.filter_by(
        book_id=book_id, user_id=user_id).first()
    issued_book_count = Book_Issues.query.filter_by(
        user_id=user_id, status="accepted").count()
    reviews = Reviews.query.filter_by(user_id=user_id, book_id=book_id).all()
    print(issued_book_count)
    if not book_issue:
        book_issue = None
    elif book_issue.status == "accepted":
        today = datetime.date.today()
        if book_issue.end_date < today:
            book_issue.status = "completed"
            db.session.add(book_issue)
            db.session.commit()
    return render_template("user/view_book.html", book=book, book_issue=book_issue, issued_book_count=issued_book_count, reviews=reviews)


@app.route("/review/<int:book_id>", methods=["POST"])
def Review(book_id):
    if not session.get("name"):
        return redirect("/logout")
    content = request.form.get("content")
    user_id = session["user_id"]
    date = datetime.date.today()
    review = Reviews(user_id=user_id, book_id=book_id,
                     date=date, content=content)
    db.session.add(review)
    db.session.commit()
    return redirect("/view-book/"+str(book_id))


@app.route("/issue-book/<int:book_id>/<status>")
def Issue_Book(book_id, status):
    if not session.get("name"):
        return redirect("/logout")
    user_id = session.get("user_id")
    if status == "pending":
        issue_date = datetime.date.today()
        end_date = datetime.date.today()
        new_issue = Book_Issues(issue_date=issue_date, end_date=end_date,
                                status=status, user_id=user_id, book_id=book_id)
        db.session.add(new_issue)
        db.session.commit()
        return redirect("/view-book/"+str(book_id))


@app.route("/reissue-book/<int:book_id>/<status>")
def Re_Issue_Book(book_id, status):
    if not session.get("name"):
        return redirect("/logout")
    user_id = session.get("user_id")
    request = Book_Issues.query.filter_by(
        user_id=user_id, book_id=book_id).first()
    request.issue_date = datetime.date.today()
    request.end_date = datetime.date.today()
    request.status = status
    db.session.add(request)
    db.session.commit()
    return redirect("/view-book/"+str(book_id))


@app.route("/read/<int:book_id>")
def Read(book_id):
    if not session.get("name"):
        return redirect("/logout")
    user_id = session.get("user_id")
    book = Books.query.filter_by(book_id=book_id).first()
    print(book)
    check = Book_Issues.query.filter_by(
        user_id=user_id, book_id=book_id).first()
    status = 0
    if check.status == "accepted":
        status = 1

    return render_template("user/read_book.html", book=check.book, status=status)


@app.route("/user-stats")
def User_Stats():
    if not session.get("name"):
        return redirect("/logout")
    user_id = session["user_id"]
    books_issued = Book_Issues.query.filter_by(
        user_id=user_id, status="completed").all()
    books_read = len(books_issued)
    currently_reading = Book_Issues.query.filter_by(
        user_id=user_id, status="accepted").count()
    requested = Book_Issues.query.filter_by(
        user_id=user_id, status="requested").count()
    genre_count = {}
    for issue in books_issued:
        gen = issue.book.genre
        if gen not in genre_count:
            genre_count[gen] = 1
        else:
            genre_count[gen] += 1
    genres = []
    counts = []
    for key in genre_count:
        genres.append(key)
        counts.append(genre_count[key])
    plt.clf()
    plt.pie(counts, labels=genres)
    plt.savefig("static/images/genre_count.png")
    return render_template("user/user_stats.html", books_read=books_read, currently_reading=currently_reading, requested=requested)


@app.route("/user-search")
def user_search():
    if not session.get("name"):
        return redirect("/logout")
    search_word = request.args.get("srch_val")
    search_val = "%"+search_word+"%"
    book_name = Books.query.filter(Books.name.like(search_val)).all()
    book_author = Books.query.filter(Books.author.like(search_val)).all()
    book_genre = Books.query.filter(Books.genre.like(search_val)).all()
    section_name = Section.query.filter(Section.name.like(search_val)).all()
    return render_template("user/user_search.html", book_name=book_name, book_author=book_author, book_genre=book_genre, section_name=section_name)

# =======================User Dashboard Code End========================
