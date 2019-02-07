import json
from typing import Counter
from Plotter import plotTimeline
from PlotterGender import genderPie
import datetime
FILEPATHBASE=r"C:\Users\Marco Wenzel\Desktop\VG\GroundTruth_"
FILEPATH=FILEPATHBASE+"31_01_2019_15_23_22"
f=open(FILEPATH+".txt", "r")
dictMoveR=[]
dictTimeR=[]
countM=0
countF=0
for line in f:
    print(line)
    x=json.loads(line)
    print (x)
    if x['ACTION'] == "IN":
        if x['Gender']=="M":
            countM += 1
        else:
            countF += 1
        dictMoveR.append(1)
        c=datetime.datetime.strptime(x['TimeStamp'],'%d-%m-%Y, %H:%M:%S')
        dictTimeR.append(c)
    else:
        if x['Gender']=="M":
            countM += 1
        else:
            countF += 1
        dictMoveR.append(-1)
        c = datetime.datetime.strptime(x['TimeStamp'], '%d-%m-%Y, %H:%M:%S')
        dictTimeR.append(c)
    print(x['ACTION'])
    print(x['TimeStamp'])

plotTimeline(dictMoveR,dictTimeR,"GT")
genderPie(countM,countF,"GT")

