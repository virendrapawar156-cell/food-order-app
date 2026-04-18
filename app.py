from flask import Flask, render_template, request, redirect, session
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = "secret123"

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["food_app"]
users_collection = db["users"]
orders_collection = db["orders"]

# ================= HOME =================
@app.route('/')
def home():
    return render_template("signup.html")


# ================= SIGNUP =================
@app.route('/signup', methods=['POST'])
def signup():
    user = {
        "name": request.form.get('Name'),
        "email": request.form.get('Email'),
        "phone": request.form.get('Phone')
    }

    users_collection.insert_one(user)

    # store user in session
    session['user'] = user["email"]

    return redirect('/order')


# ================= LOGIN =================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        phone = request.form.get('phone')

        user = users_collection.find_one({
            "email": email,
            "phone": phone
        })

        if user:
            session['user'] = email
            return redirect('/order')
        else:
            return render_template("login.html", error="Invalid email or phone ❌")

    return render_template("login.html")


# ================= ORDER PAGE =================
@app.route('/order')
def order():
    if 'user' not in session:
        return redirect('/')
    return render_template("order.html")


# ================= PLACE ORDER =================
@app.route('/place_order', methods=['POST'])
def place_order():
    if 'user' not in session:
        return redirect('/')

    order = {
        "user_email": session['user'],
        "item": request.form.get('Item'),
        "quantity": request.form.get('Quantity'),
        "address": request.form.get('address')
    }

    orders_collection.insert_one(order)

    return render_template("success.html")


# ================= LOGOUT =================
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')


# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)