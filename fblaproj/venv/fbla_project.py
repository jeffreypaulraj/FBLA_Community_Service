from flask import Flask, redirect, url_for, render_template, Response, request
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

app = Flask(__name__)

cred = credentials.Certificate("/Users/Jeffrey/Downloads/sbfbla-2d88f-firebase-adminsdk-9qpc2-d9b6f84a5a.json")
firebase_admin.initialize_app(cred, {'databaseURL': 'https://sbfbla-2d88f.firebaseio.com/'})

root = db.reference()

user = db.reference()

idNumber = None

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
    user = root.child(request.form.get('idnumber')).set({
        'Name': request.form.get('username'),
        'Id Number': request.form.get('idnumber') ,
        'Grade': request.form.get('grade'),
        'Total Hours': 0
    })
    print('Name: ' + request.form.get('username'))
    idNumber = request.form.get('idnumber')
    name = request.form.get('username')
    return render_template("index.html", idNumber = idNumber, name = name)

@app.route('/processHours', methods=['POST'])
def processHours():
    hours_entered = request.form.get('hoursEntered')
    description_entered = request.form.get('descriptionEntered')
    idNumber = request.form.get('idNumber')
    current_hours = user.child(idNumber).get('Total Hours')
    name = request.form.get('name')
    user.child(idNumber).update({'Total Hours': current_hours + hours_entered})
    return render_template("index.html", idNumber = idNumber, name = name)

@app.route('/home')
def home():
    return render_template("index.html")
    
if __name__ == '__main__':
    print('Starting')
    app.run(debug=True)
    print('Exiting')