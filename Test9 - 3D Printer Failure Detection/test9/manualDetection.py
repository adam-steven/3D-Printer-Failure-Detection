import cv2
import time
from constants import MANUAL_FPS, FAILER_TIMER

#User selects the object to be auto tracked 
class ManualDetcAndTrak:
    def __init__(self, vidWidth, vidHeight, failureCenterRange):
        self.scanPrev = 0.0

        self.manualSizeDown = 2

        self.vidWidth = vidWidth
        self.vidHeight = vidHeight

        #resized frame dimetions used for down sizing frame to optimise speed
        self.resizedWidth = int(vidWidth/self.manualSizeDown)
        self.resizedHeight = int(vidHeight/self.manualSizeDown)

        #NOTE MULTI-TRACKERS HAVE BEEN REMOVED FROM OPENCV AS OF v4.5.1 USE v4.5.0 OR EARLIER
        self.multiTracker = cv2.MultiTracker_create()
        self.objectCentrePositions = []

        #If potential object exists for minsBeforeCertain (seconds) its a definite object - i.e defObjectConFail = minsBeforeCertain * filterFPS
        self.defObjectFail = MANUAL_FPS * FAILER_TIMER
        self.failureCenterRange = failureCenterRange

    #Save the needed GUI values
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

            #Save the horizontal center of the object
            objectLineInSection = int(resizedBbox[0] + (resizedBbox[2]/2))
            self.objectCentrePositions.append([objectLineInSection, self.defObjectFail])

            cv2.destroyWindow('FrameTrack '+str(i+1))

        return frame

    def manual_tracking(self, frame):
        copyFrame = frame.copy()
        objFail = False

        #Timer delay for "MANUAL_FPS" seconds 
        time_elapsed = time.time() - self.scanPrev
        if time_elapsed > 1./MANUAL_FPS:
            self.scanPrev = time.time()

            #Downsize the frame selection box for effiecncy
            copyFrame = cv2.resize(copyFrame,(self.resizedWidth, self.resizedHeight),fx=0,fy=0, interpolation = cv2.INTER_LINEAR)

            #Track the user difined object (update the object positions)
            success, boxes = self.multiTracker.update(copyFrame)
            
            #Check if any of the objects have failed
            for i, box in enumerate(boxes):
                copyFrame, failure = self.check_for_failure(success, box, i, copyFrame) #This function also draws the objects on frame for GUI view
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

    #Resize 'selection instructions' to fit frame
    def get_optimal_font_scale(self, text, width):
        for scale in reversed(range(0, 60, 1)):
            textSize = cv2.getTextSize(text, fontFace=cv2.FONT_HERSHEY_DUPLEX, fontScale=scale/10, thickness=1)
            new_width = textSize[0][0]
            if (new_width <= width):
                return scale/10
        return 1

    #True = failure has occured
    def check_for_failure(self, success, box, boxNum, cFrame):
        #If object lost : a failure has occured
        if success == False:
            return cFrame, True

        #Draw object on frame for GUI view
        (x,y,w,h) = [int(a) for a in box]
        cv2.rectangle(cFrame, (x,y), (x+w,y+h), (255,0,0), 1)
        cv2.putText(cFrame, "dO("+str(boxNum)+") "+str(self.objectCentrePositions[boxNum][1]), (x, y - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

        #Calculate the objects current horizontal center
        currnetObjectLineInSection = int(x + (w/2))

        #If the objects current horizontal center != the objects inital horizontal center +- self.failureCenterRange : a failure has occured
        if self.objectCentrePositions[boxNum][0] - self.failureCenterRange > currnetObjectLineInSection or currnetObjectLineInSection > self.objectCentrePositions[boxNum][0] + self.failureCenterRange:
            return cFrame, True

        return cFrame, False