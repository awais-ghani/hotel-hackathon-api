import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Import graph 
import matplotlib.pyplot as plt
import numpy as np

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
    return render_template("index.html", percent=conversion_rate_viewToPurchase_percent)





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

"Working on the data:"

import csv 
cwd = os.getcwd()


#allowing python to read the files I need
e_commerce_purchases = open(cwd + '\hackathon-data\e-commerce-purchases.csv')
e_commerce_purchases_csv = csv.reader(e_commerce_purchases)
engagement_events = open(cwd + '\hackathon-data\engagement-events.csv')
engagement_events_csv = csv.reader(engagement_events)
engagement_overview = open(cwd + '\hackathon-data\engagement-overview.csv')
engagement_overview_csv = csv.reader(engagement_overview)

#create the spreadsheet data for each file as an array of the rows
engagement_events_data=[] 
for row in engagement_events_csv:
    engagement_events_data.append(row)
engagement_overview_data=[] 
for row in engagement_overview_csv:
    engagement_overview_data.append(row)
e_commerce_purchases_data=[] 
for row in e_commerce_purchases_csv:
    e_commerce_purchases_data.append(row)

"finding number of engaged users, returns a decimal (which is essentially a %)"
def total_engaged_users():
    #finding total users visiting website in 1yr
    total_users = engagement_events_data[405][2]
    avg_user_engagement = 0
    for week_number in range(34):  
        #finding avg. engaged session per user (ie. user engagement)
        user_engagement = float(engagement_overview_data[47+week_number][1])
        avg_user_engagement += user_engagement/33

    #so number of actual engaged users is these 2 multiplied
    return float(total_users)*float(avg_user_engagement)


"finding room conversion rates ie. numnber of people who add 1 of the 5 rooms to the cart AND purchase it. Returns an array containing 5 decimal values"
def room_conversion_rates():
    room_conversion_rate = []

    for room_type in range(5):
        room_addedtocart = e_commerce_purchases_data[25+room_type][2]
        room_purchased = e_commerce_purchases_data[25+room_type][3]
        #divide no. purchased by no. added to cart to see how many are actually purchased per room added to cart
        room_conversion_rate.append( float(room_purchased)/float(room_addedtocart))

    return room_conversion_rate

engagement_conversions = open(cwd + '/hackathon-data/engagement-conversions.csv')
engagement_conversions_csv = csv.reader(engagement_conversions)

#conversion RATE ie. conversions per user for engagement events
engagement_conversions_data=[] 
for row in engagement_conversions_csv:
    engagement_conversions_data.append(row)

conversion_count, user_count, conversion_rate = [], [], []
for type in range(4):
    conversion_count.append(float(engagement_conversions_data[391 + type][1]))
    user_count.append(float(engagement_conversions_data[391 + type][2]))
    value = conversion_count[type] / user_count[type]
    conversion_rate.append(value)


demographics_overview = open(cwd + '/hackathon-data/demographics-overview.csv')
demographics_overview_csv = csv.reader(demographics_overview)



demographics_overview_rows=[]
for row in demographics_overview_csv:
    demographics_overview_rows.append(row)
        
# Calculate the rate of conversion between page view and purchase
page_views_quantity = float(engagement_events_data[246][1])
purchase_quantity = float(engagement_events_data[260][1])
conversion_rate_viewToPurchase_percent = (purchase_quantity / page_views_quantity) * 100

# Calculate the users per language 
languages = demographics_overview_rows[701:]

language = []
speakers = []
for row in languages:
    language.append(row[0])
    speakers.append(float(row[1]))

# Add up non English and spanish users
nonEnglish = speakers.copy()

nonEnglish.pop(0)

nonEnglish.pop(0)

nonEnglishSpeakers = np.sum(nonEnglish)

languageCondensed = ['English', 'Spanish', 'Other 13 Languages']
speakersCondensed = [speakers[0], speakers[1], nonEnglishSpeakers]


fig = plt.figure()
ax = fig.add_axes([0,0,1,1])
ax.bar(languageCondensed,speakersCondensed, color=['green', 'yellow', 'red'])
plt.xlabel("Number of Users")
plt.ylabel("Language Spoken")
plt.savefig("./static/languages.png", bbox_inches='tight')

plt.close()

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
