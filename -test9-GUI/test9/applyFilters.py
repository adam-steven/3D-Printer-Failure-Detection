import cv2
import numpy as np
import time

#Filter out the irrelevent part of a given frame
class ApFil:
    def __init__(self, vidWidth, vidHeight, initFrames):

        self.vidWidth = vidWidth
        self.vidHeight = vidHeight
        self.oldTestingFrame = []

        self.initFrames = initFrames

        self.movingEdge = cv2.bgsegm.createBackgroundSubtractorMOG()

        #Timer
        self.hightPrev = 0.0
        self.hightFrameRate = 1

        self.kernel = np.ones((5,5),np.uint8)

        self.topCut = 10

    def update_ui_values(self, uiVals):
        self.leftCut = uiVals.cutLeftScl
        self.rightCut = self.vidWidth - uiVals.cutRightScl
        self.bottomCut = self.vidHeight - uiVals.cutBottomScl
        self.vivid = uiVals.vivid
        self.sensitivity = uiVals.sensitivityScl


    def filter_frame(self, newFrame):

        testingFrame = newFrame.copy()

        #Filter out irrelevent objects at the top of the frame/ shrick the frame 
        time_elapsed = time.time() - self.hightPrev
        if time_elapsed > 1./self.hightFrameRate:
            self.hightPrev = time.time()
            self.get_height_crop(testingFrame)

        #Crop frames to cropImg 
        croppedFrame = testingFrame[self.topCut:self.bottomCut, self.leftCut:self.rightCut]
                
        #Filter out the background 
        grayCFrame = cv2.cvtColor(croppedFrame, cv2.COLOR_BGR2GRAY)
        backFiltSum = grayCFrame
        for x in self.initFrames:
            diff = cv2.absdiff(x[self.topCut:self.bottomCut, self.leftCut:self.rightCut], grayCFrame)
            _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
            dilatedThresh = cv2.dilate(thresh, None, iterations=4)
            backFiltSum = cv2.bitwise_and(backFiltSum,dilatedThresh)

        #Filter out moving object edges
        fgmask = self.movingEdge.apply(croppedFrame)
        dilated = cv2.dilate(fgmask, None, iterations=4)
        fgmaskInvert = cv2.bitwise_not(dilated)

        #Filter out low saturation
        enhance = cv2.addWeighted(croppedFrame, 1, np.zeros(croppedFrame.shape, croppedFrame.dtype), 0, 0)
        hsv = cv2.cvtColor(enhance, cv2.COLOR_BGR2HSV)
        hue ,saturation ,value = cv2.split(hsv)                                                  
        retval, thresholded = cv2.threshold(saturation, self.vivid, 255, cv2.THRESH_BINARY)
        dilatedSaturation = thresholded #cv2.dilate(thresholded, None, iterations=2)

        #Combine the filters
        filterSum = cv2.bitwise_and(backFiltSum, fgmaskInvert)
        filterSum = cv2.bitwise_and(filterSum, dilatedSaturation)
        #medianFiltered = cv2.medianBlur(filterSum, 3)
        closing = cv2.morphologyEx(filterSum, cv2.MORPH_CLOSE, self.kernel)

        #Filter out everything above the lowest detected remaining objects 
        finalHeightFilter = self.get_low_crop(closing, (self.rightCut - self.leftCut))
        
        return self.topCut, finalHeightFilter

    def get_height_crop(self, testingFrame):
        highestMovingObject = self.vidHeight/2

        if np.any(self.oldTestingFrame):
            diff = cv2.absdiff(testingFrame, self.oldTestingFrame)
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

        self.oldTestingFrame = testingFrame.copy()
        self.topCut = int(highestMovingObject)

    def get_low_crop(self, frame, frameWidth):
        #Delete all detected objects other than the lowest one (to keep only the print(s))
        lowestObjects = 0

        contours, _ = cv2.findContours(frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            (x, y, w, h) = cv2.boundingRect(contour)

            if cv2.contourArea(contour) < self.sensitivity:
                continue
            if lowestObjects < (y - 10):
                lowestObjects = (y - 10)

        cv2.rectangle(frame, (0, 0), (frameWidth, lowestObjects), (0,0, 0), -1)
        return frame


