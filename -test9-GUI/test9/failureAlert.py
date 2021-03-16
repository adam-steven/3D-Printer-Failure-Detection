import cv2
from constants import USING_PI, FROM_EMAIL_ADDRESS, EMAIL_APP_ACCESS_PASS, TO_EMAIL_ADDRESS, GPIO_PIN
import concurrent.futures
#---Can be removed if not using pi---
from gpiozero import LED
from gpiozero import Buzzer
from time import sleep
#------------------------------------
import smtplib
import imghdr
from email.message import EmailMessage
from datetime import datetime

#Alert the user of a failure
def alert(frame):
    print("PRINT FAILURE")

    #Split task into a new thread to minimise Main freezing
    with concurrent.futures.ThreadPoolExecutor() as executor:
        #Local error alert methods
        if USING_PI == "LED":
            executor.submit(led_alert)
        elif USING_PI == "BUZZER":
            executor.submit(buzzer_alert)
        else:
            cv2.imshow("Failure Img", frame)

        #Global error alert method (email)
        if FROM_EMAIL_ADDRESS != "" and EMAIL_APP_ACCESS_PASS != "" and TO_EMAIL_ADDRESS != "":
            executor.submit(send_email, frame)
    return

def led_alert():
    led = LED(GPIO_PIN)
    for _ in range(150): #flash LED for 30 seconds
        led.toggle()
        sleep(0.2)
   
def buzzer_alert():
    buzzer = Buzzer(GPIO_PIN)
    for _ in range(8):  #buzzer beep 4 times (8 seconds)
        buzzer.toggle()
        sleep(1)

def send_email(frame):
    #Error frame converted to an img file for sending
    cv2.imwrite('failedPrint.jpg', frame) 

    #Time Stamp
    now = datetime.now()
    dateTime = now.strftime("%H:%M:%S, %d/%m/%Y")

    #Email construction (text portion)
    msg = EmailMessage()
    msg['Subject'] = 'Print Failure Alert!!!'
    msg['From'] = FROM_EMAIL_ADDRESS
    msg['To'] = TO_EMAIL_ADDRESS
    msg['X-Priority'] = '2' #X-Priority 2 specifies importance
    msg.set_content('Your printer may have failed at {}. Please see the attached image.'.format(dateTime))

    #Attach image
    with open('failedPrint.jpg', 'rb') as f:
        file_data = f.read()
        file_type = imghdr.what(f.name)
        file_name = f.name
    msg.add_attachment(file_data, maintype='image', subtype=file_type, filename=file_name)

    #Send email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(FROM_EMAIL_ADDRESS, EMAIL_APP_ACCESS_PASS) #EMAIL_APP_ACCESS_PASS != email password (for gmail go to https://myaccount.google.com/apppasswords)
        smtp.send_message(msg)
