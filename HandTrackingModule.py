import cv2
import mediapipe as mp
import time

class HandDetector:
    def __init__(self, mode = False, max_nb_hands = 2, min_det_confiance = 0.5, min_track_confiance = 0.5):
        self.mode = mode
        self.max_nb_hands = max_nb_hands
        self.min_det_confiance = min_det_confiance
        self.min_track_confiance = min_track_confiance

        #MediaPipe’s hand detection module
        #storing a reference to that module inside the object
        self.mpHands = mp.solutions.hands

        #each HandDetecor has its own detection model instance 
        self.hands = self.mpHands.Hands(
            static_image_mode = self.mode,
            max_num_hands = self.max_nb_hands,
            min_detection_confidence = self.min_det_confiance,
            min_tracking_confidence = self.min_track_confiance
        )
      
        #Provides functions to draw landmarks and connections on detected hands
        #storing a reference to that module inside the object
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img, draw = True):
        #OpenCV uses BGR but mp expects RGB
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.res = self.hands.process(imgRGB) 
        #pas seulement res pour pouvoir l'utiliser dans findPosition

        dot_style = mp.solutions.drawing_utils.DrawingSpec(color=(0, 255, 255), thickness=2, circle_radius=3)
        connection_style = mp.solutions.drawing_utils.DrawingSpec(color=(255, 0, 0), thickness=2)
        
        if (self.res.multi_hand_landmarks):
            #List of detected hands’ landmarks
            for handLms in self.res.multi_hand_landmarks:
                if(draw):
                    #Draw the 21 points and the lines connecting them on the original image.
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS,dot_style, connection_style)
        
        return img

    def findPosition(self, img, num_hand = 0, draw = True):
        lmList = []
        if (self.res.multi_hand_landmarks):
            my_hand = self.res.multi_hand_landmarks[num_hand]

            for id, lm in enumerate(my_hand.landmark):
                #print(id, lm)
                h, w, c = img.shape
                #h:height:nbr of rows, w:width:nbr of columns, c:channels:nbr of color channels per pixel
                #BGR: 3 channels, grayscale img has 1 channel

                #we convert the normalized x,y-coordinates in(0–1) to the pixel row, column
                cx, cy = int(lm.x * w), int(lm.y * h)
                #print(id, cx, cy)
                lmList.append([id, cx, cy])
                
                if(draw):
                    #if(id == 4): #bout du pouce
                    cv2.circle(img, (cx,cy), 12, (0,165,255), cv2.FILLED)

        return lmList


def main():
    cap = cv2.VideoCapture(0)
    if (not cap.isOpened()):
        print("Cannot open camera!")
        exit()

    detector = HandDetector() #on garde les parametres par defaut
    pTime = 0 #time of the previous frame
    cTime = 0 #time of the current frame

    while (True):
        success, img = cap.read()
        if (not success):
            print("Failed to capture image!")
            break

        img = detector.findHands(img)

        lmList = detector.findPosition(img, draw = False)
        if(len(lmList) != 0):
            print(lmList[4]) #bout du pouce

        cTime = time.time()
        #cTime - pTime = duration to process one frame
        #Frames Per Second
        fps = 1/(cTime - pTime)
        pTime = cTime

        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,0), 3)
        
        cv2.imshow("Image", img)
        if (cv2.waitKey(1) & 0xFF == 27):
            #press escp to close it
            break

    #Free the webcam
    cap.release()
    #Close all OpenCV windows.
    cv2.destroyAllWindows()


#to make a file both executable and importable

if (__name__ == "__main__"):
    main()