import os
import json
import sqlite3
import RPi.GPIO as GPIO
from hx711 import HX711

# Definicija pinova za HX711
dt = 5  # Data pin
sck = 6  # Clock pin

# Postavljanje putanje za spremanje konfiguracije i baze
config_file = "hx711_config.json"
db_file = "vaga_data.db"  # SQLite baza podataka

# Onemogućavanje upozorenja i postavljanje GPIO načina
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# Inicijalizacija HX711
hx711 = HX711(dout_pin=dt, pd_sck_pin=sck)

# Funkcija za očitavanje sirovih podataka
def read_raw_data(num_samples=10):
    raw_data = hx711.get_raw_data_mean(num_samples)
    return raw_data

# Funkcija za spremanje konfiguracije (offset i kalibracijski faktor)
def save_config(offset, calibration_factor):
    config = {"offset": offset, "calibration_factor": calibration_factor}
    with open(config_file, "w") as f:
        json.dump(config, f)
    print(f"Konfiguracija spremljena: {config}")

# Funkcija za učitavanje konfiguracije
def load_config():
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            config = json.load(f)
        print(f"Učitana konfiguracija: {config}")
        return config["offset"], config["calibration_factor"]
    else:
        print("Konfiguracija nije pronađena. Potrebna je inicijalizacija.")
        return None, None

# Funkcija za inicijalizaciju baze podataka
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

# Funkcija za unos podataka u bazu
def save_to_db(naziv, vrijednost):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO podaci (naziv, vrijednost) VALUES (?, ?)', (naziv, vrijednost))
    conn.commit()
    conn.close()

# Tariranje - očitavanje offseta
def tare(num_samples=10):
    print("Tariranje... Molim, ostavi vagu praznom.")
    offset = read_raw_data(num_samples)
    print(f"Offset postavljen na: {offset}")
    return offset

# Kalibracija - izračun kalibracijskog faktora
def calibrate(known_weight, offset, num_samples=10):
    print(f"Stavi poznatu masu od {known_weight}g na vagu.")
    input("Pritisni Enter kada si spreman.")
    raw_data = read_raw_data(num_samples)
    calibration_factor = (raw_data - offset) / known_weight
    print(f"Kalibracijski faktor: {calibration_factor}")
    return calibration_factor

# Očitavanje težine uz offset i kalibracijski faktor
def get_weight(offset, calibration_factor, num_samples=10):
    raw_data = read_raw_data(num_samples)
    weight = (raw_data - offset) / calibration_factor
    return weight

# Funkcija za resetiranje konfiguracije
def reset_calibration():
    if os.path.exists(config_file):
        os.remove(config_file)
        print("Postojeća konfiguracija obrisana.")
    else:
        print("Konfiguracija nije pronađena. Nema što za brisati.")

try:
    # Ponuditi korisniku opciju za resetiranje kalibracije
    reset_choice = input("Želite li resetirati kalibraciju? (da/ne): ").strip().lower()
    if reset_choice == "da":
        reset_calibration()
        offset, calibration_factor = None, None
    else:
        offset, calibration_factor = load_config()

    # Ako konfiguracija ne postoji, inicijaliziraj je
    if offset is None or calibration_factor is None:
        # Tariranje
        offset = tare()

        # Kalibracija
        known_weight = float(input("Unesi težinu poznatog objekta (g) za kalibraciju: "))
        calibration_factor = calibrate(known_weight, offset)

        # Spremanje konfiguracije
        save_config(offset, calibration_factor)

    # Inicijalizacija baze podataka
    init_db()

    # Očitavanje težine i spremanje podataka u bazu
    print("Postavi težinu na vagu za očitanje.")
    while True:
        weight = get_weight(offset, calibration_factor, 10)
        print(f"Težina: {weight:.2f} g")
       
        # Spremanje težine u bazu podataka
        save_to_db('Težina', weight)
        print(f"Težina {weight:.2f} g spremljena u bazu.")
       
except KeyboardInterrupt:
    print("Izlazim iz programa.")
finally:
    # Isključenje HX711 i čišćenje GPIO
    hx711.power_down()
    GPIO.cleanup()