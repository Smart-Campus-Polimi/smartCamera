from typing import Counter
from Plotter import plotTimeline
import matplotlib.pyplot as plt
import pymysql.cursors
import matplotlib.dates as mdates
import datetime
import json
import math
import time
from PlotterGender import genderPie
FILEPATHBASE=r"C:\Users\Marco Wenzel\Desktop\VG\GroundTruth_"
FILEPATH=FILEPATHBASE+"31_01_2019_15_23_22"
API="Rekognition"
def loadFileGt ():
    f = open(FILEPATH + ".txt", "r")
    dictMoveGT = []
    dictTimeGT = []
    countM = 0
    countF = 0
    for line in f:
        #print(line)
        x = json.loads(line)
        if x['ACTION'] == "IN":
            if x['Gender'] == "M":
                countM += 1
            else:
                countF += 1
            dictMoveGT.append(1)
            c = datetime.datetime.strptime(x['TimeStamp'], '%d-%m-%Y, %H:%M:%S')
            dictTimeGT.append(c)
        else:
            if x['Gender'] == "M":
                countM += 1
            else:
                countF += 1
            dictMoveGT.append(-1)
            c = datetime.datetime.strptime(x['TimeStamp'], '%d-%m-%Y, %H:%M:%S')
            dictTimeGT.append(c)
    #dater = [datetime.datetime.strftime(ii, "%H:%M:%S") for ii in dictTimeGT]
    a = zip(dictMoveGT, dictTimeGT)

    return a
previusTime=time.strftime('%X')

print(previusTime)
#actualTime=time.strftime('%X')
while(True):
    actualTime = time.strftime('%X')
    previusDate = datetime.datetime.strptime(previusTime, "%X")
    actualDate=datetime.datetime.strptime(actualTime, "%X")
    if ((actualDate-previusDate).seconds>30):
        print(actualTime)
        StringSQL="SELECT `*` FROM `feature` WHERE `API`='"+API+"' AND`timestamp` BETWEEN '2019-01-31 15:23:22' AND '2019-01-31 17:38:00'"
        previusTime=actualTime
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
                #dater = [datetime.datetime.strftime(ii, "%H:%M:%S") for ii in dictTimeR]
                apiZip = zip(dictMoveR, dictTimeR)
                apiList=list(apiZip)
                gtZip=loadFileGt()
                gtList = list(gtZip)
                print("len api:",str(len(apiList)))
                apiLen=len(apiList)
                print("len gt:",str(len(gtList)))
                gtLen=len(gtList)
                falseNegativeList=[]
                falseNegativeDateList=[]
                falsePositiveList = []
                falsePositiveDateList = []
                count=0
                for api, gt in zip(apiList, gtList):
                    print("iteration number: ",str(count))
                    print(api,gt)
                    if (api[0]!=0):
                        apiDate=api[1]
                        gtDate=gt[1]
                        delta=(gtDate-apiDate).total_seconds()

                        #print("diffenrent:",delta)
                        if (abs(delta)>5):
                            if (apiDate<gtDate):
                                falsePositiveList.append(api[0])
                                falsePositiveDateList.append(api[1])
                                apiList.pop(apiList.index(api))
                            else:
                                #print("position element",str(apiList.index(api)))
                                apiList.insert(apiList.index(api), (0, None))
                                falseNegativeList.append(gt[0])
                                falseNegativeDateList.append(gt[1])
                                #print(api, gt)
                                print("index of this element in gtList:",str(gtList.index(gt)))
                                #print(len(apiList))
                    count+=1

                print(str(len(apiList)))
                print(str(len(gtList)))
                #for api, gt in zip(apiList, gtList):
                    #print(api,gt)
        finally:
            connection.close()
        if (len(falseNegativeDateList)==0 or len(falseNegativeList)==0):
            print("NO FALSE NEGATIVE!!")
        else:
            plotTimeline(falseNegativeList,falseNegativeDateList,"False Negative "+API)
        if (len(falsePositiveList)==0 or len(falsePositiveDateList)==0):
            print("NO FALSE POSITIVE!!")
        else:
            plotTimeline(falsePositiveList,falsePositiveDateList,"False Positive "+API)

        mse= float((apiLen-gtLen-len(falsePositiveList))*(apiLen-gtLen-len(falsePositiveList))/gtLen)
        rmse=math.sqrt(mse)
        print("MSE: ",mse)
        print("RMSE: ",rmse)
        text_file = open(FILEPATHBASE+" Performance.txt", "w")

        text_file.write("MSE: "+ str(mse) + " \n")
        text_file.write("RMSE: "+ str(rmse) + " \n")
        text_file.write("Perfomance: "+ str(((apiLen-len(falsePositiveList))/gtLen)*100)+"%" + " \n")
        text_file.close()
