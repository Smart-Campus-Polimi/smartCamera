import RPi.GPIO as GPIO
import time
import VL53L0X


# GPIO for Sensor 1 shutdown pin
sensor1_shutdown = 20
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
timing = tof.get_timing()

def edgeFinder(pair_side_0,pair_side_1,prevEdge):
    side_0_count=0
    side_1_count=0
    count=0
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
                prevEdge="Lock"
                
        elif(prevEdge=="None"):
                prevEdge="SIDE 0"
                
        else:
                print("Still Side 0 edge")
    if (side_1_count==2):
        print("SIDE 0 COUNT OK")
        if (prevEdge=="SIDE 0"):
                print("ENTRANCE")
                prevEdge="Lock"
        elif(prevEdge=="None"):
                prevEdge="SIDE 1"
        else:
                print("Still Side 1 edge")
    return prevEdge
    
def readSensorData ():
        
       
        pair_side_0=[LASER_RANGE,LASER_RANGE]
        pair_side_1=[LASER_RANGE,LASER_RANGE]
  
        precTime=time.time()
        init=time.time()
        prevEdge="None"
        try:
            while (time.time()-init)<30:
                        
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
                if (distance_side_1 > 1100):
                    distance_side_1=LASER_RANGE
                #print("pair side 0: ",pair_side_0)
                #print("pair side 1: ",pair_side_1)
                prevEdge=edgeFinder(pair_side_0,pair_side_1,prevEdge)
                #print("main prevEdge: ",prevEdge)
        except KeyboardInterrupt:
                print('interrupted!')
readSensorData()
   