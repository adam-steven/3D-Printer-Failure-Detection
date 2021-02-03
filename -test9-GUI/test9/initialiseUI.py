import tkinter as tk
import numpy as np
from PIL import Image, ImageTk
import cv2
import numpy as np

#Initilise and handle tkinter ui elements
class UI:
    def __init__(self, vid):
        #--Interface Layout--
            #self.autoLblFrame = tk.Frame()
            #self.initialSamplesFrame = tk.Frame()
        self.optionsFrame = tk.Frame()
        self.manualSampelObjects = tk.Frame()
        self.videoFrame = tk.Frame()
        self.minUIWidth = 200

        #Grid used to add labels to the options menus
            #self.initialSamplesFrame.rowconfigure(0, minsize=50, weight=1)
            #self.initialSamplesFrame.columnconfigure([0, 1], minsize=50, weight=1)

        self.manualSampelObjects.rowconfigure(0, minsize=50, weight=1)
        self.manualSampelObjects.columnconfigure([0, 1], minsize=50, weight=1)

        #--Initialise UI Elements--
        #Create canvas from video source
        self.canvas = tk.Canvas(
            master=self.videoFrame, 
            width=vid.width, 
            height=vid.height
        )

        #########--Seperator (top gap)--#########
        self.startSep = tk.Canvas(master=self.optionsFrame, width=self.minUIWidth, height=4)
        ####################################

        self.autoStatusLbl = tk.Label(
            master=self.optionsFrame,
            text="Automatic Detection (-ENGAGED-)",
        )

            ##Create start detection button
            #self.autoHasStarted = 0
            #self.startBtn = tk.Button(
            #    master=self.startBtnFrame,
            #    text="Start Auto Detection",
            #    width=int(self.minUIWidth/8),
            #    height=2,
            #    command=self.start_auto
            #)

            ##########--Seperator Line--#########
            #self.sepLine = tk.Canvas(master=self.startBtnFrame, width=self.minUIWidth, height=4)
            #self.sepLine.create_rectangle(0, 1, self.minUIWidth, 2, fill="black", outline = 'black')
            #####################################

            #CAPTURES = list(range(1, 21))
            #DURATION = list(range(1, 31))

            ##Create drop down box for spesifiying the number of captures per second
            #self.capturesPerSecond = tk.StringVar(self.initialSamplesFrame)
            #self.capturesPerSecond.set(1)

            #self.cpsLbl = tk.Label(
            #    master=self.initialSamplesFrame,
            #    text="Captures Per Second",
            #)

            #self.cpsOpt = tk.OptionMenu(
            #    self.initialSamplesFrame, 
            #    self.capturesPerSecond, 
            #    *CAPTURES
            #)

            ##Create drop down box for spesifiying how long samples are captured (seconds) 
            #self.captureDuration = tk.StringVar(self.initialSamplesFrame)
            #self.captureDuration.set(4)

            #self.cdLbl = tk.Label(
            #    master=self.initialSamplesFrame,
            #    text="Captures Duration (Sec)",
            #)

            #self.cdOpt = tk.OptionMenu(
            #    self.initialSamplesFrame, 
            #    self.captureDuration, 
            #    *DURATION
            #)
 
        #########--Seperator Line--#########
        self.sepLine1 = tk.Canvas(master=self.optionsFrame, width=self.minUIWidth, height=4)
        self.sepLine1.create_rectangle(0, 1, self.minUIWidth, 2, fill="black", outline = 'black')
        ####################################

        #Create check box to ignod dull colour (aka. the printer)
        self.vivid = tk.IntVar()
        self.vivid.set(120)
        self.vividChk = tk.Checkbutton(
            master=self.optionsFrame, 
            text='Vivid Colour Mode',
            variable=self.vivid,
            onvalue=180,
            offvalue=120
        )

        #########--Seperator Line--#########
        self.sepLine2 = tk.Canvas(master=self.optionsFrame, width=self.minUIWidth, height=4)
        self.sepLine2.create_rectangle(0, 1, self.minUIWidth, 2, fill="black", outline = 'black')
        ####################################

        #Create slider for BLOB area threshold
        self.sensitivityScl = tk.Scale(
            master=self.optionsFrame,
            label="Sensitivity",
            from_=200, 
            to=2000,
            sliderlength=20, 
            length=self.minUIWidth,
            orient= tk.HORIZONTAL
        )
        self.sensitivityScl.set(400)

        #########--Seperator Line--#########
        self.sepLine3 = tk.Canvas(master=self.optionsFrame, width=self.minUIWidth, height=4)
        self.sepLine3.create_rectangle(0, 1, self.minUIWidth, 2, fill="black", outline = 'black')
        ####################################

        #Create slider to cut of the videos bottom
        self.cutBottomScl = tk.Scale(
            master=self.optionsFrame,
            label="Cut Off Bottom",
            from_=0, 
            to=(vid.height/2)-10,
            sliderlength=20, 
            length=self.minUIWidth,
            orient= tk.HORIZONTAL
        )
        self.cutBottomScl.set((vid.height/2)-200)

        #Create check box to set cutRightScl to cutLeftScl
        self.simetricalXcut = tk.IntVar()
        self.simetricalXcutScl = tk.Checkbutton(
            master=self.optionsFrame, 
            text='Simetrical X Cut Off',
            variable=self.simetricalXcut,
            onvalue=1,
            offvalue=0
        )
        self.simetricalXcut.set(1)

        #Create slider to cut of the videos left side
        self.cutLeftScl = tk.Scale(
            master=self.optionsFrame,
            label="Cut Off Left",
            from_=0, 
            to=(vid.width/2)-10,
            sliderlength=20, 
            length=self.minUIWidth,
            orient= tk.HORIZONTAL
        )
        self.cutLeftScl.set(500)

        #Create slider to cut of the videos right side
        self.cutRightScl = tk.Scale(
            master=self.optionsFrame,
            label="Cut Off Right",
            from_=0, 
            to=(vid.width/2)-10,
            sliderlength=20, 
            length=self.minUIWidth,
            orient= tk.HORIZONTAL
        )
        self.cutRightScl.set(500)

        #########--Seperator Line--#########
        self.sepLine4 = tk.Canvas(master=self.optionsFrame, width=self.minUIWidth, height=4)
        self.sepLine4.create_rectangle(0, 1, self.minUIWidth, 3, fill="black", outline = 'black')
        ####################################
        #########--Seperator Line--#########
        self.sepLine5 = tk.Canvas(master=self.optionsFrame, width=self.minUIWidth, height=4)
        self.sepLine5.create_rectangle(0, 1, self.minUIWidth, 3, fill="black", outline = 'black')
        ####################################

        #Create Button for "user manually selects the modle"
        self.manualHasStarted = 0
        self.manaulSelectBtn = tk.Button(
            master=self.optionsFrame,
            text="Start Manual Detection",
            width=int(self.minUIWidth/8),
            height=2,
            command=self.start_manual
        )

        #########--Seperator Line--#########
        self.sepLine6 = tk.Canvas(master=self.optionsFrame, width=self.minUIWidth, height=4)
        self.sepLine6.create_rectangle(0, 1, self.minUIWidth, 2, fill="black", outline = 'black')
        ####################################

        MANUALOBJNUM = list(range(1, 5))

        #Create drop down box for spesifiying the number objects for manual detection
        self.noOfModels = tk.StringVar(self.manualSampelObjects)
        self.noOfModels.set(1)

        self.mObjectsLbl = tk.Label(
            master=self.manualSampelObjects,
            text="Number of Models",
        )

        self.mObjectsOpt = tk.OptionMenu(
            self.manualSampelObjects, 
            self.noOfModels, 
            *MANUALOBJNUM
        )


        #--Dispay UI Elements--
        self.videoFrame.pack(side=tk.RIGHT)
            #self.autoLblFrame.pack()
            #self.initialSamplesFrame.pack()
        self.optionsFrame.pack()
        self.manualSampelObjects.pack()

        self.canvas.pack()

        self.startSep.pack()
            #self.startBtn.pack()
            #self.sepLine.pack()#------
            #self.cpsLbl.grid(row=0, column=0)
            #self.cpsOpt.grid(row=0, column=1)
            #self.cdLbl.grid(row=1, column=0)
            #self.cdOpt.grid(row=1, column=1)
        self.autoStatusLbl.pack()
        self.sepLine1.pack()#------
        self.vividChk.pack()
        self.sepLine2.pack()#------
        self.sensitivityScl.pack()
        self.sepLine3.pack()#------
        self.cutBottomScl.pack()
        self.simetricalXcutScl.pack()
        self.cutLeftScl.pack()
        self.cutRightScl.pack()
        self.sepLine4.pack()#------
        self.sepLine5.pack()#------
        self.manaulSelectBtn.pack()
        self.sepLine6.pack()#------
        self.mObjectsLbl.grid(row=0, column=0)
        self.mObjectsOpt.grid(row=0, column=1)

    #def start_auto(self):
    #    if self.autoHasStarted == 0 and self.manualHasStarted == 0:
    #        #Inital print frame for sample based background removal
    #        self.currentStartingFramesGot = 0
    #        self.initialFrames = []
    #        self.initialFrames.clear()

    #        self.totalCapFramesNeeded = int(self.captureDuration.get()) * int(self.capturesPerSecond.get())
    #        self.initialFramesGot = 0

    #        self.autoHasStarted = 1
    #        self.startBtn.config(text="Stop Auto Detection")
    #    else:
    #        self.autoHasStarted = 0
    #        self.startBtn.config(text="Start Auto Detection")

    def start_manual(self):
        if self.manualHasStarted == 0:
            #Inital print frame for sample based background removal
            self.multiTracker = cv2.MultiTracker_create()
            self.boxesGot = 0

            #Reset auto detection
            #self.autoHasStarted = 0
            self.autoStatusLbl.config(text="Automatic Detection (-OFF-)")

            self.manualHasStarted = 1
            self.manaulSelectBtn.config(text="Stop Manual Detection")
        elif self.boxesGot == 1:
            self.manualHasStarted = 0
            self.manaulSelectBtn.config(text="Start Manual Detection")
            self.multiTracker.clear()

