import serial
import sys
import signal
import RPi.GPIO as GPIO
import cv2
import os
import time
import datetime
import threading
import paho.mqtt.client as mqtt
import numpy as np
from socket import *

from collections import deque
from imutils.video import VideoStream


threads=[]
queueIN=[]
queueOUT=[]
read_serial=""

fronteIn=0
fronteOut=0
broker_address="54.68.43.185"
TOPIC="smartgate/sg1/debug"

def on_message(client,userdata,message):
    print("on_message...")
    recvMsg=str(message.payload.decode('utf-8'))
    print("message received: ",recvMsg[2:])
    if recvMsg[2:]=="Entry":
        queueOUT.append(1)
    #    queueIN.append(1)
    elif recvMsg[2:]=="Exit":
        queueIN.append(1)
       # queryOUT.append(1)

def on_connect(client,userdata,flags,rc):
    print("Connected with result code "+str(rc))
    client.subscribe(TOPIC)
    
class ThrApp(threading.Thread):
    
    def __init__(self,streamHandler,name,queue):
        
        threading.Thread.__init__(self)
        self.sH=streamHandler
        self.name=name
        self.queue=queue
    def run (self):
        d=deque()
        count=0
        i=0
        t=False
        oneTime=False
        startRecording=3
        firstFrame=0
        videoNumb=0
        pathbase="VideoGallery/"+self.name
        fourcc=cv2.VideoWriter_fourcc(*'XVID')
        encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),100]
        #self.sH.set(cv2.CAP_PROP_FPS,2)
        while self.sH.isOpened():
            
            ret,frame = self.sH.read()
            
            if(firstFrame==0):
                print("capture the environ...")
                cv2.imwrite(pathbase+".jpg",frame,encode_param)
                firstFrame=1
                print("STREAM AVAILABLE")
            d.appendleft(frame)
            if (len(self.queue)>0):
                i=1
                initVideo=time.time()
                queueInstruction=self.queue.pop()
                if queueInstruction== 0:
                    self.sH.release()
            else:
                i=0
            if (len(d)>12):
                d.pop()
                
            if (i==1 and oneTime==False):
                t=True
                oneTime=True
            elif(i==0 and oneTime==True):
                oneTime=False
            #print("startRec: "+str(startRecording))
            if (startRecording==0 ):
                timestamp= datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')
                pathname=pathbase+timestamp
                out=cv2.VideoWriter(pathname+".avi",fourcc,4,(640,480))
                for x in reversed(d):
                    #print("popping: "+ str(f.pop()))
                    #print("status: "+ f)
                    k=out.write(x)
                out.release()
                print("time to create a video",time.time()-initVideo)
                with open('indexFile','a') as i:
                    i.write(pathname[13:])
                    i.write("\n")
                    i.close()
                
                videoNumb=videoNumb+1
               # print("d size: ", str(len(d)))
               # d.clear()
               # print("d after size: ", str(len(d)))
                print("new sub video type: "+self.name+" are generated")
                count=count+11
                deltaVideoCreate=time.time()-initVideo
                print("time spent to create the video: ",deltaVideoCreate)
                
                startRecording=3
                t=False
            if (t==True):
                startRecording=startRecording-1
            
                    #cv2.imwrite(self.name+str(count)+".png",frame)
                    #count+=1
def main():
    cap=cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FPS,2)
    ret,frame=cap.read()
    print(ret)
    i=0
    j=0
    while ret==False:
        i+=1
        cap.release()
        cap=cv2.VideoCapture(i)
        ret,frame=cap.read()
    print("index of camera",str(i))
    threads.append(ThrApp(cap,"In",queueIN).start())
    print("preparing capture 2...")
    print("thread active: ", str(len(threads)))
    time.sleep(5)
    #cap2=cv2.VideoCapture("/dev/v4l/by-id/usb-046d_0825_E0B1C560-video-index0")
    cap2=cv2.VideoCapture(1)
    cap2.set(cv2.CAP_PROP_FPS,1)
    ret2,frame2=cap2.read()
    print(ret2)
    while ret2==False:
        j+=1
        cap2.release()
        cap2=cv2.VideoCapture(j)
        ret2,frame2=cap2.read()
    print("index of camera",str(j))
    print("cap2 ready")
    threads.append(ThrApp(cap2,"Out",queueOUT).start())
    print("thread active: ", str(len(threads)))
    #client=mqtt.Client("P1")
    #client.on_message=on_message
    #client.on_connect=on_connect
    #client.connect(broker_address)
    #client.subscribe(TOPIC)
    #client.loop_forever()
    ser = serial.Serial('/dev/ttyACM0', 19200, timeout = 1)
    while(True):
        line = str(ser.readline())
        
        #print(line)
        if(len(line) > 2):
            #print(line[2])
            if line[2] == '0':
                queueOUT.append(1)
                #queueIN.append(1)
            elif line[2] == '1':
                queueIN.append(1)
                #queryOUT.append(1)
if __name__=="__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            queueOUT.append(0)
            queueIN.append(0)
            sys.exit(0)
        except SystemExit:
            os._exit(0)
