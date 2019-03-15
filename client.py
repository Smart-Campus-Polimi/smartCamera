from socket import *
import time
import pickle
import zlib
import struct
import cv2
import subprocess
import paramiko
import scp
import signal
import os
import sys

ssh_client=paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#cert=paramiko.RSAKey.from_private_key_file("UC15VM.pem")
ssh_client.connect(hostname='ec2-54-68-43-185.us-west-2.compute.amazonaws.com',username ='ubuntu',key_filename="/home/pi/Desktop/clientGate/UC15VM.pem")
#ssh_client.connect(hostname="54.68.43.185",key=cert)
deltaTime=time.time()
stream_path="/home/pi/Desktop/clientGate/Streamer.py"
streamOut_path="/home/pi/Desktop/clientGate/stream.py"
global stream
CSVFILE = '5G_TransferTime.txt'
def deleteMedia(mediaPath):
    if os.path.isfile(mediaPath):
       os.remove(mediaPath) 
def signal_handler(s,frame):
    global stream
    print(stream.pid)
    print("\nprogram exiting gracefully")
    try:
       os.killpg(stream.pid, signal.SIGINT)
    except Exception :
        pass
       #sys.exit(0)
    try:
        subprocess.check_output('killall python3', shell=True)
    except Exception:
        pass

    sys.exit(0)

signal.signal(signal.SIGINT,signal_handler)
def from_stream_to():
 #   print("ENTRO")
    active=1
    with open('/home/pi/Desktop/clientGate/indexFile','r') as f:
        c=[line.rstrip("\n") for line in f.readlines()]
        f.close()
        if(len(c)>0):
            print ("video ready to send: "+ str(c[0]))
            send_To_Server(c[0])
            
            with open('/home/pi/Desktop/clientGate/indexFile','w')as t:
                print(c[1:-1])
                for x in range(1,len(c)):
                    t.write(c[x])
                    t.write("\n")
                
#    print("FINE")

def send_To_Server(fileName):
    count=0
    videoPath="/home/pi/Desktop/VideoGallery/"+fileName+".avi"
    initTransf=time.time()
    print(videoPath)
    scpC=scp.SCPClient(ssh_client.get_transport())
    scpC.put(videoPath,"/home/ubuntu/smartgate_camera/VideoGallery")
   # deleteMedia(videoPath)
    deltaT=time.time()
    with open (CSVFILE,"a") as y:
         y.write(str(deltaT))
         y.write("\n")
         y.close()
    
def send_Env_To_Server(fileName):
    count=0
    videoPath="/home/pi/Desktop/"+fileName+".jpg"
    scpC=scp.SCPClient(ssh_client.get_transport())
    scpC.put(videoPath,"/home/ubuntu/smartgate_camera/VideoGallery")
    '''
fileIn="logfileIn"
fileOut="logfileOut"

streamOut=subprocess.Popen(['python3',streamOut_path],stdout=fileOut,stderr=fileOut)
'''
stream=subprocess.Popen(['python3',stream_path])
print(stream.pid)
time.sleep(30)
send_Env_To_Server("VideoGallery/In")
send_Env_To_Server("VideoGallery/Out")

while(True):
    if (time.time()-deltaTime>1):
            initTrans=time.time()
            deltaTime=time.time()
            from_stream_to()
            deltaVid=time.time()-initTrans
           # with open ("transferVideoTime","a") as i:
            #     i.write(str(deltaVid))
             #    i.write("\n")
             #    i.close()
            #print("time to send video: ", deltaVid)
scpC.close()
print("FINE TUTTO")

