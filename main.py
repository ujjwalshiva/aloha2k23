import streamlit as st
import pandas as pd
import pytz
import datetime
import json
from pymongo.mongo_client import MongoClient

st.set_page_config(
    page_title="Aloha 2K23",
    page_icon="🎉",
    layout="wide"
)

uri = st.secrets['URL']
client = MongoClient(uri)
db = client['Aloha2K23']['DS']
ist = pytz.timezone("Asia/Kolkata")

st.image('Aloha Hero.png')
st.markdown("<p style='text-align: center;'>This is <b>AuthIn</b> for Aloha 2K23, a standalone web app developed by the team at <a href='https://gdsciare.club'> GDSC IARE Tech </a> </p> <br>",
                unsafe_allow_html=True)

menu = st.sidebar.selectbox(
    "Menu", ["🏠 Home", "✅ Check In", "🧑🏻 Add Student", "💻 View Student", "🔄️ Reset Student", "📃 Checked In Data", "📃 Not Checked In Data", "📃 All Data"])


def notCheckedInCount(db):
    query = {'lastCheckIn': 'Not Checked In'}
    count = db.count_documents(query)
    return count


def checkedInCount(db):
    query = {'lastCheckIn': {'$ne': 'Not Checked In'}}
    count = db.count_documents(query)
    return count


def totalDbCount(db):
    count = db.count_documents({})
    return count


def checkInStudent(db, roll, entryPoint):
    digits = roll.upper().strip()
    query = {'roll': {'$regex': f'.*{digits}$'}}
    result = db.find_one(query)

    if result is not None:
        name = result["name"]
        fullRoll = "23951A67"+digits
        if result["lastCheckIn"] == "Not Checked In":
            jsonData = {
                '$set': {
                    'lastCheckIn': datetime.datetime.now(ist).strftime("%H:%M:%S"),
                    'entryPoint': entryPoint
                }
            }
            updateQuery = db.update_one(query, jsonData)
            if updateQuery.matched_count > 0:
                return st.success(f"**{name} - {fullRoll}** has checked in successfully")
            else:
                return st.warning("Try Again")
        else:
            return st.error(f'**{name}** has already checked in at **{result["lastCheckIn"]}** via Entry Point **{result["entryPoint"]}**')
    else:
        return st.error("Student :red[**not available**] in Database")


def addStudent(db, name, roll, phone, section, payment, password):
    fullRoll = "23951A67" + roll.strip()
    jsonData = {
        'name': name.title(),
        'roll': fullRoll.upper(),
        'phone': phone.replace(" ", ""),
        'email': fullRoll.lower()+"@iare.ac.in",
        'section': section.upper(),
        'paymentMode': payment.title(),
        'lastCheckIn': "Not Checked In",
        'entryPoint': "Nil"
    }

    if (name and roll and phone):
        searchQuery = {'roll': {'$regex': f'.*{roll[-2:]}$'}}
        if db.find_one(searchQuery) is not None:
            return "Name already there in the database"
        else:
            if password != st.secrets['PASSKEY']:
                return ":red[**🚨 Enter Valid Password**]"
            else:
                response = db.insert_one(jsonData)
                if response.acknowledged:
                    return f"{name} has been added to **Database**"
                else:
                    return "Try Submitting again"
    else:
        return "Fill all the details"


def viewStudent(db, roll):
    digits = roll.upper().strip()
    query = {'roll': {'$regex': f'.*{digits}$'}}
    result = db.find_one(query)
    if result is not None:
        return result
    else:
        return "Student :red[**not available**] in Database"


def resetStudent(db, roll, password):
    digits = roll.upper().strip()
    query = {'roll': {'$regex': f'.*{digits}$'}}
    result = db.find_one(query)
    if password != st.secrets['PASSKEY']:
        return st.error("Enter Valid Password")
    else:
        if result is not None:
            name = result["name"]
            fullRoll = "23951A67"+digits
            if result["lastCheckIn"] != "Not Checked In":
                jsonData = {
                    '$set': {
                        'lastCheckIn': "Not Checked In",
                        'entryPoint': "Nil"
                    }
                }
                updateQuery = db.update_one(query, jsonData)
                if updateQuery.matched_count > 0:
                    return st.success(f"**{name} - {fullRoll}** check in details have been **RESET**")
                else:
                    return st.warning("Try Again")
            else:
                return st.error(f'**{name}** has not checked in yet!')
        else:
            return st.error("Student :red[**not available**] in Database")


if menu == "🏠 Home":    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Students Registered", f"{totalDbCount(db)}", "Online")
    col2.metric("Checked In", f"{checkedInCount(db)}", f"{totalDbCount(db) - checkedInCount(db)}")
    col3.metric("Not Checked In", f"{notCheckedInCount(db)}", f"{-(totalDbCount(db)) + notCheckedInCount(db) }")
    


if menu == "✅ Check In":
    st.write("This is the Check In page.")
    roll = st.text_input("Last 2 digits of Roll Number")
    entryPoint = st.selectbox("Entry Point", ["1", "2"])
    checkInBtn = st.button("Check In")
    if roll and entryPoint and checkInBtn:
        checkInStudent(db, roll, entryPoint)


if menu == "🧑🏻 Add Student":
    st.write("This is the Add Student page.")
    name = st.text_input('Name of Student')
    roll = st.text_input("Last 2 digits of Roll Number")
    phone = st.text_input("Enter Phone Number")
    section = st.selectbox("Enter Section", ["A", "B", "C"])
    payment = st.selectbox("Enter Payment Mode", ["Online", "Cash"])

    password = st.text_input(
        ":red[Password for Authentication (Ask Sathwik):]", type="password")
    addStudentBtn = st.button("Add Student")
    if addStudentBtn:
        st.warning(addStudent(db, name, roll, phone, section, payment, password))


if menu == "💻 View Student":
    st.write("This is the View Student page.")

    roll = st.text_input("Last 2 Digits of Roll Number:")
    viewStudentBtn = st.button("View Student")
    if roll and viewStudentBtn:
        st.write(viewStudent(db, roll))

if menu == "🔄️ Reset Student":
    st.write("This is the Reset Student page.")
    roll = st.text_input("Last 2 digits of Roll Number")
    password = st.text_input(
        ":red[Password for Authentication (Ask Sathwik):]", type="password")
    resetCheckInBtn = st.button("Reset Check In")
    if roll and resetCheckInBtn:
        resetStudent(db, roll, password)

if menu == "📃 Checked In Data":
    df = pd.DataFrame(
        list(db.find({"lastCheckIn": {"$ne": "Not Checked In"}})))
    if df.shape[0] == 0:
        st.error("No Check Ins done yet. Still waiting :)")
    else:
        df = df.drop('_id', axis=1)
        st.dataframe(df)

if menu == "📃 Not Checked In Data":
    df = pd.DataFrame(
        list(db.find({'lastCheckIn': 'Not Checked In'})))
    if df.shape[0] == 0:
        st.success("Looks like all have checked in!")
    else:
        df = df.drop('_id', axis=1)
        st.dataframe(df)

if menu == "📃 All Data":
    df = pd.DataFrame(list(db.find({})))
    df = df.drop('_id', axis=1)
    st.dataframe(df)

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
