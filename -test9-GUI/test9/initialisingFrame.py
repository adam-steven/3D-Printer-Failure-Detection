import cv2
import numpy as np

#Start auto print detection, capture the inital print frame, and stop the auto print detection
class InitFrames:
    def __init__(self, vid, ui, filterFPS):
        self.vid = vid
        self.ui = ui

        self.initialFrames = []

        _, self.currentFrame = self.vid.get_frame()
        _, self.oldFrame = self.vid.get_frame()

        #Size down frames
        self.currentFrame = cv2.resize(self.currentFrame,(int(self.vid.width/2), int(self.vid.height/2)),fx=0,fy=0, interpolation = cv2.INTER_CUBIC)
        self.oldFrame = cv2.resize(self.oldFrame,(int(self.vid.width/2), int(self.vid.height/2)),fx=0,fy=0, interpolation = cv2.INTER_CUBIC)

        self.motionDetectionCounter = 0
        self.printStartedCounter = 0

        #If timeBeforeSwitching = 5 (seconds) - self.statusSwitchingThreshold = 10 = timeBeforeSwitching * filterFPS
        timeBeforeSwitching = 3 #seconds
        self.statusSwitchingThreshold = timeBeforeSwitching * filterFPS

        self.currentAutoStatus = 0 # 0=ENGAGED, 1=STARTING, 2=DETECTING, 3=OFF 

    #Detect printer motion to start the auto print detection
    def starting_motion_scan(self):
        diff = cv2.absdiff(self.currentFrame, self.oldFrame)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5,5), 0)
        _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
        dilated = cv2.dilate(thresh, None, iterations=3)
        contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            self.motionDetectionCounter = self.motionDetectionCounter + 1
        elif self.motionDetectionCounter > 0:
            self.motionDetectionCounter = self.motionDetectionCounter - 1

        if self.motionDetectionCounter >= self.statusSwitchingThreshold:
            self.currentAutoStatus = 1
            self.ui.autoStatusLbl.config(text="Automatic Detection (-STARTING-)")

        self.oldFrame = self.currentFrame
        _, self.currentFrame = self.vid.get_frame()
        self.currentFrame = cv2.resize(self.currentFrame,(int(self.vid.width/2), int(self.vid.height/2)),fx=0,fy=0, interpolation = cv2.INTER_CUBIC)

    #Capture the inital print frame and detect started printing indications
    def capture_initialising_frames(self):
        #Capture inital print frame for sample based background removal
        _, newFrame = self.vid.get_frame()
        grayNFrame = cv2.cvtColor(newFrame, cv2.COLOR_BGR2GRAY)
        self.initialFrames.append(grayNFrame)

        #Test if the print head has started printing
        topCut = self.get_height_crop()
        leftCut = int(self.ui.cutLeftScl.get()/2)
        rightCut = int((self.vid.width - self.ui.cutRightScl.get())/2)
        bottomCut = int((self.vid.height - self.ui.cutBottomScl.get())/2)

        croppedOldFrame = self.oldFrame[topCut:bottomCut, leftCut:rightCut]
        croppedCurrentFrame = self.currentFrame[topCut:bottomCut, leftCut:rightCut]

        diff = cv2.absdiff(croppedOldFrame, croppedCurrentFrame)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5,5), 0)
        _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
        dilated = cv2.dilate(thresh, None, iterations=3)
        contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        bigMovingObjectDetected = 0

        for contour in contours:
            if cv2.contourArea(contour) < 10000:
                continue
            bigMovingObjectDetected = 1

        if bigMovingObjectDetected == 1:
            self.printStartedCounter = self.printStartedCounter + 1

        if self.printStartedCounter >= self.statusSwitchingThreshold:
            self.currentAutoStatus = 2
            self.ui.autoStatusLbl.config(text="Automatic Detection (-DETECTING-)")

        self.oldFrame = self.currentFrame
        _, self.currentFrame = self.vid.get_frame()
        self.currentFrame = cv2.resize(self.currentFrame,(int(self.vid.width/2), int(self.vid.height/2)),fx=0,fy=0, interpolation = cv2.INTER_CUBIC)

        return grayNFrame

    #Detect lack of printer motion to stop the auto print detection OR re-engage the auto print detection
    def stopped_motion_scan(self):
        diff = cv2.absdiff(self.currentFrame, self.oldFrame)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5,5), 0)
        _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
        dilated = cv2.dilate(thresh, None, iterations=3)
        contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            self.motionDetectionCounter = self.statusSwitchingThreshold
        else:
            self.motionDetectionCounter = self.motionDetectionCounter - 1

        if self.motionDetectionCounter <= 0:
            self.motionDetectionCounter = 0
            self.currentAutoStatus = 0
            self.ui.autoStatusLbl.config(text="Automatic Detection (-ENGAGED-)")

        self.oldFrame = self.currentFrame
        _, self.currentFrame = self.vid.get_frame()
        self.currentFrame = cv2.resize(self.currentFrame,(int(self.vid.width/2), int(self.vid.height/2)),fx=0,fy=0, interpolation = cv2.INTER_CUBIC)

    #Turn off the auto print detection if the user choses manual detection
    def manual_off(self):
        self.currentAutoStatus = 3
        self.ui.autoStatusLbl.config(text="Automatic Detection (-OFF-)")

    def get_height_crop(self):
        highestMovingObject = self.vid.height/4

        diff = cv2.absdiff(self.currentFrame, self.oldFrame)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5,5), 0)
        _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
        dilated = cv2.dilate(thresh, None, iterations=3)
        contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            (x, y, w, h) = cv2.boundingRect(contour)

            if cv2.contourArea(contour) < 10000:
                continue
            if highestMovingObject > (y+h):
                highestMovingObject = (y+h)

        return int(highestMovingObject)


