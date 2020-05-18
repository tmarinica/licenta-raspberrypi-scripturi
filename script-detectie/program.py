from picamera import PiCamera
import numpy as np
import datetime
import cv2
import time
import base64
from picamera.array import PiRGBArray
import pika



credentials = pika.PlainCredentials('admin', 'admin')
connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.100.29', 5672, '/', credentials))
channel = connection.channel()
#channel.exchange_declare(exchange='poze', exchange_type='fanout', durable='true')

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = [640, 480]
camera.framerate = 16
rawCapture = PiRGBArray(camera, size=[640, 480])
 
frontal_face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# allow the camera to warmup, then initialize the average frame, last
# uploaded timestamp, and frame motion counter
print("[INFO] warming up...")
time.sleep(5)


hasStabilityTimerAlreadyStarted = False
stabilityStartTime = None
stabilityEndTime = None

hasBetweenSendsTimeTimerAlreadyStarted = False
betweenSendsStartTime = None
betweenSendsEndTime = None
betweenSendsTimerDuration = None

print("here")

camera.start_preview()

# capture frames from the camera
for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image and initialize
    # the timestamp and occupied/unoccupied text
    frame = f.array

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    

    #print(gray)
    
    faces_frontal = frontal_face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=15,
        minSize=(30, 30)
    )

    

    if (len(faces_frontal) != 0):
        if not hasStabilityTimerAlreadyStarted:
            stabilityStartTime = time.time()
            hasStabilityTimerAlreadyStarted = True
	    print("detectez fata")
    else:
        print("not!!!!!!!!!")
        hasStabilityTimerAlreadyStarted = False
    
    if stabilityStartTime:
        if hasStabilityTimerAlreadyStarted:
            stabilityEndTime = time.time()
            stabilityDuration = stabilityEndTime - stabilityStartTime
            #print(duration)
            if stabilityDuration > 1:
                print("a trecut 1 sec de stabilitate")

                if not hasBetweenSendsTimeTimerAlreadyStarted or (hasBetweenSendsTimeTimerAlreadyStarted and betweenSendsTimerDuration >= 5): 
                    print("trimit poza...")

                    retval, buffer = cv2.imencode('.jpg', frame)
                    jpg_as_text = base64.b64encode(buffer)
                    
                    #print(jpg_as_text)

                    channel.basic_publish(exchange='poze', routing_key='poze', body=jpg_as_text)

                    hasBetweenSendsTimeTimerAlreadyStarted = False
                    betweenSendsTimerDuration = 0
                
                if not hasBetweenSendsTimeTimerAlreadyStarted:
                    hasBetweenSendsTimeTimerAlreadyStarted = True
                    betweenSendsStartTime = time.time()

                hasStabilityTimerAlreadyStarted = False

    if betweenSendsStartTime:
        betweenSendsEndTime = time.time()
        betweenSendsTimerDuration = betweenSendsEndTime - betweenSendsStartTime
        print("betweenSendsTimerDuration = "+str(betweenSendsTimerDuration))
    
    for (x,y,w,h) in faces_frontal:
        cv2.rectangle(frame, (x,y), (x+w,y+h), (255,0,0), 2)

    rawCapture.truncate(0)
    

# When everything done, release the capture
camera.stop_preview()
cap.release()
cv2.destroyAllWindows()
connection.close()