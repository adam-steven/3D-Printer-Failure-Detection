import tkinter as tk
import cv2
import numpy as np
from PIL import Image, ImageTk
import time
from random import randint

import readCapture
import initialiseUI
import applyFilters

class App:
    def __init__(self, window, window_title, video_source=0):
        self.window = window
        self.window.title(window_title)

        self.vid = readCapture.VideoCapture(video_source)
        self.ui = initialiseUI.UI(self.vid)
        self.filter = applyFilters.ApFil(self.vid, self.ui)

        self.currentDetectedContours = []

        self.contourToObjectLeeway = 50

        self.potentialObjects = [] 
        self.defintieObjects = [] 

        #Shrink the detected rectangle to seperate object overlap
        self.autoDetectionsShrink = 1.5

        #Timer
        self.scanPrev = 0.0
        self.filterFPS = 2

        self.topCut = 0

        self.manualSizeDown = 2
        self.manualFPS = 25

        #Update Camera Frame
        self.delay = 15
        self.update()

        self.window.mainloop()

    def update(self):
        #Get a frame from the video source
        ret, frame = self.vid.get_frame()
        if self.ui.manualHasStarted == 0:
            frame = self.scan(frame)
        else:
            frame = self.manual_tracking(frame)

        if ret:
            self.photo = ImageTk.PhotoImage(image = Image.fromarray(frame))
            self.ui.canvas.create_image(0, 0, image = self.photo, anchor = tk.NW)

        if self.ui.simetricalXcut.get() == 1:
            self.ui.cutRightScl.set(self.ui.cutLeftScl.get())

        self.window.after(self.delay, self.update)

    def scan(self, frame):
        #Gets a new frame for update() and proccesses it
        leftCut = self.ui.cutLeftScl.get()
        rightCut = (int(self.vid.width) - self.ui.cutRightScl.get())
        bottomCut = (int(self.vid.height) - self.ui.cutBottomScl.get())

        cropImg = np.zeros((int(self.vid.height), int(self.vid.width), 3), np.uint8)
        cropImg = cv2.rectangle(cropImg, (leftCut, self.topCut), (rightCut, bottomCut), (255, 255, 255), -1)

        if(self.ui.autoHasStarted == 1):
            time_elapsed = time.time() - self.scanPrev

            if self.ui.initialFramesGot == 1:
                if time_elapsed > 1./self.filterFPS:
                    self.scanPrev = time.time()
                    self.currentDetectedContours.clear()
                    #Filter current frame
                    self.topCut, filteredFrame = self.filter.filter_frame(frame)
                    #Get object contours from filterd frame
                    contours, hierarchy = cv2.findContours(filteredFrame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

                    newPotentialObjects = []

                    for contour in contours:
                        if cv2.contourArea(contour) < int(self.ui.sensitivityScl.get()):
                            continue
                        #Shrink the detected rectangle to seperate object overlap
                        (x, y, w, h) = cv2.boundingRect(contour)
                        resizedContour = tuple([leftCut + x, self.topCut + y, int(w/self.autoDetectionsShrink), int(h/self.autoDetectionsShrink)])
                        self.currentDetectedContours.append(resizedContour)

                        newPotentialObject = 1

                        if any(self.potentialObjects):
                            for pObject in self.potentialObjects:
                                intersect = self.rectOverLapCheck(resizedContour, pObject[0])
                                if intersect:
                                    pObject[1] = pObject[1] + 2

                                    contourYcenter = resizedContour[1]+(resizedContour[3]/2)
                                    objectYcenter = pObject[0][1]+(pObject[0][3]/2)

                                    ox = min(resizedContour[0], pObject[0][0])
                                    if (pObject[0][0] + (pObject[0][2]/2)) < resizedContour[0]:
                                        ox = ox + 1

                                    ow = max(resizedContour[2], pObject[0][2])
                                    if (pObject[0][0] + pObject[0][2]) < (resizedContour[0] + resizedContour[2]):
                                        ow = (resizedContour[0] + resizedContour[2]) - ox

                                    oh = max(resizedContour[3], pObject[0][3])
                                    oy = int((((objectYcenter+contourYcenter)/2) + objectYcenter)/2) - int(pObject[0][3]/2)
      
                                    pObject[0] = tuple([ox,oy,ow,oh])
                                    newPotentialObject = 0
                        
                        if newPotentialObject == 1:
                            newPotentialObjects.append([resizedContour, 2])

                    for npo in newPotentialObjects:
                        self.potentialObjects.append(npo)
                    newPotentialObjects.clear()

                    #Clean potentialObject list (delete object with -1 counter)(combine objects that are intersecting)
                    combinedPotentialObjects = []
                    if any(self.potentialObjects):
                        for i, pObject in enumerate(self.potentialObjects):
                            for j, potentialO in enumerate(self.potentialObjects):
                                intersect = self.rectOverLapCheck(pObject[0], potentialO[0])
                                if intersect and j != i and pObject[1] > 0 and potentialO[1] > 0:
                                    newObjectCounter = max(pObject[1], potentialO[1]) + 2
                                    pObject[1] = -1
                                    potentialO[1] = -1

                                    (o1x,o1y,o1w,o1h) = pObject[0]
                                    (o2x,o2y,o2w,o2h) = potentialO[0]

                                    ow = max(o1w, o2w)
                                    oh = int(max((o1y+o1h), (o2y+o2h)) - min(o1y, o2y))
                                    ox = int(((o1x + (o1w/2)) + (o2x + (o2w/2)))/2) - int(ow/2)
                                    oy = int(((o1y + (o1h/2)) + (o2y + (o2h/2)))/2) - int(oh/2)

                                    self.potentialObjects.pop(j) 
                                    combinedPotentialObjects.append([tuple([ox,oy,ow,oh]), newObjectCounter])
                                    
                            pObject[1] = pObject[1] - 1
                            if pObject[1] < 0:
                                self.potentialObjects.pop(i)

                    for cpo in combinedPotentialObjects:
                        self.potentialObjects.append(cpo)
                    combinedPotentialObjects.clear()
                
                #Display the contours and objects
                if any(self.potentialObjects):
                    for pObject in self.potentialObjects:
                        cv2.rectangle(frame, pObject[0], (255, 0, 0), 2)
                #else:  
                #for object in self.currentDetectedContours:
                #    cv2.rectangle(frame, object, (0, 255, 0), 2)

            else:
                #Capture inital print frame for sample based background removal
                if time_elapsed > 1./float(self.ui.capturesPerSecond.get()):
                    self.scanPrev = time.time()
                    _, newFrame = self.vid.get_frame()
                    grayNFrame = cv2.cvtColor(newFrame, cv2.COLOR_BGR2GRAY)
                    self.ui.initialFrames.append(grayNFrame)
                    self.ui.currentStartingFramesGot += 1

                    if self.ui.currentStartingFramesGot > self.ui.totalCapFramesNeeded:
                        self.ui.initialFramesGot = 1
                    return grayNFrame

        frame = cv2.addWeighted(frame, 0.8, cropImg, 0.2, 0)
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


    def manual_tracking(self, frame):
        time_elapsed = time.time() - self.scanPrev
        
        if self.ui.boxesGot == 1:
            if time_elapsed > 1./self.manualFPS:
                frame = cv2.resize(frame,(int(self.vid.width/self.manualSizeDown), int(self.vid.height/self.manualSizeDown)),fx=0,fy=0, interpolation = cv2.INTER_CUBIC)
                self.scanPrev = time.time()
                success, boxes = self.ui.multiTracker.update(frame)

                for box in boxes:
                    (x,y,w,h) = [int(a) for a in box]
                    cv2.rectangle(frame, (x,y), (x+w,y+h), (255,0,0), 1)
     
        else:
            trackerCounter = int(self.ui.noOfModels.get())
            for i in range(trackerCounter):
                 cv2.rectangle(frame, (0,0), (int(self.vid.width),50), (255, 255, 255), -1)
                 cv2.rectangle(frame, (0,0), (int(self.vid.width),50), (0, 0, 0), 2)
                 text = 'SELECT MODEL ' + str(i+1) + ' (BASE) - ENTER TO CONTINUE - AVOID SELECTING PRINT HEAD (INCLUDING NOZZLE)'
                 fontscale = self.get_optimal_font_scale(text, int(self.vid.width))
                 cv2.putText(frame, text, (10, 35), cv2.FONT_HERSHEY_SIMPLEX, fontscale, (0, 0, 0), 2)

                 bbox = cv2.selectROI('FrameTrack '+ str(i+1), frame)
                 tracker = cv2.TrackerBoosting_create()

                 frame = cv2.resize(frame,(int(self.vid.width/self.manualSizeDown), int(self.vid.height/self.manualSizeDown)),fx=0,fy=0, interpolation = cv2.INTER_CUBIC)
                 resizedBbox = tuple(int(x/self.manualSizeDown) for x in bbox)

                 self.ui.multiTracker.add(tracker, frame, resizedBbox)

                 self.ui.boxesGot = 1
                 cv2.destroyWindow('FrameTrack '+str(i+1))
        
        frame = cv2.resize(frame,(int(self.vid.width), int(self.vid.height)),fx=0,fy=0, interpolation = cv2.INTER_CUBIC)
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def get_optimal_font_scale(self, text, width):
        for scale in reversed(range(0, 60, 1)):
            textSize = cv2.getTextSize(text, fontFace=cv2.FONT_HERSHEY_DUPLEX, fontScale=scale/10, thickness=1)
            new_width = textSize[0][0]
            if (new_width <= width):
                return scale/10
        return 1

    def rectOverLapCheck(self, contourRect, objectRect):
        #(x, y, w, h)
        #Shrink the detected rectangle to seperate object overlap
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


#Create a window and pass it to the Application object
App(tk.Tk(), "OpenCV On Tincker", "test.mp4")

