from flask import Flask, redirect, url_for, render_template, Response, request
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

import pyrebase

app = Flask(__name__)

cred = credentials.Certificate("/Users/Jeffrey/Downloads/sbfbla-2d88f-firebase-adminsdk-9qpc2-d9b6f84a5a.json")
firebase_admin.initialize_app(cred, {'databaseURL': 'https://sbfbla-2d88f.firebaseio.com/'})

root = db.reference()

user = db.reference()

idNumber = None

config = {
    "apiKey": "AIzaSyByziQa01XAmoShhQjglWtQ6-BUHwkn61M",
    "authDomain": "sbfbla-2d88f.firebaseapp.com",
    "databaseURL": "https://sbfbla-2d88f.firebaseio.com",
    "projectId" : "sbfbla-2d88f",
    "storageBucket": "sbfbla-2d88f.appspot.com",
    "messagingSenderId": "391063470721",
    "appId": "1:391063470721:web:a6a9341c42b0224702c380",
    "measurementId": "G-2GLLKDXD3W"
}

firebase_auth_setup = pyrebase.initialize_app(config)

auth = firebase_auth_setup.auth()

@app.route('/')
def index():
    return 'Hello, Flask!'

@app.route('/signin')
def signin():
    return render_template("signin.html")

@app.route('/signup')
def signup():
    return render_template("signup.html")

@app.route('/signupform', methods=['POST'])
def signupForm():
    print(request.form.get('idnumber'))
    user = root.child('Users').child(request.form.get('idnumber')).set({
        'Name': request.form.get('username'),
        'Id Number': request.form.get('idnumber') ,
        'Grade': request.form.get('grade'),
        'Total Hours': 0,
        'Total Entries': 0
    })
    idNumber = request.form.get('idnumber')
    name = request.form.get('username')
    email = request.form.get('emailaddress')
    password = request.form.get('password')
    user_auth = auth.create_user_with_email_and_password(email, password)
    total_entries = 0
    total_hours = 0
    user_db = db.reference('Users')
    max_hours_user = user_db.order_by_child('Total Hours').limit_to_last(1).get()
    max_hours_user_id = next(iter(max_hours_user))
    max_hours = root.child('Users').child(max_hours_user_id).child('Total Hours').get()
    return render_template("index.html", idNumber = idNumber, name = name, total_entries = total_entries, total_hours = 0, max_hours = max_hours)

@app.route('/signinform', methods=['POST'])
def signinForm():
    email = request.form.get('emailaddress')
    password = request.form.get('password')
    idNumber = email[0:8]
    print(idNumber)
    user_auth = auth.sign_in_with_email_and_password(email, password)
    idNumber = root.child('Users').child(idNumber).child('Id Number').get()
    name = root.child('Users').child(idNumber).child('Name').get()
    total_entries = root.child('Users').child(idNumber).child('Total Entries').get()
    total_hours = root.child('Users').child(idNumber).child('Total Hours').get()
    user_db = db.reference('Users')
    max_hours_user = user_db.order_by_child('Total Hours').limit_to_last(1).get()
    max_hours_user_id = next(iter(max_hours_user))
    max_hours = root.child('Users').child(max_hours_user_id).child('Total Hours').get()
    return render_template("index.html", idNumber = idNumber, name = name, total_entries = total_entries, total_hours = total_hours, max_hours = max_hours)

@app.route('/processHours', methods=['POST'])
def processHours():
    hours_entered = int(request.form.get('hoursEntered'))
    description_entered = request.form.get('descriptionEntered')
    idNumber = request.form.get('idNumber')
    current_hours = root.child('Users').child(idNumber).child('Total Hours').get()
    current_entries = root.child('Users').child(idNumber).child('Total Entries').get()
    total_entries = current_entries + 1
    name = request.form.get('name')
    print(type(hours_entered))
    root.child('Users').child(idNumber).update({'Total Hours': current_hours + hours_entered})
    root.child('Users').child(idNumber).update({'Total Entries': total_entries})
    total_hours = root.child('Users').child(idNumber).child('Total Hours').get()
    user_db = db.reference('Users')
    max_hours_user = user_db.order_by_child('Total Hours').limit_to_last(1).get()
    max_hours_user_id = next(iter(max_hours_user))
    max_hours = root.child('Users').child(max_hours_user_id).child('Total Hours').get()
    print('Max Hours:')
    return render_template("index.html", idNumber = idNumber, name = name, total_entries = total_entries, total_hours = total_hours, max_hours = max_hours)


@app.route('/reportHours', methods=['GET'])
def reportHours():
    user_db = db.reference('Users')
    all_users = user_db.order_by_child('Grade').get()
    return render_template("report.html", all_data = all_users)


@app.route('/home')
def home():
    return render_template("index.html")
    
if __name__ == '__main__':
    print('Starting')
    app.run(debug=True)
    print('Exiting')