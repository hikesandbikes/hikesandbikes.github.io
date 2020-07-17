import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///storyboard.db")

@app.route("/")
def index():
    """Landing page for first time users"""
    return render_template("index.html")


@app.route("/stories", methods=["GET", "POST"])
@login_required
def stories():
    """See overview of stories you created"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Retrieve form submission data
        title = request.form.get("title")

        # Apologize if username or password left blank
        if not title:
            return apology("quote cannot be blank", 400)

        # Retrieve form submission data
        story = request.form.get("story")

        # Apologize if username or password left blank
        if not story:
            return apology("quote cannot be blank", 400)


        flash("Published!")

         # Book keeping (TODO: should be wrapped with a transaction)
        db.execute("INSERT INTO portfolio (id, title, story, date) VALUES(:id, :title, :story, datetime('now'))",\
                    id=session["user_id"],
                    title=title,
                    story=story)

        # Render published work
        return render_template("written.html", title=title, story=story)

     # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("stories.html")


@app.route("/overview")
@login_required
def overview():
    """Homepage of the user"""

    entries=[]

    # Get all the transactions from the user
    rows = db.execute("SELECT * FROM portfolio WHERE id = :user_id", user_id=session["user_id"])

    for i in rows:
        value = list(i.values())
        entries.append(value[0])

    if request.method== "POST":
        filename = request.form.get('filename')

        rows = db.execute("DELETE FROM portfolio WHERE id=:id AND title=:title", id=id, title=filename)

        return redirect('/overview')

    else:
        return render_template("overview.html", rows=rows, entries=entries)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to homepage
        return redirect("/overview")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Retrieve form submission data
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure username was submitted
        if not username:
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not password:
            return apology("must provide password", 400)

        # Ensure password-confirmation was submitted
        elif not confirmation:
            return apology("must provide confirmation password", 400)

        # Ensure passwords & password check are the same
        elif not password == confirmation:
            return apology("the passwords must be identical", 400)

        # Ensure username is not already taken
        namecheck = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        if len(namecheck) == 1:
            return apology("username already taken. please choose another", 400)

        # Hash the password
        hash = generate_password_hash(password)

        # Add new user to the database
        rows = db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)", username=request.form.get("username"), hash=hash)

        # Login automatically
        session["user_id"] = rows

        # Direct to overview page
        return redirect("/overview")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/buy", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        return apology("test", 400)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("quote.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
     # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":


        flash("Sold!")

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        stocks = db.execute(
            "SELECT symbol, SUM(shares) as total_shares FROM portfolio WHERE id = :user_id GROUP BY symbol HAVING total_shares > 0", user_id=session["user_id"])

        return render_template("sell.html", stocks=stocks)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
