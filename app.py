from flask import Flask, render_template, request, redirect, session
from pymongo import MongoClient
import os

# ================= TWILIO =================
try:
    from twilio.rest import Client as TwilioClient
except ImportError:
    TwilioClient = None

app = Flask(__name__)

# ================= SECRET KEY =================
app.secret_key = os.environ.get("SECRET_KEY", "secret123")

# ================= MONGODB =================
MONGO_URI = "mongodb+srv://virendrapawar:veeru12@cluster1.93rec0a.mongodb.net/food_app?retryWrites=true&w=majority&appName=Cluster1"

client = MongoClient(MONGO_URI)
db = client["food_app"]

users_collection = db["users"]
orders_collection = db["orders"]

# ================= TWILIO CONFIG (PUT YOUR REAL VALUES) =================
TWILIO_ACCOUNT_SID = "YOUR_SID"
TWILIO_AUTH_TOKEN = "YOUR_AUTH_TOKEN"
TWILIO_PHONE_NUMBER = "+1XXXXXXXXXX"

# ================= FORMAT PHONE =================
def format_phone_number(phone):
    if not phone:
        return None

    phone = phone.strip().replace(" ", "").replace("-", "")

    if phone.startswith("+91") and len(phone) == 13:
        return phone

    if len(phone) == 10 and phone.isdigit():
        return "+91" + phone

    if phone.startswith("91") and len(phone) == 12:
        return "+" + phone

    return None

# ================= SEND SMS =================
def send_order_sms(phone, item, quantity):
    print("📲 Sending SMS...")

    if not all([TwilioClient, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
        print("❌ Twilio not configured")
        return False

    to_number = format_phone_number(phone)
    print("📞 Number:", to_number)

    if not to_number:
        print("❌ Invalid phone format")
        return False

    try:
        client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        message = client.messages.create(
            body=f"🍔 Order Confirmed!\n{quantity} x {item}\nThank you for ordering!",
            from_=TWILIO_PHONE_NUMBER,
            to=to_number
        )

        print("✅ SMS SENT:", message.sid)
        return True

    except Exception as e:
        print("❌ SMS ERROR:", e)
        return False

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
    session['user'] = user["email"]

    return redirect('/options')

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
            return redirect('/options')
        else:
            return render_template("login.html", error="Invalid ❌")

    return render_template("login.html")

# ================= OPTIONS =================
@app.route('/options')
def options():
    if 'user' not in session:
        return redirect('/')
    return render_template("options.html")

# ================= CATEGORY PAGES =================
@app.route('/meal')
def meal():
    return render_template("meals.html")

@app.route('/vegetables')
def vegetables():
    return render_template("vegetables.html")

@app.route('/fastfood')
def fastfood():
    return render_template("fastfood.html")

@app.route('/fruits')
def fruits():
    return render_template("fruits.html")

@app.route('/drinks')
def drinks():
    return render_template("drinks.html")

# ================= ORDER PAGE =================
@app.route('/order')
def order():
    if 'user' not in session:
        return redirect('/')

    item = request.args.get('item')
    return render_template("order.html", item=item)

# ================= PLACE ORDER =================
@app.route('/place_order', methods=['POST'])
def place_order():
    if 'user' not in session:
        return redirect('/')

    item = request.form.get('Item')
    quantity = request.form.get('quantity')
    address = request.form.get('address')

    user = users_collection.find_one({"email": session['user']})

    order = {
        "user_email": session['user'],
        "item": item,
        "quantity": quantity,
        "address": address
    }

    orders_collection.insert_one(order)

    if user:
        send_order_sms(user.get("phone"), item, quantity)

    return render_template("success.html")

# ================= LOGOUT =================
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)