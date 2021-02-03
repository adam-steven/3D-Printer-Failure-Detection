import cv2
import numpy as np

import applyFilters


#Detects contours > potential objects > confirmed objects from a given frame
class AutoDect:
    def __init__(self, vid, ui, initFrame):
        self.vid = vid
        self.ui = ui
        self.filter = applyFilters.ApFil(self.vid, self.ui, initFrame)

        self.currentDetectedContours = [] #FOR TESTING REMOVE LATER
        self.potentialObjects = [] # [[x,y,w,h],[number of conecutive detection],[number of missed detection]]

        self.topCut = 15

    def get_contours(self, frame):
        leftCut = self.ui.cutLeftScl.get()
        self.currentDetectedContours.clear()
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

            newPotentialObject = 1

            if any(self.potentialObjects):
                for pObject in self.potentialObjects:
                    (obx, oby, obw, obh) = pObject[0]
                    averagedpObject = tuple([obx/pObject[1], oby/pObject[1], obw/pObject[1], obh/pObject[1]])

                    intersect = self.rect_over_lap_check(tuple([cx, cy, cw, ch]), averagedpObject)
                    if intersect:

                        #print ("C-O INTERSECT" + str(tuple([cx, cy, cw, ch])) + " " + str(averagedpObject))
                        
                        ox = cx + obx
                        oy = cy + oby
                        ow = cw + obw
                        oh = ch + obh

                        pObject[1] = pObject[1] + 1
                        pObject[2] = pObject[2] - 1

                        pObject[0] = tuple([ox,oy,ow,oh])
                        newPotentialObject = 0
                        
            if newPotentialObject == 1:
                newPotentialObjects.append([tuple([cx, cy, cw, ch]), 1, 0])
                #print ("NEW OBJECT ADDED (" + str([tuple([cx, cy, cw, ch]), 1, 0]) + ")")

        #Add new potential object after scan to stop detection doubling up
        for npo in newPotentialObjects:
            self.potentialObjects.append(npo)
        newPotentialObjects.clear()

        self.clean_potential_object_list()
        #resultsFrame = self.draw_detection_results(frame)

        return self.topCut

    #Clean potentialObject list (delete object with -1 counter)(combine objects that are intersecting)
    def clean_potential_object_list(self):
        cleanedPotentialObjectsArray = []
        cleanedPotentialObjectsArray.clear()

        if any(self.potentialObjects):
            #Combine overlapping objects
            for i, pObject in enumerate(self.potentialObjects):
                for j, potentialO in enumerate(self.potentialObjects):

                    (o1x,o1y,o1w,o1h) = pObject[0]
                    (o2x,o2y,o2w,o2h) = potentialO[0]

                    averagedpObject1 = tuple([o1x/pObject[1], o1y/pObject[1], o1w/pObject[1], o1h/pObject[1]])
                    averagedpObject2 = tuple([o2x/potentialO[1], o2y/potentialO[1], o2w/potentialO[1], o2h/potentialO[1]])

                    intersect = self.rect_over_lap_check(averagedpObject1, averagedpObject2)
                    if intersect and j != i and pObject[2] > -10000000 and potentialO[2] > -10000000:

                        #print ("O-O INTERSECT" + str(averagedpObject1) + " " + str(averagedpObject2))

                        ox = o1x + o2x
                        oy = o1y + o2y
                        ow = o1w + o2w
                        oh = o1h + o2h

                        newDetectedCounter = pObject[1] + potentialO[1]
                        newMissedCounter = pObject[1] + potentialO[1]

                        pObject[2] = -10000000
                        potentialO[2] = -10000000

                        self.potentialObjects.pop(j) 
                        cleanedPotentialObjectsArray.append([tuple([ox,oy,ow,oh]), newDetectedCounter, newMissedCounter])

            #Remove all objects below a counter of 0
            for pObject in self.potentialObjects:
                if pObject[1] >= pObject[2] and pObject[2] != -10000000:
                    pObject[2] = pObject[2] + 1
                    cleanedPotentialObjectsArray.append(pObject)
                #else:
                #    print ("OBJECT DELETION " + str(pObject))

            self.potentialObjects.clear()
            self.potentialObjects = cleanedPotentialObjectsArray.copy()


    def draw_detection_results(self, frame):
        copyFrame = frame.copy()

        #FOR TESTING REMOVE LATER
        for cont in self.currentDetectedContours:
            cv2.rectangle(copyFrame, cont, (0, 255, 0), 2)

        #Display the contours and objects
        if any(self.potentialObjects):
            for pObject in self.potentialObjects:
                (x, y, w, h) = pObject[0]
                averagedObject = tuple([int(x/pObject[1]), int(y/pObject[1]), int(w/pObject[1]), int(h/pObject[1])])
                cv2.rectangle(copyFrame, averagedObject, (255, 0, 0), 2)
    
        return copyFrame


    def rect_over_lap_check(self, contourRect, objectRect):
        #(x, y, w, h)
        r1Left = contourRect[0]
        r1Right = contourRect[0] + contourRect[2]
        r1Top = contourRect[1]
        r1Bottom = contourRect[1] + contourRect[3]

        r2Left = objectRect[0]
        r2Right = objectRect[0] + objectRect[2]
        r2Top = objectRect[1]
        r2Bottom = objectRect[1] + objectRect[3]

        #If one rectangle is on left side of other
        if r1Left > r2Right or r2Left > r1Right:
            return False

        #If one rectangle is above other
        if r1Top > r2Bottom or r2Top > r1Bottom:
            return False

        return True

