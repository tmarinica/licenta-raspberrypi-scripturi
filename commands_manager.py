import pika
from subprocess import Popen, PIPE
import json
from services_manager import ServicesManager
import threading
import os
import signal

credentials = pika.PlainCredentials('admin', 'admin')
connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.100.29', 5672, '/', credentials))
channel = connection.channel()

alarm = None
alarmAlreadyStarted = False

def message_received_callback(ch, method, properties, message):

    global m
    global alarm
    global alarmAlreadyStarted

    message = message.decode("utf-8")
    print("Received message ", message)

    message_dict = json.loads(message)
    name = message_dict["name"]
    parameter = message_dict["parameter"]

    print(name)
    print(parameter)

    if name == "START_LIVE_STREAM":
        print("starting live stream...")
        m.startLiveStream = True
    
    if name == "STOP_LIVE_STREAM":
        print("stopping live stream...")
        m.startLiveStream = False

    if name == "LOCK_DOOR":
        print("locking door...")
        Popen(["omxplayer", "lock.wav", "-o", "local"], stdin=PIPE, stdout=PIPE, stderr=PIPE)

    if name == "UNLOCK_DOOR":
        print("unlocking door...")
        Popen(["omxplayer", "unlock.wav", "-o", "local"], stdin=PIPE, stdout=PIPE, stderr=PIPE)

    if name == "START_ALARM" and not alarmAlreadyStarted:
        print("start alarm")
        alarm = Popen(["omxplayer", "alarm.mp3", "-o", "local"], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        alarmAlreadyStarted = True

    if name == "STOP_ALARM" and alarmAlreadyStarted:
        print("STOP_ALARM")
        alarm.communicate(input='q'.encode())
        alarmAlreadyStarted = False


    if name == "CHANGE_LIVE_STREAM_QUALITY":
        if parameter == "high":
            m.liveStreamQuality = 90
        if parameter == "medium": 
            m.liveStreamQuality = 40
        if parameter == "low":
            m.liveStreamQuality = 10


m = ServicesManager()

try:
    threading.Thread(target=m.startServices, name="Thread3", daemon=True ).start()
    
except Exception as e:
    print ("Error: unable to start thread" + str(e))


channel.basic_consume('comenzi', message_received_callback, auto_ack=True)
print('Astept comenzi...')
channel.start_consuming()




