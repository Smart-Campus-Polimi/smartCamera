import RPi.GPIO as GPIO
import time
import os
import VL53L0X
import signal,sys
import subprocess
from threading import Timer
# GPIO for Sensor 1 shutdown pin
sensor1_shutdown = 5
# GPIO for Sensor 2 shutdown pin
sensor2_shutdown = 16

GPIO.setwarnings(False)

# Setup GPIO for shutdown pins on each VL53L0X
GPIO.setmode(GPIO.BCM)
GPIO.setup(sensor1_shutdown, GPIO.OUT)
GPIO.setup(sensor2_shutdown, GPIO.OUT)

# Set all shutdown pins low to turn off each VL53L0X
GPIO.output(sensor1_shutdown, GPIO.LOW)
GPIO.output(sensor2_shutdown, GPIO.LOW)

# Keep all low for 500 ms or so to make sure they reset
time.sleep(0.50)

# Create one object per VL53L0X passing the address to give to
# each.
tof = VL53L0X.VL53L0X(address=0x2B)
tof1 = VL53L0X.VL53L0X(address=0x2D)

# Set shutdown pin high for the first VL53L0X then 
# call to start ranging 
GPIO.output(sensor1_shutdown, GPIO.HIGH)
time.sleep(0.50)
tof.start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)

# Set shutdown pin high for the second VL53L0X then 
# call to start ranging 
GPIO.output(sensor2_shutdown, GPIO.HIGH)
time.sleep(0.50)
tof1.start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)
global LASER_RANGE
LASER_RANGE=8190
global prevEdge
prevEdge="None"
#def stayInFront():
 #   print("IN FRONT")
 #   global prevEdge
 #   print(prevEdge)
 #   if (prevEdge=="SIDE 0") or (prevEdge=="SIDE 1"):
 #        subprocess.Popen(['omxplayer','-o','local','/home/pi/Desktop/clientGate/Gate_Sounds/official.mp3'])
def timerAudio():
    audioTime=subprocess.Popen(['omxplayer','-o','local','--vol','-4000','/home/pi/Desktop/clientGate/Gate_Sounds/entrance.mp3'])
    Timer(180,timerAudio).start()
def fedResetTimer():
    global prevEdge
    prevEdge="None"
    print("RESET PREV_EDGE")
global resetTimer
resetTimer=Timer(4,fedResetTimer)
timerTrace=Timer(180,timerAudio)
#global stayTrace
#stayTrace=Timer(6,stayInFront)
timing = tof.get_timing()
def signal_handler(signal,frame):
    print("\nprogram exiting gracefully--SENSORS")
    sys.exit(0)
signal.signal(signal.SIGINT,signal_handler)



def edgeFinder(pair_side_0,pair_side_1,queueOUT,queueIN):
    side_0_count=0
    global prevEdge
    global resetTimer
    side_1_count=0
    count=0
    global stayTrace
    AUDIOPATH="/home/pi/Desktop/clientGate/Gate_Sounds/"    
    #print("prevEdge: ",prevEdge)
    for x in range(0,len (pair_side_0)):
        
        if (pair_side_0[x]<(LASER_RANGE-1) and pair_side_1[x]>(LASER_RANGE-1)):
            side_0_count+=1
            #print("EDGE STARTED TO SIDE 0")
            
        elif (pair_side_1[x]<(LASER_RANGE-1) and pair_side_0[x]>(LASER_RANGE-1)):
            side_1_count+=1
            #print("EDGE STARTED TO SIDE 1")
        elif (pair_side_1[x]>(LASER_RANGE-1) and pair_side_0[x]>(LASER_RANGE-1)):
            if (prevEdge=="Lock"):
                prevEdge="None"
                print("unlock the sensors-looking for a new passage")
            
    if (side_0_count==2):
        #print("SIDE 0 COUNT OK")
        if (prevEdge=="SIDE 1"):
                print("EXIT")
                queueIN.append(1)
                #print("current audio trace", audioList[0])
                audiotrace="exit.mp3"
                audioExit=subprocess.Popen(['omxplayer','-o','local',AUDIOPATH+audiotrace])
                #audioList.append(audiotrace)
                prevEdge="Lock"
                resetTimer.cancel()
                resetTimer=Timer(6,fedResetTimer)
                resetTimer.start()
#                stayTrace.cancel()
#                stayTrace=Timer(3,stayInFront)
#                stayTrace.start()
                
        elif(prevEdge=="None"):
                prevEdge="SIDE 0"
                resetTimer.cancel()
                resetTimer=Timer(6,fedResetTimer)
                resetTimer.start()
#                stayTrace.cancel()
#                stayTrace=Timer(3,stayInFront)
#                stayTrace.start()
        #else:
               # print("Still Side 0 edge")
    if (side_1_count==2):
        #print("SIDE 0 COUNT OK")
        if (prevEdge=="SIDE 0"):
                print("ENTRANCE")
                queueOUT.append(1)
                #print("current audio trace", audioList[0])
                audiotrace="entrance.mp3"
                audioEntrance=subprocess.Popen(['omxplayer','-o','local',AUDIOPATH+audiotrace])
                #audioList.append(audiotrace)
                prevEdge="Lock"
                resetTimer.cancel()
                resetTimer=Timer(6,fedResetTimer)
                resetTimer.start()
#                stayTrace.cancel()
#                stayTrace=Timer(3,stayInFront)
#                stayTrace.start()
        elif(prevEdge=="None"):
                prevEdge="SIDE 1"
                resetTimer.cancel()
                resetTimer=Timer(6,fedResetTimer)
                resetTimer.start()
#                stayTrace.cancel()
#                stayTrace=Timer(3,stayInFront)
#                stayTrace.start()
        #else:
               # print("Still Side 1 edge")
    
    
def readSensorData (queueOUT,queueIN):
        
        file=open("/home/pi/Desktop/clientGate/processID.txt",'w')
        file.write(str(os.getpid()))
        file.close()        
        pair_side_0=[LASER_RANGE,LASER_RANGE]
        pair_side_1=[LASER_RANGE,LASER_RANGE]
        audioList=[]
        #with open("/home/pi/Desktop/clientGate/audioList.txt",'r') as a:
         #     for line in a:
          #          line=line.strip('\n')
           #         audioList.append(line)
        #print(audioList)  
        precTime=time.time()
        init=time.time()
        #prevEdge="None"
        resetTimer.start()
        timerTrace.start()
#        stayTrace.start()
        try:
            while True:
                        
                #print("delta: ",time.time()-precTime)
                precTime=time.time()
			#print("remain time: ", (time.time()-init))
                distance_side_0 = tof.get_distance()
                pair_side_0[1]=pair_side_0[0]
                pair_side_0[0]=distance_side_0
                                        #print("side_0: ",distance_side_0)
                distance_side_1 = tof1.get_distance()
                pair_side_1[1]=pair_side_1[0]
                pair_side_1[0]=distance_side_1
                if (pair_side_0[0] == 0):
                    pair_side_0[0]= pair_side_0[1]
                if (pair_side_1[0] == 0):
                    pair_side_1[0]= pair_side_1[1]
                if (distance_side_0 > 1100):
                    distance_side_0=LASER_RANGE
				#print ("sensor %d - %d mm, %d cm, iteration %d" % (tof.my_object_number, distance, (distance/10), count))
                if (distance_side_1 >1100):
                    distance_side_1=LASER_RANGE
#                print("pair side 0: ",pair_side_0)
#                print("pair side 1: ",pair_side_1)
                edgeFinder(pair_side_0,pair_side_1,queueOUT,queueIN)
                #print("main prevEdge: ",prevEdge)
        except KeyboardInterrupt:
                print('interrupted!')

   
#readSensorData([],[])
