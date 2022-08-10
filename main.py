from sys import setcheckinterval
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
import handTrack as ht
import numpy as np
import time, math
import cv2, time
import firefox as fx

#------------------------------------------------
#prints out the min, max, and avg FPS
#------------------------------------------------
def displayFPS(fpsL):
    #gets all values that arent 0
    fpsL = [i for i in fpsL if i != 0]

    print("Minimum FPS:",min(fpsL))
    print("Average FPS:",np.mean(fpsL))
    print("Maximum FPS:",max(fpsL))

#------------------------------------------------
#taking in the number of fingers up, 
#it will perform a predetermined action 
#corresponding to this number
#------------------------------------------------
def fingerContol(img, fingersUp : list, browser : fx.Browser, volPer : int, lineInfo : list, colorVol : tuple, end: bool):
    #if the thumb is down
    if fingersUp[0] == 0:
        #press the play button (pauses and plays depending on the current state of the video)
        browser.play()

    if fingersUp[1] == 0:
        browser.scrub()

    #if the middle finger is down
    if fingersUp[2] == 0:
        #press the next button on the video
        browser.next()
    
    #if the ring finger is down
    if fingersUp[3] == 0:
        browser.previous()

    #if the pinky finger is down
    if fingersUp[4] == 0:
        #set the volume 
        volume.SetMasterVolumeLevelScalar(volPer/100, None)

        #add a green circle to indicate we set the vol
        cv2.circle(img, (lineInfo[4], lineInfo[5]), 7, (0, 255, 0), cv2.FILLED)

        #change the color of the top text to green also as an indicator
        colorVol = (0,255,0)
    else:
        #change the color back to the regular blue
        colorVol = (255,0,0)
    
    #if no fingers are up
    if 1 not in fingersUp:
        #make end to true, thus killing the loop
        end = True

    #give back the value so it can be used within the main func
    return colorVol, end

#------------------------------------------------
#calculates and returns the current fps, 
#and keeps track of the fps throughout the time
#within the fpsL variable
#------------------------------------------------
def calcFPS(pTime, fpsL):
    cTime = time.time()
    fps = int(1/(cTime-pTime))
    fpsL.append(fps)

    return fps, fpsL, cTime

#------------------------------------------------
#Draws everything inside the frame including
#the volume bars, fps, and the current set vol
#------------------------------------------------
def draw(img, volPer, volBar, curVol, colorVol, fps):
    #the green rectangle on the left side
    cv2.rectangle(img, (50, 150), (85, 400), (0,255,0), 3)

    #dynamic blue rectangle that corresponds with the volume % it's currently at
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (255,0,0), cv2.FILLED)

    #puts the current volume % 
    cv2.putText(img, f"{int(volPer)}%", (40, 435), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)

    #shows the current SET volume %
    cv2.putText(img, f"Current Set Volume: {int(round(curVol))}%", (300, 70), cv2.FONT_HERSHEY_SIMPLEX, .75, colorVol, 2)

    #current FPS
    cv2.putText(img, f"FPS: {str(fps)}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

#------------------------------------------------
#main function of the file, responsible 
#for calling and running everything
#------------------------------------------------
def main(url, showBrowser=True, showFeed=True):
    end=False
    pTime = 0
    cTime = 0
    area = 0
    volBar = 400
    volPer = 0
    lineMinMax = [30, 175]
    #How much the vol goes up by, so 5=increment by 5
    smoothness = 5
    #list of FPS values
    fpsL = []
    colorVol = (255,0,0)
    prevIndexPosX = 0

    vid = cv2.VideoCapture(0)
    detector = ht.Hand(detectionConfidence=0.5, maxHands=1)

    browser = fx.Browser(url, showBrowser)
    #play the video as it starts
    browser.play()

    count = 0
    #while we are still trying to run the loop
    while not end:
        #------------------------------------------------
        #Read the video output, find the hands, plot 
        #the points, and get their positions
        #------------------------------------------------
        _, img = vid.read()
        img = detector.findHands(img, draw=showFeed)
        handLMs, bbox = detector.findPosition(img, draw=showFeed)

        #if a hand is on screen
        if len(handLMs) != 0:
            #get the area of the box (get how close the hand is to the camera)
            area =  (bbox[2]-bbox[0]) * (bbox[3]-bbox[1])//100

            #if the hand is within this ammount of space
            if 150<area<750:

                #------------------------------------------------
                #get the length from the index to thumb aswell
                #as their position. Use that to interpolate
                #the data, then smooth it out to make it 
                #less jittery. Then get the current fingers 
                #which are held up, then use that to perform
                #the commands
                #------------------------------------------------
                length, img, lineInfo = detector.findDistance(4, 8, img, draw=showFeed)

                volBar = np.interp(length, lineMinMax, [400, 150])
                volPer = np.interp(length, lineMinMax, [0, 100])

                volPer = smoothness*round(volPer/smoothness)

                fingersUp = detector.fingersUp()

                if fingersUp[1] == 0:
                    if count == 0:
                        prevIndexPosX = lineInfo[2]
                        print("Prev:",prevIndexPosX)
                        count+=1
                    else:
                        curIndexPosX = lineInfo[2]
                        print("Cur:",curIndexPosX, "Prev:",prevIndexPosX, "Prev-Cur:",prevIndexPosX-curIndexPosX)

                colorVol, end = fingerContol(img, fingersUp, browser, volPer, lineInfo, colorVol, end)

        #------------------------------------------------
        #get the current set volume, calculate the FPS,
        #and draw everything on the screen
        #------------------------------------------------
        curVol = volume.GetMasterVolumeLevelScalar()*100

        fps, fpsL, cTime = calcFPS(pTime, fpsL)
        pTime = cTime

        draw(img, volPer, volBar, curVol, colorVol, fps)

        if showFeed:
            cv2.imshow("Video Feed", img)

        # cv2.waitKey(1)

        if cv2.waitKey(1) and end:
            #display the min, max, and avg fps in the console
            cv2.destroyAllWindows()
            displayFPS(fpsL)
            break

if __name__ == '__main__':
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))

    volMin = volume.GetVolumeRange()[0]
    volMax = volume.GetVolumeRange()[1]

    url = "https://www.youtube.com/watch?v=-thh5_bpGGY&list=RD-thh5_bpGGY&start_radio=1"
    main(url, showBrowser=True)