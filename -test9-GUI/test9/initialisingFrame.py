import cv2
import numpy as np
from constants import FILTER_FPS, FSM_TIMER, STARTING_STATE_FAIL_SAFE

#BLOB detection to get moving objects
def get_contours(currentFrame, oldFrame):
    diff = cv2.absdiff(currentFrame, oldFrame)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 20, 255, cv2.THRESH_BINARY)
    _, contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return contours

#Start auto print detection, capture the inital print frame, and stop the auto print detection
class InitFrames:
    def __init__(self, vidWidth, vidHeight):
        self.vidWidth = vidWidth
        self.vidHeight = vidHeight

        self.sizedDownVidWidth = int(vidWidth/3)
        self.sizedDownVidHeight = int(vidHeight/3)

        self.initialFrames = []

        #Size down previous frame
        self.oldFrame = []

        self.motionDetectionCounter = 0
        self.printStartedCounter = 0

        #Convert FSM_TIMER to seconds by taking the FPS into account
        self.statusSwitchingThreshold = FILTER_FPS * FSM_TIMER

    #Save the needed GUI values
    def update_ui_values(self, uiVals):
        self.leftCut = int(uiVals.cutLeftScl/2)
        self.rightCut = int((self.vidWidth - uiVals.cutRightScl)/2)
        self.bottomCut = int((self.vidHeight - uiVals.cutBottomScl)/2)

    #Detect printer motion to start and stop the auto print detection
    def motion_scan(self, frame, status):
        currentFrame = cv2.resize(frame,(self.sizedDownVidWidth, self.sizedDownVidHeight),fx=0,fy=0, interpolation = cv2.INTER_CUBIC)

        if np.any(self.oldFrame):
            contours = get_contours(currentFrame, self.oldFrame)

            movingObjectDetected = False

            for contour in contours:
                if cv2.contourArea(contour) < 200: #BLOB area check to ignore any inital plastic leak
                    continue
                movingObjectDetected = True
                break

            #If motion detected and in the ENGAGED state move to STARTING
            if movingObjectDetected == True: 
                self.motionDetectionCounter += 1
                if self.motionDetectionCounter > self.statusSwitchingThreshold:
                    self.motionDetectionCounter = self.statusSwitchingThreshold
                    if status == 0:
                        self.initialFrames.clear()
                        status = 1 
            #If motion not detected and in the OFF state move to ENGAGED
            else:
                self.motionDetectionCounter -= 1
                if self.motionDetectionCounter < 0:
                    self.motionDetectionCounter = 0
                    status = 0
        
        if status != 1:
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
        croppedOldFrame = self.oldFrame[0:self.bottomCut, self.leftCut:self.rightCut]
        croppedCurrentFrame = currentFrame[0:self.bottomCut, self.leftCut:self.rightCut]

        contours = get_contours(croppedCurrentFrame, croppedOldFrame)

        bigMovingObjectDetected = False

        for contour in contours:
            if cv2.contourArea(contour) < 1500:
                continue
            bigMovingObjectDetected = True
            break

        if bigMovingObjectDetected == True:
            self.printStartedCounter = self.printStartedCounter + 1

        if self.printStartedCounter > self.statusSwitchingThreshold or len(self.initialFrames) >= STARTING_STATE_FAIL_SAFE:
            self.printStartedCounter = 0
            status = 2

        self.oldFrame = currentFrame.copy()
        return status, frame

