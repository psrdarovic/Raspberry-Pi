import RPi.GPIO as GPIO
from gpiozero import Servo
import time

servoPin=23
button=26
buttonState=False
buttonPress=False
servo = Servo(servoPin)

webFeeder=False

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print('Raspberry Pi Servo');
try:
    while True:
        if GPIO.input(button)==False and buttonPress==False:
            buttonPress=True
            if buttonState==False:
                buttonState=True
            else:
                buttonState=False
        if GPIO.input(button)==True and buttonPress==True:
            buttonPress=False
       
        if buttonState==True:
            buttonState=False
            #servo.mid()
            servo.value=0.2
            time.sleep(0.19)
            #servo.detach()
        elif buttonState==False:
            servo.detach()
            
        
        
        '''
        if buttonState==True:
            #servo.value=0.9
            servo.mid()
            print('mid')
        elif buttonState==False:
            servo.detach()
        ''' 
    
except KeyboardInterrupt:
    print('Program stop')
