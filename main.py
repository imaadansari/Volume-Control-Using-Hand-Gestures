import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

wCam,hCam=640,480

cap=cv2.VideoCapture(0)
cap.set(3,wCam)
cap.set(4,hCam)

pTime=0 

detector=htm.handDetector(detentionCon=1,maxHands=1)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
#volume.GetMute()
#volume.GetMasterVolumeLevel()
volRange=volume.GetVolumeRange()


minVol, maxVol=volRange[0],volRange[1]
vol=-5
volBar=400
volPer=0
area=0
smoothness=5
colorVol=(255,0,0)

while True:
    success,img=cap.read()
    img=cv2.flip(img,1)

    img=detector.findHands(img)
    lmList,bbox=detector.findPosition(img,draw=True)
    if len(lmList)!=0:

        area=(bbox[2]-bbox[0])*(bbox[3]-bbox[1])//100
        #print(area)

        if 250<area<1000:

            cv2.circle(img,(wCam-20,20),15,(0,255,0),cv2.FILLED)
            #Find distance between index and thumb
            length,img,lineInfo=detector.findDistance(4,8,img)

            # Convert Volume
            volBar=np.interp(length,[50,230],[400,150])
            volPer=np.interp(length,[50,230],[0,100])

            volPer=smoothness*(volPer//smoothness)
           #check fingers up
            fingers=detector.fingersUp()
            print(fingers)
           
            if fingers[3]==0:
                volume.SetMasterVolumeLevelScalar(volPer/100,None)
                cv2.circle(img,(lineInfo[4],lineInfo[5]),7,(0,255,0),cv2.FILLED)
                colorVol=(0,255,0)
            else:
                colorVol=(255,0,0)
    else:
        volBar=400
        volPer=0

    cv2.rectangle(img,(50,150),(85,400),(0,255,255),3)
    cv2.rectangle(img,(50,int(volBar)),(85,400),(0,255,255),cv2.FILLED)
    cv2.putText(img,f'{int(volPer)} %',(50,450),cv2.FONT_HERSHEY_COMPLEX,1,(255,0,0),1)
    curVol=int(volume.GetMasterVolumeLevelScalar()*100)
    cv2.putText(img,f'SET VOL: {curVol}%',(wCam-300,70),cv2.FONT_HERSHEY_COMPLEX,1,colorVol,2)


    cTime=time.time()
    fps=1/(cTime-pTime)
    pTime=cTime

    cv2.putText(img,f'FPS: {int(fps)}',(40,70),cv2.FONT_HERSHEY_COMPLEX,1,(255,0,0),2)
    cv2.imshow("Img",img)
    cv2.waitKey(1)
