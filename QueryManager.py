import MySQLdb
import json
import datetime
def queryConstructor(values):
    db = MySQLdb.connect("10.79.5.210","root","root","smartgateDB")
    cursor =db.cursor()
    sql="INSERT INTO feature (gender,ethnicity,age,smile,mustache,beard,eyeglasses,sunglasses,emotion,move_type,timestamp,API) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    cursor.execute(sql,values)
    db.commit()
    print(cursor.rowcount,"record inserted.")
    db.close()
    
def fetchData(jsonResponse,timestamp,move_type):
    sunglasses=swapValue(jsonResponse["Sunglasses"])
    print (sunglasses)
    eyeglasses=swapValue(jsonResponse["Eyeglasses"])
    print (eyeglasses)
    smile=swapValue(jsonResponse["Smile"])
    print (smile)
    mustache=swapValue(jsonResponse["Mustache"])
    print (mustache)
    beard =swapValue(jsonResponse["Beard"])
    print(beard)
    if jsonResponse["Gender"]["Value"]=="Female":
        gender= -jsonResponse["Gender"]["Confidence"]
    else:
        gender= jsonResponse["Gender"]["Confidence"]
    print(gender)
    age=(jsonResponse["AgeRange"]["Low"] + jsonResponse["AgeRange"]["High"])/2
    print(age)
    emotion=dominantEmotion(jsonResponse["Emotions"])
    print (emotion)
    datetime_object = datetime.datetime.strptime(timestamp,'%d-%m-%Y %H:%M:%S')
    #newStringTime=datetime_object.strftime('YYYY-MM-DD HH:MM:SS')
    val=(gender,"NONE",age,smile,mustache,beard,eyeglasses,sunglasses,emotion,move_type,datetime_object,"Rekognition")
    #print(json.dumps(jsonResponse,sort_keys=False,indent=3))
    return val

def swapValue(a):
    if a["Value"]==False:
        return -a["Confidence"]
    else:
        return a["Confidence"]
def dominantEmotion(jr):
    dominantE=0
    dominantV="none"
    print(jr)
    for e in jr:
        if e["Confidence"]>dominantE:
            dominantE=e["Confidence"]
            dominantV=e["Type"]
    if dominantE < 50:
        return "none"
    else:
        return dominantV
        
