
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from flask import Flask, render_template, request, redirect, flash, jsonify, make_response, session
from datetime import datetime, timedelta
import hashlib
import jwt
from flask_session import Session
from babel.numbers import format_currency



uri = "mongodb+srv://zulian:zulian@cluster0.ttjbb4o.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['pesona-wisata']

SECRET_KEY = 'secret1141'
TOKEN_KEY = 'mytoken'

# Create flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'f3cfe9ed8fae309f02079dbf'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route('/', methods=['GET'])
def index():
    wisatas = db.wisata.find()

    return render_template('index.html', wisatas=wisatas)
    # return session.get("name")
    # return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('name'):
        return redirect('/')

    if request.method == 'GET':
        return render_template('register.html')

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        password_hash = hashlib.sha256(password. encode('utf-8')).hexdigest()

        doc = {
            "name": name,
            "email": email,
            "category": 'visitor',
            "password": password_hash
        }
        db.users.insert_one(doc)

        flash('Register successful')
        return redirect('/register')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('name'):
        return redirect('/')

    if request.method == 'GET':
        return render_template('login.html')

    if request.method == 'POST':
        email = request.form["email"]
        password = request.form["password"]
        pw_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
        result = db.users.find_one(
            {
                "email": email,
                "password": pw_hash,
            }
        )

        if result:
            session["name"] = result['name']
            session["email"] = result['email']
            session["category"] = result['category']

            flash('Logout successful')
            return redirect('/')

        else:
            flash("Username dan password tidak sesuai")
            return redirect('/login')

@app.route('/logout', methods=['GET'])
def logout():
    flash('Logout successful')
    session["name"] = None
    session["email"] = None
    session["category"] = None

    return redirect("/")

@app.route('/admin-wisata', methods=['POST', 'GET'])
def wisata():
    wisatas = db.wisata.find()
    return render_template('admin-wisata.html', wisatas=wisatas)

@app.route('/admin-add-wisata', methods=['POST', 'GET'])
def add_wisata():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        location = request.form.get('location')
        # total_tickets = int(request.form.get('total_tickets'))

        today = datetime.now()
        mytime = today.strftime('%Y-%m-%d-%H-%M-%S')
        file = request.files['image_wisata']
        extension = file.filename.split('.')[-1]
        filename = f'static/images/wisata-{name}-{mytime}.{extension}'
        file.save(filename)

        price = float(request.form.get('price'))
        # formatted_price = format_currency(price, 'IDR', locale='id_ID')
        db.wisata.insert_one({
            'name': name,
            'description': description,
            'location': location,
            'price': price,
            'image_wisata': filename,
        })
        return redirect('/admin/wisata')

    if request.method == 'GET':
        return render_template('admin-add-wisata.html')
