import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

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
db = SQL("sqlite:///finance.db")




@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    rows=db.execute("""
        SELECT symbol, SUM(shares) as totalshares
        FROM transactions
        WHERE user_id = :user_id
        GROUP BY symbol
        HAVING totalshares;
        """, user_id = session["user_id"] )
    holdings = []
    grand_total= 0
    for row in rows:
        stock = lookup(row["symbol"])
        holdings.append({
            "symbol": stock["symbol"],
            "name": stock["name"],
            "shares": row["totalshares"],
            "price": usd(stock["price"]),
            "total": usd(stock["price"]*row["totalshares"])
        })
        grand_total += stock["price"]*row["totalshares"]
    rows = db.execute("SELECT cash FROM users WHERE id=:user_id", user_id=session["user_id"])
    cash = rows[0]["cash"]
    grand_total += cash
    return render_template("index.html",holdings=holdings,cash=usd(cash),grand_total = usd(grand_total))





@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")




@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        elif not request.form.get("confirmation"):
            return apology("must provide confirmation", 400)


        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        if int(len(rows) > 0):
            return apology("username taken", 400)
           # flash("username taken")
            return render_template("register.html", )

        else:
            username = request.form.get("username")
            password = request.form.get("password")
            confirmation = request.form.get("confirmation")
            hash = generate_password_hash(password)

            if not check_password_hash(hash, confirmation):
                return apology("must provide same password", 400)

            db.execute("INSERT INTO users(username,hash)VALUES(?,?)", username,hash)

        flash("Registerd")
        return render_template("index.html")


    return render_template("register.html")


import csv 
cwd = os.getcwd()

engagement_conversions = open(cwd + '\hackathon-data\engagement-conversions.csv')
engagement_conversions_csv = csv.reader(engagement_conversions)

engagement_events = open(cwd + '\hackathon-data\engagement-events.csv')
engagement_events_csv = csv.reader(engagement_events)


rows=[]
for row in engagement_conversions_csv:
    rows.append(row)



def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
