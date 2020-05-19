import pika
from subprocess import Popen, PIPE
import json

credentials = pika.PlainCredentials('admin', 'admin')
connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.100.29', 5672, '/', credentials))
channel = connection.channel()

liveStreamProcess = None

print("Starting detected faces proces...")
detectFacesProcess = Popen(['python3', '/home/pi/scripts/script-detectie/program.py'], stdout=PIPE, stderr=PIPE)

def message_received_callback(ch, method, properties, message):

    global liveStreamProcess
    global detectFacesProcess

    message = message.decode("utf-8")
    print("Received message ", message)

    message_dict = json.loads(message)
    command = message_dict["command"]
    parameter = message_dict["parameter"]

    print(command)
    print(parameter)

    if command == "START_LIVE_STREAM_SCRIPT" and liveStreamProcess is None:
        print("Stopping detected faces process...")

        detectFacesProcess.terminate()
        detectFacesProcess = None

        print("Starting live stream process...")
        liveStreamProcess = Popen(['python3', '/home/pi/scripts/script-live-stream/program.py'], stdout=PIPE, stderr=PIPE)
    
    if command == "STOP_LIVE_STREAM_SCRIPT" and liveStreamProcess is not None:
        print("Stopping live stream...")
        liveStreamProcess.terminate()
        liveStreamProcess = None

        print("Starting detected faces proces...")
        detectFacesProcess = Popen(['python3', '/home/pi/scripts/script-detectie/program.py'], stdout=PIPE, stderr=PIPE)


channel.basic_consume('comenzi', message_received_callback, auto_ack=True)

print('Astept comenzi...')

channel.start_consuming()


