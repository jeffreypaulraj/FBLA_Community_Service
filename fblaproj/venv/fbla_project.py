from flask import Flask, redirect, url_for, render_template, Response, request
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

import pyrebase
import json

import datetime
from datetime import timedelta

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
    return render_template("newsignin.html", message = "")

@app.route('/signup')
def signup():
    return render_template("newsignup.html")

@app.route('/signupform', methods=['POST'])
def signupForm():
    print(request.form.get('idnumber'))
    user = root.child('Users').child(request.form.get('idnumber')).set({
        'Name': request.form.get('username'),
        'Id Number': request.form.get('idnumber') ,
        'Grade': request.form.get('grade'),
        'Total Hours': 0,
        'Total Entries': 0,
        'CSA Category': 'No Award'
    })
    idNumber = request.form.get('idnumber')
    name = request.form.get('username')
    email = request.form.get('emailaddress')
    password = request.form.get('password')
    grade = request.form.get('grade')
    user_auth = auth.create_user_with_email_and_password(email, password)
    
    max_hours = get_max_hours()
    csa_category = root.child('Users').child(idNumber).child('CSA Category').get()
    return render_template("index.html", idNumber = idNumber, name = name, total_entries = 0, total_hours = 0, max_hours = max_hours, csa_category = csa_category, grade = grade)

@app.route('/signinform', methods=['POST'])
def signinForm():
    email = request.form.get('emailaddress')
    password = request.form.get('password')
    idNumber = email[0:8]
    try:
        user_auth = auth.sign_in_with_email_and_password(email, password)

        name, total_entries,csa_category,total_hours,grade, entry_log = retrieve_data(idNumber)
        entry_date_list,entry_description_list,entry_stime_list,entry_etime_list, entry_hours_list = get_entry_log(entry_log)


        max_hours = get_max_hours()
        return render_template("index.html", idNumber = idNumber, name = name, total_entries = total_entries, total_hours = total_hours, max_hours = max_hours, csa_category = csa_category, grade = grade,
        entry_date_list = entry_date_list, entry_description_list = entry_description_list, entry_stime_list = entry_stime_list, entry_etime_list = entry_etime_list,
        entry_hours_list = entry_hours_list)
    except:
        return render_template("newsignin.html", message = "Failed Login. Try Again!")

@app.route('/processHours', methods=['POST'])
def processHours():
    date_entered = request.form.get('dateEntered')
    
    start_time_entered = request.form.get('startTimeEntered')
    end_time_entered = request.form.get('endTimeEntered')
    FMT = '%H:%M'
    elapsed_time = datetime.datetime.strptime(end_time_entered, FMT) - datetime.datetime.strptime(start_time_entered, FMT)
    hours_entered = round(elapsed_time.seconds/3600,2)
    
    description_entered = request.form.get('descriptionEntered')
    idNumber = request.form.get('idNumber')
    current_time = datetime.datetime.now()
    current_time_formatted = current_time.strftime("%Y-%m-%d %I:%M:%S %p")
    name,current_entries,csa_category,current_hours,grade,entry_log = retrieve_data(idNumber)
    entry_date_list,entry_description_list,entry_stime_list,entry_etime_list, entry_hours_list = get_entry_log(entry_log)


    total_entries = current_entries + 1
    name = request.form.get('name')
    total_hours = current_hours + hours_entered

    root.child('Users').child(idNumber).child('Entry Log').child(current_time_formatted).set({
        'Description': description_entered,
        'Hours Entered': hours_entered,
        'Date': date_entered,
        'Start Time': start_time_entered,
        'End Time': end_time_entered
    })

    if total_hours <= 50:
        root.child('Users').child(idNumber).update({'CSA Category': 'No Award'})
    elif total_hours >50 and total_hours <= 200:
        root.child('Users').child(idNumber).update({'CSA Category': 'CSA Community'})
    elif total_hours > 200 and total_hours <= 500:
        root.child('Users').child(idNumber).update({'CSA Category': 'CSA Service'})
    else:
        root.child('Users').child(idNumber).update({'CSA Category': 'CSA Achievement'})

    root.child('Time Log').child(current_time_formatted).set({
        'Name': root.child('Users').child(idNumber).child('Name').get(),
        'ID Number': idNumber,
        'Date of Service': date_entered,
        'Hours Logged': hours_entered,
        'Description of Hours': description_entered,
        'Total Hours': total_hours,
        'CSA Category': root.child('Users').child(idNumber).child('CSA Category').get(),
        'Timestamp': current_time_formatted
    })
    
    root.child('Users').child(idNumber).update({'Total Hours': total_hours})
    root.child('Users').child(idNumber).update({'Total Entries': total_entries})
    
    max_hours = get_max_hours()
    return render_template("index.html", idNumber = idNumber, name = name, total_entries = total_entries, total_hours = total_hours, max_hours = max_hours, csa_category = csa_category, grade = grade,
    entry_date_list = entry_date_list, entry_description_list = entry_description_list, entry_stime_list = entry_stime_list, entry_etime_list = entry_etime_list,
    entry_hours_list = entry_hours_list)

@app.route('/profileChange', methods=['POST'])
def profileChange():
    new_grade = request.form.get('newGradeEntered')
    new_name = request.form.get('newNameEntered')
    idNumber = request.form.get('idNumber')
    new_id_number = request.form.get('newidNumberEntered')
    
    name,total_entries,csa_category,total_hours,grade,entry_log = retrieve_data(idNumber)
    max_hours = get_max_hours()
    entry_date_list,entry_description_list,entry_stime_list,entry_etime_list, entry_hours_list = get_entry_log(entry_log)
    if new_name != "":
        root.child('Users').child(idNumber).update({'Name': new_name})
        name = new_name
    if new_grade != "":
        root.child('Users').child(idNumber).update({'Grade': new_grade})
        grade = new_grade
    if new_id_number != "":
        root.child('Users').child(idNumber).update({'Id Number': new_id_number})
        user = root.child('Users').child(new_id_number).set({
            'Name': name,
            'Id Number': new_id_number ,
            'Grade': grade,
            'Total Hours': total_hours,
            'Total Entries': total_entries,
            'CSA Category': csa_category
        })
        root.child('Users').child(idNumber).delete()
        idNumber = new_id_number
    return render_template("index.html", idNumber = idNumber, name = name, total_entries = total_entries, total_hours = total_hours, max_hours = max_hours, csa_category = csa_category, grade = grade,
    entry_date_list = entry_date_list, entry_description_list = entry_description_list, entry_stime_list = entry_stime_list, entry_etime_list = entry_etime_list,
    entry_hours_list = entry_hours_list)


@app.route('/reportHours', methods=['GET','POST'])
def reportHours():
    user_db = db.reference('Users')
    all_users = user_db.order_by_child('Grade').get()
    all_users = dict(all_users)
    name_list = []
    id_number_list = []
    grade_list = []
    csa_list = []
    hours_list = []
    entries_list = []
    for i in range (len(all_users)):
        name_list.append(all_users[list(all_users.keys())[i]]['Name'])
        id_number_list.append(all_users[list(all_users.keys())[i]]['Id Number'])
        grade_list.append(all_users[list(all_users.keys())[i]]['Grade'])
        hours_list.append(all_users[list(all_users.keys())[i]]['Total Hours'])
        entries_list.append(all_users[list(all_users.keys())[i]]['Total Entries'])
        csa_list.append(all_users[list(all_users.keys())[i]]['CSA Category'])
    return render_template("report.html", all_users = all_users, name_list = name_list, id_number_list = id_number_list, grade_list = grade_list,
    entries_list = entries_list,hours_list = hours_list, csa_list = csa_list)

@app.route('/dateView', methods=['GET','POST'])
def dateView():
    start_date = request.form.get('startDateEntered')
    end_date = request.form.get('endDateEntered')
    start_tuple = (start_date[0:4], start_date[5:7], start_date[8:10])
    end_tuple = (end_date[0:4], end_date[5:7], end_date[8:10])
    print(start_tuple)
    time_db = db.reference('Time Log')
    all_users = time_db.order_by_child('Date of Service').get()
    all_users = dict(all_users)
    name_list = []
    id_number_list = []
    description_list = []
    csa_list = []
    date_list = []
    total_hours_list = []
    entered_hours_list = []
    timestamp_list = []
    for i in range (len(all_users)):
        date = all_users[list(all_users.keys())[i]]['Date of Service']
        log_tuple = (date[0:4], date[5:7], date[8:10])
        if start_tuple <= log_tuple <= end_tuple:
            name_list.append(all_users[list(all_users.keys())[i]]['Name'])
            id_number_list.append(all_users[list(all_users.keys())[i]]['ID Number'])
            description_list.append(all_users[list(all_users.keys())[i]]['Description of Hours'])
            total_hours_list.append(all_users[list(all_users.keys())[i]]['Total Hours'])
            entered_hours_list.append(all_users[list(all_users.keys())[i]]['Hours Logged'])
            date_list.append(all_users[list(all_users.keys())[i]]['Date of Service'])
            csa_list.append(all_users[list(all_users.keys())[i]]['CSA Category'])
            timestamp_list.append(all_users[list(all_users.keys())[i]]['Timestamp'])
    return render_template("dateview.html", all_users = all_users, name_list = name_list, id_number_list = id_number_list, description_list = description_list,
    date_list = date_list,total_hours_list = total_hours_list, csa_list = csa_list, entered_hours_list = entered_hours_list, timestamp_list = timestamp_list)


@app.route('/home')
def home():
    return render_template("index.html")

def get_max_hours():
    user_db = db.reference('Users')
    max_hours_user = user_db.order_by_child('Total Hours').limit_to_last(1).get()
    max_hours_user_id = next(iter(max_hours_user))
    max_hours = root.child('Users').child(max_hours_user_id).child('Total Hours').get()
    return max_hours

def retrieve_data(idNumber):
    name = root.child('Users').child(idNumber).child('Name').get()
    current_entries = root.child('Users').child(idNumber).child('Total Entries').get()
    csa_category = root.child('Users').child(idNumber).child('CSA Category').get()
    total_hours = root.child('Users').child(idNumber).child('Total Hours').get()
    grade = root.child('Users').child(idNumber).child('Grade').get()
    entry_log = root.child('Users').child(idNumber).child('Entry Log').get()
    return name,current_entries,csa_category,total_hours,grade, entry_log
    
def get_entry_log(entry_log):
    entry_date_list = []
    entry_stime_list = []
    entry_etime_list = []
    entry_description_list = []
    entry_hours_list = []
    for key, value in entry_log.items():
        for key_2, value_2 in value.items():
            if key_2 == 'Description':
                entry_description_list.append(value_2)
            if key_2 == 'Date':
                entry_date_list.append(value_2)
            if key_2 == 'Start Time':
                entry_stime_list.append(value_2)
            if key_2 == 'End Time':
                entry_etime_list.append(value_2)
            if key_2 == 'Hours Entered':
                entry_hours_list.append(value_2)
    return entry_date_list,entry_description_list,entry_stime_list,entry_etime_list, entry_hours_list
            
if __name__ == '__main__':
    print('Starting')
    app.run(debug=True)
    print('Exiting')