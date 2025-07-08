
import time
import os
import json
from hx711 import HX711
from RPLCD.i2c import CharLCD
import RPi.GPIO as GPIO

# ------------------
# Konfiguracija PINOVA
# ------------------
DT = 5      # Data pin
SCK = 6     # Clock pin
LCD_ADDR = 0x27  # I2C adresa LCD-a

# ------------------
# Inicijalizacija
# ------------------
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

try:
    lcd = CharLCD('PCF8574', LCD_ADDR)
except Exception as e:
    print("❌ LCD nije pronađen:", e)
    lcd = None

hx = HX711(dout_pin=DT, pd_sck_pin=SCK)

# ------------------
# Tare funkcija
# ------------------
print("▶️ Tariranje... makni sve s vage.")
if lcd:
    lcd.clear()
    lcd.write_string("Tariranje...")

offset = hx.get_raw_data_mean(15)
print(f"[INFO] Offset (tara): {offset}")
time.sleep(1)

# ------------------
# Kalibracija - koristi poznatu masu
# ------------------
known_weight = 100  # grama
input(f"▶️ Stavi {known_weight}g na vagu i stisni ENTER...")

raw_with_weight = hx.get_raw_data_mean(15)
calibration_factor = (raw_with_weight - offset) / known_weight
print(f"[INFO] Kalibracijski faktor: {calibration_factor:.4f}")

# ------------------
# Test očitanja u petlji
# ------------------
print("\n▶️ Očitavanje težine (CTRL+C za prekid)")
if lcd:
    lcd.clear()
    lcd.write_string("Mjerenje krece...")

try:
    while True:
        raw = hx.get_raw_data_mean(10)
        weight = (raw - offset) / calibration_factor
        rounded = round(weight)
        print(f"Tezina: {rounded} g")

        if lcd:
            lcd.clear()
            lcd.write_string(f"Tezina: {rounded}g")

        time.sleep(2)

except KeyboardInterrupt:
    print("\nPrekinuto od strane korisnika.")
finally:
    if lcd:
        lcd.clear()
    GPIO.cleanup()
