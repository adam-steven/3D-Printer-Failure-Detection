import cv2
import numpy as np

import applyFilters


#Detects contours > potential objects > confirmed objects from a given frame
class AutoDect:
    def __init__(self, vid, ui, initFrame, filterFPS):
        self.vid = vid
        self.ui = ui
        self.filter = applyFilters.ApFil(self.vid, self.ui, initFrame)

        self.currentDetectedContours = [] #FOR TESTING REMOVE LATER
        self.potentialObjects = [] # [[x,y,w,h],[number of conecutive detection],[number of missed detection]]
        self.definiteObjects = [] # [[x,y,w,h],[number of missed detection (RESETS)]]

        self.topCut = 15

        #If potential object exists for minsBeforeCertain (seconds) its a definite object - i.e defObjectConFrames = minsBeforeCertain * filterFPS
        minsBeforeCertain = 60 #seconds
        self.defObjectConFrames = filterFPS * minsBeforeCertain


    def get_contours(self, frame):
        leftCut = self.ui.cutLeftScl.get()
        self.currentDetectedContours.clear() #FOR TESTING REMOVE LATER
        #Filter current frame
        self.topCut, filteredFrame = self.filter.filter_frame(frame)
        cv2.imshow("filter", filteredFrame)

        #Get object contours from filterd frame
        contours, hierarchy = cv2.findContours(filteredFrame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        newPotentialObjects = []

        for contour in contours:
            if cv2.contourArea(contour) < int(self.ui.sensitivityScl.get()):
                continue

            (cx, cy, cw, ch) = cv2.boundingRect(contour)
            cx = leftCut + cx
            cy = self.topCut + cy
            self.currentDetectedContours.append(tuple([cx, cy, cw, ch])) #FOR TESTING REMOVE LATER

            newPotentialObject = True

            #Check if any of the contours are in a definite object
            if any(self.definiteObjects):
                newPotentialObject = self.not_touching_a_definite_object(tuple([cx, cy, cw, ch])) 

            #Check if any of the contours are in a potential object
            if any(self.potentialObjects) and newPotentialObject == True:
                for pObject in self.potentialObjects:
                    (obx, oby, obw, obh) = pObject[0]
                    averagedpObject = [val/pObject[1] for val in pObject[0]]

                    _, _, intersect = self.rect_over_lap_check(tuple([cx, cy, cw, ch]), averagedpObject)
                    if intersect:
                        #Calculate the avarage between the contour & pObject for the new pObject values
                        ox, oy, ow, oh, consDetection, missDetection = self.calculate_avaraged_pobject(cx,cy,cw,ch, obx,oby,obw,obh, pObject[1],pObject[2], 1,-1)

                        pObject[0] = tuple([ox,oy,ow,oh])
                        pObject[1] = consDetection
                        pObject[2] = missDetection

                        newPotentialObject = False
                        break

            if newPotentialObject == True:
                newPotentialObjects.append([tuple([cx, cy, cw, ch]), 1, 0])

        #Add new potential object after scan to stop detection doubling up
        for npo in newPotentialObjects:
            self.potentialObjects.append(npo)
        newPotentialObjects.clear()

        self.clean_potential_object_list()
        objectLost = self.handle_definite_objects()

        return self.topCut, objectLost

    #Clean potentialObject list (delete object with -1 counter)(combine objects that are intersecting)
    def clean_potential_object_list(self):
        cleanedPotentialObjectsArray = []
        cleanedPotentialObjectsArray.clear()

        if any(self.potentialObjects):
            #Combine overlapping objects
            for i, pObject in enumerate(self.potentialObjects):
                for j, potentialO in enumerate(self.potentialObjects):
                    if j != i:
                        (o1x,o1y,o1w,o1h) = pObject[0]
                        (o2x,o2y,o2w,o2h) = potentialO[0]

                        averagedpObject1 = [val/pObject[1] for val in pObject[0]]
                        averagedpObject2 = [val/potentialO[1] for val in potentialO[0]]

                        _, _, intersect = self.rect_over_lap_check(averagedpObject1, averagedpObject2)
                        if intersect and pObject[2] > -10000000 and potentialO[2] > -10000000:

                            #Combine the pObjects to a new pObject
                            ox, oy, ow, oh, consDetection, missDetection = self.calculate_avaraged_pobject(o1x,o1y,o1w,o1h, o2x,o2y,o2w,o2h, pObject[1],pObject[1], potentialO[1],potentialO[1])
                            cleanedPotentialObjectsArray.append([tuple([ox,oy,ow,oh]), consDetection, missDetection])

                            #Delete the old pObjects
                            pObject[2] = -10000000
                            potentialO[2] = -10000000
                            self.potentialObjects.pop(j) 
                        
            #Remove all objects below a counter of 0
            for pObject in self.potentialObjects:
                if pObject[1] >= pObject[2] and pObject[2] != -10000000:
                    pObject[2] = pObject[2] + 1
                    cleanedPotentialObjectsArray.append(pObject)

            self.potentialObjects.clear()

            #Check if any of the potential object are in a definite object
            if any(self.definiteObjects):
                for pObject in cleanedPotentialObjectsArray:
                    averagedpObject = [val/pObject[1] for val in pObject[0]]

                    if self.not_touching_a_definite_object(averagedpObject) == True:
                        self.potentialObjects.append(pObject)
            else:
                self.potentialObjects = cleanedPotentialObjectsArray.copy()


    def handle_definite_objects(self):
        #Check if their is new definite object
        if any(self.potentialObjects):
            for pObject in self.potentialObjects:
                if pObject[1] > self.defObjectConFrames: 
                    averagedpObject = [int(val/pObject[1]) for val in pObject[0]]
                    self.definiteObjects.append([averagedpObject, self.defObjectConFrames])
                    pObject[2] = -10000000

        #Check if any definite object are lost
        stillAliveObjects = []
        stillAliveObjects.clear()
        objectLost = False
        if any(self.definiteObjects):
            for dObject in self.definiteObjects:
                if dObject[1] >= 0:
                    stillAliveObjects.append(dObject)
                else:
                    objectLost = True
                    
                dObject[1] = dObject[1] - 1
            
            self.definiteObjects.clear()
            self.definiteObjects = stillAliveObjects.copy()
            
        #Return True is a definite object is deleted
        return objectLost


    def draw_detection_results(self, frame):
        copyFrame = frame.copy()

        #FOR TESTING REMOVE LATER
        for cont in self.currentDetectedContours:
            cv2.rectangle(copyFrame, cont, (0, 255, 0), 2)

        #Display the potential objects
        if any(self.potentialObjects):
            for pObject in self.potentialObjects:
                averagedObject = [int(val/pObject[1]) for val in pObject[0]]
                cv2.rectangle(copyFrame, averagedObject, (255, 0, 0), 2)
                cv2.putText(copyFrame, "pO "+str(pObject[1])+" "+str(pObject[2]), (averagedObject[0], averagedObject[1] - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

        #Display the definite objects
        if any(self.definiteObjects):
            for dObject in self.definiteObjects:
                cv2.rectangle(copyFrame, dObject[0], (0, 0, 255), 2)
                cv2.putText(copyFrame, "dO "+str(dObject[1]), (dObject[0][0], dObject[0][1] - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        return copyFrame

    def calculate_avaraged_pobject(self, x1,y1,w1,h1, x2,y2,w2,h2, cons1,miss1, cons2,miss2):
        ox = x1 + x2
        oy = y1 + y2
        ow = w1 + w2
        oh = h1 + h2

        consDetection = cons1 + cons2
        missDetection = miss1 + miss2

        return ox, oy, ow, oh, consDetection, missDetection

    def not_touching_a_definite_object(self, contourRect):
        for dObject in self.definiteObjects:
            intersectWidth , intersectHeight, intersect = self.rect_over_lap_check(contourRect, dObject[0])
            if intersect:

                #Check if the object centers are in the same sector (10 sectors)
                contourLineOnScreen = round(((contourRect[0] + (contourRect[2]/2))/self.vid.width) * 10) 
                objectLineOnScreen = round(((dObject[0][0] + (dObject[0][2]/2))/self.vid.width) * 10) 

                if intersectWidth > int(dObject[0][2]/2) and intersectHeight > int(dObject[0][3]/2) and contourLineOnScreen == objectLineOnScreen:
                    dObject[1] = self.defObjectConFrames 

                return False

        return True

    def rect_over_lap_check(self, contourRect, objectRect):
        #contourRectLeft = contourRect[0]                           objectRectLeft = objectRect[0]
        #contourRectRight = contourRect[0] + contourRect[2]         objectRectRight = objectRect[0] + objectRect[2]
        #contourRectTop = contourRect[1]                            objectRectTop = objectRect[1]
        #contourRectBottom = contourRect[1] + contourRect[3]        objectRectBottom = objectRect[1] + objectRect[3]

        intersectW = min((contourRect[0] + contourRect[2]), (objectRect[0] + objectRect[2])) - max(contourRect[0], objectRect[0])
        intersectH = min((contourRect[1] + contourRect[3]), (objectRect[1] + objectRect[3])) - max(contourRect[1], objectRect[1])

        if intersectW < 0 or intersectH < 0:
            return 0, 0, False

        return intersectW, intersectH, True

