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

class App:
    def __init__(self, window, window_title, video_source=0):
        self.window = window
        self.window.title(window_title)

        #Set timer
        self.scanPrev = 0.0
        self.filterFPS = 2

        #Set classes
        self.vid = readCapture.VideoCapture(video_source)
        self.ui = initialiseUI.UI(self.vid)
        self.initFrame = initialisingFrame.InitFrames(self.vid, self.ui, self.filterFPS)
        self.automatic = automaticDetection.AutoDect(self.vid, self.ui, self.initFrame, self.filterFPS)
        self.manual = manualDetection.ManualDetcAndTrak(self.vid, self.ui)
        self.fAlert = failureAlert.FailAlert(self.vid)

        #Set frame top crop
        self.topCut = 0

        #object failure startus
        self.objFail = False

        #Update Camera Frame
        self.delay = 15
        self.update()

        self.window.mainloop()

    def update(self):
        #Get a frame from the video source
        ret, frame = self.vid.get_frame()

        if ret:
            if self.ui.manualHasStarted == 0:
                frame = self.scan(frame)
            else:
                frame = self.manual_detection(frame)

            if self.ui.autoSensitivityChange:
                boxSides = round(math.sqrt(self.ui.sensitivityScl.get()))
                x = int(self.vid.width/2 - boxSides/2)
                y = int(self.vid.height/2 - boxSides/2)
                cv2.rectangle(frame, (x, y), (boxSides+x,boxSides+y), (255, 255, 255), 2)
                self.ui.autoSensitivityChange = False

            if self.ui.failureRangeChange:
                cv2.line(frame, (int(self.vid.width/2), 0), (int(self.vid.width/2),int(self.vid.height)), (255, 0, 0), 2)
                cv2.line(frame, (int(self.vid.width/2 - self.ui.failureRangeScl.get()), 0), (int(self.vid.width/2 - self.ui.failureRangeScl.get()),int(self.vid.height)), (0, 255, 0), 2)
                cv2.line(frame, (int(self.vid.width/2 + self.ui.failureRangeScl.get()), 0), (int(self.vid.width/2 + self.ui.failureRangeScl.get()),int(self.vid.height)), (0, 255, 0), 2)
                self.ui.failureRangeChange = False

            if self.objFail == True:
                self.fAlert.alert(frame)
                self.objFail = False

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

        time_elapsed = time.time() - self.scanPrev
        if time_elapsed > 1./self.filterFPS:
            self.scanPrev = time.time()

            if self.initFrame.currentAutoStatus == 0:
                self.initFrame.starting_motion_scan()
            elif self.initFrame.currentAutoStatus == 1:
                grayNFrame = self.initFrame.capture_initialising_frames()
                return grayNFrame
            elif self.initFrame.currentAutoStatus == 2:
                self.initFrame.stopped_motion_scan()
                self.topCut, self.objFail = self.automatic.get_contours(frame)

        #Give the appropriate info on GUI camera view 
        drawnOnFrame = self.automatic.draw_detection_results(frame)        
        drawnOnFrame = cv2.addWeighted(drawnOnFrame, 0.8, cropImg, 0.2, 0)
        return cv2.cvtColor(drawnOnFrame, cv2.COLOR_BGR2RGB)

    def manual_detection(self, frame):
        if self.ui.boxesGot == 1:
            editedframe, self.objFail = self.manual.manual_tracking(frame)
        else:
            #Stop automatic detection
            self.initFrame.manual_off()
            editedframe = self.manual.manual_object_seletion(frame)

        return cv2.cvtColor(editedframe, cv2.COLOR_BGR2RGB)


#Create a window and pass it to the Application object
App(tk.Tk(), "OpenCV On Tincker", "test.mp4")

