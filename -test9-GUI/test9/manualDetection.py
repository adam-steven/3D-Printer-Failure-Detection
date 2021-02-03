import cv2
import numpy as np
import time

#User selects the object to be auto tracked 
class ManualDetcAndTrak:
    def __init__(self, vid, ui):
        self.ui = ui
        self.vid = vid

        self.scanPrev = 0.0

        self.manualSizeDown = 2
        self.manualFPS = 25

    def manual_object_seletion(self, frame):
        #Get user to select the objects
        trackerCounter = int(self.ui.noOfModels.get())
        for i in range(trackerCounter):
            #Reset frame size
            frame = cv2.resize(frame,(int(self.vid.width), int(self.vid.height)),fx=0,fy=0, interpolation = cv2.INTER_CUBIC)

            #Draw selection instructions
            cv2.rectangle(frame, (0,0), (int(self.vid.width),50), (255, 255, 255), -1)
            cv2.rectangle(frame, (0,0), (int(self.vid.width),50), (0, 0, 0), 2)
            text = 'SELECT MODEL ' + str(i+1) + ' (BASE) - ENTER TO CONTINUE - AVOID SELECTING PRINT HEAD (INCLUDING NOZZLE)'
            fontscale = self.get_optimal_font_scale(text, int(self.vid.width))
            cv2.putText(frame, text, (10, 35), cv2.FONT_HERSHEY_SIMPLEX, fontscale, (0, 0, 0), 2)

            #User selection
            bbox = cv2.selectROI('FrameTrack '+ str(i+1), frame)
            tracker = cv2.TrackerBoosting_create()

            #Downsize the frame selection box for effiecncy
            frame = cv2.resize(frame,(int(self.vid.width/self.manualSizeDown), int(self.vid.height/self.manualSizeDown)),fx=0,fy=0, interpolation = cv2.INTER_CUBIC)
            resizedBbox = tuple(int(x/self.manualSizeDown) for x in bbox)

            self.ui.multiTracker.add(tracker, frame, resizedBbox)

            self.ui.boxesGot = 1
            cv2.destroyWindow('FrameTrack '+str(i+1))

        return frame

    def manual_tracking(self, frame):
        time_elapsed = time.time() - self.scanPrev

        if time_elapsed > 1./self.manualFPS:
            frame = cv2.resize(frame,(int(self.vid.width/self.manualSizeDown), int(self.vid.height/self.manualSizeDown)),fx=0,fy=0, interpolation = cv2.INTER_CUBIC)
            self.scanPrev = time.time()
            success, boxes = self.ui.multiTracker.update(frame)

            for box in boxes:
                (x,y,w,h) = [int(a) for a in box]
                cv2.rectangle(frame, (x,y), (x+w,y+h), (255,0,0), 1)
        
        frame = cv2.resize(frame,(int(self.vid.width), int(self.vid.height)),fx=0,fy=0, interpolation = cv2.INTER_CUBIC)
        return frame

    #Size selection instructions to fit frame
    def get_optimal_font_scale(self, text, width):
        for scale in reversed(range(0, 60, 1)):
            textSize = cv2.getTextSize(text, fontFace=cv2.FONT_HERSHEY_DUPLEX, fontScale=scale/10, thickness=1)
            new_width = textSize[0][0]
            if (new_width <= width):
                return scale/10
        return 1

