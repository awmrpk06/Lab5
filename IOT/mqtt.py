from flask import Flask, render_template, request
from flask_mqtt import Mqtt
import pyrebase
from datetime import datetime

app = Flask(__name__)
app.config['MQTT_BROKER_URL'] = 'mqtt.flespi.io'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = 'ul8rL18u7pCr1PL5pmSti8NvTOy9s2NNbJ2Nz07weyL3dmWswEMCBnXkZmhgcURe'
app.config['MQTT_PASSWORD'] = ''
app.config['MQTT_REFRESH_TIME'] = 1.0  # refresh time in seconds
#firebase
firebaseConfig = {
    "apiKey": "AIzaSyChZeyXodT_uJiykzmsw201LPVXgk4HFcE",
    "databaseURL":"https://lab5-c600f-default-rtdb.firebaseio.com",
    "authDomain": "lab5-c600f.firebaseapp.com",
    "projectId": "lab5-c600f",
    "storageBucket": "lab5-c600f.appspot.com",
    "messagingSenderId": "807353309157",
    "appId": "1:807353309157:web:000d51ae2688aea3f7810c",
    "measurementId": "G-TB967Q3ZRZ"
  }
firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()
flag = 0
temp = ""
humid = ""
#
mqtt = Mqtt(app)
@app.route('/',methods = ['GET','POST'])
def index():
    return render_template('index.html')

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    print("Connected")
    mqtt.subscribe('/topic/temp')
    mqtt.subscribe('/topic/humid')

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )
    global flag,temp,humid
    if(data['topic'] == "/topic/humid"):
        humid = {"Humid": data['payload']}
        #set flag
        flag = flag + 1
    elif(data['topic'] == "/topic/temp"):
        temp = {"Temp": data['payload']}
        #set flag
        flag = flag + 1
    if flag == 2:
        #get time
        now = datetime.now()
        date = now.strftime("%d %m,%Y")
        current_time = now.strftime("%H:%M:%S")
        time = date + " " + current_time
        #up value to db
        value = {**temp, **humid}
        #print(value)
        db.child(date).child(current_time).set(value)
        #realtime
        value = {**value, **{"Time" : time}}
        db.child("1").set(value)
        flag = 0
    print('topic received: '+ data['topic'])
    print('data received: '+ data['payload'])
    

