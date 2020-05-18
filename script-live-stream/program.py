from picamera import PiCamera
import pika
import time
from picamera.array import PiRGBArray
import cv2
import base64

credentials = pika.PlainCredentials('admin', 'admin')
connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.100.29', 5672, '/', credentials))
channel = connection.channel()


# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = [640, 480]
camera.framerate = 16
rawCapture = PiRGBArray(camera, size=[640, 480])

# allow the camera to warmup, then initialize the average frame, last
# uploaded timestamp, and frame motion counter
print("[INFO] warming up...")
time.sleep(5)

# capture frames from the camera
for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image and initialize
    # the timestamp and occupied/unoccupied text
    frame = f.array

    retval, buffer = cv2.imencode('.jpg', frame)
    jpg_as_text = base64.b64encode(buffer);

    channel.basic_publish(exchange='live-stream', routing_key='live-stream', body=jpg_as_text)
    
    #print("trimit poza...")
    #time.sleep(0.5)

    rawCapture.truncate(0)

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
connection.close()