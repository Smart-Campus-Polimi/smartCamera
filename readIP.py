import subprocess
import paho.mqtt.client as mqtt #import the client1
broker_address="34.244.160.143"
def on_connect(client,userdata,flags,rc):
        print("Connected with result code "+str(rc))
        client.subscribe(TOPIC)
def on_publish(mosq, obj, mid):
    print("mid: " + str(mid))
p = subprocess.Popen(["iwconfig"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
#out,err = p.communicate()
text = p.communicate()[0]
client2 = mqtt.Client("mdet")
client2.connect(broker_address)
client2.on_publish=on_publish
print(client2.publish("sgc/ip",text))#publis
print(text)
s=subprocess.Popen(["ifconfig"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
second=s.communicate()[0]
print(second)
print(client2.publish("sgc/ip",second))
