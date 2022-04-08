import cv2, time, math
import mediapipe as mp

#Hand class for everything
class Hand():
    handLms = []
    tipIds = [4, 8, 12, 16, 20]
    #gets everything ready to use, with the configs and stuff as well as args
    def __init__(self, mode=False, maxHands=2, detectionConfidence=0.5, trackConfidence=0.5) -> None:
        self.mode = mode
        self.maxHands = maxHands
        self.detectionConfidence = detectionConfidence
        self.trackConfidence = trackConfidence

        self.mpHands = mp.solutions.hands
        self.mpDraw = mp.solutions.drawing_utils
        self.hands = self.mpHands.Hands(static_image_mode=self.mode, max_num_hands=self.maxHands, min_detection_confidence=self.detectionConfidence, min_tracking_confidence=self.trackConfidence)

    #finds the hand on the cap and will draw points (if set to true)
    def findHands(self, img, draw=True) -> any:
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:
            for hLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, hLms, self.mpHands.HAND_CONNECTIONS)

        return img

    #returns a list of the positions of the main points in the hand (check mediapipe website for the main points)
    def findPosition(self, img, handNum=0, draw=True) -> tuple:
        xList = []
        yList = []
        bbox = []

        self.handLMs = []

        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNum]

            for i, lm in enumerate(myHand.landmark):
                height, width, channels = img.shape
                currentX, currentY = int(lm.x*width), int(lm.y*height)

                xList.append(currentX)
                yList.append(currentY)

                self.handLMs.append([i ,currentX, currentY])

                if draw:
                    cv2.circle(img, (currentX, currentY), 5, (255, 0, 255), cv2.FILLED)

            xMin, xMax = min(xList), max(xList)
            yMin, yMax = min(yList), max(yList)
            
            bbox = xMin, yMin, xMax, yMax

            if draw:
                cv2.rectangle(img, (bbox[0]-25, bbox[1]-25), (bbox[2]+25, bbox[3]+25), (0, 255, 0), 2)

        return self.handLMs, bbox

    def findDistance(self, point1, point2, img, draw=True):
        thumbPosX, thumbPosY = self.handLMs[point1][1], self.handLMs[point1][2]
        indexPosX, indexPosY = self.handLMs[point2][1], self.handLMs[point2][2]
        middleX, middleY =  (thumbPosX + indexPosX) // 2, (thumbPosY + indexPosY) // 2

        if draw:
            cv2.circle(img, (thumbPosX, thumbPosY), 9, (255,0,0), cv2.FILLED)
            cv2.circle(img, (indexPosX, indexPosY), 9, (255,0,0), cv2.FILLED)
            cv2.line(img, (thumbPosX, thumbPosY), (indexPosX, indexPosY), (255, 255, 255), 5)
            cv2.circle(img, (middleX, middleY), 3, (255,255,255))

        lineLen = math.hypot(indexPosX - thumbPosX, indexPosY - thumbPosY)

        return lineLen, img, [thumbPosX, thumbPosY, indexPosX, indexPosY, middleX, middleY]

    def fingersUp(self):
        fingers = []

        #accounting for the thumb, this one checks the x value "[1]" instead of the others checking y val
        if self.handLMs[self.tipIds[0]][1] > self.handLMs[self.tipIds[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)

                #accounts for the fingers
        for id in range(1, 5):
            #if "8" == index finger is less than the 6 point, it means it's open
            if self.handLMs[self.tipIds[id]][2] < self.handLMs[self.tipIds[id] - 2][2]:
                #the finger is open
                fingers.append(1)
            else:
                #the finger is closed
                fingers.append(0)

        return fingers

    # def lineTrack(self):
    #     lineLen = 0;

    #     if self.fingersUp[1] == 0:


def main():
    pTime = 0
    cTime = 0

    vid = cv2.VideoCapture(0)
    dectector = Hand()
    while True:
        _, img = vid.read()
        img = dectector.findHands(img)
        handLMs = dectector.findPosition(img)

        # if len(handLMs) != 0 :
        #   print(handLMs[4], handLMs[8])

        cTime = time.time()
        fps = int(1/(cTime-pTime))
        pTime = cTime

        cv2.putText(img, str(fps), (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        cv2.imshow("Video Feed", img)

        if cv2.waitKey(1) & 0xFF == 27:
            break


if __name__ == '__main__':
    main()
