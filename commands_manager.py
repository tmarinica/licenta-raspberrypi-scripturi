import pika
from subprocess import Popen, PIPE
import json
from services_manager import ServicesManager
import threading

credentials = pika.PlainCredentials('admin', 'admin')
connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.100.29', 5672, '/', credentials))
channel = connection.channel()

def message_received_callback(ch, method, properties, message):

    global m

    message = message.decode("utf-8")
    print("Received message ", message)

    message_dict = json.loads(message)
    command = message_dict["command"]
    parameter = message_dict["parameter"]

    print(command)
    print(parameter)

    if command == "START_LIVE_STREAM_SCRIPT":
        print("starting live stream...")
        m.startLiveStream = True
    
    if command == "STOP_LIVE_STREAM_SCRIPT":
        print("stopping live stream...")
        m.startLiveStream = False

m = ServicesManager()

try:
    threading.Thread(target=m.startServices, name="Thread3", daemon=True ).start()
    
except Exception as e:
    print ("Error: unable to start thread" + str(e))


channel.basic_consume('comenzi', message_received_callback, auto_ack=True)
print('Astept comenzi...')
channel.start_consuming()