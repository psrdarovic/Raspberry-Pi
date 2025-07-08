import os
import json
import sqlite3
import RPi.GPIO as GPIO
from hx711 import HX711

# Postavke
dt = 5  # Data pin za HX711
sck = 6  # Clock pin za HX711
config_file = "hx711_config.json"
db_file = "vaga_data.db"

# Inicijalizacija HX711
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
hx711 = HX711(dout_pin=dt, pd_sck_pin=sck)

# Funkcije za rad s konfiguracijom
def save_config(offset, calibration_factor):
    config = {"offset": offset, "calibration_factor": calibration_factor}
    with open(config_file, "w") as f:
        json.dump(config, f)
    print(f"Konfiguracija spremljena: {config}")

def load_config():
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            config = json.load(f)
        print(f"Učitana konfiguracija: {config}")
        return config["offset"], config["calibration_factor"]
    else:
        print("Konfiguracija nije pronađena.")
        return None, None

# Funkcije za inicijalizaciju baze i unos podataka
def init_db():
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS podaci (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        naziv TEXT NOT NULL,
        vrijednost REAL NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    ''')
    conn.commit()
    conn.close()

def save_to_db(naziv, vrijednost):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO podaci (naziv, vrijednost) VALUES (?, ?)', (naziv, vrijednost))
    conn.commit()
    conn.close()

def update_database_record(record_id, new_value):
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute('UPDATE podaci SET vrijednost = ? WHERE id = ?', (new_value, record_id))
        conn.commit()
        print(f"Zapis s ID-om {record_id} ažuriran na {new_value} g.")
    except sqlite3.Error as e:
        print(f"Greška pri ažuriranju zapisa: {e}")
    finally:
        conn.close()

# Funkcije za HX711
def tare(num_samples=10):
    print("Tariranje... Molim, ostavi vagu praznom.")
    offset = hx711.get_raw_data_mean(num_samples)
    print(f"Offset postavljen na: {offset}")
    return offset

def calibrate(known_weight, offset, num_samples=10):
    print(f"Stavi poznatu masu od {known_weight}g na vagu.")
    input("Pritisni Enter kada si spreman.")
    raw_data = hx711.get_raw_data_mean(num_samples)
    calibration_factor = (raw_data - offset) / known_weight
    print(f"Kalibracijski faktor: {calibration_factor}")
    return calibration_factor

def get_weight(offset, calibration_factor, num_samples=10):
    raw_data = hx711.get_raw_data_mean(num_samples)
    weight = (raw_data - offset) / calibration_factor
    return weight

# Funkcija za unos novog kalibracijskog faktora
def update_calibration_factor():
    offset, calibration_factor = load_config()

    if offset is None:
        print("Nema postojeće konfiguracije. Prvo pokrenite tariranje.")
        return

    print(f"Trenutni kalibracijski faktor: {calibration_factor:.6f}")
    try:
        new_calibration_factor = float(input("Unesite novi kalibracijski faktor: "))
        save_config(offset, new_calibration_factor)
        print("Kalibracijski faktor uspješno ažuriran.")
    except ValueError:
        print("Greška: Molimo unesite valjani broj.")

# Glavni program
def main():
    print("Opcije:")
    print("1. Očitavanje težine")
    print("2. Unos novog kalibracijskog faktora")
    print("3. Ažuriranje zapisa u bazi")
    print("4. Izlaz")

    # Učitavanje konfiguracije
    offset, calibration_factor = load_config()
    if offset is None or calibration_factor is None:
        print("Potrebna inicijalizacija.")
        offset = tare()
        known_weight = float(input("Unesi težinu poznatog objekta (g) za kalibraciju: "))
        calibration_factor = calibrate(known_weight, offset)
        save_config(offset, calibration_factor)

    init_db()

    while True:
        try:
            choice = int(input("Odaberite opciju (1-4): "))
            if choice == 1:
                weight = get_weight(offset, calibration_factor, 10)
                print(f"Težina: {weight:.2f} g")
                save_to_db("Težina", weight)
            elif choice == 2:
                update_calibration_factor()
            elif choice == 3:
                record_id = int(input("Unesite ID zapisa: "))
                new_value = float(input("Unesite novu vrijednost (g): "))
                update_database_record(record_id, new_value)
            elif choice == 4:
                print("Izlaz iz programa.")
                break
            else:
                print("Neispravan odabir.")
        except ValueError:
            print("Greška: Molimo unesite valjani broj.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Prekid programa.")
    finally:
        hx711.power_down()
        GPIO.cleanup()
