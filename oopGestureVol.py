from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from sys import setcheckinterval
from comtypes import CLSCTX_ALL
import browserControl as bc
import handTrack as ht
import numpy as np
import time, cv2, time

class Main():
    def __init__(self, showBrowser=True, showFeed=True) -> None:
        self.pTime = 0
        self.cTime = 0
        self.area = 0
        self.volBar = 400
        self.volPer = 0
        self.lineMinMax = [30, 175]
        #How much the vol goes up by, so 5=increment by 5
        self.smoothness = 5

        self.fps = 0
        self.fpsL = []
        self.colorVol = (255,0,0)

        self.showBrowser=showBrowser
        self.showFeed = showFeed

        self.vid = cv2.VideoCapture(0)
        self.detector = ht.Hand(detectionConfidence=0.5, maxHands=1)

        self.browser = bc.Browser(self.showBrowser)
        self.browser.play()

        self.devices = AudioUtilities.GetSpeakers()
        self.interface = self.devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(self.interface, POINTER(IAudioEndpointVolume))

    def update(self) -> None:
        while True:
            _, self.img = self.vid.read()
            self.img = self.detector.findHands(self.img, draw=self.showFeed)
            handLMs, bbox = self.detector.findPosition(self.img, draw=self.showFeed)

            if len(handLMs) != 0:
                area =  (bbox[2]-bbox[0]) * (bbox[3]-bbox[1])//100
                
                if 150<area<750:
                    self.length, self.img, self.lineInfo = self.detector.findDistance(4, 8, self.img, draw=self.showFeed)

                    self.calcVol()

                    self.fingersUp = self.detector.fingersUp()
                    
                    self.fingerControl()
    
            self.curVol = self.volume.GetMasterVolumeLevelScalar()*100

            self.draw()
            self.trackFPS()

            if self.showFeed:
                cv2.imshow("Video Feed", self.img)

            if cv2.waitKey(1) & 0xFF == 27:
                self.displayFPS()
                break
    
    def fingerControl(self) -> None:
        if self.fingersUp[0] == 0:
            self.browser.play()

        #If the middle finger is down
        if self.fingersUp[2] == 0:
            #press the next button on the video
            self.browser.next()
        
        #if the pinky finger is down set the volume
        if self.fingersUp[4] == 0:
            self.volume.SetMasterVolumeLevelScalar(self.volPer/100, None)

            #add a greencircle to indicate we set the vol
            cv2.circle(self.img, (self.lineInfo[4], self.lineInfo[5]), 7, (0, 255, 0), cv2.FILLED)

            #change the color of the top text to green also as an indicator
            self.colorVol = (0,255,0)
        else:
            self.colorVol = (255,0,0)


    def draw(self) -> None:
            cv2.rectangle(self.img, (50, 150), (85, 400), (0,255,0), 3)
            cv2.putText(self.img, f"{int(self.volPer)}%", (40, 435), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)

            cv2.rectangle(self.img, (50, int(self.volBar)), (85, 400), (255,0,0), cv2.FILLED)

            cv2.putText(self.img, f"Current Set Volume: {int(round(self.curVol))}%", (300, 70), cv2.FONT_HERSHEY_SIMPLEX, .75, self.colorVol, 2)

            cv2.putText(self.img, f"FPS: {str(self.fps)}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    def calcVol(self) -> None:
        self.volBar = np.interp(self.length, self.lineMinMax, [400, 150])
        self.volPer = np.interp(self.length, self.lineMinMax, [0, 100])

        self.volPer = self.smoothness*round(self.volPer/self.smoothness)

    def trackFPS(self) -> None:
        self.cTime = time.time()
        self.fps = int(1/(self.cTime-self.pTime))
        self.fpsL.append(self.fps)
        self.pTime = self.cTime

    def displayFPS(self) -> None:
        self.fpsL = [i for i in self.fpsL if i != 0]

        print("Minimum FPS:",min(self.fpsL))
        print("Average FPS:",np.mean(self.fpsL))
        print("Maximum FPS:",max(self.fpsL))


if __name__ == '__main__':
    control = Main(showBrowser=False)
    control.update()