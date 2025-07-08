import RPi.GPIO as GPIO
from hx711 import HX711

dout_pin=5
sck_pin=6

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(dout_pin, GPIO.IN)
GPIO.setup(sck_pin, GPIO.OUT)


hx711= HX711(dout_pin=dout_pin, sck_pin=sck_pin, gain_channel_A=128, select_channel='A')

hx711.tare("Dovršeno.Postavi težinu")
try:
    while True:
        weight=hx711.get_weight_mean(10)
        print(f"weight:{weight:.2f}grams")
except KeyboardInterrupt:
    print("Exiting")
    
finally:
    hx711.power_down()
    GPIO.cleanup()
    
    