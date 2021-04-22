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

from constants import FILTER_FPS

class App:
    def __init__(self, window, window_title, video_source=0):
        self.window = window
        self.window.title(window_title)

        #Set timer
        self.scanPrev = 0.0

        #Set classes
        self.vid = readCapture.VideoCapture(video_source)
        self.vidWidth = int(self.vid.width)
        self.vidHeight = int(self.vid.height)

        self.uiVals = uiValues.UIVals(self.vidWidth, self.vidHeight)
        self.ui = initialiseUI.UI(self.vidWidth, self.vidHeight, self.uiVals)

        self.initFrame = initialisingFrame.InitFrames(self.vidWidth, self.vidHeight)
        self.initFrame.update_ui_values(self.uiVals)
        self.currentAutoInitStatus = 0 #0=ENGAGED, 1=STARTING, 2=DETECTING, 3=OFF 

        self.automatic = automaticDetection.AutoDect()
        self.initialisedAutomaticsFilters = False #applyFilters.py need intitlised later in automaticDetection.py

        self.manual = None #does manualDetection.py need to be (re)intitlised and ran

        #set object failure variable
        self.objFail = False

        #Set frame top crop (for GUI only)
        self.topCut = 0

        #Update Camera Frame
        self.delay = 1
        self.update()

        self.window.mainloop()

    def update(self):
        #Get a frame from the video source
        ret, frame = self.vid.get_frame()

        #If frame get is successful
        if ret: 
            if self.ui.manualHasStarted == False:
                frame = self.scan(frame) #automatic detection
            else:
                frame = self.manual_detection(frame) #manual detection

            #If GUI values are change display on GUI camera view 
            if self.ui.valuesChange:
                frame, self.ui.valuesChange = self.display_ui_changes(frame) #2nd returned parameter always False to reset self.ui.valuesChange

            #If failure detected alert user
            if self.objFail == True:
                failureAlert.alert(frame)
                self.objFail = False

            #Display the edited camera view (frame) on the GUI
            self.photo = ImageTk.PhotoImage(image = Image.fromarray(frame))
            self.ui.canvas.create_image(0, 0, image = self.photo, anchor = tk.NW)

        self.window.after(self.delay, self.update) #UI infinite loop

    #Automatic detection
    def scan(self, frame): 
        #Timer delay for "FILTER_FPS" seconds  
        time_elapsed = time.time() - self.scanPrev
        if time_elapsed > 1./FILTER_FPS:
            self.scanPrev = time.time()

            #Update FSM status based on movement : ENGAGED -> STARTING OR OFF -> ENGAGED
            self.currentAutoInitStatus = self.initFrame.motion_scan(frame, self.currentAutoInitStatus)

            #If ENGAGED
            if self.currentAutoInitStatus == 0:
                #Clear previous objects and forget about previous applyFilters.py initilisations
                if self.initialisedAutomaticsFilters:
                    self.automatic.clear_objects()
                    self.initialisedAutomaticsFilters = False
                self.ui.autoStatusLbl.config(text="Automatic Detection (-ENGAGED-)")  
            #If STARTING   
            elif self.currentAutoInitStatus == 1:
                self.ui.autoStatusLbl.config(text="Automatic Detection (-STARTING-)")
                self.currentAutoInitStatus, grayNFrame = self.initFrame.capture_initialising_frames(frame) #Take screenshots for sample based background removal
                return grayNFrame
            #If DETECTING
            elif self.currentAutoInitStatus == 2:
                #Intitlise applyFilters.py in automaticDetection.py if needed
                if not self.initialisedAutomaticsFilters:
                    self.ui.autoStatusLbl.config(text="Automatic Detection (-DETECTING-)")
                    self.initialisedAutomaticsFilters = self.automatic.initialise_apply_filters(self.vidWidth, self.vidHeight, self.initFrame.initialFrames)
                    self.automatic.update_ui_values(self.uiVals)
                self.topCut, self.objFail = self.automatic.get_contours(frame) #AUTOMATIC OBJECT DETECTION CALL

        #Draw the detected objects onto the GUI camera feed 
        if self.currentAutoInitStatus == 2:
            frame = self.automatic.draw_detection_results(frame)  
            
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    #Manual detection
    def manual_detection(self, frame):
        editedframe = frame

        #If manual detection has started
        if self.manual:
            #If user has select objects to track
            if any(self.manual.objectCentrePositions):
                editedframe, self.objFail = self.manual.manual_tracking(frame) #MANUAL OBJECT TRACKING CALL
                if self.objFail: 
                    self.ui.start_manual()
            else:
                editedframe = self.manual.manual_object_seletion(frame, self.uiVals.noOfModels) #User object seletion
        else:
            #Stop automatic detection and Start Manual 
            self.currentAutoInitStatus = 3
            self.ui.autoStatusLbl.config(text="Automatic Detection (-OFF-)")
            self.manual = manualDetection.ManualDetcAndTrak(self.vidWidth, self.vidHeight, self.uiVals.failureRangeScl)

        #If user click manual stop button reset manual config
        if self.ui.manualHasStopped == True:
            self.manual = None
            self.ui.manualHasStarted = False
            self.ui.manualHasStopped = False

        return cv2.cvtColor(editedframe, cv2.COLOR_BGR2RGB)

    #Display UI changes on the camera feed
    def display_ui_changes(self, frame):
        fr = self.uiVals.failureRangeScl 

        #Area of detection
        if self.ui.widgetName == "Crop": 
            leftCut = self.uiVals.cutLeftScl
            rightCut = (self.vidWidth - self.uiVals.cutRightScl)
            bottomCut = (self.vidHeight - self.uiVals.cutBottomScl)

            cropImg = np.zeros((self.vidHeight, self.vidWidth, 3), np.uint8)
            cropImg = cv2.rectangle(cropImg, (leftCut, self.topCut), (rightCut, bottomCut), (255, 255, 255), -1)

            frame = cv2.addWeighted(frame, 0.8, cropImg, 0.2, 0)

        #Minimum object area to count
        elif self.ui.widgetName == "Sensitivity":
            boxSides = round(math.sqrt(self.uiVals.sensitivityScl))
            x = int(self.vidWidth/2 - boxSides/2)
            y = int(self.vidHeight/2 - boxSides/2)
            cv2.rectangle(frame, (x, y), (boxSides+x,boxSides+y), (255, 255, 255), 2)

        #Horizontal Failure Leeway
        elif self.ui.widgetName == "FailureRange":
            cv2.line(frame, (int(self.vidWidth/2), 0), (int(self.vidWidth/2),self.vidHeight), (255, 0, 0), 2)
            cv2.line(frame, (int(self.vidWidth/2 - fr), 0), (int(self.vidWidth/2 - fr),self.vidHeight), (0, 255, 0), 2)
            cv2.line(frame, (int(self.vidWidth/2 + fr), 0), (int(self.vidWidth/2 + fr),self.vidHeight), (0, 255, 0), 2)

        #Update the other classes about the UI changes (they store values seperatly as to not constanly request info from the UI class)
        if not self.manual:
            self.automatic.update_ui_values(self.uiVals)
            self.initFrame.update_ui_values(self.uiVals)
        else:
            self.manual.set_ui_values(fr)

        return frame, False


#Create a window and pass it to the Application object
App(tk.Tk(), "3D Print Failure Detection", "test.mp4")

