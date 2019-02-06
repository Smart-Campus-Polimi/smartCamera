import numpy as np
import cv2
import time
import sys
import boto3
import datetime
import re
import os
from ApiManager import apiManager
#(optional)if we want to compare Amazon Rekognition API with Face++ API
#from ApiFaceManager import sendReq
global match

def deleteMedia(mediaPath):
    if os.path.isfile(mediaPath):
       os.remove(mediaPath)    
def detect_faces(match,f_cascade, colored_img,forbiddenCord,noise, scaleFactor = 1.010):
    relif=0
    match=0
    noise=0
    img_copy = np.copy(colored_img)
    #convert the test image to gray image as opencv face detector expects gray images
    gray = cv2.cvtColor(img_copy, cv2.COLOR_BGR2GRAY)
    
    #let's detect multiscale (some images may be closer to camera than others) images
    faces = f_cascade.detectMultiScale(gray, scaleFactor=scaleFactor, minNeighbors=5);
    
    #go over list of faces and draw them as rectangles on original colored img
    for (x, y, w, h) in faces:
        if ((w*h)>20000):
                cv2.rectangle(img_copy, (x, y), (x+w, y+h), (0, 255, 0), 2)
                relif=relif+1
                match+=1
                for cc in forbiddenCord:
                        #print(cc)
                        #print("first element",str(cc[0]))
                        if (abs(cc[0]-x))==0 and (abs(cc[1]-y))==0:
                                 print("NOISE DETECTED")
                       	         match-=1
                                 noise=1								 
   # print("number of faces: "+ str(relif))
   # print("match semi: "+str(match))
    return match,img_copy,noise
	
'''(optional) if we use  PIR sensors instead of TOF sensors,
    we have to use this method for capturing a "train" of people (not precise)
 '''
def passImage(alreadyActivated,matchedResults):
    singlePerson=0
    trainActivation=0
    str1=""
    for x in range(0,len(matchedResults)):
        str1=str1+str(matchedResults[x])
        if(matchedResults[x]>0 ):
            singlePerson=singlePerson+1
    if(singlePerson==1 and matchedResults[-1]!=0):
        return alreadyActivated,1
    #print("stringList: "+str1)
    trainActivation=re.findall(r'0*1+0+1+0*',str1)
    #print("regex matching: "+str(trainActivation))
    if (len(trainActivation)>0 and alreadyActivated!=1):
        alreadyActivated=1
        return alreadyActivated,1
    
    return alreadyActivated,0
	
#(optional) in absence of  the light, we can use this function to make the image lighter    
def adjust_gamma(image, gamma=1.5):
	# build a lookup table mapping the pixel values [0, 255] to
	# their adjusted gamma values
	invGamma = 1.0 / gamma
	table = np.array([((i / 255.0) ** invGamma) * 255
		for i in np.arange(0, 256)]).astype("uint8")
 
	# apply gamma correction using the lookup table
	return cv2.LUT(image, table)

def envNoise(path,f_cascade,scaleFactor=1.020):
    test2 = cv2.imread(path)
    img_copy = np.copy(test2)
    blackList=[]
    #convert the test image to gray image as opencv face detector expects gray images
    gray = cv2.cvtColor(img_copy, cv2.COLOR_BGR2GRAY)
    
    #let's detect multiscale (some images may be closer to camera than others) images
    faces = f_cascade.detectMultiScale(gray, scaleFactor=scaleFactor, minNeighbors=5);
    
    #go over list of faces and draw them as rectangles on original colored img
    for (x, y, w, h) in faces:
        if((w*h)>20000):
                cv2.rectangle(img_copy, (x, y), (x+w, y+h), (0, 255, 0), 2)
                blackList.append([x,y,w,h])
                #print(blackList)
    return blackList,img_copy
#function for drawing the rectangle that underlines captured face 
def drawRect(list,image):
    img_copy = np.copy(image)
    for (x, y, w, h) in list:
          cv2.rectangle(img_copy, (x, y), (x+w, y+h), (255,0,0), 2)
    return img_copy
    
def main ():

    matchedResults=[]
    forbiddenCord=[]
    alreadyActivated=0
    tIn=time.time()
    result=0
	#variable that contains the video name 
    param=sys.argv[1]
    
    lbp_face_cascade = cv2.CascadeClassifier('classificator/data/case.xml')
    print("classifier ready")
    relif=0
    global match
    match=0
    photo = "VideoGallery/Frames/frames"
    count = 0
    noise=0
	#returnMask=0
	
	#preparing phase: at the beginning, gate send to server two image. In this way we can find image background noise
    if (param[0]=="I"):
        print("entro IN")
        forbiddenCord,img_copy=envNoise("VideoGallery/In.jpg",lbp_face_cascade)
        cv2.imwrite("In.png",img_copy)
    else:
        print("entro OUT")
        forbiddenCord,img_copy=envNoise("VideoGallery/Out.jpg",lbp_face_cascade)
        cv2.imwrite("Out.png",img_copy)
    print ("forbidden coordinate:",forbiddenCord)

    videoPath="VideoGallery/"+param
    # preparing phase: create a session for Amazon API 
    session = boto3.Session(profile_name='default')
    client=session.client('rekognition','us-west-2')
	   
    #load video
    print(videoPath)
    cap=cv2.VideoCapture(videoPath+'.avi')
    entireVideoTime=time.time()
	
	#iterating on the video frame
    while (cap.isOpened()):
        
        t1 = time.time()
		#save each frame as a png image, this image must be sent to Amazon API
        ret,frame =cap.read()
        my_photo = photo+param+" "+str(count)+".png"
        cv2.imwrite(my_photo,frame)
        test2 = cv2.imread(my_photo)
        t2 = time.time()
        dt2 = t2 - t1
        
        t1 = time.time()
		
        #adjusted_image = adjust_gamma(test2, gamma=1.5)
		
        match,faces_detected_img,noise = detect_faces(match,lbp_face_cascade, test2,forbiddenCord,noise)
        matchedResults.append(match)
        deltaFilterTime=time.time()-t1
        print("time spent to filter an image: ",deltaFilterTime)
        print("match:",match)
        print("noise:",noise)
        #matchedResults=matchedResults+str(match)
        #alreadyActivated,result=passImage(alreadyActivated,matchedResults)
     
        cv2.imwrite(my_photo,faces_detected_img)
        #returnMask=returnMask+match
		#if the filter detects people in the image 
        if (match>0):
            boxList=[]
           
            noise=0
            match=0
			# image preparation for sending to the API
            imgfile=open(my_photo,"rb")
            imgbytes=imgfile.read()
            imgobj={'Bytes':imgbytes}
            imgfile.close()
			
            if (param[:2]=="In"):
                timestamp=param[2:]
            else:
                timestamp=param[3:]
           
            
            apiRequestTime=time.time()
			#image request 
            peopleCounted,boxList=apiManager(client,imgobj,my_photo,timestamp,param)
			#(optional)if we want to compare Amazon Rekognition API with Face++ API
            #facePeopleCounted=sendReq(my_photo,timestamp,param)
            deltaApiRequestTime=time.time()-apiRequestTime
            print("time to send and receive results from api: ",deltaApiRequestTime)
			#(optional) if we want to see the bounding box provided by Amazon on our image
			'''
            apiImg=drawRect(boxList,test2)
            my_photo_API = photo+param+" "+"APiRect "+str(count)+".png"
            print(cv2.imwrite(my_photo_API,apiImg))
            print(my_photo_API)
			'''
            print ("people from  Rek API: "+ str(peopleCounted))
			#delete media on the machine
            deleteMedia(my_photo)  
			#with TOF, no more than one person can be detected in a video
            if(peopleCounted>0):
                cap.release()
            
        if count==12 :
            cap.release()
		
        count=count+1
        
    print("chiudo video: "+param)    #plt.imshow(convertToRGB(faces_detected_img))
    deltaEntireVideo=time.time()-entireVideoTime
    print("time spent to handle a video: ",deltaEntireVideo)
    cv2.destroyAllWindows()
	#delete media on the machine
    deleteMedia(videoPath+'.avi')
if __name__=="__main__":
    main()
