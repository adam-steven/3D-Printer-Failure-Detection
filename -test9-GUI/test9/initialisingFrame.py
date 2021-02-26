import cv2
import numpy as np

#Start auto print detection, capture the inital print frame, and stop the auto print detection
class InitFrames:
    def __init__(self, vidWidth, vidHeight, filterFPS):
        self.vidWidth = vidWidth
        self.vidHeight = vidHeight

        self.sizedDownVidWidth = int(vidWidth/2)
        self.sizedDownVidHeight = int(vidHeight/2)

        self.initialFrames = []

        #Size down previous frame
        self.oldFrame = []

        self.motionDetectionCounter = 0
        self.printStartedCounter = 0

        #If timeBeforeSwitching = 5 (seconds) - self.statusSwitchingThreshold = 10 = timeBeforeSwitching * filterFPS
        self.statusSwitchingThreshold = filterFPS * 5  #seconds


    def update_ui_values(self, uiVals):
        self.leftCut = int(uiVals.cutLeftScl/2)
        self.rightCut = int((self.vidWidth - uiVals.cutRightScl)/2)
        self.bottomCut = int((self.vidHeight - uiVals.cutBottomScl)/2)

    #Detect printer motion to start the auto print detection
    def starting_motion_scan(self, frame):
        status = 0 

        currentFrame = cv2.resize(frame,(self.sizedDownVidWidth, self.sizedDownVidHeight),fx=0,fy=0, interpolation = cv2.INTER_CUBIC)

        if np.any(self.oldFrame):
            diff = cv2.absdiff(currentFrame, self.oldFrame)
            gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5,5), 0)
            _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
            dilated = cv2.dilate(thresh, None, iterations=3)
            contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            if contours:
                self.motionDetectionCounter += 1
            elif self.motionDetectionCounter > 0:
                self.motionDetectionCounter -= 1

            if self.motionDetectionCounter >= self.statusSwitchingThreshold:
                status = 1

        self.oldFrame = currentFrame.copy()
        return status


    #Capture the inital print frame and detect started printing indications
    def capture_initialising_frames(self, frame):
        status = 1 

        #Capture inital print frame for sample based background removal
        currentFrame = cv2.resize(frame,(self.sizedDownVidWidth, self.sizedDownVidHeight),fx=0,fy=0, interpolation = cv2.INTER_CUBIC)
        grayNFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        self.initialFrames.append(grayNFrame)

        #Test if the print head has started printing
        topCut = self.get_height_crop(currentFrame)

        croppedOldFrame = self.oldFrame[topCut:self.bottomCut, self.leftCut:self.rightCut]
        croppedCurrentFrame = currentFrame[topCut:self.bottomCut, self.leftCut:self.rightCut]

        diff = cv2.absdiff(croppedOldFrame, croppedCurrentFrame)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5,5), 0)
        _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
        dilated = cv2.dilate(thresh, None, iterations=3)
        contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        bigMovingObjectDetected = 0

        for contour in contours:
            if cv2.contourArea(contour) < 8000:
                continue
            bigMovingObjectDetected = 1

        if bigMovingObjectDetected == 1:
            self.printStartedCounter = self.printStartedCounter + 1

        if self.printStartedCounter >= self.statusSwitchingThreshold:
            status = 2

        self.oldFrame = currentFrame.copy()
        return status, frame

    #Detect lack of printer motion to stop the auto print detection OR re-engage the auto print detection
    def stopped_motion_scan(self, frame):
        status = 3

        currentFrame = cv2.resize(frame,(self.sizedDownVidWidth, self.sizedDownVidHeight),fx=0,fy=0, interpolation = cv2.INTER_CUBIC)

        diff = cv2.absdiff(currentFrame, self.oldFrame)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5,5), 0)
        _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
        dilated = cv2.dilate(thresh, None, iterations=3)
        contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            self.motionDetectionCounter = self.statusSwitchingThreshold
        else:
            self.motionDetectionCounter -= 1

        if self.motionDetectionCounter <= 0:
            self.motionDetectionCounter = 0
            status = 0

        self.oldFrame = currentFrame.copy()
        return status

    def get_height_crop(self, frame):
        highestMovingObject = self.vidHeight/4

        diff = cv2.absdiff(frame, self.oldFrame)
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


