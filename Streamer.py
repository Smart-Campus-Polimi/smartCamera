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
import boto3 
import io
import multiprocessing as mp

CSVFILE = '5G_CreationFile.txt'
VIDEO_SIZE=15
FRAME_AFTER = 3

threads=[]
queueIN=[]
queueOUT=[]
read_serial=""

'''
instead of using a USB connection for communicating
with ToF sensors, we can use wi-fi communication.
I am going to comment all part useful for wi-fi communication
'''

session = boto3.Session(profile_name='default')
rekognition = session.client('rekognition', 'eu-west-1')
agender = PyAgender()

#callback function used for reconnect the client to the broker
def signal_handler(signal,frame):
    print("\nprogram exiting gracefully--STREAMER")
    queueOUT.append(0)
    queueIN.append(0)
    sys.exit(0)
signal.signal(signal.SIGINT,signal_handler)


def reko_worker(frame):
    rtt = time.time()
    _, buff = cv2.imencode('.jpg', frame)
    byte_img = io.BytesIO(buff).getvalue()
    response = rekognition.detect_faces(Image= {'Bytes': byte_img}, Attributes=['ALL'])
    print("Request time: ", time.time()-rtt)
    
    return response  

def local_worker(frame):
    rtt = time.time()
    _, buff = cv2.imencode('.jpg', frame)
    byte_img = io.BytesIO(buff).getvalue()
    response = agender.detect_genders_ages(byte_img)    
    print("Request time: ", time.time()-rtt)
    
    return response
    
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
            queueIN.append(1)
        elif recvMsg=="OUT":
            outTrace=subprocess.Popen(['omxplayer','-o','local','/home/pi/Desktop/clientGate/Gate_Sounds/exit.mp3'])
            queueOUT.append(1)
   
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
    def __init__(self, streamHandler ,name, queue):
        threading.Thread.__init__(self)
        self.camera = streamHandler
        self.name = name
        self.queue = queue
    
    def run (self):
        frames_queue = deque()

        event_present = False
        t = False
        first_time = False
        startRecording = FRAME_AFTER
        firstFrame = True
        '''
        pathbase = "/home/pi/Desktop/VideoGallery/"+self.name
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),100]
        '''
        while self.camera.isOpened():
            ret, frame = self.camera.read()
            '''
            if the frame read is the fist use this one
            for detecting the environmental noise
            
            if firstFrame:
                print("capture the environ...")
                cv2.imwrite(pathbase+".jpg",frame,encode_param)
                firstFrame = False
                print("STREAM AVAILABLE")
            ''' 
            #append the new frame to the FRAME QUEUE that represents a "possible" video
            frames_queue.append(frame)
            
            #each video is composed by VIDEO_SIZE frames    
            if len(frames_queue) > VIDEO_SIZE:
                frames_queue.pop()
            
            #if the sensors detect something, video creation phase is started
            if len(self.queue)>0:
                event_present = True
                initVideo=time.time()
                queueInstruction = self.queue.pop()
                if queueInstruction == 0:
                    self.camera.release()
            else:
                 event_present = False
                         
            '''
            this part is the trickiest one in the all script.
            we need to have two variable:
            event_present --> underline the exact moment when the video creation is
                  taken into charge:TRIGGER_TIME
            first_time --> avoid the creation of multiple video about the
                        same passage
            '''
            if event_present and not first_time:
                t=True
                first_time = True
            elif not event_present:
                first_time = False

            '''
            each video is composed by two parts:
            first part: set of frames stored before the TRIGGER_TIME,
                        in general are 2/3 of VIDEO_SIZE
            second part: set of frames stored after the TRIGGER_TIME,
                        in general are 1/3 of VIDEO_SIZE
            when all the frames are stored, the video will be created
            '''
            if startRecording == 0:
                timestamp = datetime.datetime.now().strftime('%d-%m-%Y_%H:%M:%S')
                '''
                pathname = pathbase + timestamp
                out = cv2.VideoWriter(pathname+".avi",fourcc,4,(640,480))
                '''
                '''
                we write the frame into the video in reverse order,
                in this way the frames appear in chronological order.
                '''
 
                time_request = time.time()                    
                with mp.Pool(processes=len(frames_queue)) as pool:
                    output = pool.map(reko_worker, list(frames_queue))

                print("Total time to process: ", time.time() - time_request)
                
                print("number of results: ", len(output))
                for res in output:
                    print(res['FaceDetails'])
                
                startRecording = FRAME_AFTER
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
    
    
    j=0
    camera1_index = 0
    isReading = False

    while not isReading:
        if camera1_index>0:
            camera1.release()
        camera1=cv2.VideoCapture(camera1_index)
        camera1.set(cv2.CAP_PROP_FPS,2)
        isReading, frame = camera1.read()
        print("Open camera 1? ", isReading)
        camera1_index += 1
            
    print("index of camera 1",str(camera1_index))
    
    isReading = False
    time.sleep(5)
    
    #camera 2
    print("preparing capture 2...")
    
    camera2_index = camera1_index + 1
    while not isReading:
        if camera2_index > camera1_index+1:
            camera2.release()
        camera2=cv2.VideoCapture(camera2_index)
        camera2.set(cv2.CAP_PROP_FPS,2)
        isReading, frame = camera2.read()
        print("Open camera 2? ", isReading)
        camera2_index += 1

    print("index of camera 2",str(camera2_index))
    
    
    #Creating Threads
    threads.append(ThrApp(camera1, "In", queueIN).start())
    threads.append(ThrApp(camera2, "Out", queueOUT).start())
    
    threads.append(ThrMosq(queueIN,queueOUT).start())
    
    print("thread active: ", str(len(threads)))
    if len(threads) < 3:
        print("ERROR THREADS", len(threads))
        
    readSensorData(queueOUT, queueIN)
        

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
