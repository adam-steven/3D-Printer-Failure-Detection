#Variables The User Can Change Before Running The Progam

#UI Constants In UIValues.py

#failure alert variables 
USING_PI = "" # "LED" || "BUZZER" || ""
GPIO_PIN = 4

FROM_EMAIL_ADDRESS = ""
EMAIL_APP_ACCESS_PASS = ""
TO_EMAIL_ADDRESS = ""

#main app
FILTER_FPS = 1 #how many frames are proccessed per SECONDS
FAILER_TIMER = 10  #how many SECONDS of missed modle detection before a failure is garenteed 

#initialising frame variables
FSM_TIMER = 5 #how many SECONDS of movement detection before the detection state switchs (ENGAGED -> STARTING -> DETECTING | OFF -> ENGAGED)

#manual detection
MANUAL_FPS = 25 #how many frames are proccessed per SECONDS

#read capture 
FRAME_WIDTH = 720 #max camera feed width
FRAME_HEIGHT = 480 #max camera feed height





