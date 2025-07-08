import RPi.GPIO as GPIO
from hx711 import HX711

dt=5
sck=6

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(dt, GPIO.IN)
GPIO.setup(sck, GPIO.OUT)


hx711= HX711(dout_pin=dt, pd_sck_pin=sck)
'''
hx711.zero()
print("Dovršeno.Postavi težinu")
'''


hx711.set_offset(int(hx711.get_weight_mean(10)))
print("Dovršeno.Postavi težinu")


try:
    while True:
        weight=hx711.get_weight_mean(10)
        print(f"weight:{weight:.2f}grams")
except KeyboardInterrupt:
    print("Exiting")
    
finally:
    hx711.power_down()
    GPIO.cleanup()
    