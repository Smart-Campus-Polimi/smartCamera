from typing import Counter
from Plotter import plotTimeline
import matplotlib.pyplot as plt
import pymysql.cursors
import matplotlib.dates as mdates
import datetime
from PlotterGender import genderPie



API="Rekognition"
StringSQL="SELECT `*` FROM `feature` WHERE `API`='"+API+"' AND`timestamp` BETWEEN '2019-01-31 15:23:22' AND '2019-01-31 17:38:00'"
connection = pymysql.connect(host="10.79.5.210",
                             user='root',
                             password='root',
                             db="smartgateDB",
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
dictMoveR=[]
dictTimeR=[]
countM=0
countF=0
try:
    with connection.cursor() as cursor:
        # Read a single record
        sql = StringSQL
        cursor.execute(sql,)
        result = cursor.fetchall()
        for x in result:
            if x['move_type']=="IN":
                if x['gender'] > 0:
                    countM+=1
                else:
                    countF+=1
                dictMoveR.append(1)
                dictTimeR.append(x['timestamp'])
            else:
                if x['gender'] > 0:
                    countM+=1
                else:
                    countF+=1
                dictMoveR.append(-1)
                dictTimeR.append(x['timestamp'])
            #print(x['move_type'])
            #print(x['timestamp'])
        dater = [datetime.datetime.strftime(ii, "%H:%M:%S") for ii in dictTimeR]


finally:
    connection.close()

plotTimeline(dictMoveR,dictTimeR,API)
genderPie(countM,countF,API)