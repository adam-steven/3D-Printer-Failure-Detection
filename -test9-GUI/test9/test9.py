import tkinter as tk
from PIL import Image, ImageTk
import cv2
import numpy as np
import time
import math

import readCapture
import initialiseUI
import initialisingFrame
import automaticDetection
import manualDetection
import failureAlert
import uiValues

class App:
    def __init__(self, window, window_title, video_source=0):
        self.window = window
        self.window.title(window_title)

        #Set timer
        self.scanPrev = 0.0
        self.filterFPS = 1

        #Set classes
        self.vid = readCapture.VideoCapture(video_source)
        self.vidWidth = int(self.vid.width)
        self.vidHeight = int(self.vid.height)

        self.uiVals = uiValues.UIVals(self.vidWidth, self.vidHeight)
        self.ui = initialiseUI.UI(self.vidWidth, self.vidHeight, self.uiVals)

        self.initFrame = initialisingFrame.InitFrames(self.vidWidth, self.vidHeight, self.filterFPS)
        self.initFrame.update_ui_values(self.uiVals)
        self.currentAutoInitStatus = 0 # 0=ENGAGED, 1=STARTING, 2=DETECTING, 3=OFF 

        self.automatic = automaticDetection.AutoDect()
        self.initialisedAutomaticsFilters = False

        self.manual = None

        self.objFail = False

        #Set frame top crop
        self.topCut = 0

        #Update Camera Frame
        self.delay = 15
        self.update()

        self.window.mainloop()

    def update(self):
        #Get a frame from the video source
        ret, frame = self.vid.get_frame()

        if ret:
            if self.ui.manualHasStarted == False:
                frame = self.scan(frame)
            else:
                frame = self.manual_detection(frame)

            if self.ui.valuesChange:
                frame, self.ui.valuesChange = self.displayUiChanges(frame)

            if self.objFail == True:
                failureAlert.alert(frame)
                self.objFail = False

            self.photo = ImageTk.PhotoImage(image = Image.fromarray(frame))
            self.ui.canvas.create_image(0, 0, image = self.photo, anchor = tk.NW)

        self.window.after(self.delay, self.update)


    def scan(self, frame): 
        time_elapsed = time.time() - self.scanPrev
        if time_elapsed > 1./self.filterFPS:
            self.scanPrev = time.time()

            if self.currentAutoInitStatus == 0:
                self.ui.autoStatusLbl.config(text="Automatic Detection (-ENGAGED-)")
                self.currentAutoInitStatus = self.initFrame.starting_motion_scan(frame)
            elif self.currentAutoInitStatus == 1:
                self.ui.autoStatusLbl.config(text="Automatic Detection (-STARTING-)")
                self.currentAutoInitStatus, grayNFrame = self.initFrame.capture_initialising_frames(frame)
                return grayNFrame
            elif self.currentAutoInitStatus == 2:
                if not self.initialisedAutomaticsFilters:
                    self.ui.autoStatusLbl.config(text="Automatic Detection (-DETECTING-)")
                    self.initialisedAutomaticsFilters = self.automatic.initialiseApplyFilters(self.vidWidth, self.vidHeight, self.ui, self.initFrame.initialFrames)
                    self.automatic.update_ui_values(self.uiVals, self.filterFPS)
                self.currentAutoInitStatus = self.initFrame.stopped_motion_scan(frame)
                self.topCut, self.objFail = self.automatic.get_contours(frame)
            else:
                self.currentAutoInitStatus = self.initFrame.stopped_motion_scan(frame)
            
        #Give the appropriate info on GUI camera view 
        drawnOnFrame = self.automatic.draw_detection_results(frame)        
        return cv2.cvtColor(drawnOnFrame, cv2.COLOR_BGR2RGB)

    def manual_detection(self, frame):
        editedframe = frame

        if self.manual:
            if any(self.manual.objectCentrePositions):
                editedframe, self.objFail = self.manual.manual_tracking(frame)
                if self.objFail: 
                    self.ui.start_manual()
            else:
                editedframe = self.manual.manual_object_seletion(frame, self.ui.noOfModels.get())
        else:
            #Stop automatic detection and Start Manual 
            self.currentAutoInitStatus = 3
            self.ui.autoStatusLbl.config(text="Automatic Detection (-OFF-)")
            self.manual = manualDetection.ManualDetcAndTrak(self.vidWidth, self.vidHeight, self.uiVals.failureRangeScl)

        if self.ui.manualHasStopped == True:
            self.manual = None
            self.ui.manualHasStarted = False
            self.ui.manualHasStopped = False

        return cv2.cvtColor(editedframe, cv2.COLOR_BGR2RGB)

    def displayUiChanges(self, frame):
        #Gets a new frame for update() and proccesses it
        leftCut = self.ui.cutLeftScl.get()
        rightCut = (self.vidWidth - self.ui.cutRightScl.get())
        bottomCut = (self.vidHeight - self.ui.cutBottomScl.get())

        cropImg = np.zeros((self.vidHeight, self.vidWidth, 3), np.uint8)
        cropImg = cv2.rectangle(cropImg, (leftCut, self.topCut), (rightCut, bottomCut), (255, 255, 255), -1)

        frame = cv2.addWeighted(frame, 0.8, cropImg, 0.2, 0)

        boxSides = round(math.sqrt(self.ui.sensitivityScl.get()))
        x = int(self.vidWidth/2 - boxSides/2)
        y = int(self.vidHeight/2 - boxSides/2)
        cv2.rectangle(frame, (x, y), (boxSides+x,boxSides+y), (255, 255, 255), 2)

        cv2.line(frame, (int(self.vidWidth/2), 0), (int(self.vidWidth/2),self.vidHeight), (255, 0, 0), 2)
        cv2.line(frame, (int(self.vidWidth/2 - self.ui.failureRangeScl.get()), 0), (int(self.vidWidth/2 - self.ui.failureRangeScl.get()),self.vidHeight), (0, 255, 0), 2)
        cv2.line(frame, (int(self.vidWidth/2 + self.ui.failureRangeScl.get()), 0), (int(self.vidWidth/2 + self.ui.failureRangeScl.get()),self.vidHeight), (0, 255, 0), 2)

        if not self.manual:
            self.automatic.update_ui_values(self.uiVals, self.filterFPS)
            self.initFrame.update_ui_values(self.uiVals)
        else:
            self.manual.set_ui_values(self.ui.failureRangeScl.get())

        return frame, False


#Create a window and pass it to the Application object
App(tk.Tk(), "3D Print Failure Detection", "test.mp4")

