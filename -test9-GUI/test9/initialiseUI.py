import tkinter as tk
import numpy as np
from PIL import Image, ImageTk
import cv2

#Initilise and handle tkinter ui elements
class UI:
    def __init__(self, vidWidth, vidHeight, uiVals):

        self.uiVals = uiVals

        #Bools to give GUI indecation when sliders are used 
        self.valuesChange = False

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
            width=vidWidth, 
            height=vidHeight
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

        #Create check box to ignore dull colour (aka. the printer)
        self.vivid = tk.IntVar()
        self.vividChk = tk.Checkbutton(
            master=self.optionsFrame, 
            text='Vivid Colour Mode',
            variable=self.vivid,
            onvalue=180,
            offvalue=120,
            command=self.update_ui_vals
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
            command=self.update_ui_vals
        )

        #########--Seperator Line--#########
        self.sepLine3 = tk.Canvas(master=self.optionsFrame, width=self.minUIWidth, height=4)
        self.sepLine3.create_rectangle(0, 1, self.minUIWidth, 2, fill="black", outline = 'black')
        ####################################

        #Create slider to cut of the videos bottom
        self.cutBottomScl = tk.Scale(
            master=self.optionsFrame,
            label="Cut Off Bottom",
            from_=0, 
            to=int(vidHeight/2)-10,
            sliderlength=20, 
            length=self.minUIWidth,
            orient= tk.HORIZONTAL,
            command=self.update_ui_vals
        )

        #Create check box to set cutRightScl to cutLeftScl
        self.simetricalXcut = tk.IntVar()
        self.simetricalXcutScl = tk.Checkbutton(
            master=self.optionsFrame, 
            text='Simetrical X Cut Off',
            variable=self.simetricalXcut,
            onvalue=True,
            offvalue=False
        )
        self.simetricalXcut.set(True)

        #Create slider to cut of the videos left side
        self.cutLeftScl = tk.Scale(
            master=self.optionsFrame,
            label="Cut Off Left",
            from_=0, 
            to=int(vidWidth/2)-10,
            sliderlength=20, 
            length=self.minUIWidth,
            orient= tk.HORIZONTAL,
            command=self.update_ui_vals
        )

        #Create slider to cut of the videos right side
        self.cutRightScl = tk.Scale(
            master=self.optionsFrame,
            label="Cut Off Right",
            from_=0, 
            to=int(vidWidth/2)-10,
            sliderlength=20, 
            length=self.minUIWidth,
            orient= tk.HORIZONTAL,
            command=self.update_ui_vals
        )

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
        self.manualHasStarted = False
        self.manualHasStopped = False
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

        self.mObjectsLbl = tk.Label(
            master=self.manualSampelObjects,
            text="Number of Models",
        )

        self.mObjectsOpt = tk.OptionMenu(
            self.manualSampelObjects, 
            self.noOfModels, 
            *MANUALOBJNUM,
            command=self.update_ui_vals
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
            label="Time Before Dection Is Certain (Secs)",
            from_=5, 
            to=120,
            sliderlength=20, 
            length=self.minUIWidth,
            orient= tk.HORIZONTAL,
            command=self.update_ui_vals
        )

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
            command=self.update_ui_vals
        )

        #set the intrface starting values 
        self.update_ui_interface()

        #--Dispay UI Elements--
        self.videoFrame.pack(side=tk.RIGHT)
        self.optionsFrame.pack()
        self.manualSampelObjects.pack()
        self.universalSetting.pack()

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

        self.canvas.pack()

    def start_manual(self):
        if self.manualHasStarted == 0:
            self.manualHasStarted = True
            self.manaulSelectBtn.config(text="Stop Manual Detection")
        else:
            self.manualHasStopped = True
            self.manaulSelectBtn.config(text="Start Manual Detection")

    #change the values for the gui interface options
    def update_ui_interface(self): 
        vivid, certianTimeScl, failureRangeScl, cutLeftScl, cutRightScl, cutBottomScl, sensitivityScl, noOfModels = self.uiVals.get_vals()

        self.vivid.set(vivid)
        self.sensitivityScl.set(sensitivityScl)
        self.cutBottomScl.set(cutBottomScl)
        self.cutLeftScl.set(cutLeftScl)
        self.cutRightScl.set(cutRightScl)
        self.noOfModels.set(noOfModels)
        self.certianTimeScl.set(certianTimeScl)
        self.failureRangeScl.set(failureRangeScl)

    #change the values of the uiValues class
    def update_ui_vals(self, value=0):

        self.valuesChange = True

        vivid = self.vivid.get()
        certianTimeScl = self.certianTimeScl.get()
        failureRangeScl = self.failureRangeScl.get()
        cutLeftScl = self.cutLeftScl.get()
        cutRightScl = self.cutRightScl.get()
        cutBottomScl = self.cutBottomScl.get()
        sensitivityScl = self.sensitivityScl.get()
        noOfModels = self.noOfModels.get()

        #lock the two vertical sliders
        if self.simetricalXcut.get() == True:
            self.cutRightScl.set(cutLeftScl)
            cutRightScl = cutLeftScl

        self.uiVals.set_vals(vivid, certianTimeScl, failureRangeScl, cutLeftScl, cutRightScl, cutBottomScl, sensitivityScl, noOfModels)

    
