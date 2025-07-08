
import time
import os
import json
from datetime import datetime
import RPi.GPIO as GPIO
from gpiozero import Servo
from hx711 import HX711
from mfrc522 import SimpleMFRC522

# Pokušaj uključivanja LCD-a
try:
    from RPLCD.i2c import CharLCD
    lcd = CharLCD('PCF8574', 0x27)
except Exception as e:
    print( "LCD nije pronađen:", e)
    lcd = None

# ------------------
# PIN KONFIGURACIJA
# ------------------
DT = 5          # HX711 data
SCK = 6         # HX711 clock
SERVO_PIN = 23  # Servo signal

# ------------------
# INICIJALIZACIJA
# ------------------
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

hx = HX711(dout_pin=DT, pd_sck_pin=SCK)
rfid_reader = SimpleMFRC522()
servo = Servo(SERVO_PIN)
servo.value = None  # servo u mirovanju

# Korisnici
users = {
    "1037899540957": "Zuti",
    "907446455955": "Sivko"
}

# ------------------
# TARA I KALIBRACIJA
# ------------------
print("Tariranje vage...")
if lcd:
    lcd.clear()
    lcd.write_string("Tariram...")

offset = hx.get_raw_data_mean(15)
print(f"[INFO] Offset: {offset}")
time.sleep(1)

known_weight = 42
input(f"Stavi {known_weight}g i stisni ENTER...")
raw_with_weight = hx.get_raw_data_mean(15)
calibration_factor = (raw_with_weight - offset) / known_weight
print(f"[INFO] Kalibracijski faktor: {calibration_factor:.4f}")

# ------------------
# GLAVNA PETLJA
# ------------------
print("Spremno: RFID + vaga + servo")
try:
    while True:
        if lcd:
            lcd.clear()
            lcd.write_string("Prisloni RFID...")
        print("Cekanje na RFID...")

        id, text = rfid_reader.read()
        user_id = str(id).strip()

        weight = (hx.get_raw_data_mean(10) - offset) / calibration_factor
        rounded = round(weight)

        if user_id in users:
            name = users[user_id]
            now = datetime.now().strftime("%d.%m.%Y %H:%M")
            print(f"{name} ({user_id}) → {rounded}g u {now}")
            if lcd:
                lcd.clear()
                lcd.write_string(f"{name}\n{rounded}g")

            print("Servo aktiviran!")
            servo.value = 0.2
            time.sleep(0.4)
            servo.value = None
        else:
            print(f"Nepoznat RFID: {user_id}")
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
