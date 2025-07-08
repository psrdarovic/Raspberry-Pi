import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()

try:
    data_to_write="Zuti tu si"
    
    print("Place your card near the reader")
    reader.write(data_to_write)
    print("data written to the card successfully!")

finally:
    GPIO.cleanup()