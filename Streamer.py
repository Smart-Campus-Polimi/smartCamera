import serial
import sys
import signal
import RPi.GPIO as GPIO
import cv2
import os
import time
import subprocess
import datetime
import threading
import paho.mqtt.client as mqtt
import numpy as np
import VL53L0X
from socket import *
from SensorsEdge import readSensorData
from collections import deque
from imutils.video import VideoStream

CSVFILE = '5G_CreationFile.txt'

threads=[]
queueIN=[]
queueOUT=[]
read_serial=""

'''
instead of using a USB connection for communicating
with ToF sensors, we can use wi-fi communication.
I am going to comment all part useful for wi-fi communication
'''


#callback function used for fill the thread's queue


#callback function used for reconnect the client to the broker
def signal_handler(signal,frame):
    print("\nprogram exiting gracefully--STREAMER")
    queueOUT.append(0)
    queueIN.append(0)
    sys.exit(0)
signal.signal(signal.SIGINT,signal_handler)


class ThrMosq(threading.Thread):
    def __init__(self,queueIN,queueOUT):
        threading.Thread.__init__(self)
        self.qIn=queueIN
        self.qOut=queueOUT
        self.broker_address="34.244.160.143"
        self.TOPIC="sgc/detection"
		
    def on_message(self,client,userdata,message):
        print("on_message...")
        recvMsg=str(message.payload.decode('utf-8'))
        print("message received: ",recvMsg)
        if recvMsg=="IN":
            inTrace=subprocess.Popen(['omxplayer','-o','local','/home/pi/Desktop/clientGate/Gate_Sounds/entrance.mp3'])
            print("OKK")
            queueOUT.append(1)
    #    queueIN.append(1)
        elif recvMsg=="OUT":
            outTrace=subprocess.Popen(['omxplayer','-o','local','/home/pi/Desktop/clientGate/Gate_Sounds/exit.mp3'])
            queueIN.append(1)
       # queryOUT.append(1)
	   
    def on_connect(self,client,userdata,flags,rc):
        print("Connected with result code "+str(rc))
        if rc==0:
             print("connected OK")
             client.subscribe(self.TOPIC)
        else:
             print("Bad connection")
             client.loop_stop()
    
    def run (self):
	    
        client = mqtt.Client()
        client.on_connect =self.on_connect
        client.on_message = self.on_message
        
        client.connect(self.broker_address, 1883, 60)
        client.loop_forever()		
    
class ThrApp(threading.Thread):
    
    def __init__(self,streamHandler,name,queue):
        
        threading.Thread.__init__(self)
        self.sH=streamHandler
        self.name=name
        self.queue=queue
    def run (self):
        d=deque()
        #count=0
        TRIGGER_TIME=0
        VIDEO_SIZE=15
        t=False
        oneTime=False
        startRecording=3
        firstFrame=0
        videoNumb=0
        pathbase="/home/pi/Desktop/VideoGallery/"+self.name
        fourcc=cv2.VideoWriter_fourcc(*'XVID')
        encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),100]
        #self.sH.set(cv2.CAP_PROP_FPS,2)
        while self.sH.isOpened():
            #read the frame
            ret,frame = self.sH.read()
            '''
            if the frame read is the fist use this one
            for detecting the environmental noise
            '''
            if(firstFrame==0):
                print("capture the environ...")
                cv2.imwrite(pathbase+".jpg",frame,encode_param)
                firstFrame=1
                print("STREAM AVAILABLE")
            #append the new frame to the FRAME QUEUE that represents a "possible" video
            d.appendleft(frame)
            #if the sensors detect something, video creation phase is started
            if (len(self.queue)>0):
                TRIGGER_TIME=1
                initVideo=time.time()
                queueInstruction=self.queue.pop()
                if queueInstruction== 0:
                    self.sH.release()
            else:
                TRIGGER_TIME=0
            #each video is composed by VIDEO_SIZE frames    
            if (len(d)>VIDEO_SIZE):
                d.pop()
            '''
            this part is the trickiest one in the all script.
            we need to have two variable:
            i --> underline the exact moment when the video creation is
                  taken into charge:TRIGGER_TIME
            oneTime --> avoid the creation of multiple video about the
                        same passage
            '''
            if (TRIGGER_TIME==1 and oneTime==False):
                t=True
                oneTime=True
            elif(TRIGGER_TIME==0 and oneTime==True):
                oneTime=False

            '''
            each video is composed by two parts:
            first part: set of frames stored before the TRIGGER_TIME,
                        in general are 2/3 of VIDEO_SIZE
            second part: set of frames stored after the TRIGGER_TIME,
                        in general are 1/3 of VIDEO_SIZE
            when all the frames are stored, the video will be created
            '''
            if (startRecording==0 ):
                timestamp= datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')
                pathname=pathbase+timestamp
                out=cv2.VideoWriter(pathname+".avi",fourcc,4,(640,480))
                '''
                we write the frame into the video in reverse order,
                in this way the frames appear in chronological order.
                '''
               
                for x in reversed(d):
                   # print(x.shape)
                   # reversingImage=time.time()
                    rows,cols,color=x.shape
                    M=cv2.getRotationMatrix2D((cols/2,rows/2),90,1)
                    reverseImg=cv2.warpAffine(x,M,(cols,rows))
                    #reverseTime=time.time()-reversingImage
                    #print("time to reverse image: ", reverseTime)
                    k=out.write(reverseImg)
                out.release()
                print("time to create a video",time.time()-initVideo)
                '''
                add the name of the video into the list of video ready to send to the server
                '''
                with open('/home/pi/Desktop/clientGate/indexFile','a') as i:
                    print(pathname[30:])
                    i.write(pathname[30:])
                    i.write("\n")
                    i.close()
                
                videoNumb=videoNumb+1

                print("new sub video type: "+self.name+" are generated")
                #count=count+11
                deltaVideoCreate=time.time()-initVideo
                with open(CSVFILE, "a") as j:
                     j.write(str(deltaVideoCreate))
                     j.write("\n")
                     j.close()
                print("time spent to create the video: ",deltaVideoCreate)
                
                startRecording=3
                t=False
            if (t==True):
                startRecording=startRecording-1
 
def main():
    '''
    preparing phase:
    assign  usb port at each cameras.
    assign a usb port to the sensor
    create a thread per camera, passing the corrispondent queue. 
    '''
    
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
    '''
    ser = serial.Serial('/dev/ttyACM0', 19200, timeout = 1)
    while(True):
        line = str(ser.readline())

        if(len(line) > 2):
 
            if line[2] == '0':
                queueOUT.append(1)

            elif line[2] == '1':
                queueIN.append(1)
    '''
    threads.append(ThrMosq(queueIN,queueOUT).start())
    print("thread active: ", str(len(threads)))
    readSensorData(queueOUT,queueIN)
        

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
    sys.exit(0)
    queueOUT.append(0)
    queueIN.append(0)
