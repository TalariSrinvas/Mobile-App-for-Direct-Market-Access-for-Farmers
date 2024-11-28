from os import pathconf_names
from flask import Flask, request, render_template, redirect, url_for, session
from database import engine
from sqlalchemy.sql import text
from database import add_product_to_db, add_orders_to_db, accept_order

app = Flask(__name__)
app.secret_key = "your_secret_key"


def load_products_from_db():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM products"))
        products = []
        for row in result:
            products.append(row._asdict())
        return products


def load_fproducts_from_db(uid):
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM products WHERE fid=:uid"),
                              {"uid": uid})
        products = []
        for row in result:
            products.append(row._asdict())
        return products


def load_bproducts_from_db(uid):
    with engine.connect() as conn:
        result = conn.execute(
            text(
                "SELECT Products.url as img,Products.pname as name,Orders.quantity as qt,Orders.price as pri FROM Orders,Products WHERE Orders.fid=Products.fid AND Orders.pid=Products.pid AND Orders.status='Ordered' AND Orders.bid=:uid"
            ), {"uid": uid})
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


def load_full_order_details(uid):
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT 
                    Orders.oid,
                    Orders.quantity,
                    Orders.price,
                    Orders.status,
                    Products.pname,
                    Products.url,
                    Products.pid,
                    Users.uname AS buyer_name,
                    Users.mobilno AS mobilno,
                    Users.email AS email,
                    Users.nationality as nationality,
                    Users.stat as stat,
                    Users.dist as dist,
                    Users.town as town,
                    Users.hno as hno
                FROM 
                    Orders
                JOIN 
                    Products ON Orders.pid = Products.pid
                JOIN 
                    UserD AS Users ON Orders.bid = Users.uid
                WHERE Orders.fid= :uid AND Orders.status= 'Ordered'
                """), {"uid": uid})
        orders = []
        for row in result:
            orders.append(row._asdict())
        return orders


def load_full_accepted_details(uid):
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT 
                    Orders.oid,
                    Orders.quantity,
                    Orders.price,
                    Orders.status,
                    Products.pname,
                    Products.url,
                    Products.pid,
                    Users.uname AS buyer_name,
                    Users.mobilno AS mobilno,
                    Users.email AS email,
                    Users.nationality as nationality,
                    Users.stat as stat,
                    Users.dist as dist,
                    Users.town as town,
                    Users.hno as hno
                FROM 
                    Orders
                JOIN 
                    Products ON Orders.pid = Products.pid
                JOIN 
                    UserD AS Users ON Orders.bid = Users.uid
                WHERE Orders.fid= :uid AND Orders.status= 'Accepted'
                """), {"uid": uid})
        orders = []
        for row in result:
            orders.append(row._asdict())
        return orders


def load_full_delivered_details(uid):
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT 
                    Orders.oid,
                    Orders.quantity,
                    Orders.price,
                    Orders.status,
                    Products.pname,
                    Products.url,
                    Products.pid,
                    Users.uname AS buyer_name,
                    Users.mobilno AS mobilno,
                    Users.email AS email,
                    Users.nationality as nationality,
                    Users.stat as stat,
                    Users.dist as dist,
                    Users.town as town,
                    Users.hno as hno
                FROM 
                    Orders
                JOIN 
                    Products ON Orders.pid = Products.pid
                JOIN 
                    UserD AS Users ON Orders.bid = Users.uid
                WHERE Orders.fid= :uid AND Orders.status= 'Delivered'
                """), {"uid": uid})
        orders = []
        for row in result:
            orders.append(row._asdict())
        return orders


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
def home():
    logged_in = "username" in session
    return render_template('home.html', logged_in=logged_in)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/login")
def login():
    return render_template('login.html')


@app.route("/about")
def about():
    logged_in = "username" in session
    return render_template('about.html', logged_in=logged_in)


@app.route("/SingUp")
def SingUp():
    return render_template('SingUp.html')


@app.route("/log")
def log():
    return render_template('log.html')


@app.route("/service")
def service():
    return render_template('service.html')


@app.route("/view")
def view():
    uid = session.get('uid')
    temp = request.args.get('temp')

    if temp == "1":
        orders = load_full_order_details(uid)
        logged_in = "username" in session
        return render_template('view.html',
                               orders=orders,
                               logged_in=logged_in,
                               temp=temp)
    elif temp == "2":
        orders = load_full_accepted_details(uid)
        logged_in = "username" in session
        return render_template('view.html',
                               orders=orders,
                               logged_in=logged_in,
                               temp=temp)
    elif temp == "3":
        orders = load_full_delivered_details(uid)
        logged_in = "username" in session
        return render_template('view.html',
                               orders=orders,
                               logged_in=logged_in,
                               temp=temp)
    return redirect(url_for('dashboard'))


@app.route("/products")
def products():
    logged_in = "username" in session
    products = load_products_from_db()
    return render_template('products.html',
                           products=products,
                           logged_in=logged_in)


@app.route("/add")
def add():
    return render_template('add.html')


@app.route("/Add", methods=["POST"])
def Add():
    data = request.form
    username = session["username"]
    uid = session["uid"]
    add_product_to_db(data, username, uid)
    return redirect(url_for('dashboard'))


@app.route("/accept", methods=["POST"])
def accept():
    oid = request.form.get('oid')
    accept_order(oid)
    return redirect(url_for('dashboard'))


@app.route("/product")
def product():

    pid = request.args.get('pid')
    fid = request.args.get('fid')
    if not pid:
        return "Product ID not provided", 400
    products = load_products_from_db()
    try:
        pid = int(pid)
        fid = int(fid)
    except ValueError:
        return "Invalid Product ID", 400
    users = load_UserD_from_db()
    user = next((u for u in users if u["uid"] == fid), None)
    pd = next((u for u in products if u["pid"] == pid), None)
    if pd is None:
        return "Product not found", 404
    return render_template('product.html', pd=pd, user=user)


@app.route('/placeorder', methods=['POST', 'GET', 'PUT'])
def placeorder():

    fid = request.args.get('fid')
    pid = request.args.get('pid')
    bid = session.get('uid')

    quantity = request.form.get('orderQuantity')
    total_price = request.form.get('totalPrice')
    add_orders_to_db(fid, pid, bid, quantity, total_price)
    return redirect(url_for("home"))


@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    utype = session["utype"]
    uid = session["uid"]
    users = load_UserD_from_db()

    ordered = len(load_full_order_details(uid))
    accepted = len(load_full_accepted_details(uid))
    delivered = len(load_full_delivered_details(uid))

    user = next((u for u in users if u["uname"] == username), None)

    if user:
        if utype == "Farmer":
            products = load_fproducts_from_db(uid)
            return render_template("dashboard.html",
                                   user=user,
                                   products=products,
                                   ordered=ordered,
                                   accepted=accepted,
                                   delivered=delivered)
        elif utype == "Buyer":
            products = load_bproducts_from_db(uid)
            return render_template("dashboard1.html",
                                   user=user,
                                   products=products,
                                   ordered=ordered,
                                   accepted=accepted,
                                   delivered=delivered)
        elif utype == "Admin":
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
