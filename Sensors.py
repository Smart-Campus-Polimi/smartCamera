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

timing = tof.get_timing()
'''
flag_0=False
flag_1=False
new_ts_0=0
new_ts_1=0
'''
def readSensorData (queueOut,queueIn):
	MIN_MOVEMENT=0.4
	flag_0=False
	flag_1=False
	new_ts_0=0
	new_ts_1=0
	init=time.time()
	precTime=time.time()
	try:
		while (time.time()-init)<30:
                        
                        print("delta: ",time.time()-precTime)
                        precTime=time.time()
			#print("remain time: ", (time.time()-init))
                        distance_side_0 = tof.get_distance()
                        #print("side_0: ",distance_side_0)
                        distance_side_1 = tof1.get_distance()
                        
                        if (distance_side_0 > 1100):
                                distance_side_0=8190
				#print ("sensor %d - %d mm, %d cm, iteration %d" % (tof.my_object_number, distance, (distance/10), count))
                        if (distance_side_1 > 1100):
                                distance_side_1=8190
				#print ("%d - Error" % tof.my_object_number)
                        print("side_0: ",distance_side_0)
                        print("side_1: ",distance_side_1)
                        if (distance_side_0 < 8000 and flag_0==False):
				#print("first enter")
                                new_ts_0=time.time()
                                flag_0=True
                        if (distance_side_1 < 8000 and flag_1 ==False):
				#print("second enter")
                                new_ts_1=time.time()
                                flag_1=True
				#print ("sensor %d - %d mm, %d cm, iteration %d" % (tof1.my_object_number, distance, (distance/10), count))
                        
                        if (flag_0==True and flag_1==True):
				#print("third enter")
                                if (new_ts_0 > new_ts_1):
                                        flag_0= False
                                        flag_1=False
                                        print("Entrata")
                                        
                                        queueIn.append(1)
                                        time.sleep(0.25)
                                elif (new_ts_0< new_ts_1):
                                        flag_0= False
                                        flag_1= False
					
                                        print("Uscita")
                                        queueOut.append(1)
                                        time.sleep(0.25)
                        if (time.time()-MIN_MOVEMENT> new_ts_0 and distance_side_0> 8000):
                                        flag_0= False	
                        if (time.time()-MIN_MOVEMENT> new_ts_1 and distance_side_1> 8000):
                                        flag_1= False
	except KeyboardInterrupt:
		print('interrupted!')

