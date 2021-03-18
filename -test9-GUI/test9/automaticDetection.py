import cv2

import applyFilters
import detectedObject

from constants import FAILER_TIMER, FILTER_FPS

#Checks in 2 gives contour rectangles are touching
def rect_over_lap_check(contourRect, objectRect):
    #intersect width = the furthest left, right side - the furthest right, left side
    intersectW = min((contourRect[0] + contourRect[2]), (objectRect[0] + objectRect[2])) - max(contourRect[0], objectRect[0])
    #intersect height = the hightest, object bottom - the lowest, object top
    intersectH = min((contourRect[1] + contourRect[3]), (objectRect[1] + objectRect[3])) - max(contourRect[1], objectRect[1])

    if intersectW < 0 or intersectH < 0:
        return 0, 0, False

    return intersectW, intersectH, True

#Detects contours > potential objects > confirmed objects
class AutoDect:
    def __init__(self):
        self.objects = [] #array of detectedObject.py
        self.filter = None

    #Delete all existing saved objects
    def clear_objects(self):
        self.objects.clear()

    #Save the needed GUI values
    def update_ui_values(self, uiVals):
        #If potential object exists for minsBeforeCertain (seconds) its a definite object - i.e defObjectConFrames = minsBeforeCertain * filterFPS
        self.defObjectFail = FAILER_TIMER * FILTER_FPS #seconds
        self.defObjectConFrames = FILTER_FPS * uiVals.certianTimeScl
        self.failureCenterRange = uiVals.failureRangeScl
        self.leftCut = uiVals.cutLeftScl
        self.objSizeThresh = uiVals.sensitivityScl

        #Tell applyFilters.py to save its needed GUI values 
        if self.filter:
            self.filter.update_ui_values(uiVals)

    #Set the applyFilters.py class
    def initialise_apply_filters(self, vidWidth, vidHeight, initFrames):
        self.filter = applyFilters.ApFil(vidWidth, vidHeight, initFrames)
        return True

    #MAIN AUTOMATIC OBJECT DETECTION FUCNTION
    def get_contours(self, frame):
        #Filter current frame
        topCut, filteredFrame = self.filter.filter_frame(frame)
        #cv2.imshow("filter", filteredFrame)

        #Get object contours from filterd frame
        _, contours, _ = cv2.findContours(filteredFrame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        newPotentialObjects = []

        #Go though the contours ordering new and recurring objects 
        for contour in contours:
            if cv2.contourArea(contour) < int(self.objSizeThresh):
                continue

            #Reposition contours to be in the full frame (instead of the cropped frame)
            (cx, cy, cw, ch) = cv2.boundingRect(contour)
            cx = self.leftCut + cx
            cy = topCut + cy

            newPotentialObject = True

            #compair the contour agenst the pre-existing objects
            for obj in self.objects:
                #Check if the current contour and object are touching
                avgLoc, cons, miss = obj.get_avr_obj()
                intersectWidth, intersectHeight, intersect = rect_over_lap_check(list((cx, cy, cw, ch)), avgLoc)

                #If they are touching (its a recurring object)
                if intersect:

                    objCenterLineMin = int(avgLoc[0] + (avgLoc[2]/2)) - self.failureCenterRange
                    objCenterLineMax = int(avgLoc[0] + (avgLoc[2]/2)) + self.failureCenterRange
                    contCenterLine = int(cx + (cw/2))
                    
                    #If the contour & object interct is geater that a 3rd of the object's size
                    if intersectWidth > int(avgLoc[2]/1.5) and intersectHeight > int(avgLoc[3]/1.5):
                        #If the contour's horizontal center = the object's horizontal center +- self.failureCenterRange
                        if objCenterLineMin < contCenterLine < objCenterLineMax:
                            obj.set_avr_obj(tuple([cx, cy, cw, ch]), 1, -1) #Add the counter's values to the object
                            
                            #If the object lasts for long enough to be a definite object
                            #Set the objects misses to 0 as it is now following the definite object rules (misses > self.defObjectFail = failure)  
                            if cons + 1 >= self.defObjectConFrames:
                                obj.reset_obj_misses()

                    newPotentialObject = False
                    break

            #If not touching any objects (its a new object)
            if newPotentialObject == True:
                newPotentialObjects.append(tuple([cx, cy, cw, ch])) #Add to the array of newPotentialObjects

        #Add new potential object after scan to stop detections doubling up
        for npo in newPotentialObjects:
            self.objects.append(detectedObject.Obj(npo, 1 , 0))
        newPotentialObjects.clear()

        #Delete objects that: are touching or were missed to many times. (+ identify failures)
        objectLost = self.clean_object_list()

        return topCut, objectLost

    #Clean potentialObject list 
    # *combine objects that are intersecting
    # *delete potential object with cons < misses
    # *delete definite object with misses > self.defObjectFail
    def clean_object_list(self):
        defObjectConFrames = self.defObjectConFrames
        objectLost = False

        #Combine overlapping objects
        for i, objI in enumerate(self.objects):
            for j, objJ in enumerate(self.objects):
                if i != j:
                    avgLocI, consI, missI = objI.get_avr_obj()
                    avgLocJ, consJ, missJ = objJ.get_avr_obj()

                    #check if the objects are touching
                    _, _, intersect = rect_over_lap_check(avgLocI, avgLocJ)
                    if intersect and missI > -1000 and missJ > -1000:

                        objJCenterLineMin = int(avgLocJ[0] + (avgLocJ[2]/2)) - self.failureCenterRange
                        objJCenterLineMax = int(avgLocJ[0] + (avgLocJ[2]/2)) + self.failureCenterRange
                        objICenterLine = int(avgLocI[0] + (avgLocI[2]/2))

                        #If object 1's horizontal center = the object 2's horizontal center +- self.failureCenterRange
                        if objJCenterLineMin < objICenterLine < objJCenterLineMax:
                            objI.set_avr_obj(avgLocJ, consJ, missJ) #Add the object 2's values to the object 1's
                            objJ.set_obj(tuple([0,0,0,0]), -10005, -10000) #set object 2's values to a garenteed deletion state

                            #If the combined object becomes a definite object
                            #Set the objects misses to 0 as it is now following the definite object rules (misses > self.defObjectFail = failure)  
                            if (consI + consJ) >= defObjectConFrames:
                                objI.reset_obj_misses()
                        break

        #Remove all objects that have been missed more than detected
        for obj in self.objects[:]:
            location, cons, misses = obj.get_obj()

            #Add 1 to the objects miss counter
            obj.set_obj(location, cons, (misses + 1)) 

            #If the object is a definite
            if cons >= defObjectConFrames:
                #If misses > self.defObjectFail : a failure has occured
                if misses > self.defObjectFail:
                    self.objects.remove(obj)
                    objectLost = True
            #If the object is a potential
            else: 
                #If cons < misses : delete the object (false positive)
                if cons < misses:
                    self.objects.remove(obj)

        return objectLost

    #Draw the detected objects onto the GUI camera feed
    def draw_detection_results(self, frame):
        copyFrame = frame.copy()

        blue = (255, 0, 0)
        red = (0, 0, 255)

        for obj in self.objects:
            avgLoc, cons, misses = obj.get_avr_obj()
            if cons < self.defObjectConFrames: #If the object is a potential : use blue
                cv2.rectangle(copyFrame,  (avgLoc[0], avgLoc[1]),  (avgLoc[2]+avgLoc[0], avgLoc[3]+avgLoc[1]), blue, 2)
                cv2.putText(copyFrame, "pO "+str(cons)+" "+str(misses), (avgLoc[0], avgLoc[1] - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, blue, 1)
            else: #If the object is a definite : use red
                cv2.rectangle(copyFrame, (avgLoc[0], avgLoc[1]),  (avgLoc[2]+avgLoc[0], avgLoc[3]+avgLoc[1]), red, 2)
                cv2.putText(copyFrame, "dO "+str(cons)+" "+str(misses), (avgLoc[0], avgLoc[1] - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, red, 1)

        return copyFrame





