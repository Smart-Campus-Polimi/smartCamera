import time
import requests
import json
import os
import boto3
import datetime
from QueryManager import queryConstructor,fetchData,swapValue
import paho.mqtt.client as mqtt #import the client1
broker_address="10.79.5.210"
left=0
top=0
height=0
width=0 
def on_publish(mosq, obj, mid):
    print("mid: " + str(mid))
def DetectFrontEndFace(resp):
    storedArea=0
    for x in  resp['FaceDetails']:
        top=int(x["BoundingBox"]["Top"]*480)
        left=int(x["BoundingBox"]["Left"]*640)
        height=int(x["BoundingBox"]["Height"]*480)
        width=int(x["BoundingBox"]["Width"]*640)
        area=abs((left+width)*(top+height))
        if area>storedArea:
            storedArea=area
    return storedArea
def apiManager(client,imgobj,my_photo,timestamp,param):
    print(timestamp)
    boundingList=[]
   # client3 = mqtt.Client("m") #create new instance
    print("CONNESSIONE")
   # print("client 3 connect: ",client3.connect(broker_address))
    client2 = mqtt.Client("mdet") #create new instance
    print("client2 connect: ", client2.connect(broker_address)) #connect to broker
    client2.on_publish=on_publish
    #client3.on_publish=on_publish
    imgattrs=['ALL']
    start_firstAPI = time.time()
    timeAtomicReq=time.time()
    response = client.detect_faces(Image=imgobj,Attributes=imgattrs)
    deltaAtomicReq=time.time()-timeAtomicReq
    print("atomic Request Time: ",deltaAtomicReq)
    print (response)
    print ("APICall1: "+ str(time.time()-start_firstAPI))
    counter=0
    print('Detected labels for ' + my_photo)
    frontEndArea=DetectFrontEndFace(response)
    for bb in response['FaceDetails']:
        top=int(bb["BoundingBox"]["Top"]*480)
        left=int(bb["BoundingBox"]["Left"]*640)
        height=int(bb["BoundingBox"]["Height"]*480)
        width=int(bb["BoundingBox"]["Width"]*640)
        if (abs((left+width)*(top+height))==frontEndArea):
            if (param[:2]=="In"):
                 res=fetchData(bb,timestamp,"IN")
            else:
                res=fetchData(bb,timestamp,"OUT")
            print(res)
            queryConstructor(res)
            jobj={}
            jobj["Gender"]=bb["Gender"]["Value"]
            jobj["Age"]=res[2]
            jobj["Timestamp"] =timestamp
            print(bb["BoundingBox"]["Top"])
            
            boundingList.append((left,top,width,height))
            jsonData = json.dumps(jobj)
            client3 = mqtt.Client("m") #create new instance
            client3.connect(broker_address)
            print(client3.publish("sgc/peopleFeature",jsonData))#publis
            counter=counter +1
            print("counter:",counter)
    if counter > 0:
            #timestamp= datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        print('persone rilevate '+ str(counter))
        message="PRIMA API Client 2:I 0%d %s"%(counter,timestamp)
        print(message)
        jobj={}
        if (param[:2]=="In"):
                jobj["In"] = counter
                jobj["Out"] = 0
        else:
                jobj["In"]=0
                jobj["Out"]=counter
        jobj["Timestamp"] =timestamp
        jsonData = json.dumps(jobj)
        print (json.dumps(jobj,sort_keys=False,indent=3))
        client2 =mqtt.Client("mDet")
        client2.connect(broker_address)
        print(client2.publish("sgc/peopleDetection",jsonData,qos=1))#publis
        #call(["mosquitto_pub","-h","10.79.5.210","-t","smartgate/sg1/mlc/c","-m",jsonData])
        
    return counter,boundingList
