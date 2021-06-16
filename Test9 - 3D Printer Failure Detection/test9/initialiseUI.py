import tkinter as tk
from constants import GUI_WIDTH

#Initilise and handle tkinter ui elements
class UI:
    def __init__(self, vidWidth, vidHeight, uiVals):

        self.uiVals = uiVals

        #Bools to give GUI indecation when sliders are used 
        self.valuesChange = False

        #Initialise GUI containors
        guiContatianer = tk.Frame()
        feedContatianer = tk.Frame()

        optionsFrame = tk.Frame(guiContatianer)
        manualSampelObjects = tk.Frame(guiContatianer)
        universalSetting = tk.Frame(guiContatianer)
        videoFrame = tk.Frame(feedContatianer)
        minUIWidth = GUI_WIDTH


        #--Initialise UI Elements--
        #Create canvas from video source
        self.canvas = tk.Canvas(
            master=videoFrame, 
            width=vidWidth, 
            height=vidHeight
        )

        #########--Seperator (top gap)--#########
        startSep = tk.Canvas(master=optionsFrame, width=minUIWidth, height=4)
        startSep.create_rectangle(0, 1, minUIWidth, 3, fill="black", outline = 'black')
        ####################################

        self.autoStatusLbl = tk.Label(
            master=optionsFrame,
            text="Automatic Detection (-ENGAGED-)"
        )

        #########--Seperator Line--#########
        sepLine1 = tk.Canvas(master=optionsFrame, width=minUIWidth, height=4)
        sepLine1.create_rectangle(0, 1, minUIWidth, 3, fill="black", outline = 'black')
        ####################################

        #Create check box to ignore dull colour (aka. the printer)
        self.vivid = tk.IntVar()
        self.vividChk = tk.Checkbutton(
            master=optionsFrame, 
            text='Vivid Colour Mode',
            variable=self.vivid,
            onvalue=180,
            offvalue=120,
            command=self.update_ui_vals
        )

        #########--Seperator Line--#########
        sepLine2 = tk.Canvas(master=optionsFrame, width=minUIWidth, height=4)
        sepLine2.create_rectangle(0, 1, minUIWidth, 2, fill="black", outline = 'black')
        ####################################

        #Create slider for BLOB area threshold
        self.sensitivityScl = tk.Scale(
            master=optionsFrame,
            label="Object Size Threshold (Area)",
            from_=200, 
            to=2000,
            sliderlength=20, 
            length=minUIWidth,
            orient= tk.HORIZONTAL,
            command=self.update_sensitivity
        )

        #########--Seperator Line--#########
        sepLine3 = tk.Canvas(master=optionsFrame, width=minUIWidth, height=4)
        sepLine3.create_rectangle(0, 1, minUIWidth, 2, fill="black", outline = 'black')
        ####################################

        #Create slider to cut of the videos bottom
        self.cutBottomScl = tk.Scale(
            master=optionsFrame,
            label="Cut Off Bottom",
            from_=0, 
            to=int(vidHeight/2)-10,
            sliderlength=20, 
            length=minUIWidth,
            orient= tk.HORIZONTAL,
            command=self.update_crop
        )

        #Create check box to set cutRightScl to cutLeftScl
        self.simetricalXcut = tk.BooleanVar()
        self.simetricalXcutScl = tk.Checkbutton(
            master=optionsFrame, 
            text='Simetrical X Cut Off',
            variable=self.simetricalXcut,
            onvalue=True,
            offvalue=False,
            command=self.update_crop
        )
        self.simetricalXcut.set(True)

        #Create slider to cut of the videos left side
        self.cutLeftScl = tk.Scale(
            master=optionsFrame,
            label="Cut Off Left",
            from_=0, 
            to=int(vidWidth/2)-10,
            sliderlength=20, 
            length=minUIWidth,
            orient= tk.HORIZONTAL,
            command=self.update_crop
        )

        #Create slider to cut of the videos right side
        self.cutRightScl = tk.Scale(
            master=optionsFrame,
            label="Cut Off Right",
            from_=0, 
            to=int(vidWidth/2)-10,
            sliderlength=20, 
            length=minUIWidth,
            orient= tk.HORIZONTAL,
            command=self.update_crop
        )

        #########--Seperator Line--#########
        sepLine4 = tk.Canvas(master=optionsFrame, width=minUIWidth, height=4)
        sepLine4.create_rectangle(0, 1, minUIWidth, 3, fill="black", outline = 'black')
        ####################################

        manualLbl = tk.Label(
            master=optionsFrame,
            text="Manual Detection"
        )

        #########--Seperator Line--#########
        sepLine5 = tk.Canvas(master=optionsFrame, width=minUIWidth, height=4)
        sepLine5.create_rectangle(0, 1, minUIWidth, 3, fill="black", outline = 'black')
        ####################################

        #Create Button for "user manually selects the modle"
        self.manualHasStarted = False
        self.manualHasStopped = False
        self.manaulSelectBtn = tk.Button(
            master=optionsFrame,
            text="Start Manual Detection",
            width=int(minUIWidth/8),
            height=2,
            command=self.start_manual
        )

        #########--Seperator Line--#########
        sepLine6 = tk.Canvas(master=optionsFrame, width=minUIWidth, height=4)
        sepLine6.create_rectangle(0, 1, minUIWidth, 2, fill="black", outline = 'black')
        ####################################

        MANUALOBJNUM = list(range(1, 5))

        #Create drop down box for spesifiying the number objects for manual detection
        self.noOfModels = tk.StringVar(manualSampelObjects)

        mObjectsLbl = tk.Label(
            master=manualSampelObjects,
            text="Number of Models",
        )

        self.mObjectsOpt = tk.OptionMenu(
            manualSampelObjects, 
            self.noOfModels, 
            *MANUALOBJNUM,
            command=self.update_ui_vals
        )

        #########--Seperator Line--#########
        sepLine7 = tk.Canvas(master=universalSetting, width=minUIWidth, height=4)
        sepLine7.create_rectangle(0, 1, minUIWidth, 3, fill="black", outline = 'black')
        ####################################

        universalLbl = tk.Label(
            master=universalSetting,
            text="Universal Setting"
        )

        #########--Seperator Line--#########
        sepLine8 = tk.Canvas(master=universalSetting, width=minUIWidth, height=4)
        sepLine8.create_rectangle(0, 1, minUIWidth, 3, fill="black", outline = 'black')
        ####################################

        #Create slider to indicate to time before certain
        self.certianTimeScl = tk.Scale(
            master=universalSetting,
            label="Time Before Dection Is Certain (Secs)",
            from_=5, 
            to=120,
            sliderlength=20, 
            length=minUIWidth,
            orient= tk.HORIZONTAL,
            command=self.update_ui_vals
        )

        #########--Seperator Line--#########
        sepLine9 = tk.Canvas(master=universalSetting, width=minUIWidth, height=4)
        sepLine9.create_rectangle(0, 1, minUIWidth, 2, fill="black", outline = 'black')
        ####################################

        #Create slider to indicate to time before certain
        self.failureRangeScl = tk.Scale(
            master=universalSetting,
            label="Horizontal Failure Range",
            from_=5, 
            to=100,
            sliderlength=20, 
            length=minUIWidth,
            orient= tk.HORIZONTAL,
            command= self.update_failure_range
        )

        #set the intrface starting values 
        self.update_ui_interface()

        #--Dispay UI Elements--
        guiContatianer.grid(row=0, column=0)
        feedContatianer.grid(row=0, column=1)

        videoFrame.pack()
        optionsFrame.pack()
        manualSampelObjects.pack()
        universalSetting.pack()

        startSep.pack()#-------
        self.autoStatusLbl.pack()#
        sepLine1.pack()#------
        self.vividChk.pack()
        sepLine2.pack()#------
        self.sensitivityScl.pack()
        sepLine3.pack()#------
        self.cutBottomScl.pack()
        self.simetricalXcutScl.pack()
        self.cutLeftScl.pack()
        self.cutRightScl.pack()
        sepLine4.pack()#------
        manualLbl.pack()#
        sepLine5.pack()#------
        self.manaulSelectBtn.pack()
        sepLine6.pack()#------
        mObjectsLbl.grid(row=0, column=0)
        self.mObjectsOpt.grid(row=0, column=1)
        sepLine7.pack()#------
        universalLbl.pack()#
        sepLine8.pack()#------
        self.certianTimeScl.pack()
        sepLine9.pack()#------
        self.failureRangeScl.pack()

        self.canvas.pack()

    #start and stop manual detection on button press
    def start_manual(self):
        if self.manualHasStarted == 0:
            self.manualHasStarted = True
            self.manaulSelectBtn.config(text="Stop Manual Detection")
        else:
            self.manualHasStopped = True
            self.manaulSelectBtn.config(text="Start Manual Detection")

    #Change the values for the gui interface options from uiValues.py
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

    #----Specify specific GUI elements are being changed----
    def update_crop(self, _=0):
        self.update_ui_vals(_, "Crop")

    def update_sensitivity(self, _=0):
        self.update_ui_vals(_, "Sensitivity")

    def update_failure_range(self, _=0):
        self.update_ui_vals(_, "FailureRange")
    #-------------------------------------------------------

    #Change the values of the uiValues class
    def update_ui_vals(self, _=0, widgetName="NonImp"):

        self.valuesChange = True
        self.widgetName = widgetName

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

    
