from picamera import PiCamera
import numpy as np
import datetime
import cv2
import time
import base64
from picamera.array import PiRGBArray
import pika
import sys
import base64
import socket

import threading

class ServicesManager:

    credentials = pika.PlainCredentials('admin', 'admin')
    connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.100.29', 5672, '/', credentials))
    channel = connection.channel()

    # initialize the camera and grab a reference to the raw camera capture
    camera = PiCamera()
    camera.resolution = [640, 480]
    camera.framerate = 16
    rawCapture = PiRGBArray(camera, size=[640, 480])
     
    frontal_face_cascade = cv2.CascadeClassifier('/home/pi/scripts/haarcascade_frontalface_alt.xml')
    fullbody_cascade = cv2.CascadeClassifier('/home/pi/scripts/haarcascade_fullbody.xml')

    hasStabilityTimerAlreadyStarted = False
    stabilityStartTime = None
    stabilityEndTime = None

    hasBetweenSendsTimeTimerAlreadyStarted = False
    betweenSendsStartTime = None
    betweenSendsEndTime = None
    betweenSendsTimerDuration = None


    currentFrame = None

    startLiveStream = False
    liveStreamQuality = 40

    def startServices(self):
        print("[INFO] warming up...")
        time.sleep(5)

        TCP_IP = "192.168.100.10"

        TCP_PORT = 8000

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((TCP_IP, TCP_PORT))
        try:
            threading.Thread(target=self.sendFrameThroughSocket, name="Thread1", daemon=True ).start()
            threading.Thread(target=self.detectFace, name="Thread2", daemon= True).start()
        except Exception as e:
            print ("Error: unable to start thread" + str(e))

        # capture frames from the camera
        for f in self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True):
            # grab the raw NumPy array representing the image and initialize
            # the timestamp and occupied/unoccupied text
            #frame = f.array
            self.currentFrame = f.array

            self.rawCapture.truncate(0)
        
        # When everything done, release the capture
        self.sock.close()
        cv2.destroyAllWindows()
        self.connection.close()

    def sendFrameThroughSocket(self):
        while True:
            
            if self.startLiveStream == False:
                print("Live stream is off, sleeping for 1 sec...")
                time.sleep(1)
                continue
            
            if self.currentFrame is None:
                continue


            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), self.liveStreamQuality]

            retval, buffer = cv2.imencode('.jpg', self.currentFrame, encode_param)
            
            jpg_as_text = base64.b64encode(buffer)
            
            self.sock.sendall(jpg_as_text)
            self.sock.sendall('*'.encode())

    def detectFace(self):
    
        while True:
            frame = self.currentFrame

            if frame is None:
                 continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)

            faces_frontal = self.frontal_face_cascade.detectMultiScale(gray)
            #full_bodies = self.fullbody_cascade.detectMultiScale(gray, 1.5, 1)

            if (len(faces_frontal) != 0):
                if not self.hasStabilityTimerAlreadyStarted:
                    self.stabilityStartTime = time.time()
                    self.hasStabilityTimerAlreadyStarted = True
                    print ("detectez fata")
            else:
                print("not!!!!!!!!!")
                self.hasStabilityTimerAlreadyStarted = False
            
            if self.stabilityStartTime:
                if self.hasStabilityTimerAlreadyStarted:
                    self.stabilityEndTime = time.time()
                    self.stabilityDuration = self.stabilityEndTime - self.stabilityStartTime
                    #print(duration)
                    if self.stabilityDuration > 1:
                        print("a trecut 1 sec de stabilitate")

                        if not self.hasBetweenSendsTimeTimerAlreadyStarted or (self.hasBetweenSendsTimeTimerAlreadyStarted and self.betweenSendsTimerDuration >= 1): 
                            print("trimit poza...")

                            retval, buffer = cv2.imencode('.jpg', frame)
                            jpg_as_text = base64.b64encode(buffer)
                            
                            #print(jpg_as_text)

                            self.channel.basic_publish(exchange='poze', routing_key='poze', body=jpg_as_text)

                            self.hasBetweenSendsTimeTimerAlreadyStarted = False
                            self.betweenSendsTimerDuration = 0
                        
                        if not self.hasBetweenSendsTimeTimerAlreadyStarted:
                            self.hasBetweenSendsTimeTimerAlreadyStarted = True
                            self.betweenSendsStartTime = time.time()

                        self.hasStabilityTimerAlreadyStarted = False

            if self.betweenSendsStartTime:
                self.betweenSendsEndTime = time.time()
                self.betweenSendsTimerDuration = self.betweenSendsEndTime - self.betweenSendsStartTime
                print("betweenSendsTimerDuration = "+str(self.betweenSendsTimerDuration))
            
            for (x,y,w,h) in faces_frontal:
                cv2.rectangle(frame, (x,y), (x+w,y+h), (255,0,0), 2)

            #for (x,y,w,h) in full_bodies:
                #cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
            
            cv2.imshow("frame", frame)

            k = cv2.waitKey(1) & 0xff
            if k == 27: # press 'ESC' to quit^M
                self.currentFrame = None
                break
