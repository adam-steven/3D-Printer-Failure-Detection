import cv2
import constants
import concurrent.futures
#Remove if not using pi
from gpiozero import LED
from gpiozero import Buzzer
from time import sleep
#------
import smtplib
import imghdr
from email.message import EmailMessage
from datetime import datetime

#Alert User
def alert(frame):
    print("PRINT FAILURE")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        if constants.USING_PI == "LED":
            executor.submit(led_alert)
        elif constants.USING_PI == "BUZZER":
            executor.submit(buzzer_alert)
        else:
            cv2.imshow("Failure Img", frame)

        if constants.FROM_EMAIL_ADDRESS != "" and constants.EMAIL_APP_ACCESS_PASS != "" and constants.TO_EMAIL_ADDRESS != "":
            executor.submit(send_email, frame)
    return

def led_alert():
    led = LED(constants.GPIO_PIN)
    for _ in range(150): #flash for 30 min
        led.toggle()
        sleep(0.2)
   
def buzzer_alert():
    buzzer = Buzzer(constants.GPIO_PIN)
    for _ in range(8):  #beep 4 times
        buzzer.toggle()
        sleep(1)

def send_email(frame):
    cv2.imwrite('failedPrint.jpg', frame) 

    now = datetime.now()
    dateTime = now.strftime("%H:%M:%S, %d/%m/%Y")

    msg = EmailMessage()
    msg['Subject'] = 'Print Failure Alert!!!'
    msg['From'] = constants.FROM_EMAIL_ADDRESS
    msg['To'] = constants.TO_EMAIL_ADDRESS
    msg['X-Priority'] = '2'
    msg.set_content('Your printer may have failed at {}. Please see the attached image.'.format(dateTime))

    with open('failedPrint.jpg', 'rb') as f:
        file_data = f.read()
        file_type = imghdr.what(f.name)
        file_name = f.name

    msg.add_attachment(file_data, maintype='image', subtype=file_type, filename=file_name)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(constants.FROM_EMAIL_ADDRESS, constants.EMAIL_APP_ACCESS_PASS)

        smtp.send_message(msg)
