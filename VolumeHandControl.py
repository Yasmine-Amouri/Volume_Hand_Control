import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
from pycaw.pycaw import AudioUtilities

#gets the default speaker device on my system
device = AudioUtilities.GetSpeakers()
#access the volume interface 
volume = device.EndpointVolume
t = volume.GetVolumeRange() #(-65.25, 0.0, 0.03125)
minVol = t[0]
maxVol = t[1]

vol = 0
volPer = 0 #pourcentage du volume
volBar = 400 #0% correspond pos du pt bas du rectangle

# Calibration values (observed for my hand)
min_ratio = 0.3   # fingers almost touching
max_ratio = 2.1   # fingers fully open

# Smoothing factor
alpha = 0.2
smoothed_ratio = None

#Parameters
width_cam, height_cam = 640, 480

cap = cv2.VideoCapture(0)
cap.set(3, width_cam)
cap.set(4, height_cam)

pTime = 0 #time of the previous frame

detector = htm.HandDetector(min_det_confiance = 0.7)

if(not cap.isOpened()):
   print("Failed to open camera!")

while(True):
    success, img = cap.read(0)

    if(not success):
      print("Failed to capture image")
      break

    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw = False)

    if(len(lmList)!=0):
        #on a besoin du bout du pouce
        x1, y1 = lmList[4][1], lmList[4][2]
        cv2.circle(img, (x1,y1), 12, (0,165,255), cv2.FILLED)

        #on a besoin du bout de l'index
        x2, y2 = lmList[8][1], lmList[8][2]
        cv2.circle(img, (x2,y2), 12, (0,165,255), cv2.FILLED)

        #center
        cx, cy = (x1 + x2)//2, (y1+y2)//2

        #on dessine une ligne entre pouce et index
        cv2.line(img, (x1,y1), (x2,y2), (0,166,255), 3)
        #center
        cv2.circle(img, (cx,cy), 12, (255,255,255), cv2.FILLED)

        #longueur du segment entre pouce index
        #au lieu de sqrt((x1-x2)^2 + (y1-y2)^2)
        L = math.hypot(x1-x2,y1-y2)
       
        x3, y3 = lmList[0][1], lmList[0][2]   # wrist
        x4, y4 = lmList[5][1], lmList[5][2]   # index MCP (knuckle)
        H = math.hypot(x3-x4,y3-y4)

        if(H == 0):
           H = 1
        ratio = L / H
        #print("ratio ",ratio)
        ratio = max(min_ratio, min(max_ratio, ratio))

        if (smoothed_ratio is None):
            smoothed_ratio = ratio
        else:
            smoothed_ratio = alpha * ratio + (1 - alpha) * smoothed_ratio


        #max L = 340 et min L = 22
        #maxVol = -60.25 et maxVol = 0
        #conversion linéaire entre deux intervalles
        vol = np.interp(smoothed_ratio, [min_ratio,max_ratio], [minVol,maxVol])
        volPer = np.interp(smoothed_ratio, [min_ratio,max_ratio], [0,100])
        volBar = np.interp(volPer, [0,100], [400,150])
        #print(vol)
        volume.SetMasterVolumeLevel(vol,None)

    #barre de volume
    cv2.rectangle(img, (50,150), (85,400), (0,165,255), 3) #(85,400) point en bas à droite du rectangle et (50,150) point en haut à gauche du rectangle
    cv2.rectangle(img, (50,int(volBar)), (85,400), (0,165,255), cv2.FILLED)
    cv2.putText(img, f'{int(volPer)}%', (50, 440), cv2.FONT_HERSHEY_PLAIN, 2, (0,165,255), 3)

    cTime = time.time() #time of the current frame
    #cTime - pTime = duration to process one frame
    #Frames Per Second
    fps = 1/(cTime - pTime)
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0,165,255), 3)
    
    cv2.imshow("Volume Hand Control", img)

    if (cv2.waitKey(1) & 0xFF == 27):
        #press escp to close it
        break

#Free the webcam
cap.release()
#Close all OpenCV windows.
cv2.destroyAllWindows()