import socket
from picamera import PiCamera
import time
from picamera.array import PiRGBArray
import cv2
import sys
import base64


TCP_IP = "192.168.100.10"

TCP_PORT = 8000


# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = [608, 480]
camera.framerate = 16
rawCapture = PiRGBArray(camera, size=[608, 480])

# allow the camera to warmup, then initialize the average frame, last
# uploaded timestamp, and frame motion counter
print("[INFO] warming up...")
time.sleep(5)

camera.start_preview()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((TCP_IP, TCP_PORT))
# capture frames from the camera
for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image and initialize
    # the timestamp and occupied/unoccupied text
    frame = f.array

    
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 20]

    retval, buffer = cv2.imencode('.jpg', frame, encode_param)
    
    jpg_as_text = base64.b64encode(buffer)
    
    jpg_as_text = jpg_as_text + '*'

    #print ("Sending image...")

    sock.sendall(jpg_as_text)    

    #time.sleep(5)    

    rawCapture.truncate(0)

sock.close()

# When everything done, release the capture
cap.release()
camera.stop_preview()