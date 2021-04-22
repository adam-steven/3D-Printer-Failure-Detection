#Variables The User Can Change Before Running The Progam

#Failure alert variables 
USING_PI = "" # "LED" || "BUZZER" || ""
GPIO_PIN = 4

FROM_EMAIL_ADDRESS = "" #sender email address 
EMAIL_APP_ACCESS_PASS = "" #EMAIL_APP_ACCESS_PASS != email password (for gmail go to https://myaccount.google.com/apppasswords)
TO_EMAIL_ADDRESS = "" #reciever email address 

#Main app
FILTER_FPS = 1 #how many frames are proccessed per SECONDS
FAILER_TIMER = 15  #how many SECONDS of missed modle detection before a failure is garenteed 

#Initialising frame variables
FSM_TIMER = 5 #how many SECONDS of movement detection before the detection state switchs (ENGAGED -> STARTING -> DETECTING | OFF -> ENGAGED)
STARTING_STATE_FAIL_SAFE = 20 #if the STARTING state does not switch to DETECTING before this many captured frames, force the FSM to switch

#Manual detection
MANUAL_FPS = 25 #how many frames are proccessed per SECONDS

#Read capture 
FRAME_WIDTH = 720 #max camera feed width
FRAME_HEIGHT = 480 #max camera feed height

#GUI 
#UI Start Values In UIValues.py
GUI_WIDTH = 250 #width of the Left GUI elements (does not affect the camera feed size)  




