
import time
import os
import json
from hx711 import HX711
from RPLCD.i2c import CharLCD
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from datetime import datetime

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
    print("LCD nije pronađen:", e)
    lcd = None

hx = HX711(dout_pin=DT, pd_sck_pin=SCK)
rfid_reader = SimpleMFRC522()

# Poznati korisnici
users = {
    "1037899540957": "Zuti",
    "907446455955": "Sivko"
}

# ------------------
# Tare funkcija
# ------------------
print("Tariranje... makni sve s vage.")
if lcd:
    lcd.clear()
    lcd.write_string("Tariranje...")

offset = hx.get_raw_data_mean(15)
print(f"[INFO] Offset (tara): {offset}")
time.sleep(1)

# ------------------
# Kalibracija - koristi poznatu masu
# ------------------
known_weight = 42 # grama
input(f"Stavi {known_weight}g na vagu i stisni ENTER...")

raw_with_weight = hx.get_raw_data_mean(15)
calibration_factor = (raw_with_weight - offset) / known_weight
print(f"[INFO] Kalibracijski faktor: {calibration_factor:.4f}")

# ------------------
# Glavna petlja
# ------------------
print("\n Spremno: očitava težinu i čita RFID (CTRL+C za prekid)")
if lcd:
    lcd.clear()
    lcd.write_string("Spremno za RFID...")

try:
    while True:
        # RFID
        if lcd:
            lcd.clear()
            lcd.write_string("Prisloni RFID...")
        print("Cekanje na RFID...")

        id, text = rfid_reader.read()
        user_id = str(id).strip()

        # očitanje težine
        raw = hx.get_raw_data_mean(10)
        weight = (raw - offset) / calibration_factor
        rounded = round(weight)

        if user_id in users:
            name = users[user_id]
            timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")
            print(f"{name} ({user_id}) jeo {rounded}g [{timestamp}]")
            if lcd:
                lcd.clear()
                lcd.write_string(f"{name}\n{rounded}g")
        else:
            print(f" Nepoznat RFID: {user_id}")
            if lcd:
                lcd.clear()
                lcd.write_string("Nepoznat RFID!")

        time.sleep(2)

except KeyboardInterrupt:
    print("\nPrekinuto od strane korisnika.")
finally:
    if lcd:
        lcd.clear()
    GPIO.cleanup()
