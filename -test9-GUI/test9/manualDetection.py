import cv2
import numpy as np
import time

#start
     #self.multiTracker = cv2.MultiTracker_create()
     #self.boxesGot = 0
     #self.objectCentrePositions = []

#stop
        #self.multiTracker.clear()
        #self.objectCentrePositions.clear()

#User selects the object to be auto tracked 
class ManualDetcAndTrak:
    def __init__(self, vidWidth, vidHeight, failureCenterRange):
        self.scanPrev = 0.0

        self.manualSizeDown = 2
        self.manualFPS = 25

        self.vidWidth = vidWidth
        self.vidHeight = vidHeight

        self.resizedWidth = int(vidWidth/self.manualSizeDown)
        self.resizedHeight = int(vidHeight/self.manualSizeDown)

        self.multiTracker = cv2.MultiTracker_create()
        self.objectCentrePositions = []

        #If potential object exists for minsBeforeCertain (seconds) its a definite object - i.e defObjectConFail = minsBeforeCertain * filterFPS
        self.defObjectFail = self.manualFPS * 10
        self.failureCenterRange = failureCenterRange

    def set_ui_values(self, failureCenterRange):
        self.failureCenterRange = failureCenterRange

    def manual_object_seletion(self, frame, noOfModels):

        #Get user to select the objects
        trackerCounter = int(noOfModels)
        for i in range(trackerCounter):
            #Reset frame size
            frame = cv2.resize(frame,(self.vidWidth, self.vidHeight),fx=0,fy=0, interpolation = cv2.INTER_LINEAR)

            #Draw selection instructions
            cv2.rectangle(frame, (0,0), (self.vidWidth,50), (255, 255, 255), -1)
            cv2.rectangle(frame, (0,0), (self.vidWidth,50), (0, 0, 0), 2)
            text = 'SELECT MODEL ' + str(i+1) + ' (BASE) - ENTER TO CONTINUE - AVOID SELECTING PRINT HEAD (INCLUDING NOZZLE)'
            fontscale = self.get_optimal_font_scale(text, self.vidWidth)
            cv2.putText(frame, text, (10, 35), cv2.FONT_HERSHEY_SIMPLEX, fontscale, (0, 0, 0), 2)

            #User selection
            bbox = cv2.selectROI('FrameTrack '+ str(i+1), frame)
            tracker = cv2.TrackerBoosting_create()

            #Downsize the frame selection box for effiecncy
            frame = cv2.resize(frame,(self.resizedWidth, self.resizedHeight),fx=0,fy=0, interpolation = cv2.INTER_LINEAR)
            resizedBbox = tuple(int(x/self.manualSizeDown) for x in bbox)

            self.multiTracker.add(tracker, frame, resizedBbox)

            objectLineInSection = int(resizedBbox[0] + (resizedBbox[2]/2))
            self.objectCentrePositions.append([objectLineInSection, self.defObjectFail])

            cv2.destroyWindow('FrameTrack '+str(i+1))

        return frame

    def manual_tracking(self, frame):
        copyFrame = frame.copy()
        objFail = False

        time_elapsed = time.time() - self.scanPrev

        if time_elapsed > 1./self.manualFPS:

            copyFrame = cv2.resize(copyFrame,(self.resizedWidth, self.resizedHeight),fx=0,fy=0, interpolation = cv2.INTER_LINEAR)
            self.scanPrev = time.time()
            success, boxes = self.multiTracker.update(copyFrame)

            
            for i, box in enumerate(boxes):
                copyFrame, failure = self.check_for_failure(success, box, i, copyFrame)
                if failure:
                    self.objectCentrePositions[i][1] = self.objectCentrePositions[i][1] - 1
                else:
                    self.objectCentrePositions[i][1] = self.defObjectFail

                if self.objectCentrePositions[i][1] < 0:
                    objFail = True
                    break

        #Reset frame size
        copyFrame = cv2.resize(copyFrame,(self.vidWidth, self.vidHeight),fx=0,fy=0, interpolation = cv2.INTER_LINEAR)
        return copyFrame, objFail

    #Size selection instructions to fit frame
    def get_optimal_font_scale(self, text, width):
        for scale in reversed(range(0, 60, 1)):
            textSize = cv2.getTextSize(text, fontFace=cv2.FONT_HERSHEY_DUPLEX, fontScale=scale/10, thickness=1)
            new_width = textSize[0][0]
            if (new_width <= width):
                return scale/10
        return 1

    #True = failure has occured
    def check_for_failure(self, success, box, boxNum, cFrame):
        if success == False:
            return cFrame, True

        (x,y,w,h) = [int(a) for a in box]
        cv2.rectangle(cFrame, (x,y), (x+w,y+h), (255,0,0), 1)
        cv2.putText(cFrame, "dO("+str(boxNum)+") "+str(self.objectCentrePositions[boxNum][1]), (x, y - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

        currnetObjectLineInSection = int(x + (w/2))

        if self.objectCentrePositions[boxNum][0] - self.failureCenterRange > currnetObjectLineInSection or currnetObjectLineInSection > self.objectCentrePositions[boxNum][0] + self.failureCenterRange:
            return cFrame, True

        return cFrame, False