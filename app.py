from os import pathconf_names
from flask import Flask, request, render_template, redirect, url_for, session
from database import engine
from sqlalchemy.sql import text
from database import add_product_to_db
app = Flask(__name__)
app.secret_key = "your_secret_key"


def load_products_from_db():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM products"))
        products = []
        for row in result:
            products.append(row._asdict())
        return products


def load_users_from_db():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM USR"))
        users = []
        for row in result:
            users.append(row._asdict())
        return users


def load_UserD_from_db():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM UserD"))
        users = []
        for row in result:
            users.append(row._asdict())
        return users


def load_ordered_from_db(uid):
    with engine.connect() as conn:
        result = conn.execute(
            text(
                "SELECT * FROM Orders WHERE status='Ordered' AND (fid=:uid OR bid=:uid)"
            ), {"uid": uid})
        ordered = []
        for row in result:
            ordered.append(row._asdict())
        return ordered


def load_accepted_from_db(uid):
    with engine.connect() as conn:
        result = conn.execute(
            text(
                "SELECT * FROM Orders WHERE status='Accepted' AND (fid=:uid OR bid=:uid)"
            ), {"uid": uid})
        accepted = []
        for row in result:
            accepted.append(row._asdict())
        return accepted


def load_delivered_from_db(uid):
    with engine.connect() as conn:
        result = conn.execute(
            text(
                "SELECT * FROM Orders WHERE status='Delivered' AND (fid=:uid OR bid=:uid)"
            ), {"uid": uid})
        delivered = []
        for row in result:
            delivered.append(row._asdict())
        return delivered


@app.route("/")
def login():
    return render_template('login.html')


@app.route("/home")
def home():
    products = load_products_from_db()
    return render_template('home.html', products=products)


@app.route("/SingUp")
def SingUp():
    return render_template('SingUp.html')


@app.route("/log")
def log():
    return render_template('log.html')


@app.route("/add")
def add():
    return render_template('add.html')

@app.route("/Add", methods=["POST"])
def Add():
    data=request.form
    username = session["username"]
    uid = session["uid"]
    add_product_to_db(data,username,uid)
    return redirect(url_for('dashboard'))
@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))

    products = load_products_from_db()
    username = session["username"]
    utype = session["utype"]
    uid = session["uid"]
    users = load_UserD_from_db()

    ordered = len(load_ordered_from_db(uid))
    accepted = len(load_accepted_from_db(uid))
    delivered = len(load_delivered_from_db(uid))

    user = next((u for u in users if u["uname"] == username), None)

    if user:
        if utype == "Farmer":
            return render_template("dashboard.html",
                                   user=user,
                                   products=products,
                                   ordered=ordered,
                                   accepted=accepted,
                                   delivered=delivered)
        elif utype == "Buyer":
            return redirect(url_for("home"))

    return redirect(url_for("login"))


@app.route("/check_user", methods=["POST"])
def check_user():
    username = request.form.get("uid")
    password = request.form.get("pwd")
    users = load_users_from_db()  # This is a list of dictionaries

    # Find the user in the list
    user = next((u for u in users if u["uname"] == username), None)

    if user:
        if user["pwd"] == password:  # Replace with password hash check in production
            session["username"] = username
            session["utype"] = user["utype"]
            session["uid"] = user['uid']
            return redirect(url_for("home"))
        else:
            error = "Incorrect password!"
    else:
        error = "User does not exist!"

    # Re-render the login page with the error message
    return render_template("log.html", error=error)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
