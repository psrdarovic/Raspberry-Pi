import time
import os
import json
import sqlite3
from datetime import datetime
import threading
from flask import Flask
import RPi.GPIO as GPIO
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
from hx711 import HX711
from mfrc522 import SimpleMFRC522

# ----------------------------
# Flask aplikacija
# ----------------------------
app = Flask(__name__)
PORT = 3002

# ----------------------------
# Servo koristi pigpio PWM
# ----------------------------
factory = PiGPIOFactory()
servo = Servo(23, pin_factory=factory)
time.sleep(1)
servo.value = None

# ----------------------------
# LCD
# ----------------------------
try:
    from RPLCD.i2c import CharLCD
    lcd = CharLCD('PCF8574', 0x27)
except Exception as e:
    print("LCD nije pronađen:", e)
    lcd = None

# ----------------------------
# PIN KONFIGURACIJA
# ----------------------------
DT = 5
SCK = 13

# ----------------------------
# Inicijalizacija GPIO
# ----------------------------
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

hx = HX711(dout_pin=DT, pd_sck_pin=SCK)
rfid_reader = SimpleMFRC522()

# ----------------------------
# RFID korisnici
# ----------------------------
users = {
    "1037899540957": "Zuti",
    "907446455955": "Sivko"
}

# ----------------------------
# SQLite baza
# ----------------------------
CONFIG_FILE= "hx711_config.json"
DB_FILE = "hrana_log.db"

def save_config(offset, factor):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"offset": offset, "calibration_factor": factor}, f)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
        return config["offset"], config["calibration_factor"]
    return None, None


def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS logovi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ime TEXT NOT NULL,
        tezina INTEGER NOT NULL,
        vrijeme TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()

def save_log(name, weight, time_str):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO logovi (ime, tezina, vrijeme) VALUES (?, ?, ?)", (name, weight, time_str))
    conn.commit()
    conn.close()

init_db()
# ----------------------------
# Anti-spam postavke
# ----------------------------
last_feed_time = 0
MIN_INTERVAL = 60  # sekundi
trenutna_kolicina=0

# ----------------------------
# Tariranje i kalibracija
# ----------------------------
offset, calibration_factor = load_config()

if offset is None or calibration_factor is None:
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

    save_config(offset, calibration_factor)
else:
    print(f"[INFO] Učitano iz configa: Offset={offset}, Faktor={calibration_factor:.4f}")

# ----------------------------
# Glavna petlja RFID + vaga
# ----------------------------
def loop_sustav():
    global last_feed_time
    while True:
        weight = (hx.get_raw_data_mean(10) - offset) / calibration_factor
        rounded = round(weight)
        trenutna_kolicina=rounded
       
        if lcd:
            lcd.clear()
            vrijeme=datetime.now().strftime("%H:%M")
            lcd.write_string(f"Yuumi\n{vrijeme}\n{rounded}g")
        print("Čekam RFID...")

        id, text = rfid_reader.read()
        user_id = str(id).strip()

        if user_id in users:
            name = users[user_id]
            now = datetime.now().strftime("%d.%m.%Y %H:%M")
            print(f"{name} ({user_id}) → {rounded}g u {now}")
            if lcd:
                lcd.clear()
                lcd.write_string(f"{name}\n{rounded}g")
                save_log(name, rounded, now)
            else:
                print("Već hranjen nedavno.")
                if lcd:
                    lcd.clear()
                    lcd.write_string("Vec hranjen!")
        else:
            print(f"Nepoznat RFID: {user_id}")
            if lcd:
                lcd.clear()
                lcd.write_string("Nepoznat RFID!")

        time.sleep(2)

# ----------------------------
# Flask rute
# ----------------------------
@app.route("/stanje")
def stanje():
    return str(round((hx.get_raw_data_mean(10) - offset) / calibration_factor))

@app.route("/otvori")
def otvori():
    global last_feed_time
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    if time.time() - last_feed_time > MIN_INTERVAL:
        print("Hranjenje pokrenuto putem weba!")
        servo.value = 0.07
        time.sleep(1)
        servo.value = None
        last_feed_time = time.time()
        save_log("Feeding", 0, now)
        return "Hrana izbačena!"
    else:
        return " Već hranjeno nedavno!"

@app.route("/log")
def log():
    conn = sqlite3.connect("hrana_log.db")
    c = conn.cursor()
    c.execute("SELECT ime, tezina, vrijeme FROM logovi ORDER BY id DESC LIMIT 10")
    podaci = c.fetchall()
    conn.close()
    return "\n".join([f"{ime} - {tezina}g - {vrijeme}" for ime, tezina, vrijeme in podaci])
    print(podaci)

# ----------------------------
# Pokretanje
# ----------------------------
init_db()

if __name__ == "__main__":
    try:
        threading.Thread(target=loop_sustav, daemon=True).start()
        app.run(host="0.0.0.0", port=PORT)
    except KeyboardInterrupt:
        print("\nPrekinuto od strane korisnika.")
    finally:
        if lcd:
            lcd.clear()
        GPIO.cleanup()