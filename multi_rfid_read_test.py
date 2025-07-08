import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from time import sleep

reader = SimpleMFRC522()

try:
    while True:
        print("Place your card near the reader")
        id, text = reader.read()
        
        if id is not None:
            print("ID: %s\nText: %s" % (id, text))
            sleep(3)
            

except KeyboardInterrupt:
    print("Exiting...")
finally:
    GPIO.cleanup()