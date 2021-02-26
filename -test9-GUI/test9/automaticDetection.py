import cv2
import numpy as np

import applyFilters
import detectedObject

def rect_over_lap_check(contourRect, objectRect):
    #contourRectLeft = contourRect[0]                           objectRectLeft = objectRect[0]
    #contourRectRight = contourRect[0] + contourRect[2]         objectRectRight = objectRect[0] + objectRect[2]
    #contourRectTop = contourRect[1]                            objectRectTop = objectRect[1]
    #contourRectBottom = contourRect[1] + contourRect[3]        objectRectBottom = objectRect[1] + objectRect[3]

    intersectW = min((contourRect[0] + contourRect[2]), (objectRect[0] + objectRect[2])) - max(contourRect[0], objectRect[0])
    intersectH = min((contourRect[1] + contourRect[3]), (objectRect[1] + objectRect[3])) - max(contourRect[1], objectRect[1])

    if intersectW < 0 or intersectH < 0:
        return 0, 0, False

    return intersectW, intersectH, True

#Detects contours > potential objects > confirmed objects
class AutoDect:
    def __init__(self):
        self.objects = []
        self.filter = None

    #When the user updates the UI, the main app calls this function to update the UI valuse 
    def update_ui_values(self, uiVals, filterFPS):
        #If potential object exists for minsBeforeCertain (seconds) its a definite object - i.e defObjectConFrames = minsBeforeCertain * filterFPS
        self.defObjectFail = 10 * filterFPS #seconds
        self.defObjectConFrames = filterFPS * uiVals.certianTimeScl
        self.failureCenterRange = uiVals.failureRangeScl
        self.leftCut = uiVals.cutLeftScl
        self.objSizeThresh = uiVals.sensitivityScl

        if self.filter:
            self.filter.update_ui_values(uiVals)

    def initialiseApplyFilters(self, vidWidth, vidHeight, ui, initFrames):
        self.filter = applyFilters.ApFil(vidWidth, vidHeight, initFrames)
        return True

    def get_contours(self, frame):
        #Filter current frame
        topCut, filteredFrame = self.filter.filter_frame(frame)
        cv2.imshow("filter", filteredFrame)

        #Get object contours from filterd frame
        contours, hierarchy = cv2.findContours(filteredFrame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        newPotentialObjects = []

        for contour in contours:
            if cv2.contourArea(contour) < int(self.objSizeThresh):
                continue

            (cx, cy, cw, ch) = cv2.boundingRect(contour)
            cx = self.leftCut + cx
            cy = topCut + cy

            newPotentialObject = True

            for obj in self.objects:
                avgLoc, cons, miss = obj.get_avr_obj()
                intersectWidth, intersectHeight, intersect = rect_over_lap_check(tuple([cx, cy, cw, ch]), avgLoc)
                if intersect:

                    objCenterLineMin = int(avgLoc[0] + (avgLoc[2]/2)) - self.failureCenterRange
                    objCenterLineMax = int(avgLoc[0] + (avgLoc[2]/2)) + self.failureCenterRange
                    contCenterLine = int(cx + (cw/2))
                    
                    if intersectWidth > int(avgLoc[2]/1.5) and intersectHeight > int(avgLoc[3]/1.5):
                        if objCenterLineMin < contCenterLine < objCenterLineMax:
                            if cons < self.defObjectConFrames:
                                missDegrader = -1 #to insure the miss counter never goes below -1 
                                if miss < 1: missDegrader = 0
                                obj.set_avr_obj(tuple([cx, cy, cw, ch]), 1, missDegrader)
                            else:
                                obj.set_avr_obj(tuple([0, 0, 0, 0]), 0, -miss)

                    newPotentialObject = False
                    break

            if newPotentialObject == True:
                newPotentialObjects.append(tuple([cx, cy, cw, ch]))

        #Add new potential object after scan to stop detection doubling up
        for npo in newPotentialObjects:
            self.objects.append(detectedObject.Obj(npo, 1 , 0))
        newPotentialObjects.clear()

        objectLost = self.clean_object_list()

        return topCut, objectLost

    #Clean potentialObject list (delete object with -1 counter)(combine objects that are intersecting)
    def clean_object_list(self):
        defObjectConFrames = self.defObjectConFrames
        objectLost = False

        #Combine overlapping objects
        for i, objI in enumerate(self.objects):
            for j, objJ in enumerate(self.objects):
                if i != j:
                    avgLocI, consI, missI = objI.get_avr_obj()
                    avgLocJ, consJ, missJ = objJ.get_avr_obj()

                    _, _, intersect = rect_over_lap_check(avgLocI, avgLocJ)
                    if intersect and missI > -1000 and missJ > -1000:

                        objJCenterLineMin = int(avgLocJ[0] + (avgLocJ[2]/2)) - self.failureCenterRange
                        objJCenterLineMax = int(avgLocJ[0] + (avgLocJ[2]/2)) + self.failureCenterRange
                        objICenterLine = int(avgLocI[0] + (avgLocI[2]/2))

                        if objJCenterLineMin < objICenterLine < objJCenterLineMax:
                            objI.set_avr_obj(avgLocJ, consJ, missJ)
                            objJ.set_obj(tuple([0,0,0,0]), -10005, -10000)

                            if (consI + consJ) >= defObjectConFrames:
                                objI.set_avr_obj(tuple([0, 0, 0, 0]), 0, -(missI + missJ))
                        break

        #Remove all objects that have been missed more than detected
        for obj in self.objects[:]:
            location, cons, misses = obj.get_obj()

            obj.set_obj(location, cons, (misses + 1)) 

            if cons >= defObjectConFrames:
                if misses > self.defObjectFail:
                    self.objects.remove(obj)
                    objectLost = True
            else:
                if cons < misses:
                    self.objects.remove(obj)

        return objectLost


    def draw_detection_results(self, frame):
        copyFrame = frame.copy()

        blue = (255, 0, 0)
        red = (0, 0, 255)

        for obj in self.objects:
            avgLoc, cons, misses = obj.get_avr_obj()
            if cons < self.defObjectConFrames:
                cv2.rectangle(copyFrame, avgLoc, blue, 2)
                cv2.putText(copyFrame, "pO "+str(cons)+" "+str(misses), (avgLoc[0], avgLoc[1] - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, blue, 1)
            else:
                cv2.rectangle(copyFrame, avgLoc, red, 2)
                cv2.putText(copyFrame, "dO "+str(cons)+" "+str(misses), (avgLoc[0], avgLoc[1] - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, red, 1)

        return copyFrame





