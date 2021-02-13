import tkinter as tk
import numpy as np
from PIL import Image, ImageTk
import cv2
import numpy as np

#Initilise and handle tkinter ui elements
class UI:
    def __init__(self, vid):

        #Bools to give GUI indecation when sliders are used 
        self.autoSensitivityChange = False
        self.failureRangeChange = False

        #Initialise GUI containors
        self.optionsFrame = tk.Frame()
        self.manualSampelObjects = tk.Frame()
        self.universalSetting = tk.Frame()
        self.videoFrame = tk.Frame()
        self.minUIWidth = 200

        #Grid used to add labels to the options menus
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
        self.startSep.create_rectangle(0, 1, self.minUIWidth, 3, fill="black", outline = 'black')
        ####################################

        self.autoStatusLbl = tk.Label(
            master=self.optionsFrame,
            text="Automatic Detection (-ENGAGED-)"
        )

        #########--Seperator Line--#########
        self.sepLine1 = tk.Canvas(master=self.optionsFrame, width=self.minUIWidth, height=4)
        self.sepLine1.create_rectangle(0, 1, self.minUIWidth, 3, fill="black", outline = 'black')
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
            label="Object Size Threshold (Area)",
            from_=200, 
            to=2000,
            sliderlength=20, 
            length=self.minUIWidth,
            orient= tk.HORIZONTAL,
            command=self.auto_sensitivity_change
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

        self.manualLbl = tk.Label(
            master=self.optionsFrame,
            text="Manual Detection"
        )

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

        #########--Seperator Line--#########
        self.sepLine7 = tk.Canvas(master=self.universalSetting, width=self.minUIWidth, height=4)
        self.sepLine7.create_rectangle(0, 1, self.minUIWidth, 3, fill="black", outline = 'black')
        ####################################

        self.universalLbl = tk.Label(
            master=self.universalSetting,
            text="Universal Setting"
        )

        #########--Seperator Line--#########
        self.sepLine8 = tk.Canvas(master=self.universalSetting, width=self.minUIWidth, height=4)
        self.sepLine8.create_rectangle(0, 1, self.minUIWidth, 3, fill="black", outline = 'black')
        ####################################

        #Create slider to indicate to time before certain
        self.certianTimeScl = tk.Scale(
            master=self.universalSetting,
            label="Time Before Failure Is Certain (Secs)",
            from_=5, 
            to=300,
            sliderlength=20, 
            length=self.minUIWidth,
            orient= tk.HORIZONTAL
        )
        self.certianTimeScl.set(60)

        #########--Seperator Line--#########
        self.sepLine9 = tk.Canvas(master=self.universalSetting, width=self.minUIWidth, height=4)
        self.sepLine9.create_rectangle(0, 1, self.minUIWidth, 2, fill="black", outline = 'black')
        ####################################

        #Create slider to indicate to time before certain
        self.failureRangeScl = tk.Scale(
            master=self.universalSetting,
            label="Horizontal Failure Range",
            from_=5, 
            to=100,
            sliderlength=20, 
            length=self.minUIWidth,
            orient= tk.HORIZONTAL,
            command=self.failure_range_change
        )
        self.failureRangeScl.set(30)


        #--Dispay UI Elements--
        self.videoFrame.pack(side=tk.RIGHT)
        self.optionsFrame.pack()
        self.manualSampelObjects.pack()
        self.universalSetting.pack()

        self.canvas.pack()

        self.startSep.pack()#-------
        self.autoStatusLbl.pack()#
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
        self.manualLbl.pack()#
        self.sepLine5.pack()#------
        self.manaulSelectBtn.pack()
        self.sepLine6.pack()#------
        self.mObjectsLbl.grid(row=0, column=0)
        self.mObjectsOpt.grid(row=0, column=1)
        self.sepLine7.pack()#------
        self.universalLbl.pack()#
        self.sepLine8.pack()#------
        self.certianTimeScl.pack()
        self.sepLine9.pack()#------
        self.failureRangeScl.pack()

    def start_manual(self):
        if self.manualHasStarted == 0:
            #Inital print frame for sample based background removal
            self.multiTracker = cv2.MultiTracker_create()
            self.boxesGot = 0
            self.objectCentrePositions = []

            #Reset auto detection
            self.autoStatusLbl.config(text="Automatic Detection (-OFF-)")

            self.manualHasStarted = 1
            self.manaulSelectBtn.config(text="Stop Manual Detection")
        elif self.boxesGot == 1:
            self.manualHasStarted = 0
            self.manaulSelectBtn.config(text="Start Manual Detection")
            self.multiTracker.clear()
            self.objectCentrePositions.clear()


    def auto_sensitivity_change(self, value):
        self.autoSensitivityChange = True

    def failure_range_change(self, value):
        self.failureRangeChange = True
