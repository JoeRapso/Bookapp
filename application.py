import os, requests

from flask import Flask, session, render_template, request, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Homepage
@app.route("/")
def index():
    return render_template("index.html")

# Register new user
@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/register_success", methods=["POST"])
def register_success():

    username = request.form.get("username")
    password = request.form.get("password")

    login = db.execute("SELECT username, password FROM users WHERE username = :username AND password = :password", {"username": username, "password": password}).fetchone()    
    if login is None:
        db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
                {"username": username, "password": password})
        db.commit()
        return render_template("register_success.html")    
    return render_template("error.html", message="This Username & Password already exists, please type in new ones")

@app.route("/login")
def login():
    return render_template("login.html")

# Needs work
@app.route("/logout")   
def logout():
    session.clear()
    return redirect("/")

@app.route("/my_account", methods=["POST"])
def my_account():

    username = request.form.get("username")
    password = request.form.get("password")

    login = db.execute("SELECT username, password FROM users WHERE username = :username AND password = :password", {"username": username, "password": password}).fetchone()    
    if login is None:
        return render_template("error.html", message="The Username or Password is incorrect. Please enter the right one.")
    return render_template("my_account.html")


@app.route("/books", methods=["POST", "GET"])
def books():
    
    query = request.form.get("query")
    query = query.title()
    
    bookSearch = db.execute("SELECT id, title, author, isbn, year FROM books WHERE (title LIKE :query) OR (author LIKE :query) OR  (isbn LIKE :query) OR (year LIKE :query)", {"query": "%" + query + "%"}).fetchall()
    if bookSearch is None:
        return render_template("error.html", message="No matches")
    return render_template("books.html", bookSearch=bookSearch)

@app.route("/books/<int:book_id>")
def book(book_id):


    book = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
    if book is None:
        return render_template("error.html", message="No such book.")

    ## Goodreads api no longer active. Find other book api platform

    # res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "qYowhj7mrc7CpAPljeHQ", "isbns": book.isbn})
    # data = res.json()
    # rating = data['books'][0]['average_rating']
    # reviewCount = data['books'][0]['work_ratings_count']
    # print(rating, reviewCount)
    
    ##
    return render_template("book.html", book=book) #, rating=rating, reviewCount=reviewCount)


@app.route("/review", methods=["POST"])
def review():

    username = request.form.get("username")
    isbn = request.form.get("isbn")
    rating = request.form.get("rating")
    review = request.form.get("review")


    db.execute("INSERT INTO reviews (username, isbn, rating, review) VALUES (:username, :isbn, :rating, :review)",
            {"username": username, "isbn": isbn, "rating": rating, "review": review})
    db.commit()
    return render_template("review.html")















